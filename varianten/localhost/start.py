"""Startprofil fuer Server und zwei Clients auf einem Geraet."""

from pathlib import Path
import sys


def _project_root() -> Path:
    for directory in Path(__file__).resolve().parents:
        if (directory / "tools/variant_start.py").is_file() and (directory / "src/server.py").is_file():
            return directory
    raise SystemExit("Projektdateien nicht gefunden: src/server.py und tools/variant_start.py")


sys.path.insert(0, str(_project_root()))
from tools.variant_start import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main("localhost"))
