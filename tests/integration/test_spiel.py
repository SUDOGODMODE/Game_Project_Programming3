"""Die eigenstaendigen Kurstests in die gemeinsame Auswahl einbinden."""
import unittest

from src import test_spiel as regeln


def load_tests(loader, tests, pattern):
    return loader.loadTestsFromModule(regeln)
