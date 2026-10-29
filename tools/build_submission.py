"""Create a new reviewable ZIP with source documents and SHA256 manifests."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRS = {
    ".git", ".venv", "venv", "env", "ENV", "__pycache__", ".pytest_cache",
    ".mypy_cache", ".ruff_cache", ".tox", ".nox", ".idea", ".vscode",
    "dist", "build", "node_modules", ".aws", ".ssh", ".codex", ".agents",
}


def _included(relative):
    parts = relative.parts
    if any(part in EXCLUDED_DIRS or part.startswith(".env") for part in parts):
        return False
    if "logs" in parts and parts[:2] != ("docs", "evidence"):
        return False
    name = relative.name.lower()
    if name in {".ds_store", "thumbs.db", "desktop.ini", "credentials", ".coverage"} or name.startswith("._"):
        return False
    if name.endswith((".pyc", ".pyo", ".pyd", ".zip", ".tmp", ".swp", ".swo", ".pem", ".key", ".p12", ".pfx", "~")):
        return False
    if name.endswith(".log") and parts[:2] != ("docs", "evidence"):
        return False
    return True


def _files(root):
    # Never follow symlinks out of the selected source tree.
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if path.is_file() and not path.is_symlink() and not any(parent.is_symlink() for parent in path.parents if parent != root.parent):
            if _included(relative):
                yield path, relative


def build_submission(repo_root, output):
    """Package actual files; exclusive output/checksum creation, no source changes."""
    repo_root = Path(repo_root).resolve()
    output = Path(output)
    checksum_path = output.with_name(output.name + ".sha256")
    if output.exists() or checksum_path.exists():
        raise FileExistsError(f"Ausgabe existiert bereits: {output} oder {checksum_path}")
    if not repo_root.is_dir():
        raise FileNotFoundError(repo_root)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest = {}
    with output.open("xb") as stream:
        try:
            with checksum_path.open("x", encoding="utf-8") as checksum_stream:
                with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                    roots = [(repo_root, repo_root.name)]
                    originals = repo_root.parent / "Dokumente"
                    if originals.is_dir():
                        roots.append((originals, "Dokumente"))
                    for root, prefix in roots:
                        for path, relative in _files(root):
                            if path.resolve() in (output.resolve(), checksum_path.resolve()):
                                continue
                            member = f"{prefix}/{relative.as_posix()}"
                            data = path.read_bytes()
                            archive.writestr(member, data)
                            manifest[member] = hashlib.sha256(data).hexdigest()
                    status = (
                        "# Abgabestatus\n\n"
                        "Technisches Paket aus tatsächlich vorhandenen Dateien.\n"
                        "Erstellt: " + datetime.now(timezone.utc).isoformat() + "\n\n"
                        "Offen: persönliche Reflexion durch den Projektverantwortlichen; "
                        "eigene Prüfung/Überarbeitung und Erklärung des technischen Berichts; "
                        "menschliches Regel-/Protokoll-Gegenlesen, Lesepartnerschaft, reale "
                        "Zweipersonenpartie, Echo/Handshake-Fremdtests mit Rollenwechsel, "
                        "Dreirechnerpartie mit fremden IPs und gemeinsamem Bild, gegenseitiger "
                        "Fremdclienttest und Livevorführung. Keine vollständige Abgabeerfüllung "
                        "oder Punktezahl wird behauptet.\n\n"
                        "Aktuelle tatsächliche lokale Ergebnisse siehe docs/status/final_test_verdict.md "
                        "und docs/evidence; historische Belege behalten ihren ursprünglichen Stand. "
                        "Das Vorhandensein einer Datei ist keine Behauptung über einen neuen Testlauf.\n"
                    ).encode("utf-8")
                    member = f"{repo_root.name}/ABGABESTATUS.md"
                    archive.writestr(member, status)
                    manifest[member] = hashlib.sha256(status).hexdigest()
                    archive.writestr("SHA256SUMS.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
                stream.flush()
                with output.open("rb") as archive_stream:
                    digest = hashlib.file_digest(archive_stream, "sha256").hexdigest()
                checksum_stream.write(f"{digest}  {output.name}\n")
        except BaseException:
            # Only remove the newly-created incomplete archive, never old evidence.
            stream.close()
            output.unlink(missing_ok=True)
            raise
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    default = ROOT / "dist" / ("Schiffe_versenken_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ") + ".zip")
    parser.add_argument("--output", type=Path, default=default, help="Neues ZIP; Standard zeitgestempelt unter dist/")
    args = parser.parse_args()
    try:
        path = build_submission(ROOT, args.output)
    except OSError as exc:
        parser.exit(1, f"Abgabepaket konnte nicht erstellt werden: {exc}\n")
    print(path)
    print(path.with_name(path.name + ".sha256"))


if __name__ == "__main__":
    main()
