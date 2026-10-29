"""Build real ZIPs and verify payloads, source layout and independent digests."""
import hashlib
import importlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile


class PackagingTests(unittest.TestCase):
    def builder(self):
        self.assertIsNotNone(importlib.util.find_spec('tools.build_submission'), 'Submission builder is missing')
        return importlib.import_module('tools.build_submission').build_submission

    def fixture(self, base):
        repo = base / 'Game_Project_Programming3'
        files = {
            'README.md': 'See ../Dokumente/source.txt\n', 'REGELN.md': 'rules', 'PROTOKOLL.md': 'protocol',
            'src/board.py': 'CORE = True\n', 'src/netz.py': 'TRANSPORT = True\n',
            'src/server.py': 'SERVER = True\n', 'src/client_gui.py': 'GUI = True\n',
            'tests/meilenstein_02/test_core.py': 'test fixture', 'tools/run_tests.py': 'runner',
            'bilder/ship.png': 'image bytes fixture', 'docs/status/open.md': 'External tests pending',
            '.git/config': 'git secret', '.venv/bin/python': 'venv', 'src/__pycache__/board.pyc': 'cache',
            '.env': 'SECRET=x', 'docs/.env.local': 'SECRET=y', '.pytest_cache/cache': 'cache',
            'logs/local.jsonl': 'runtime', 'docs/evidence/original.txt': 'immutable original',
        }
        for name, value in files.items():
            path = repo / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(value)
        originals = base / 'Dokumente'
        originals.mkdir()
        (originals / 'source.txt').write_text('original source')
        return repo

    def test_archive_contains_dependencies_assets_tests_sources_and_verified_manifest(self):
        build = self.builder()
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            repo = self.fixture(base)
            output = base / 'submission.zip'
            self.assertEqual(Path(build(repo, output)), output)
            with zipfile.ZipFile(output) as archive:
                names = set(archive.namelist())
                prefix = repo.name + '/'
                for name in ('README.md', 'src/board.py', 'src/netz.py', 'src/server.py', 'src/client_gui.py', 'tests/meilenstein_02/test_core.py', 'bilder/ship.png', 'docs/evidence/original.txt'):
                    self.assertIn(prefix + name, names)
                self.assertIn('Dokumente/source.txt', names)
                self.assertEqual(archive.read('Dokumente/source.txt'), b'original source')
                self.assertEqual(archive.read(prefix + 'src/board.py'), b'CORE = True\n')
                for name in names:
                    parts = Path(name).parts
                    self.assertFalse(any(part in ('.git', '.venv', '__pycache__', '.pytest_cache', 'logs') or part.startswith('.env') for part in parts), name)
                manifest = json.loads(archive.read('SHA256SUMS.json'))
                files = {n for n in names if not n.endswith('/') and n != 'SHA256SUMS.json'}
                self.assertEqual(set(manifest), files)
                for name, digest in manifest.items():
                    self.assertEqual(hashlib.sha256(archive.read(name)).hexdigest(), digest, name)

    def test_existing_archive_is_preserved_byte_for_byte(self):
        build = self.builder()
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            repo = self.fixture(base)
            output = base / 'old.zip'
            output.write_bytes(b'original archive evidence')
            with self.assertRaises(FileExistsError): build(repo, output)
            self.assertEqual(output.read_bytes(), b'original archive evidence')
