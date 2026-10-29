# GUI-Bilder und SVG-Flotte

## Erhaltenes ImageGen-PNG

Am 27.10.2026 für dieses Projekt mit dem eingebauten **ImageGen**-Werkzeug
erzeugt, ohne Bildvorlage. Keine Aussage über eigenhändisches Zeichnen.

- `schiff_imagegen_original.png`: unverändertes generiertes Original,
  tatsächlich **1254×1254 Pixel**, PNG mit Alpha. Der gewünschte 1024-Pixel-
  Wert im Prompt wurde vom Werkzeug nicht übernommen.
- `schiff.png`: **256×256 Pixel**, PNG mit Alpha. Aus dem Original mit
  `sips -z 256 256 ... --out ...` skaliert. Der Benutzer hat die Skalierung
  mit sips ausdrücklich freigegeben. Die Skalierung wurde danach erneut aus
  dem erhaltenen Original ausgeführt; das Original bleibt zur Herkunft erhalten.
- Anzeige: Tk `PhotoImage(...).subsample(4)`, **64×64 Pixel**. Die Referenz
  `ship_image` lebt am Fenster; Laden, Anzeigen und Freigeben geschehen im
  Tk-Hauptthread. Der Dateipfad wird relativ zu `__file__` aufgelöst.

Das Bild ist ausschliesslich Dekoration im Fenstertitelbereich. Es hat keine
Funktion für Regeln, Flottenpositionen oder Schussergebnisse. Seine
Darstellung und Lebensdauer werden an echten Tk-Pixeln geprüft; tatsächliche
Testergebnisse stehen im unabhängigen Endprüfbericht.

Prompt:

> Use case: stylized-concept. Asset type: small decorative PNG for an
> educational Battleship desktop game. Generate one original compact
> illustration of a single friendly navy-blue patrol ship viewed three-quarter
> from above, clean readable silhouette and a few soft blue highlights,
> centered with generous transparent padding. Genuine transparent background,
> square 1024 by 1024 pixels (fixed power-of-two size), no sea rectangle, no
> text, no logos, no watermark, no game boards, no UI. It must remain
> recognisable when displayed at 64 by 64 pixels.

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
`src/ship_art.py` liest mit `xml.etree.ElementTree` die verwendeten Polygone,
Rechtecke, Kreise, Ellipsen und Linien und zeichnet sie als Tk-Canvas-Objekte.
Skalierung und Drehung um 90 Grad erfolgen beim Zeichnen; bei senkrechter
Platzierung zeigt der Bug nach unten. Es braucht weder eine SVG-Bibliothek
noch native SVG-Unterstützung in Tk. Die Quellen werden relativ zu
`__file__` gefunden. Die beiden PNG-Dateien und ihre Headeranzeige bleiben
erhalten.
