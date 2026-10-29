"""Manuellen M3-Angriffstest gegen einen separat gestarteten Server ausführen."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from tests.meilenstein_03.test_angriff import main


if __name__ == "__main__":
    main()
