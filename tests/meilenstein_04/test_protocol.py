"""Protokollkatalog und dokumentierte Partie gegen den Server prüfen.

Die Aufzeichnung entsteht an sendall-Ersatzobjekten, ohne TCP-Verbindungen
oder GUI. Diese Tests sind deshalb kein Nachweis eines Netzwerklaufs.
"""
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import re
import unittest

import server


ROOT = Path(__file__).resolve().parents[2]


class RecordingSocket:
    """Sammelt serialisierte Nachrichten mit ihrem tatsächlichen Empfänger."""

    def __init__(self, slot, outgoing):
        self.slot = slot
        self.outgoing = outgoing

    def sendall(self, data):
        for line in data.decode("utf-8").splitlines():
            self.outgoing.append((self.slot, json.loads(line)))


class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.markdown = (ROOT / "PROTOKOLL.md").read_text(encoding="utf-8")
        self.protocol = json.loads(
            (ROOT / "docs/protocol/protocol.json").read_text(encoding="utf-8")
        )
        self.required = {
            name: set(message["requiredFields"])
            for name, message in self.protocol["messages"].items()
        }

    def assert_message_complete(self, message, source):
        self.assertIsInstance(message, dict, f"{source}: Nachricht muss ein Objekt sein")
        name = message.get("type")
        self.assertIn(name, self.required, f"{source}: unbekannter Nachrichtentyp {name!r}")
        self.assertFalse(
            self.required[name] - message.keys(),
            f"{source}: Pflichtfelder fehlen bei {name}",
        )
        if name == "state":
            self.assertEqual(
                set(message), self.required[name],
                f"{source}: state muss genau die dokumentierte erlaubte Sicht enthalten",
            )

    def test_json_and_markdown_catalogs_have_complete_consistent_examples(self):
        expected_types = {
            "join", "welcome", "waiting", "gameStart", "place", "placeAck",
            "shoot", "result", "getState", "state", "leave", "opponentLeft",
            "gameOver", "error",
        }
        self.assertEqual(
            set(self.required), expected_types, "Der Katalog hat 14 Spielnachrichtentypen"
        )
        self.assertEqual(self.protocol["version"], "0.5", "M4 verwendet Protokollversion 0.5")
        self.assertIn(
            f'Protokoll {self.protocol["version"]}', self.markdown,
            "Markdown- und JSON-Version müssen übereinstimmen",
        )

        for name, specification in self.protocol["messages"].items():
            with self.subTest(catalog="JSON", message=name):
                self.assertEqual(specification["example"].get("type"), name)
                self.assert_message_complete(specification["example"], f"JSON {name}")
                self.assertIn(
                    specification["direction"], ("client_to_server", "server_to_client")
                )
                self.assertTrue(specification["trigger"].strip(), f"Anlass für {name} fehlt")

        markdown_catalog = {}
        markdown_directions = {}
        self.assertIn("## Nachrichtenkatalog", self.markdown, "Die Katalogtabelle fehlt")
        self.assertIn("### join", self.markdown, "Der Katalog beginnt mit dem join-Beispiel")
        catalog = self.markdown.split("## Nachrichtenkatalog", 1)[1].split("### join", 1)[0]
        for line in catalog.splitlines():
            if not line.startswith("| `"):
                continue
            columns = [column.strip() for column in line.strip("|").split("|")]
            name = columns[0].strip("`")
            fields = set(re.findall(r"`([^`]+)`", columns[2]))
            markdown_catalog[name] = {"type"} | fields
            markdown_directions[name] = columns[1]
        self.assertEqual(
            markdown_catalog, self.required,
            "Markdown-Tabelle und JSON-Katalog müssen dieselben Pflichtfelder nennen",
        )
        expected_directions = {
            name: "C → S" if message["direction"] == "client_to_server" else "S → C"
            for name, message in self.protocol["messages"].items()
        }
        self.assertEqual(
            markdown_directions, expected_directions,
            "Markdown und JSON müssen dieselbe Nachrichtenrichtung nennen",
        )
        self.assertTrue(
            self.protocol["messages"]["state"]["unsolicited"],
            "Der Katalog muss die ungefragten M4-Zustände kenntlich machen",
        )

        examples_seen = set()
        blocks = re.findall(r"```(?:json|text)\n(.*?)```", self.markdown, re.DOTALL)
        for block in blocks:
            for line in block.splitlines():
                if "{" not in line:
                    continue
                with self.subTest(example=line):
                    message = json.loads(line[line.index("{"):])
                    self.assert_message_complete(message, "Markdown-Beispiel")
                    examples_seen.add(message["type"])
        self.assertEqual(
            examples_seen, expected_types,
            "Für jeden Typ ist ein vollständiges JSON-Beispiel nötig",
        )
        self.assert_message_complete(self.protocol["stateExample"], "JSON stateExample")

    def test_complete_documented_game_preserves_recipients_order_and_reset(self):
        heading = "## Ablaufbeispiel einer vollständigen Partie"
        self.assertIn(heading, self.markdown, "Das vollständige Partie-Beispiel fehlt")
        example = self.markdown.split(heading, 1)[1]
        blocks = re.findall(r"```text\n(.*?)```", example, re.DOTALL)
        self.assertEqual(
            len(blocks), 3, "Erwartet: Beitritt/Platzierung, erste Schüsse, Ende/Abgang"
        )

        rows = []
        pattern = r"^\| (\d+) \| ([AB]) \| `([^`]+)` \| (hit|miss|sunk) \| (.*?) \| (.*?) \|$"
        for number, slot, field, result, sunk, turn in re.findall(pattern, example, re.MULTILINE):
            rows.append({
                "number": int(number), "slot": slot, "field": field,
                "result": result, "sunk": json.loads(sunk), "turn": json.loads(turn),
            })
        self.assertEqual(
            [row["number"] for row in rows], list(range(1, 34)),
            "Die Zugtabelle muss alle 33 Schüsse lückenlos festlegen",
        )

        outgoing = []
        sockets = {slot: RecordingSocket(slot, outgoing) for slot in ("A", "B")}
        connections = {slot: {"slot": None, "leaving": False} for slot in ("A", "B")}
        game = server.new_game()
        shots_played = 0

        def handle(slot, message):
            nonlocal shots_played
            if message["type"] == "shoot":
                self.assertLess(shots_played, len(rows), "Mehr Schüsse als in der Zugtabelle")
                row = rows[shots_played]
                self.assertEqual(
                    (slot, message["field"]), (row["slot"], row["field"]),
                    f"Schuss {row['number']}: ausgeschriebenes Beispiel weicht von Tabelle ab",
                )
                shots_played += 1
            server.handle(message, connections[slot], game, sockets[slot])
            if message["type"] == "leave":
                self.assertTrue(
                    connections[slot]["leaving"], "leave muss den Aufräumablauf auslösen"
                )
                server.remove_player(connections[slot], game)

        def replay_block(block):
            for line in block.splitlines():
                route, encoded = line.split("  ", 1)
                message = json.loads(encoded)
                if route.endswith("→ S"):
                    self.assertEqual(
                        outgoing, [], f"Vor {line} blieben unerwartete Antworten übrig"
                    )
                    handle(route[0], message)
                else:
                    for recipient in route.split("→ ")[1].split("/"):
                        self.assertTrue(outgoing, f"Die dokumentierte Antwort fehlt: {line}")
                        self.assertEqual(
                            outgoing.pop(0), (recipient, message),
                            f"Empfänger, Reihenfolge oder Payload weichen ab: {line}",
                        )
            self.assertEqual(outgoing, [], "Der Beispielabschnitt lässt Antworten undokumentiert")

        with redirect_stdout(io.StringIO()):
            replay_block(blocks[0])
            replay_block(blocks[1])
            self.assertEqual(
                shots_played, 2, "Der mittlere Abschnitt beschreibt die ersten zwei Schüsse"
            )

            # Die Tabelle beschreibt alle nicht ausgeschriebenen Zwischenschüsse.
            for row in rows[shots_played:-1]:
                with self.subTest(shot=row["number"]):
                    handle(row["slot"], {"type": "shoot", "field": row["field"]})
                    expected_result = {
                        "type": "result", "field": row["field"], "result": row["result"],
                        "sunk": row["sunk"], "turn": row["turn"],
                    }
                    expected_responses = [(row["slot"], expected_result)]
                    expected_responses.extend(
                        (slot, {"type": "state", **game["core"].state(slot)})
                        for slot in ("A", "B")
                    )
                    self.assertEqual(
                        outgoing, expected_responses,
                        f"Schuss {row['number']}: direkte Antwort muss vor beiden "
                        "gefilterten Zuständen liegen",
                    )
                    for recipient, message in outgoing:
                        self.assert_message_complete(
                            message, f"Schuss {row['number']}, Empfänger {recipient}"
                        )
                    outgoing.clear()

            replay_block(blocks[2])

        self.assertEqual(
            shots_played, 33, "Die dokumentierte Partie muss alle 33 Schüsse ausführen"
        )
        self.assertEqual(game["taken"], ["A"], "Nach Bobs Abgang bleibt nur Alice verbunden")
        self.assertIsNone(connections["B"]["slot"], "Bobs Slot muss nach leave frei sein")
        empty_state = {
            "phase": "waiting", "turn": None, "ownShips": [],
            "shotsAtOpponent": {}, "shotsAtSelf": {}, "winner": None,
        }
        for slot in ("A", "B"):
            self.assertEqual(
                game["core"].state(slot), empty_state,
                f"Reset muss die ganze Sicht von {slot} leeren",
            )
