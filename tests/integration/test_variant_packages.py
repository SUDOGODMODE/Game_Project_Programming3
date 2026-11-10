"""Jedes Profil-ZIP muss allein und mit geprueften Quellen nutzbar sein."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from tools.build_submission import build_submission


class VariantPackageTests(unittest.TestCase):
    def fixture(self, base):
        repo = base / "Game_Project_Programming3"
        files = {
            "README.md": "profile selection\n",
            "REGELN.md": "rules\n",
            "PROTOKOLL.md": "Protokoll 0.6 with gameOver\n",
            "src/board.py": "compat\n",
            "src/spiel.py": "core\n",
            "src/test_spiel.py": "tests\n",
            "src/netz.py": "transport\n",
            "src/server.py": "server\n",
            "src/client_gui.py": "client\n",
            "bilder/schiff.png": "image\n",
            "bilder/flotte/carrier.svg": "svg\n",
            "tests/integration/test_spiel.py": "test index\n",
            "docs/status/overview.md": "status\n",
            "docs/evidence/final/score.txt": "actual evidence\n",
            "varianten/localhost/start.py": "# localhost entry\n",
            "varianten/localhost/START.md": "localhost instructions\n",
            "varianten/zwei_rechner/start.py": "# zwei_rechner entry\n",
            "varianten/zwei_rechner/START.md": "zwei_rechner instructions\n",
            ".git/config": "secret",
            ".venv/bin/python": "interpreter",
            "src/__pycache__/spiel.pyc": "cache",
            "logs/run.jsonl": "private runtime log",
            ".env": "SECRET=x",
            "bilder/.DS_Store": "desktop metadata",
        }
        for relative, contents in files.items():
            path = repo / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(contents, encoding="utf-8")
        originals = base / "Dokumente"
        originals.mkdir()
        (originals / "auftrag_original").write_text("original assignment", encoding="utf-8")
        return repo

    def contents(self, archive_path):
        with zipfile.ZipFile(archive_path) as archive:
            names = set(archive.namelist())
            root_members = [n for n in names if n.endswith("/src/spiel.py")]
            self.assertEqual(len(root_members), 1)
            prefix = root_members[0].removesuffix("src/spiel.py")
            data = {name: archive.read(name) for name in names if not name.endswith("/")}
        return prefix, data

    def test_two_variant_archives_have_independent_roots_and_selected_entrypoints(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            repo = self.fixture(base)
            outputs = {}
            for profile in ("localhost", "zwei_rechner"):
                path = base / f"{profile}.zip"
                self.assertEqual(Path(build_submission(repo, path, variant=profile)), path)
                outputs[profile] = (path, *self.contents(path))
            self.assertNotEqual(outputs["localhost"][1], outputs["zwei_rechner"][1])
            required = ("README.md", "REGELN.md", "PROTOKOLL.md", "src/spiel.py",
                        "src/test_spiel.py", "src/netz.py", "src/server.py", "src/client_gui.py",
                        "bilder/schiff.png", "bilder/flotte/carrier.svg",
                        "tests/integration/test_spiel.py", "docs/status/overview.md",
                        "docs/evidence/final/score.txt", "START_HIER.md", "start.py", "PROFIL.txt")
            for profile, (path, prefix, data) in outputs.items():
                with self.subTest(profile=profile):
                    parts = Path(prefix).parts
                    self.assertEqual(len(parts), 2, prefix)
                    self.assertEqual(parts[1], repo.name)
                    self.assertEqual(parts[0], f"Schiffe_versenken_{profile}")
                    for relative in required:
                        self.assertIn(prefix + relative, data)
                    self.assertEqual(data[prefix + "start.py"],
                                     f"# {profile} entry\n".encode())
                    self.assertIn(profile.encode(), data[prefix + "START_HIER.md"])
                    self.assertEqual(data[prefix + "PROFIL.txt"], (profile + "\n").encode())
                    original = parts[0] + "/Dokumente/auftrag_original"
                    self.assertIn(original, data)
                    self.assertEqual(data[original], b"original assignment")
                    for name in data:
                        parts = Path(name).parts
                        self.assertFalse(any(part in {".git", ".venv", "__pycache__", "logs"}
                                             or part.startswith(".env") for part in parts), name)
                        self.assertNotIn(".DS_Store", parts)
                    manifest = json.loads(data["SHA256SUMS.json"])
                    self.assertEqual(set(manifest), set(data) - {"SHA256SUMS.json"})
                    for name, digest in manifest.items():
                        self.assertEqual(hashlib.sha256(data[name]).hexdigest(), digest, name)
                    digest, filename = path.with_name(path.name + ".sha256").read_text().split()
                    self.assertEqual(filename, path.name)
                    self.assertEqual(digest, hashlib.sha256(path.read_bytes()).hexdigest())

    def test_invalid_profile_and_existing_archive_are_rejected_without_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            repo = self.fixture(base)
            archive = base / "archive.zip"
            with self.assertRaises(ValueError):
                build_submission(repo, archive, variant="unknown")
            self.assertFalse(archive.exists())
            archive.write_bytes(b"old archive")
            with self.assertRaises(FileExistsError):
                build_submission(repo, archive, variant="localhost")
            self.assertEqual(archive.read_bytes(), b"old archive")


if __name__ == "__main__":
    unittest.main(verbosity=2)
