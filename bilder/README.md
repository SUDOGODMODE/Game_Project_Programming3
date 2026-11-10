# GUI-Bilder und SVG-Flotte

## Schiffsbild

- `schiff_imagegen_original.png`: Originaldatei, **1254×1254 Pixel**, PNG
  mit Alpha.
- `schiff.png`: **256×256 Pixel**, PNG mit Alpha, mit `sips -z 256 256 ... --out ...`
  aus dem Original skaliert. Das Original bleibt zur Herkunft erhalten.
- Anzeige: Tk `PhotoImage(...).subsample(4)`, **64×64 Pixel**. Die Referenz
  `ship_image` lebt am Fenster; Laden, Anzeigen und Freigeben geschehen im
  Tk-Hauptthread. Der Dateipfad wird relativ zu `__file__` aufgelöst.

Das Bild ist ausschliesslich Dekoration im Fenstertitelbereich. Es hat keine
Funktion für Regeln, Flottenpositionen oder Schussergebnisse.

SHA256:

```text
e782035a381767bf73a9e803a4ba362d447ef7c1ab6ee0298b69d390a608989e  schiff_imagegen_original.png
cae1a7472f82eb8714f24f91f33f860122c7090156958359992e5582e31aca81  schiff.png
```

## SVG-Flotte

Die grafische Oberfläche in Meerblau verwendet zusätzlich fünf transparente
SVG-Quellen für die Flottenplanung und die eigenen bestätigten Schiffe:

| Quelle | Schiff | Felder / viewBox |
|---|---|---|
| [flotte/carrier.svg](flotte/carrier.svg) | Flugzeugträger | 5 / `0 0 200 40` |
| [flotte/battleship.svg](flotte/battleship.svg) | Schlachtschiff | 4 / `0 0 160 40` |
| [flotte/cruiser.svg](flotte/cruiser.svg) | Kreuzer | 3 / `0 0 120 40` |
| [flotte/submarine.svg](flotte/submarine.svg) | U-Boot | 3 / `0 0 120 40` |
| [flotte/destroyer.svg](flotte/destroyer.svg) | Zerstörer | 2 / `0 0 80 40` |

Die Draufsichten in Hellblau und Stahlblau zeigen den Bug nach rechts.
`src/gui/ship_art.py` liest mit `xml.etree.ElementTree` die verwendeten Polygone,
Rechtecke, Kreise, Ellipsen und Linien und zeichnet sie als Tk-Canvas-Objekte.
Skalierung und Drehung um 90 Grad erfolgen beim Zeichnen; bei senkrechter
Platzierung zeigt der Bug nach unten. Es braucht weder eine SVG-Bibliothek
noch native SVG-Unterstützung in Tk. Die Quellen werden relativ zu
`__file__` gefunden. Die beiden PNG-Dateien und ihre Headeranzeige bleiben
erhalten.
