"""Kurze lokale Sprengung eines neu bestaetigt versenkten eigenen Schiffes."""
import math
import time


class ShipEffects:
    """Nur Darstellung: veraendert weder Spielzustand noch Netzwerkverkehr.

    Alle Aufrufe und ``after``-Callbacks gehoeren in den Tk-Hauptthread.
    Der erste Snapshot bildet nur die Ausgangslage, auch bei alten Wracks.
    """

    DURATION = 1.15

    def __init__(self, root, own_buttons, enabled=lambda: True):
        self.root = root
        self.cells = own_buttons
        self.enabled = enabled
        self._previous = {}
        self._bursts = []
        self._after_id = None
        self._closed = False

    @property
    def active(self):
        return bool(self._bursts)

    def observe(self, ships):
        if self._closed:
            return
        if not ships:
            self.reset()
            return
        current = {}
        for ship in ships:
            cells = tuple(ship.get("cells", ()))
            key = (ship.get("type"), cells)
            sunk = bool(cells) and set(cells).issubset(ship.get("hits", ()))
            current[key] = sunk
            if sunk and key in self._previous and not self._previous[key] and self.enabled():
                self._bursts.append((cells, time.monotonic()))
        self._previous = current
        if self._bursts and self._after_id is None:
            self._tick()

    def _clear(self):
        for canvas in self.cells.values():
            canvas.delete("explosion")

    def _tick(self):
        self._after_id = None
        self._clear()
        if self._closed or not self.enabled():
            self._bursts.clear()
            return
        now = time.monotonic()
        self._bursts = [(cells, start) for cells, start in self._bursts if now - start < self.DURATION]
        for cells, start in self._bursts:
            self._draw_burst(cells, now - start)
        if self._bursts:
            self._after_id = self.root.after(33, self._tick)

    @staticmethod
    def _position(field):
        return ord(field[0]) - ord("A"), int(field[1:]) - 1

    def _draw_burst(self, fields, elapsed):
        positions = [self._position(field) for field in fields]
        left = min(x for x, y in positions) - 1
        right = max(x for x, y in positions) + 1
        top = min(y for x, y in positions) - 1
        bottom = max(y for x, y in positions) + 1
        burst_center_x = sum(x + .5 for x, y in positions) / len(positions)
        burst_center_y = sum(y + .5 for x, y in positions) / len(positions)
        for field, canvas in self.cells.items():
            col, row = self._position(field)
            if not (left <= col <= right and top <= row <= bottom):
                continue
            cell_size = float(canvas.cget("width"))
            self._draw_pressure_ring(canvas, cell_size, burst_center_x, burst_center_y, col, row, elapsed)
            for index, (x, y) in enumerate(positions):
                age = elapsed - index * .035
                if not 0 <= age < .95:
                    continue
                center_x, center_y = (x + .5 - col) * cell_size, (y + .5 - row) * cell_size
                self._draw_fireball(canvas, cell_size, center_x, center_y, age)
                self._draw_sparks(canvas, cell_size, center_x, center_y, age, index)
                self._draw_smoke(canvas, cell_size, center_x, center_y, age)

    @staticmethod
    def _draw_pressure_ring(canvas, cell_size, center_x, center_y, col, row, elapsed):
        """Ein durchgehender Druckring ueber mehreren Canvas-Feldern."""
        if elapsed < .55:
            radius = cell_size * (.15 + 2 * elapsed)
            center_x, center_y = (center_x - col) * cell_size, (center_y - row) * cell_size
            canvas.create_oval(center_x - radius, center_y - radius, center_x + radius, center_y + radius,
                               outline="#ffe3b0" if elapsed < .2 else "#bd8e70",
                               width=2 if elapsed < .25 else 1, tags="explosion")

    @staticmethod
    def _draw_fireball(canvas, cell_size, center_x, center_y, age):
        """Den kurzen sternfoermigen Feuerball eines Schiffsfeldes zeichnen."""
        if age < .28:
            radius = cell_size * (.26 + .20 * math.sin(age / .28 * math.pi))
            points = []
            for spoke in range(16):
                angle = spoke * math.pi / 8
                r = radius if spoke % 2 == 0 else radius * .48
                points.extend((center_x + math.cos(angle) * r, center_y + math.sin(angle) * r))
            color = "#fff0c2" if age < .075 else "#ffc078" if age < .16 else "#f38c59"
            canvas.create_polygon(*points, fill=color, outline="", tags="explosion")

    @staticmethod
    def _draw_sparks(canvas, cell_size, center_x, center_y, age, index):
        """Deterministische Funken; kein Spielzufall und kein weiterer Thread."""
        if age < .62:
            for spark in range(7):
                angle = spark * math.tau / 7 + index * .9
                distance = cell_size * (.20 + age * 1.1)
                px = center_x + math.cos(angle) * distance
                py = center_y + math.sin(angle) * distance + cell_size * age * age * .25
                tail = cell_size * .11 * (1 - age / .62)
                canvas.create_line(px, py, px - math.cos(angle) * tail,
                                   py - math.sin(angle) * tail,
                                   fill="#ffe0a0" if age < .3 else "#bc7755",
                                   width=2, tags="explosion")

    @staticmethod
    def _draw_smoke(canvas, cell_size, center_x, center_y, age):
        """Rauch gleicht sich ohne Alpha-Abhaengigkeit dem Meer an."""
        if .22 < age < .95:
            fade = (age - .22) / .73
            base = canvas.winfo_rgb(canvas.cget("background"))
            # Tk liefert 16-Bit-Farbkanaele; 257 rechnet sie auf 8 Bit um.
            smoke = tuple(int(83 * (1 - fade) + channel / 257 * fade) for channel in base)
            color = "#%02x%02x%02x" % smoke
            for cloud in range(2):
                radius = cell_size * (.10 + fade * .12)
                px = center_x + (cloud - .5) * cell_size * .24
                py = center_y - cell_size * (fade * .42 + cloud * .09)
                canvas.create_oval(px - radius, py - radius, px + radius, py + radius,
                                   fill=color, outline="", tags="explosion")

    def stop(self):
        """Nur laufende Bilder stoppen; bestaetigte Verluste bleiben bekannt."""
        if self._after_id is not None:
            self.root.after_cancel(self._after_id)
            self._after_id = None
        self._bursts.clear()
        self._clear()

    def reset(self):
        self.stop()
        self._previous.clear()

    def close(self):
        if self._closed:
            return
        self.reset()
        self._closed = True
        self.enabled = lambda: False
