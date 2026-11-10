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
            'src/board.py': 'COMPAT = True\n', 'src/spiel.py': 'CORE = True\n',
            'src/test_spiel.py': 'CORE_TESTS = True\n', 'src/netz.py': 'TRANSPORT = True\n',
            'src/server.py': 'SERVER = True\n', 'src/client_gui.py': 'GUI = True\n',
            'src/testclient.py': 'TEST_CLIENT = True\n', 'src/test_netz.py': 'NETWORK_TESTS = True\n',
            'tests/meilenstein_02/test_core.py': 'test fixture', 'tools/run_tests.py': 'runner',
            'tests/meilenstein_06/test_netz.py': 'course test wrapper',
            'tests/meilenstein_06/test_server_port.py': 'port tests',
            'bilder/ship.png': 'image bytes fixture', 'docs/status/open.md': 'External tests pending',
            'docs/status/05_requirements.md': 'M5 results',
            'docs/status/06_requirements.md': 'M6 results',
            'docs/evidence/06_final_2026-11-10/discover_green.txt': '190 tests passed',
            'docs/evidence/05_end.png': 'image evidence fixture',
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
        (originals / 'Auftrag_Meilenstein6.docx').write_bytes(b'original M6 source fixture')
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
                for name in ('README.md', 'src/board.py', 'src/spiel.py', 'src/test_spiel.py',
                             'src/netz.py', 'src/server.py', 'src/client_gui.py',
                             'src/testclient.py', 'src/test_netz.py',
                             'tests/meilenstein_02/test_core.py',
                             'tests/meilenstein_06/test_netz.py',
                             'tests/meilenstein_06/test_server_port.py',
                             'bilder/ship.png', 'docs/evidence/original.txt',
                             'docs/status/05_requirements.md',
                             'docs/status/06_requirements.md',
                             'docs/evidence/06_final_2026-11-10/discover_green.txt',
                             'docs/evidence/05_end.png'):
                    self.assertIn(prefix + name, names)
                self.assertIn('Dokumente/source.txt', names)
                self.assertIn('Dokumente/Auftrag_Meilenstein6.docx', names)
                self.assertEqual(archive.read('Dokumente/source.txt'), b'original source')
                self.assertEqual(archive.read(prefix + 'src/spiel.py'), b'CORE = True\n')
                status = archive.read(prefix + 'ABGABESTATUS.md').decode('utf-8')
                self.assertIn('docs/status/06_requirements.md', status)
                self.assertIn('Zweirechnerlauf', status)
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

    def test_local_development_tooling_is_excluded_from_archive(self):
        build = self.builder()
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            repo = self.fixture(base)
            for name in ('.specify/memory/constitution.md', '.agents/skills/local/SKILL.md'):
                path = repo / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('local development instructions')
            output = base / 'submission.zip'
            build(repo, output)
            with zipfile.ZipFile(output) as archive:
                for name in archive.namelist():
                    self.assertTrue({'.specify', '.agents'}.isdisjoint(Path(name).parts), name)
                self.assertIn(repo.name + '/src/spiel.py', archive.namelist())
