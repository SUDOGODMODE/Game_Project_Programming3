"""Reproduzierbarer lokaler Nachweis mit zwei oder drei echten Tk-Fenstern und TCP.

Die absichtlich bekannten Testflotten und Mitschnitte beider Testsichten
sind kein Fremdrechnernachweis und kein öffentlicher Spielmitschnitt.
"""
import argparse
from copy import deepcopy
from datetime import datetime
import json
import os
from pathlib import Path
import re
import signal
import socket
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from client_gui import BattleshipWindow, tk
from tests.fixtures import FLEET, FLEET_CELLS, MISSES


def server_command(profile, repo_root, python, port, log_file):
    """Der Profilmodus nutzt den echten Starteinstieg statt direkt server.py."""
    if profile is None:
        return [python, "-u", str(repo_root / "src/server.py"), "--host", "127.0.0.1",
                "--port", str(port), "--log-file", str(log_file)]
    if profile != "localhost":
        raise ValueError(f"Unbekanntes Serverprofil: {profile}")
    if type(port) is not int or not 1 <= port <= 65535:
        raise ValueError("Das localhost-Profil braucht einen Port von 1 bis 65535")
    return [python, "-u", str(repo_root / "varianten/localhost/start.py"),
            "server", "--port", str(port)]


def available_loopback_port():
    """Reserviert kurz einen lokalen freien Port; der Launcher akzeptiert Port 0 nicht."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def stop_server_process(process, *, grouped):
    """Stoppt im Profilmodus Wrapper und gestarteten Server als Prozessgruppe."""
    def send_signal(sig):
        if grouped:
            try:
                os.killpg(process.pid, sig)
            except ProcessLookupError:
                pass
        elif process.poll() is None:
            process.send_signal(sig)

    send_signal(signal.SIGINT)
    try:
        process.wait(timeout=3)
    except subprocess.TimeoutExpired:
        send_signal(signal.SIGKILL)
        process.wait(timeout=3)


def window_pair_layout(width, height):
    """Zwei Fenster eng nebeneinander und ein Bildausschnitt nur um sie herum."""
    left = 10
    right = left + width + 10
    region = f"0,25,{right + width + 10},{height + 65}"
    return left, right, region


def game_windows_visible(image, left, right, scale=1):
    """Prueft sichtbare, gleich gestaltete Kopf-, Status- und Brettbereiche beider Fenster.

    Koordinaten sind Bildschirmpunkte; scale rechnet sie in Bildpixel um (Retina: 2).
    """
    pairs = []
    try:
        for origin in (left, right):
            colors = [tuple(image.get((origin + dx) * scale, y * scale)) for dx, y in
                      ((500, 100), (100, 170), (500, 250))]
            if any(len(color) != 3 or not (color[2] >= color[1] + 8 > color[0] + 15)
                   for color in colors):
                return False
            pairs.append(colors)
    except (IndexError, KeyError, ValueError, tk.TclError):
        return False
    return all(abs(a - b) <= 8 for first, second in zip(*pairs)
               for a, b in zip(first, second))


def capture_game_pair(root, apps, target, width, height, screen_width):
    """Speichert eine gepruefte Aufnahme von einem oder zwei echten Spielfenstern."""
    if sys.platform != "darwin":
        return None, "Automatische Aufnahme nur fuer macOS vorbereitet"
    compact_left, compact_right, compact_region = window_pair_layout(width, height)
    layouts = [
        ("compact", compact_left, compact_right, compact_region),
        ("wide", 10, screen_width - width - 10, f"0,25,{screen_width},{height + 65}"),
    ]
    if len(apps) == 1:
        layouts = [("single", 10, 10, f"0,25,{width + 20},{height + 65}")]
    failures = []
    for label, left, right, region in layouts:
        if (len(apps) == 2 and right < left + width + 10) or int(region.split(",")[2]) > screen_width:
            failures.append(f"{label}: Fenster passen nicht nebeneinander auf den Bildschirm")
            continue
        for x, app in zip((left, right), apps):
            app.root.geometry(f"{width}x{height}+{x}+50")
            app.root.attributes("-topmost", True)
            app.root.lift()
        root.update()
        time.sleep(0.15)
        root.update()
        with tempfile.TemporaryDirectory(prefix="battleship_capture_") as directory:
            candidate = Path(directory) / "screen.png"
            capture = subprocess.run(["screencapture", "-x", "-R", region, str(candidate)],
                                     capture_output=True, text=True)
            if capture.returncode != 0 or not candidate.is_file() or candidate.stat().st_size == 0:
                failures.append(f"{label}: {capture.stderr.strip() or 'screencapture lieferte keine Bilddatei'}")
                continue
            try:
                image = tk.PhotoImage(file=str(candidate))
                scale = round(image.width() / int(region.split(",")[2]))
                visible = game_windows_visible(image, left, right, scale)
            except tk.TclError as error:
                failures.append(f"{label}: Bild konnte nicht geprueft werden: {error}")
                continue
            if not visible:
                diagnostic = target.with_name(f"{target.stem}_{label}_diagnostic.png")
                diagnostic.write_bytes(candidate.read_bytes())
                failures.append(f"{label}: Spielfenster nicht erkannt; Bild {image.width()}x{image.height()}, "
                                f"Region {region}; Diagnose: {diagnostic.name}")
                continue
            target.write_bytes(candidate.read_bytes())
            return label, None
    return None, "; ".join(failures)


def capture_game_montage(root, apps, target, width, height, screen_width):
    """Kopiert echte Einzelaufnahmen unveraendert nebeneinander; keine UI-Zeichnung."""
    images = []
    for app in apps:
        for other in apps:
            other.root.attributes("-topmost", False)
        single = target.with_name(f"{target.stem}_{app.name}.png")
        layout, error = capture_game_pair(root, (app,), single, width, height, screen_width)
        if not layout:
            return None, error
        images.append(tk.PhotoImage(master=root, file=str(single)))
    montage = tk.PhotoImage(master=root, width=sum(i.width() for i in images),
                           height=max(i.height() for i in images))
    x = 0
    for image in images:
        root.tk.call(str(montage), "copy", str(image), "-to", x, 0)
        x += image.width()
    montage.write(str(target), format="png")
    return "Montage echter Einzelaufnahmen (screencapture), unveraendert nebeneinander", None


def save_evidence(output, report, messages, *, completed):
    """Erst nach allen Pruefungen PASS speichern; Teilversuche bleiben FAIL."""
    log = (output / "server.txt").read_text(encoding="utf-8")
    unsafe = any(value in log for value in ("ownShips", "shotsAtSelf", "Carrier", "Traceback"))
    missing_capture = any(key.endswith("screenshot_unavailable") for key in report)
    report["result"] = "PASS" if completed and not unsafe and not missing_capture else "FAIL"
    if unsafe:
        report["error"] = "Serverlog enthaelt private Payloads oder einen Traceback"
    elif missing_capture:
        report.setdefault("error", "Angeforderter Bildnachweis nicht gelungen")
    elif not completed:
        report.setdefault("error", "Lauf nicht erfolgreich abgeschlossen")
    report["finished"] = datetime.now().astimezone().isoformat()
    (output / "client_messages.jsonl").write_text(
        "".join(json.dumps(entry, ensure_ascii=False) + "\n" for entry in messages), encoding="utf-8")
    (output / "result.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def place_individual_fleets(alice, bob, until, report):
    """Bedient die echten Platzierungsfelder fuer zwei unterschiedliche Flotten."""
    bob_fleet = [{**ship, "start": "A" + str(i + 6)} for i, ship in enumerate(FLEET)]
    for app, fleet in ((alice, FLEET), (bob, bob_fleet)):
        for ship in fleet:
            start, direction = app.placement_vars[ship["type"]]
            start.set(ship["start"])
            direction.set(ship["direction"])
        app.place_button.invoke()
        until(lambda app=app: len(app.last_state["ownShips"]) == 5)
    until(lambda: all(a.last_state["phase"] == "shooting" for a in (alice, bob)))
    assert alice.last_state["ownShips"] != bob.last_state["ownShips"]
    report["checks"].append("Individuelle Flotten und serverbestaetigte Platzierung")



def verify_private_rejections(alice, bob, until, report):
    """Ungueltige Klicks bleiben privat und veraendern keinen bestaetigten Zustand."""
    states_before = [deepcopy(a.last_state) for a in (alice, bob)]
    bob_notice = bob.status_var.get()
    alice.target_buttons["J10"].invoke()
    until(lambda: "NOT_YOUR_TURN" in alice.status_var.get())
    assert [a.last_state for a in (alice, bob)] == states_before
    assert bob.status_var.get() == bob_notice
    report["out_of_turn"] = alice.status_var.get()
    bob.target_buttons["J10"].invoke()
    until(lambda: alice.last_state["shotsAtSelf"].get("J10") == "miss"
          and bob.last_state["shotsAtOpponent"].get("J10") == "miss")
    assert alice.own_buttons["J10"].cget("text") == bob.target_buttons["J10"].cget("text") == "·"
    states_before = [deepcopy(a.last_state) for a in (alice, bob)]
    alice.target_buttons["B6"].invoke()
    until(lambda: "DUPLICATE_SHOT" in alice.status_var.get())
    assert [a.last_state for a in (alice, bob)] == states_before
    report["duplicate_shot"] = alice.status_var.get()
    report["checks"].append("Beide Ablehnungen privat; beide Zustaende unveraendert")



def finish_match(alice, bob, until, process, report):
    """Spielt die restlichen bestaetigten Zuege und prueft das gemeinsame Ende."""
    # Restliche Flotte mit abwechselnden echten Button-Klicks versenken.
    targets = [field[0] + str(int(field[1:]) + 5) for field in FLEET_CELLS]
    targets.remove("B6")
    misses = [f for f in MISSES if f != "J10"]
    for index, target in enumerate(targets):
        alice.target_buttons[target].invoke()
        until(lambda target=target: target in alice.last_state["shotsAtOpponent"]
              and target in bob.last_state["shotsAtSelf"])
        if index < len(targets) - 1:
            miss = misses[index]
            bob.target_buttons[miss].invoke()
            until(lambda miss=miss: miss in bob.last_state["shotsAtOpponent"]
                  and miss in alice.last_state["shotsAtSelf"])
    assert all(a.last_state["phase"] == "finished" and a.last_state["winner"] == "A"
               and a.last_state["turn"] is None for a in (alice, bob))
    assert len(alice.last_state["shotsAtOpponent"]) + len(bob.last_state["shotsAtOpponent"]) == 33
    until(lambda: "Gewonnen" in alice.status_var.get() and "Verloren" in bob.status_var.get())
    assert process.poll() is None, "Server hat die beendete Partie nicht ueberlebt"
    report["end_status"] = {"Alice": alice.status_var.get(), "Bob": bob.status_var.get()}
    report["checks"].append("Vollstaendige 33-Schuss-Partie, Sieg und Niederlage in beiden Fenstern")
    report["checks"].append("Server laeuft nach dem Spielende weiter")


def verify_private_states(messages, report):
    """Jede aufgezeichnete Sicht darf nur die Flotte ihres Empfaengers enthalten."""
    for entry in messages:
        message = entry["message"]
        if message.get("type") != "state":
            continue
        assert set(message) == {"type", "phase", "turn", "ownShips", "shotsAtOpponent", "shotsAtSelf", "winner",
                                "score"}
        assert not any(key in message for key in ("opponentShips", "players", "ships"))
        own_cells = {c for ship in message["ownShips"] for c in ship["cells"]}
        if entry["recipient"] == "Zuschauer":
            assert message["ownShips"] == [], "Zuschauer erhielt eine private Flotte"
        if entry["recipient"] == "Alice" and own_cells:
            assert own_cells == set(FLEET_CELLS)
        if entry["recipient"] == "Bob" and own_cells:
            assert own_cells == set([c[0] + str(int(c[1:]) + 5) for c in FLEET_CELLS])
    report["checks"].append("Alle echten Zustandsnachrichten enthalten ausschliesslich die jeweilige eigene Flotte")


def public_state(state, slot="A"):
    """Oeffentliche Schuesse aus Perspektive A, ohne private Flotte."""
    view = deepcopy(state)
    view["ownShips"] = []
    if slot == "B":
        view["shotsAtSelf"], view["shotsAtOpponent"] = view["shotsAtOpponent"], view["shotsAtSelf"]
    return view


def verify_spectator_updates(messages, report):
    """Vergleicht die gesamten Zustandsfolgen ab B6, nicht nur den Endzustand."""
    views = {name: [] for name in ("Alice", "Bob", "Zuschauer")}
    # Nach einer Revanche tauschen die Slots; welcome nennt den neuen Slot.
    slots = {"Alice": "A", "Bob": "B", "Zuschauer": "A"}
    for entry in messages:
        name, state = entry["recipient"], entry["message"]
        if name in slots and state.get("type") == "welcome":
            slots[name] = state["slot"]
        if name not in views or state.get("type") != "state":
            continue
        if name == "Zuschauer":
            assert state["ownShips"] == []
        view = public_state(state, slots[name])
        if not views[name] and view["shotsAtOpponent"].get("B6") != "hit":
            continue
        if not views[name] or views[name][-1] != view:
            views[name].append(view)
    assert views["Zuschauer"], "Kein Zuschauerzustand nach B6"
    assert views["Alice"] == views["Zuschauer"], "Zuschauerfolge weicht von Alice ab"
    assert views["Bob"] and views["Bob"] == views["Zuschauer"][:len(views["Bob"])], "Zuschauerfolge weicht von Bob ab"
    report["spectator_states_compared"] = len(views["Zuschauer"])
    report["checks"].append("Alle oeffentlichen Zustandsfolgen ab B6 einschliesslich Spielende und Reset verglichen")


def play_rematch(alice, bob, spectator, until, process, report, capture):
    """Revanche ueber echte Knoepfe: Ablehnungen, Start ohne Neustart und erster Zug.

    capture(name, apps) nimmt eine Montage auf. Bob war in der ersten Partie B
    und ist nach dem Slottausch A, also der erste Schuetze der zweiten Partie.
    """
    trio = (alice, bob, spectator)
    expected_score = "Alice 1 : 0 Bob"
    assert all(a.score_label.cget("text") == expected_score for a in trio)
    assert all(str(a.rematch_button.cget("state")) == "normal" for a in trio)
    report["checks"].append(f"Punktestand nach der ersten Partie in allen drei Fenstern: {expected_score}")

    before = [deepcopy(a.last_state) for a in trio]
    spectator.rematch_button.invoke()
    until(lambda: "SPECTATOR_ONLY" in spectator.status_var.get())
    spectator_rejection = spectator.status_var.get()
    alice.rematch_button.invoke()
    until(lambda: "Alice will eine Revanche" in bob.status_var.get()
          and "Alice will eine Revanche" in spectator.status_var.get()
          and "warte auf den Gegner" in alice.status_var.get())
    alice.rematch_button.invoke()
    until(lambda: "DUPLICATE_REMATCH" in alice.status_var.get())
    assert [a.last_state for a in trio] == before, "Ein einzelner Wunsch darf keine Partie starten"
    report["rematch_rejections"] = {"Zuschauer": spectator_rejection, "Alice doppelt": alice.status_var.get()}
    report["checks"].append("Revanche vom Zuschauer und doppelter Wunsch privat abgelehnt; ein Wunsch startet nichts")

    bob.rematch_button.invoke()
    until(lambda: alice.slot == "B" and bob.slot == "A"
          and all(a.last_state["phase"] == "placing" for a in trio))
    assert all(not a.last_state["ownShips"] and not a.last_state["shotsAtOpponent"]
               and not a.last_state["shotsAtSelf"] for a in trio)
    assert len({str(a.last_state["score"]) for a in trio}) == 1
    assert all(a.score_label.cget("text") == "Bob 0 : 1 Alice" for a in trio)
    assert process.poll() is None
    report["checks"].append("Zweiter Wunsch startet die Revanche ohne Serverneustart: leere Bretter, "
                            "gleicher Punktestand fuer alle, Bob jetzt A")

    place_individual_fleets(alice, bob, until, report)
    assert all(a.last_state["turn"] == "A" for a in (alice, bob))
    bob.target_buttons["A1"].invoke()
    until(lambda: bob.last_state["shotsAtOpponent"].get("A1") == "hit"
          and alice.last_state["shotsAtSelf"].get("A1") == "hit")
    until(lambda: not any(a.effects.active for a in (alice, bob)))
    report["checks"].append("Erster Zug der Revanche von Bob, der in der ersten Partie nicht begonnen hat")
    capture("rematch_first_move.png", trio)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    default_output = ROOT / "docs/evidence" / ("run_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f"))
    parser.add_argument("--output", type=Path, default=default_output,
                        help="Neuer Ausgabeordner; Standard: eigener zeitgestempelter Ordner")
    parser.add_argument("--server-profile", choices=("localhost",),
                        help="Server ueber den echten localhost-Starteinstieg starten")
    parser.add_argument("--screenshot", action="store_true", help="Unter macOS beide Fenster aufnehmen")
    parser.add_argument("--spectator", action="store_true",
                        help="Drittes unveraendertes Fenster nach B6; mit --screenshot echte Montage und Ablehnung")
    parser.add_argument("--final-screenshot", action="store_true",
                        help="Unter macOS beide Fenster nach Spielende aufnehmen")
    parser.add_argument("--pause-for-capture", action="store_true",
                        help="Nach B6 bis zur Datei capture_continue oder maximal 180 s weiterzeichnen")
    parser.add_argument("--rematch", action="store_true",
                        help="Meilenstein 8: mit Zuschauer, Revanche-Ablehnungen und zweiter Partie ohne Neustart")
    args = parser.parse_args()
    if args.rematch:
        args.spectator = args.final_screenshot = True
    try:
        args.output.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        parser.error(f"Ausgabeordner existiert bereits: {args.output}; bitte einen neuen Ordner waehlen")
    log_path = args.output / "server.txt"
    messages = []
    report = {"started": datetime.now().astimezone().isoformat(),
              "scope": "Automatisierte lokale TCP-Partie mit zwei echten Tk-Fenstern",
              "server_profile": args.server_profile or "direct", "checks": [], "result": "FAIL"}
    if args.spectator:
        report["scope"] = "Automatisierte lokale TCP-Partie mit zwei Spielern und einem unveraenderten Zuschauerfenster"
    if args.rematch:
        report["scope"] = "Zwei Partien hintereinander mit Revanche, zwei Spielern und einem Zuschauer, ein Serverprozess"
    completed = False

    class RecordedWindow(BattleshipWindow):
        def process_message(self, message):
            messages.append({"recipient": self.name, "message": deepcopy(message)})
            super().process_message(message)

    root = None
    apps = []
    process = None
    spectator = None
    grouped_server = args.server_profile is not None and os.name == "posix"
    with log_path.open("w", encoding="utf-8") as server_log:
        try:
            requested_port = available_loopback_port() if args.server_profile else 0
            command = server_command(args.server_profile, ROOT, sys.executable, requested_port,
                                     (args.output / "server_messages.jsonl").resolve())
            process = subprocess.Popen(
                command, stdout=server_log, stderr=subprocess.STDOUT,
                start_new_session=grouped_server,
            )
            deadline = time.monotonic() + 5
            port = None
            while time.monotonic() < deadline:
                match = re.search(r"Server wartet auf Port (\d+)", log_path.read_text())
                if match:
                    port = int(match.group(1))
                    break
                if process.poll() is not None:
                    raise AssertionError(log_path.read_text())
                time.sleep(0.01)
            assert port is not None, "Server meldet keinen Start"
            if args.server_profile:
                assert port == requested_port, "Profilserver lauscht nicht auf dem gewaehlten Port"
                report["server_start_entry"] = "varianten/localhost/start.py"
            report["server_port"] = port
            root = tk.Tk()
            root.withdraw()

            def new_window(name):
                top = tk.Toplevel(root)
                sock = socket.create_connection(("127.0.0.1", port), timeout=3)
                sock.settimeout(None)
                app = RecordedWindow(top, sock, name)
                apps.append(app)
                return app

            def until(condition):
                deadline = time.monotonic() + 3
                while time.monotonic() < deadline:
                    root.update()
                    if condition():
                        if spectator is None or all(
                            public_state(a.last_state, a.slot) == spectator.last_state
                            for a in apps if not a.closed and a.slot in ("A", "B")
                        ):
                            return
                    time.sleep(0.005)
                raise AssertionError("GUI-Bedingung nicht erreicht: " + str([a.status_var.get() for a in apps if not a.closed]))

            alice = new_window("Alice")
            until(lambda: alice.slot == "A" and alice.last_state["phase"] == "waiting")
            bob = new_window("Bob")
            until(lambda: bob.slot == "B" and all(a.last_state["phase"] == "placing" for a in (alice, bob)))
            report["checks"].append("Beitritt, Warten und ungefragter Spielstart")
            place_individual_fleets(alice, bob, until, report)

            alice.target_buttons["B6"].invoke()
            until(lambda: alice.last_state["shotsAtOpponent"].get("B6") == "hit"
                  and bob.last_state["shotsAtSelf"].get("B6") == "hit")
            assert alice.target_buttons["B6"].cget("text") == bob.own_buttons["B6"].cget("text") == "X"
            assert all(a.last_state["turn"] == "B" for a in (alice, bob))
            report["checks"].append("Klick B6 aktualisiert beide Fenster ohne getState")

            if args.spectator:
                spectator = new_window("Zuschauer")
                until(lambda: any(e["recipient"] == "Zuschauer" and e["message"].get("type") == "spectator"
                                  for e in messages))
                role = next(e["message"] for e in messages
                            if e["recipient"] == "Zuschauer" and e["message"].get("type") == "spectator")
                assert "slot" not in role and "symbol" not in role and spectator.slot is None
                assert spectator.last_state["ownShips"] == []
                assert spectator.target_buttons["B6"].cget("text") == "X"
                report["checks"].append("Spaeter Zuschauerbeitritt nach B6: spectator ohne Slot, sofort oeffentliche Sicht")

            # Beide echten Fenster nebeneinander; Aufnahme enthält den gleichen Zug.
            root.update()
            width = max(a.root.winfo_reqwidth() for a in (alice, bob))
            height = max(a.root.winfo_reqheight() for a in (alice, bob))
            screen_width = root.winfo_screenwidth()
            left_x, right_x, image_region = window_pair_layout(width, height)
            for x, app in ((left_x, alice), (right_x, bob)):
                app.root.geometry(f"{width}x{height}+{x}+50")
                app.root.lift()
            root.update()
            report["window_size"] = [width, height]
            if args.screenshot and not args.spectator:
                until(lambda: all(a.root.winfo_viewable() for a in (alice, bob)))
                layout, error = capture_game_pair(root, (alice, bob), args.output / "two_windows.png",
                                                  width, height, screen_width)
                if layout:
                    report["checks"].append("Echter Screenshot beider Fenster nach B6")
                    report["screenshot_layout"] = layout
                else:
                    report["screenshot_unavailable"] = error
            if args.pause_for_capture:
                (args.output / "capture_ready").write_text("Beide Fenster nach Alices Treffer auf B6; B am Zug.\n")
                print("CAPTURE_READY", flush=True)
                deadline = time.monotonic() + 180
                while not (args.output / "capture_continue").exists():
                    if time.monotonic() > deadline:
                        raise TimeoutError("Bildaufnahme nicht innerhalb von 180 s bestaetigt")
                    root.update()
                    time.sleep(0.01)

            verify_private_rejections(alice, bob, until, report)

            if spectator is not None:
                trio = (alice, bob, spectator)
                assert all(a.connected and not a.closed for a in trio)
                assert spectator.own_buttons["J10"].cget("text") == "·"
                if args.screenshot:
                    layout, error = capture_game_montage(root, trio, args.output / "three_windows.png",
                                                         width, height, screen_width)
                    if layout:
                        report["screenshot_layout"] = layout
                        report["screenshot"] = "three_windows.png"
                    else:
                        report["screenshot_unavailable"] = error
                before = [deepcopy(a.last_state) for a in trio]
                notices = [a.status_var.get() for a in (alice, bob)]
                message_start = len(messages)
                spectator.target_buttons["H10"].invoke()
                until(lambda: "SPECTATOR_ONLY" in spectator.status_var.get())
                # Ein nachfolgender getState ist eine TCP-Barriere hinter der Ablehnung.
                spectator.refresh_button.invoke()
                until(lambda: any(e["recipient"] == "Zuschauer" and e["message"].get("type") == "state"
                                  for e in messages[message_start:]))
                assert [a.last_state for a in trio] == before
                assert [a.status_var.get() for a in (alice, bob)] == notices
                assert all(e["recipient"] == "Zuschauer" for e in messages[message_start:])
                spectator.target_buttons["H10"].invoke()
                until(lambda: "SPECTATOR_ONLY" in spectator.status_var.get())
                report["spectator_rejection"] = spectator.status_var.get()
                report["checks"].append("Echter Zuschauerklick privat mit SPECTATOR_ONLY abgelehnt; drei Zustaende unveraendert")
                if args.screenshot:
                    for app in trio:
                        app.root.attributes("-topmost", False)
                    layout, error = capture_game_pair(root, (spectator,), args.output / "spectator_rejection.png",
                                                      width, height, screen_width)
                    if layout:
                        report["spectator_screenshot"] = "spectator_rejection.png"
                    else:
                        report["spectator_screenshot_unavailable"] = error
                    report["capture_note"] = (
                        "Montage echter Aufnahmen: three_windows.png zeigt links Alice, mittig Bob, rechts Zuschauer "
                        "nach Bobs J10. Drei TCP-Verbindungen blieben offen; waehrend der Aufnahmen kein Spielzug. "
                        "Einzeldateien three_windows_*.png stammen aus screencapture; Tk PhotoImage copy kopiert "
                        "nur ihre Pixel. spectator_rejection.png ist eine echte Einzelaufnahme nach einem Klick. "
                        "Der unveraenderte Client ignoriert spectator; Rollen-/Siegtexte sind keine Zuschaueranzeige."
                    )
                    (args.output / "README.md").write_text(
                        "# Meilenstein 7: lokaler GUI-Nachweis\n\n" + report["capture_note"] +
                        "\n\nserver.txt und server_messages.jsonl stammen aus derselben Partie. "
                        "client_messages.jsonl enthaelt die aufgezeichneten Testsichten; result.json die Pruefungen.\n",
                        encoding="utf-8")

            def capture_montage(name, capture_apps):
                if not args.screenshot:
                    return
                layout, error = capture_game_montage(root, capture_apps, args.output / name,
                                                     width, height, screen_width)
                if layout:
                    report.setdefault("rematch_screenshots", []).append(name)
                else:
                    report[f"{Path(name).stem}_screenshot_unavailable"] = error

            if args.rematch:
                # Der Knopf ist waehrend der Partie gesperrt; der Wunsch geht deshalb
                # direkt in die Sendewarteschlange, wie bei einem veralteten Client.
                # Zuschauerstatus aus dem Serverzustand neu zeichnen, damit kein alter Fehlertext im Bild steht.
                spectator.refresh_button.invoke()
                until(lambda: messages[-1]["recipient"] == "Zuschauer" and messages[-1]["message"]["type"] == "state")
                before = [deepcopy(a.last_state) for a in (alice, bob, spectator)]
                notices = [a.status_var.get() for a in (bob, spectator)]
                assert str(alice.rematch_button.cget("state")) == "disabled"
                alice._request({"type": "rematch"})
                until(lambda: "WRONG_PHASE" in alice.status_var.get())
                report["rematch_running_rejection"] = alice.status_var.get()
                capture_montage("rematch_rejection_running.png", (alice, bob, spectator))
                # getState danach ist eine TCP-Barriere hinter der Ablehnung.
                alice.refresh_button.invoke()
                until(lambda: messages[-1]["recipient"] == "Alice" and messages[-1]["message"]["type"] == "state")
                assert [a.last_state for a in (alice, bob, spectator)] == before
                assert [a.status_var.get() for a in (bob, spectator)] == notices
                assert not any(e["message"].get("type") == "rematchRequested" for e in messages)
                report["checks"].append("Revanche waehrend laufender Partie nur Alice mit WRONG_PHASE abgelehnt")

            finish_match(alice, bob, until, process, report)
            if spectator is not None:
                until(lambda: any(e["recipient"] == "Zuschauer" and e["message"].get("type") == "gameOver"
                                  for e in messages))

            if args.final_screenshot:
                until(lambda: all(a.root.winfo_viewable() for a in (alice, bob)))
                until(lambda: not any(a.effects.active for a in (alice, bob)))
                assert "Gewonnen" in alice.status_var.get() and "Verloren" in bob.status_var.get()
                final_image = args.output / "two_windows_finished.png"
                final_apps = (alice, bob) if spectator is None else (alice, bob, spectator)
                capture = capture_game_pair if spectator is None else capture_game_montage
                if spectator is not None:
                    final_image = args.output / "three_windows_finished.png"
                layout, error = capture(root, final_apps, final_image, width, height, screen_width)
                if layout:
                    report["checks"].append("Echter Screenshot beider Fenster nach Spielende")
                    report["final_screenshot"] = final_image.name
                    report["final_screenshot_layout"] = layout
                else:
                    report["final_screenshot_unavailable"] = error

            if args.rematch:
                play_rematch(alice, bob, spectator, until, process, report, capture_montage)
                report["capture_note"] = (
                    "Montagen echter Einzelaufnahmen (screencapture), links Alice, mittig Bob, rechts Zuschauer. "
                    "three_windows_finished.png: Ende der ersten Partie mit Punktestand Alice 1 : 0 Bob. "
                    "rematch_first_move.png: nach Bobs erstem Schuss A1 der zweiten Partie; Bob ist nach dem "
                    "Slottausch A. rematch_rejection_running.png: Alices Revanchewunsch waehrend der laufenden "
                    "ersten Partie, privat mit WRONG_PHASE abgelehnt. Der Knopf ist dann gesperrt; das Werkzeug "
                    "legt den Wunsch deshalb direkt in Alices Sendewarteschlange. Alle anderen Revanchewuensche "
                    "sind echte Knopfklicks."
                )
                (args.output / "README.md").write_text(
                    "# Meilenstein 8: lokaler GUI-Nachweis der Revanche\n\n" + report["capture_note"] +
                    "\n\nserver.txt und server_messages.jsonl stammen aus demselben Serverprozess fuer beide "
                    "Partien. client_messages.jsonl enthaelt die aufgezeichneten Fenstersichten; result.json "
                    "die Pruefungen.\n", encoding="utf-8")
            else:
                before_rejected = [deepcopy(a.last_state) for a in (alice, bob)]
                alice_notice = alice.status_var.get()
                assert "H10" not in bob.last_state["shotsAtOpponent"]
                assert bob.target_buttons["H10"].cget("state") == "normal"
                bob.target_buttons["H10"].invoke()
                until(lambda: "WRONG_PHASE" in bob.status_var.get())
                assert [a.last_state for a in (alice, bob)] == before_rejected
                assert alice.status_var.get() == alice_notice
                assert process.poll() is None, "Server hat die Ablehnung nach Spielende nicht ueberlebt"
                report["post_game_rejection"] = bob.status_var.get()
                report["checks"].append("Echter Klick nach Spielende wird privat ohne Zustandsaenderung abgelehnt")

            # WM_DELETE_WINDOW verwendet exakt diesen registrierten Handler.
            bob.root.tk.call(bob.root.protocol("WM_DELETE_WINDOW"))
            until(lambda: alice.last_state["phase"] == "waiting")
            assert not alice.last_state["ownShips"] and not alice.last_state["shotsAtSelf"]
            assert "verlassen" in alice.status_var.get()
            carol = new_window("Carol")
            # Nach der Revanche war Bob A; sein freier Slot geht an Carol.
            free_slot = "A" if args.rematch else "B"
            until(lambda: carol.slot == free_slot and all(a.last_state["phase"] == "placing" for a in (alice, carol)))
            assert all(not a.last_state["ownShips"] for a in (alice, carol))
            report["checks"].append("Fensterkreuz, Abbruchanzeige, leerer Reset und Ersatzbeitritt")

            if spectator is not None:
                assert spectator.slot is None and spectator.connected
                assert any(e["recipient"] == "Zuschauer" and e["message"].get("type") == "opponentLeft"
                           for e in messages)
                verify_spectator_updates(messages, report)

            verify_private_states(messages, report)

            completed = True
        except Exception as exc:
            report["error"] = f"{type(exc).__name__}: {exc}"
            raise
        finally:
            for app in apps:
                if not app.closed:
                    app.close()
            if root is not None:
                root.destroy()
            if process is not None:
                stop_server_process(process, grouped=grouped_server)
            server_log.flush()
            save_evidence(args.output, report, messages, completed=completed)
    assert report["result"] == "PASS", report.get("error", "Nachweispruefung fehlgeschlagen")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
