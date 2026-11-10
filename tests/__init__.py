"""Regressionstests, nach ursprünglichem Schwerpunkt gruppiert.

Der Kursbefehl ``python3 -m unittest discover`` startet im Projektordner.
Dabei muss Python die eigenständigen Programme unter ``src/`` finden können.
Der gemeinsame Teststarter setzt denselben Pfad bereits selbst.
"""
from pathlib import Path
import sys


SOURCE = str(Path(__file__).resolve().parents[1] / "src")
if SOURCE not in sys.path:
    sys.path.insert(0, SOURCE)
