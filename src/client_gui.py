"""Tk-Client: Anfragen ueber Queues, verbindliche Bretter nur aus Serverzustaenden."""
from __future__ import annotations

import argparse
from copy import deepcopy
from pathlib import Path
import queue
import random
import socket
import threading

try:
    import tkinter as tk
    from tkinter import ttk
    from sea_cell import SeaCell, SEA
except ImportError:
    tk = None
    ttk = None
    SEA = "#143c50"

from board import COLUMNS, FLEET, ship_cells
from netz import read_messages, send
from ship_art import draw_svg, SHIP_NAMES
from ship_effects import ShipEffects

SHIP_IMAGE_PATH = Path(__file__).resolve().parents[1] / "bilder" / "schiff.png"
NAVY = "#0b2333"
PANEL = "#103247"
TEXT = "#e0eff4"
MUTED = "#92b3c3"
ACCENT = "#68ced7"


def empty_state(phase="waiting"):
    return {
        "phase": phase, "turn": None, "ownShips": [],
        "shotsAtOpponent": {}, "shotsAtSelf": {}, "winner": None,
    }


class BattleshipWindow:
    """Ein Fenster und eine Verbindung; alle Widgetzugriffe bleiben im Tk-Thread.

    ``sock`` ist bereits verbunden. Der Aufrufer erzeugt ``root`` und startet
    dessen mainloop im Hauptthread. Empfang und Versand blockieren nur ihre
    eigenen Arbeitsthreads. Nach einem Abbruch bleibt das Fenster lesbar.
    """

    def __init__(self, root, sock, name):
        self.root = root
        self.sock = sock
        self.name = name
        self.slot = None
        self.connected = True
        self.closed = False
        self.last_state = empty_state()
        self._waiting_notice = ""
        self.incoming = queue.Queue()
        self.outgoing = queue.Queue()
        self.stopped = threading.Event()
        self._after_id = None
        self.own_buttons = {}
        self.target_buttons = {}
        self.placement_vars = {}
        self._placement_widgets = []

        root.title(f"Schiffe versenken · {name}")
        root.protocol("WM_DELETE_WINDOW", self.close)
        root.configure(background=NAVY, padx=18, pady=14)
        self._build_interface()
        self.effects = ShipEffects(root, self.own_buttons, enabled=self.effects_enabled.get)

        self.randomize_fleet()
        self.draw_state(self.last_state)
        self.status_var.set("Verbunden; Anmeldung wird gesendet …")
        # Die Ziele halten kein Window und damit auch keine Tk-Objekte fest.
        self.receive_thread = threading.Thread(
            target=self._receive, args=(sock, self.incoming, self.stopped), name=f"receive-{name}", daemon=True,
        )
        self.send_thread = threading.Thread(
            target=self._send, args=(sock, self.outgoing, self.incoming, self.stopped), name=f"send-{name}", daemon=True,
        )
        self.receive_thread.start()
        self.send_thread.start()
        self._request({"type": "join", "player": name})
        self._after_id = root.after(25, self._poll_messages)

    def _build_interface(self):
        root = self.root
        # Ein einheitliches ttk-Theme zeigt die Farben auch unter macOS an.
        style = ttk.Style(root)
        style.theme_use("clam")
        self.font = "Avenir Next" if root.tk.call("tk", "windowingsystem") == "aqua" else "Segoe UI"
        style.configure("Naval.TFrame", background=PANEL)
        style.configure("Naval.TLabel", background=PANEL, foreground=TEXT, font=(self.font, 10))
        style.configure("Naval.TButton", background="#244e64", foreground=TEXT, borderwidth=0,
                        padding=(12, 7), font=(self.font, 10))
        style.map("Naval.TButton", background=[("active", "#35677d"), ("disabled", "#183b50")],
                  foreground=[("disabled", "#64899c")])
        style.configure("Launch.Naval.TButton", background=ACCENT, foreground=NAVY, font=(self.font, 10, "bold"))
        style.map("Launch.Naval.TButton", background=[("active", "#92e4e8"), ("disabled", "#214a5c")],
                  foreground=[("disabled", "#7295a5")])
        for control in ("TEntry", "TCombobox"):
            style.configure(f"Naval.{control}", fieldbackground="#1a4155", background="#244e64",
                            foreground=TEXT, arrowcolor=ACCENT, bordercolor="#345e72",
                            insertcolor=TEXT, padding=3)
            style.map(f"Naval.{control}", fieldbackground=[("readonly", "#1a4155"), ("disabled", PANEL)],
                      foreground=[("disabled", "#6f91a2")], selectbackground=[("readonly", "#1a4155")],
                      selectforeground=[("readonly", TEXT)])
        style.configure("Naval.TCheckbutton", background=NAVY, foreground=MUTED, font=(self.font, 9))
        style.map("Naval.TCheckbutton", background=[("active", NAVY)], foreground=[("active", TEXT)])

        header = tk.Frame(root, background=NAVY)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        # Both creation and disposal belong to this Tk thread. Workers never
        # receive a Window/PhotoImage reference. Asset is independent of cwd.
        self.ship_image = tk.PhotoImage(master=root, file=str(SHIP_IMAGE_PATH)).subsample(4)
        self.ship_image_label = tk.Label(
            header, image=self.ship_image, background=NAVY,
        )
        self.ship_image_label.grid(row=0, column=0, rowspan=2, padx=(0, 12))
        tk.Label(header, text="Schiffe versenken", background=NAVY, foreground=TEXT,
                 font=(self.font, 24, "bold"), anchor="w").grid(row=0, column=1, sticky="sw")
        tk.Label(header, text=f"{self.name}  /  Deine Flotte. Dein Kommando.", background=NAVY,
                 foreground=MUTED, font=(self.font, 10), anchor="w").grid(row=1, column=1, sticky="nw")
        header.columnconfigure(1, weight=1)
        self.phase_label = tk.Label(header, text="Verbinden", background="#18445a", foreground=ACCENT,
                                    font=(self.font, 10, "bold"), padx=12, pady=6)
        self.phase_label.grid(row=0, column=2, rowspan=2, sticky="e")
        self.status_var = tk.StringVar(root, "Verbunden; Anmeldung wird gesendet …")
        tk.Label(root, textvariable=self.status_var, anchor="w", justify="left", wraplength=700,
                 background="#174156", foreground=TEXT, font=(self.font, 11), padx=14, pady=10).grid(
            row=1, column=0, columnspan=2, sticky="ew", pady=(0, 12),
        )
        self._build_grid("Deine Flotte", 0, self.own_buttons, own=True)
        self._build_grid("Zielraster", 1, self.target_buttons, own=False)
        legend = tk.Frame(root, background=NAVY)
        legend.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(9, 12))
        for label, color in (("●  Wasser", "#9cbac9"), ("×  Treffer", "#ffb39a"),
                             ("◎  Versenkender Treffer", "#ff8b70"), ("Leeres Zielfeld = unbekannt", MUTED)):
            tk.Label(legend, text=label, background=NAVY, foreground=color,
                     font=(self.font, 9)).pack(side="left", padx=(0, 20))

        placement = tk.Frame(root, background=PANEL, padx=12, pady=10)
        placement.grid(row=4, column=0, columnspan=2, sticky="ew")
        tk.Label(placement, text="Flotte planen", background=PANEL, foreground=TEXT,
                 font=(self.font, 13, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))
        for column, label in ((2, "Startfeld"), (3, "Richtung")):
            tk.Label(placement, text=label, background=PANEL, foreground=MUTED,
                     font=(self.font, 9)).grid(row=0, column=column, padx=8)
        for row, ship in enumerate(FLEET, 1):
            ship_type = ship["type"]
            start = tk.StringVar(root)
            direction = tk.StringVar(root)
            self.placement_vars[ship_type] = (start, direction)
            miniature = tk.Canvas(placement, width=94, height=22, background=PANEL, highlightthickness=0)
            miniature.grid(row=row, column=0, padx=(0, 10))
            draw_svg(miniature, ship_type, 0, 1, ship["size"] * 18, 20)
            ttk.Label(placement, text=f"{SHIP_NAMES[ship_type]}  ({ship['size']})", style="Naval.TLabel").grid(
                row=row, column=1, padx=(0, 12), sticky="w")
            start_entry = ttk.Entry(placement, textvariable=start, width=6, style="Naval.TEntry")
            start_entry.grid(row=row, column=2, padx=6, pady=2)
            direction_box = ttk.Combobox(placement, textvariable=direction, values=("h", "v"), width=4,
                                         state="readonly", style="Naval.TCombobox")
            direction_box.grid(row=row, column=3, padx=6, pady=2)
            self._placement_widgets.extend((start_entry, direction_box))
        ttk.Label(placement, text="h = rechts    v = unten\nKoordinaten anpassen, dann\ndeine Flotte senden.",
                  style="Naval.TLabel", justify="left").grid(
            row=1, column=4, rowspan=2, padx=(20, 0), sticky="nw",
        )
        self.randomize_button = ttk.Button(placement, text="Neu mischen", command=self.randomize_fleet, style="Naval.TButton")
        self.randomize_button.grid(row=3, column=4, rowspan=1, padx=(20, 0), pady=3, sticky="ew")
        self.place_button = ttk.Button(placement, text="Flotte senden", command=self.place_fleet, style="Launch.Naval.TButton")
        self.place_button.grid(row=4, column=4, rowspan=2, padx=(20, 0), pady=3, sticky="ew")
        placement.columnconfigure(4, weight=1)

        actions = tk.Frame(root, background=NAVY)
        actions.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        self.refresh_button = ttk.Button(actions, text="Zustand abfragen", style="Naval.TButton",
                                         command=lambda: self._request({"type": "getState"}))
        self.refresh_button.pack(side="left")
        self.effects_enabled = tk.BooleanVar(root, True)
        ttk.Checkbutton(actions, text="Sprengungseffekte", variable=self.effects_enabled, style="Naval.TCheckbutton",
                        command=self._toggle_effects).pack(side="left", padx=16)
        ttk.Button(actions, text="Beenden", command=self.close, style="Naval.TButton").pack(side="right")
        root.columnconfigure(0, weight=1)
        root.columnconfigure(1, weight=1)

    def _toggle_effects(self):
        if not self.effects_enabled.get():
            self.effects.stop()

    def _build_grid(self, title, column, buttons, *, own):
        panel = tk.Frame(self.root, background=PANEL, padx=12, pady=10)
        panel.grid(row=2, column=column, padx=(0, 6) if own else (6, 0), sticky="nsew")
        tk.Label(panel, text=title, background=PANEL, foreground=TEXT,
                 font=(self.font, 15, "bold")).pack(anchor="w")
        summary = tk.Label(panel, text="", background=PANEL, foreground=MUTED, font=(self.font, 9))
        summary.pack(anchor="w", pady=(0, 7))
        if own:
            self.own_summary = summary
        else:
            self.target_summary = summary
        frame = tk.Frame(panel, background=SEA)
        frame.pack()
        for col, letter in enumerate(COLUMNS, 1):
            tk.Label(frame, text=letter, background=PANEL, foreground=MUTED,
                     font=(self.font, 9, "bold"), pady=3).grid(row=0, column=col, sticky="ew")
        for row in range(1, 11):
            tk.Label(frame, text=str(row), width=2, background=PANEL, foreground=MUTED,
                     font=(self.font, 9, "bold"), padx=2).grid(row=row, column=0, sticky="ns")
            for col, letter in enumerate(COLUMNS, 1):
                field = f"{letter}{row}"
                button = SeaCell(frame, field, command=None if own else lambda cell=field: self.shoot(cell))
                button.grid(row=row, column=col, sticky="nsew")
                buttons[field] = button

    def _request(self, message):
        if self.connected and not self.closed:
            self.outgoing.put(message)

    def shoot(self, field):
        """Nur die Anfrage senden; auch Zugfolge und Doppelbeschuss prueft der Server."""
        self._request({"type": "shoot", "field": field})

    def place_fleet(self):
        ships = [
            {"type": ship_type, "start": start.get().strip().upper(), "direction": direction.get()}
            for ship_type, (start, direction) in self.placement_vars.items()
        ]
        self._request({"type": "place", "ships": ships})

    def randomize_fleet(self):
        """Eine gueltige, nicht vorhersehbar feste Vorlage nur in die Eingaben setzen."""
        occupied = set()
        for ship in FLEET:
            candidates = []
            for letter in COLUMNS:
                for row in range(1, 11):
                    for direction in ("h", "v"):
                        start = f"{letter}{row}"
                        cells = ship_cells(start, direction, ship["size"])
                        if cells is not None and not occupied.intersection(cells):
                            candidates.append((start, direction, cells))
            start, direction, cells = random.choice(candidates)
            occupied.update(cells)
            variables = self.placement_vars[ship["type"]]
            variables[0].set(start)
            variables[1].set(direction)

    @staticmethod
    def _receive(sock, incoming, stopped):
        # Diese Funktion und _send greifen ausschliesslich auf Socket/Queues zu.
        detail = ""
        try:
            for message in read_messages(sock):
                if stopped.is_set():
                    break
                incoming.put(message)
        except (OSError, UnicodeError) as exc:
            detail = str(exc)
        finally:
            if not stopped.is_set():
                incoming.put({"type": "disconnected", "message": detail})

    @staticmethod
    def _send(sock, outgoing, incoming, stopped):
        while not stopped.is_set():
            message = outgoing.get()
            if message is None or stopped.is_set():
                break
            try:
                send(sock, message)
            except OSError as exc:
                incoming.put({"type": "disconnected", "message": str(exc)})
                break

    def _poll_messages(self):
        self._after_id = None
        if self.closed:
            return
        # Alle aktuell eingetroffenen Meldungen in ihrer Reihenfolge anwenden.
        while True:
            try:
                message = self.incoming.get_nowait()
            except queue.Empty:
                break
            self.process_message(message)
        self._after_id = self.root.after(25, self._poll_messages)

    def draw_state(self, state):
        """Die gesamte erlaubte Sicht neu zeichnen; einzige Brett-Zeichenfunktion."""
        self.last_state = deepcopy(state)
        ships = set()
        hits = set()
        segments = {}
        for ship in state.get("ownShips", []):
            cells = ship.get("cells", [])
            ships.update(cells)
            hits.update(ship.get("hits", []))
            vertical = len(cells) > 1 and cells[0][0] == cells[1][0]
            for index, field in enumerate(cells):
                segments[field] = (ship["type"], index, len(cells), vertical)
        symbols = {"miss": "·", "hit": "X", "sunk": "#"}
        colors = {"": SEA, "S": SEA, "·": "#18394b", "X": "#493a3c", "#": "#573d3c"}
        phase = state.get("phase", "waiting")
        for field, button in self.own_buttons.items():
            symbol = "X" if field in hits else "S" if field in ships else ""
            symbol = symbols.get(state.get("shotsAtSelf", {}).get(field), symbol)
            button.set_content(symbol, ship=segments.get(field), background=colors[symbol], state="disabled")
        for field, button in self.target_buttons.items():
            symbol = symbols.get(state.get("shotsAtOpponent", {}).get(field), "")
            button.set_content(
                symbol, background=colors[symbol],
                state="normal" if self.connected and phase == "shooting" else "disabled",
            )
        total = len(ships)
        self.own_summary.configure(text=f"{total - len(hits)} von {total} Schiffsfeldern intakt" if total else "Deine Schiffe erscheinen nach der Bestätigung.")
        shots = state.get("shotsAtOpponent", {})
        hit_count = sum(result in ("hit", "sunk") for result in shots.values())
        self.target_summary.configure(text=f"{hit_count} Treffer bei {len(shots)} Schüssen" if shots else "Wähle ein Feld für deinen nächsten Schuss.")
        phase_text = {"waiting": "Warte auf Gegner", "placing": "Flotte planen", "shooting": "Dein Zug" if state.get("turn") == self.slot else "Gegner am Zug",
                      "finished": "Sieg" if state.get("winner") == self.slot else "Partie beendet"}
        self.phase_label.configure(text=phase_text.get(phase, phase))
        if self.connected:
            self.effects.observe(state.get("ownShips", []))
        else:
            self.effects.reset()
        can_place = self.connected and phase == "placing" and not state.get("ownShips")
        for widget in self._placement_widgets:
            widget.configure(state=("readonly" if isinstance(widget, ttk.Combobox) else "normal") if can_place else "disabled")
        self.place_button.configure(state="normal" if can_place else "disabled")
        self.randomize_button.configure(state="normal" if can_place else "disabled")
        self.refresh_button.configure(state="normal" if self.connected else "disabled")
        if phase == "waiting":
            status = self._waiting_notice or "Warte auf Gegner."
        elif phase == "placing":
            status = "Flotte bestaetigt; warte auf die gegnerische Platzierung." if state.get("ownShips") else "Flotte planen und senden (h = rechts, v = unten)."
        elif phase == "shooting":
            status = "Du bist am Zug. Klicke ein Feld im Zielraster." if state.get("turn") == self.slot else "Der Gegner ist am Zug."
        elif phase == "finished":
            status = "Gewonnen! Alle gegnerischen Schiffe sind versenkt." if state.get("winner") == self.slot else "Verloren. Deine Flotte wurde versenkt."
        else:
            status = f"Phase: {phase}"
        self.status_var.set(status)

    def process_message(self, message):
        """Im Tk-Thread aufrufen; direkte Antworten zeichnen keine Spielzuege."""
        kind = message.get("type")
        if kind == "state":
            self.draw_state(message)
        elif kind == "welcome":
            self.slot = message["slot"]
            self.root.title(f"Schiffe versenken · {self.name} · Spieler {self.slot}")
            self.status_var.set(f"Willkommen, {self.name}. Spieler {self.slot}; warte auf Gegner.")
        elif kind == "waiting":
            self.status_var.set("Warte auf Gegner.")
        elif kind == "gameStart":
            self._waiting_notice = ""
            self.status_var.set("Neue Partie. Warte auf Serverzustand zur Flottenplatzierung.")
        elif kind == "opponentLeft":
            self._waiting_notice = f"{message.get('player', 'Gegner')} hat das Spiel verlassen. Runde zurueckgesetzt; warte auf Gegner."
            self.status_var.set(self._waiting_notice)
        elif kind == "error":
            self.status_var.set(f"Fehler {message.get('code', '')}: {message.get('message', 'Anfrage abgelehnt')}")
        elif kind == "placeAck":
            self.status_var.set("Flotte angenommen; warte auf Serverzustand.")
        elif kind == "result":
            self.status_var.set(f"Schuss auf {message.get('field')}: {message.get('result')}. Warte auf Serverzustand.")
        elif kind == "gameOver":
            self.status_var.set("Gewonnen!" if message.get("winner") == self.slot else "Verloren. Partie beendet.")
        elif kind == "disconnected":
            self.connected = False
            self._stop_connection()
            self.draw_state(self.last_state)
            detail = f" ({message['message']})" if message.get("message") else ""
            self.status_var.set(f"Verbindung beendet{detail}. Fenster kann geschlossen werden.")
        elif kind == "broken":
            self.status_var.set("Fehler: ungueltige Servernachricht empfangen.")

    def _stop_connection(self):
        self.stopped.set()
        self.outgoing.put(None)
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        self.sock.close()

    def close(self):
        """Fensterkreuz: Socket sofort beenden; niemals auf ein Netzwerkpaket warten."""
        if self.closed:
            return
        self.closed = True
        self.connected = False
        self.effects.close()
        self._stop_connection()
        if self._after_id is not None:
            self.root.after_cancel(self._after_id)
            self._after_id = None
        self.ship_image_label.configure(image="")
        self.ship_image = None
        self.ship_image_label = None
        self.root.destroy()
        # Variable.__del__ ruft Tcl auf. Referenzen daher hier im Tk-Thread
        # freigeben statt bei einer spaeteren zyklischen Garbage-Collection.
        self.placement_vars.clear()
        self.status_var = None
        self.effects_enabled = None
        self._placement_widgets.clear()
        self.own_buttons.clear()
        self.target_buttons.clear()
        self.place_button = self.randomize_button = self.refresh_button = None
        self.root = None


def main():
    parser = argparse.ArgumentParser(description="Schiffe versenken mit zwei grafischen Rastern")
    parser.add_argument("host", nargs="?", default="127.0.0.1")
    parser.add_argument("name", nargs="?", default="Spieler")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()
    if tk is None:
        parser.exit(1, "tkinter fehlt. Python mit Tk-Unterstuetzung installieren und python3 -m tkinter pruefen.\n")
    try:
        # Verbindung vor dem Tk-Fenster herstellen: keine Netzwartezeit in mainloop.
        sock = socket.create_connection((args.host, args.port), timeout=5)
        sock.settimeout(None)
    except OSError as exc:
        parser.exit(1, f"Verbindung fehlgeschlagen: {exc}\n")
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        sock.close()
        parser.exit(1, f"Tk-Fenster nicht verfuegbar: {exc}\n")
    window = BattleshipWindow(root, sock, args.name)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        window.close()


if __name__ == "__main__":
    main()
