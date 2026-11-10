"""Schreibt Nachrichtenmetadaten als JSONL, ohne private Nachrichteninhalte."""
from datetime import datetime, timezone
import json
from pathlib import Path
import threading

MESSAGE_TYPES = frozenset({
    "join", "place", "shoot", "getState", "leave", "broken", "welcome",
    "waiting", "gameStart", "placeAck", "result", "state", "opponentLeft",
    "gameOver", "error",
})
ERROR_CODES = frozenset({
    "ALREADY_JOINED", "GAME_FULL", "MISSING_PLAYER", "NOT_JOINED",
    "INVALID_JSON", "UNKNOWN_TYPE", "CELL_OUT_OF_BOUNDS", "DUPLICATE_SHOT",
    "INVALID_PLACEMENT", "INVALID_PLAYER", "NOT_YOUR_TURN", "WRONG_PHASE",
})


class EventLog:
    """Besitzt eine exklusiv neu angelegte Datei; record/close teilen eine Sperre.

    Jeder Eintrag wird vor der Rueckgabe geflusht. Wiederholtes close ist
    erlaubt; spaete Serverworker schreiben nicht in die geschlossene Datei.
    """

    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._file = self.path.open("x", encoding="utf-8")

    def record(self, direction, peer, message, slot=None):
        """Schreibt erlaubte Metadaten; False, wenn das Log schon geschlossen ist.

        Unbekannte Typen werden als unknown protokolliert. Nur bekannte,
        ausgehende Fehlercodes kommen ins Log, keine freien Clienttexte.
        """
        if direction not in ("<-", "->"):
            raise ValueError("direction must be <- or ->")
        kind = message.get("type")
        kind = kind if isinstance(kind, str) and kind in MESSAGE_TYPES else "unknown"
        row = {
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="microseconds"),
            "direction": direction, "peer": str(peer),
            "slot": slot if slot in ("A", "B") else None, "type": kind,
        }
        code = message.get("code")
        if direction == "->" and kind == "error" and isinstance(code, str) and code in ERROR_CODES:
            row["code"] = code
        with self._lock:
            if self._file.closed:
                return False
            self._file.write(json.dumps(row, ensure_ascii=False) + "\n")
            self._file.flush()
        return True

    def close(self):
        with self._lock:
            self._file.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
