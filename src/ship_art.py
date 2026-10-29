"""Kleine SVG-Flotte als echte Canvas-Vektoren, ohne Zusatzpakete.

Die SVG-Quellen unter ``bilder/flotte`` zeigen den Bug nach rechts. Nur die
dort verwendeten Grundformen werden gelesen; dies ist kein allgemeiner
SVG-Renderer. ``draw_svg`` darf ausserhalb eines Canvas zeichnen: Tk schneidet
das Bild am Widgetrand ab. So kann jede Rasterzelle ihren Schiffsausschnitt
zeigen. Alle Canvas-Aufrufe erfolgen durch den Aufrufer im Tk-Hauptthread.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from math import isfinite
from pathlib import Path
from typing import TYPE_CHECKING
import xml.etree.ElementTree as ET

if TYPE_CHECKING:
    import tkinter as tk


ASSET_DIRECTORY = Path(__file__).resolve().parents[1] / "bilder" / "flotte"
SHIP_NAMES = {
    "Carrier": "Flugzeugträger",
    "Battleship": "Schlachtschiff",
    "Cruiser": "Kreuzer",
    "Submarine": "U-Boot",
    "Destroyer": "Zerstörer",
}
SHIP_ASSETS = {
    "Carrier": ASSET_DIRECTORY / "carrier.svg",
    "Battleship": ASSET_DIRECTORY / "battleship.svg",
    "Cruiser": ASSET_DIRECTORY / "cruiser.svg",
    "Submarine": ASSET_DIRECTORY / "submarine.svg",
    "Destroyer": ASSET_DIRECTORY / "destroyer.svg",
}


@dataclass(frozen=True)
class SvgShape:
    """Grundform mit flachen x/y-Koordinaten im SVG-Koordinatensystem."""

    kind: str
    coordinates: tuple[float, ...]
    fill: str
    stroke: str
    stroke_width: float


@dataclass(frozen=True)
class SvgArtwork:
    width: float
    height: float
    shapes: tuple[SvgShape, ...]


def _numbers(value: str) -> tuple[float, ...]:
    numbers = tuple(float(part) for part in value.replace(",", " ").split())
    if not all(isfinite(number) for number in numbers):
        raise ValueError("SVG-Koordinaten muessen endlich sein")
    return numbers


@lru_cache(maxsize=len(SHIP_ASSETS))
def load_svg(ship_type: str) -> SvgArtwork:
    """Liest eine ausgelieferte Quelle unabhaengig vom Arbeitsverzeichnis.

    Das unveraenderliche Ergebnis wird je Schiffstyp zwischengespeichert.
    Unbekannte Typen oder nicht unterstuetzte SVG-Formen sind Fehler.
    """
    try:
        source = SHIP_ASSETS[ship_type]
    except KeyError as exc:
        raise ValueError(f"Unbekannter Schiffstyp: {ship_type}") from exc
    root = ET.parse(source).getroot()
    view_box = _numbers(root.attrib["viewBox"])
    if len(view_box) != 4 or view_box[:2] != (0, 0) or min(view_box[2:]) <= 0:
        raise ValueError(f"Ungueltige SVG-viewBox: {source.name}")
    shapes = []
    for element in root:
        kind = element.tag.rsplit("}", 1)[-1]
        if kind in ("title", "desc"):
            continue
        attributes = element.attrib
        number = lambda key, default="0": float(attributes.get(key, default))
        if kind == "polygon":
            coordinates = _numbers(attributes["points"])
            if len(coordinates) < 6 or len(coordinates) % 2:
                raise ValueError(f"Ungueltiges SVG-Polygon: {source.name}")
        elif kind == "line":
            coordinates = tuple(number(key) for key in ("x1", "y1", "x2", "y2"))
        elif kind == "rect":
            x, y, width, height = (number(key) for key in ("x", "y", "width", "height"))
            coordinates = (x, y, x + width, y + height)
        elif kind in ("circle", "ellipse"):
            x, y = number("cx"), number("cy")
            rx = number("r") if kind == "circle" else number("rx")
            ry = number("r") if kind == "circle" else number("ry")
            coordinates = (x - rx, y - ry, x + rx, y + ry)
        else:
            raise ValueError(f"Nicht unterstuetzte SVG-Form: {kind}")
        stroke_width = number("stroke-width", "1")
        if not all(isfinite(value) for value in (*coordinates, stroke_width)):
            raise ValueError(f"Ungueltige SVG-Koordinaten: {source.name}")
        shapes.append(SvgShape(kind, coordinates,
                               attributes.get("fill", "black").replace("none", ""),
                               attributes.get("stroke", "none").replace("none", ""),
                               stroke_width))
    return SvgArtwork(view_box[2], view_box[3], tuple(shapes))


def draw_svg(canvas: tk.Canvas, ship_type: str, x: float, y: float,
             length: float, thickness: float, vertical: bool = False,
             tags: tuple[str, ...] = ()) -> list[int]:
    """Zeichnet ein Schiff und gibt die Canvas-Item-IDs zurueck.

    ``x, y`` ist die linke obere Ecke des gesamten Schiffsrechtecks.
    Horizontal misst es ``length × thickness``, vertikal
    ``thickness × length``. Vertikal wird die Quelle um 90 Grad im
    Uhrzeigersinn gedreht, der Bug zeigt nach unten. Negative Positionen
    sind erlaubt; ``tags`` wird jedem erzeugten Item zugewiesen.
    """
    if not all(isfinite(value) for value in (x, y, length, thickness)) or min(length, thickness) <= 0:
        raise ValueError("Schiffsgroesse muss positiv und Koordinaten muessen endlich sein")
    artwork = load_svg(ship_type)
    along, across = length / artwork.width, thickness / artwork.height
    stroke_scale = min(along, across)

    def point(source_x: float, source_y: float) -> tuple[float, float]:
        if vertical:
            return x + thickness - source_y * across, y + source_x * along
        return x + source_x * along, y + source_y * across

    items = []
    for shape in artwork.shapes:
        pairs = [point(shape.coordinates[index], shape.coordinates[index + 1])
                 for index in range(0, len(shape.coordinates), 2)]
        coordinates = tuple(value for pair in pairs for value in pair)
        width = max(0.5, shape.stroke_width * stroke_scale)
        if shape.kind == "line":
            item = canvas.create_line(*coordinates, fill=shape.stroke, width=width,
                                      capstyle="round", tags=tags)
        else:
            options = {"fill": shape.fill, "outline": shape.stroke, "width": width, "tags": tags}
            if shape.kind == "polygon":
                item = canvas.create_polygon(*coordinates, joinstyle="round", **options)
            else:
                xs, ys = zip(*pairs)
                box = (min(xs), min(ys), max(xs), max(ys))
                if shape.kind == "rect":
                    item = canvas.create_rectangle(*box, **options)
                else:
                    item = canvas.create_oval(*box, **options)
        items.append(item)
    return items
