"""Fensterloser Client für die Netztests in test_netz.py."""

import queue
import socket
import threading
import time

from netz import read_messages, send


ENDE = object()


class Testclient:
    """Liest Servernachrichten im Hintergrund und stellt sie den Tests bereit."""

    def __init__(self, host, port, name=None):
        self.sock = socket.create_connection((host, port), timeout=2)
        self.sock.settimeout(None)
        self.eingang = queue.Queue()
        self.alle = []
        self.leser = threading.Thread(target=self._lesen, daemon=True)
        self.leser.start()
        if name is not None:
            self.schicke({"type": "join", "player": name})

    def _lesen(self):
        try:
            for nachricht in read_messages(self.sock):
                self.eingang.put(nachricht)
        finally:
            self.eingang.put(ENDE)

    def schicke(self, nachricht):
        send(self.sock, nachricht)

    def empfange(self, sekunden=2.0):
        """Holt die nächste Nachricht; ein Timeout zeigt die bisherige Folge."""
        try:
            nachricht = self.eingang.get(timeout=sekunden)
        except queue.Empty:
            typen = [eintrag.get("type") for eintrag in self.alle]
            raise AssertionError(f"keine Nachricht nach {sekunden}s; bisher: {typen}") from None
        if nachricht is ENDE:
            raise AssertionError(f"Server hat die Verbindung beendet; bisher: {self.alle!r}")
        self.alle.append(nachricht)
        return nachricht

    def erwarte(self, typ, sekunden=2.0):
        """Prüft die nächste Nachricht, ohne eine falsche Reihenfolge zu verdecken."""
        nachricht = self.empfange(sekunden)
        assert nachricht.get("type") == typ, f"erwartet {typ!r}, bekommen {nachricht!r}"
        return nachricht

    def warte_auf(self, typ, sekunden=2.0):
        """Überspringt andere Typen, merkt sie aber in ``alle``."""
        ende = time.monotonic() + sekunden
        while True:
            rest = ende - time.monotonic()
            if rest <= 0:
                typen = [eintrag.get("type") for eintrag in self.alle]
                raise AssertionError(f"kein {typ!r} innerhalb {sekunden}s; bisher: {typen}")
            nachricht = self.empfange(rest)
            if nachricht.get("type") == typ:
                return nachricht

    def keine(self, typ, sekunden=0.15):
        """Prüft, dass innerhalb der Frist keine Nachricht dieses Typs kommt."""
        ende = time.monotonic() + sekunden
        while True:
            rest = ende - time.monotonic()
            if rest <= 0:
                return
            try:
                nachricht = self.eingang.get(timeout=rest)
            except queue.Empty:
                return
            if nachricht is ENDE:
                raise AssertionError("Server hat die Verbindung unerwartet beendet")
            self.alle.append(nachricht)
            if nachricht.get("type") == typ:
                raise AssertionError(f"unerwartete Nachricht: {nachricht!r}")

    def schliessen(self):
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        self.sock.close()
        self.leser.join(timeout=2)
