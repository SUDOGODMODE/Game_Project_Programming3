"""Create a new reviewable ZIP with source documents and SHA256 manifests."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
VARIANTS = ("localhost", "zwei_rechner")
EXCLUDED_DIRS = {
    ".git", ".venv", "venv", "env", "ENV", "__pycache__", ".pytest_cache",
    ".mypy_cache", ".ruff_cache", ".tox", ".nox", ".idea", ".vscode",
    "dist", "build", "node_modules", ".aws", ".ssh", ".codex", ".agents", ".specify",
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
        if not path.is_file() or path.is_symlink():
            continue
        has_symlink_parent = any(
            parent.is_symlink() for parent in path.parents if parent != root.parent
        )
        if not has_symlink_parent and _included(relative):
            yield path, relative


def _submission_status():
    """Kennzeichnet technische Paketdateien und weiterhin offene Personenaufgaben."""
    return (
        "# Abgabestatus\n\n"
        "Technisches Paket aus tatsächlich vorhandenen Dateien.\n"
        "Erstellt: " + datetime.now(timezone.utc).isoformat() + "\n\n"
        "Offen: persönliche Reflexion durch den Projektverantwortlichen; "
        "menschliches Regel-/Protokoll-Gegenlesen, Lesepartnerschaft, reale "
        "Zweipersonenpartie, ein echter Zweirechnerlauf mit "
        "Server-Terminalausgabe und gemeinsamem Bild, gegenseitiger "
        "Fremdclienttest und Livevorführung. Keine vollständige Abgabeerfüllung "
        "oder Punktezahl wird behauptet.\n\n"
        "Das Vorhandensein einer Datei ist keine Behauptung über einen neuen Testlauf.\n"
    ).encode("utf-8")


def _write_member(archive, manifest, member, data):
    """Schreibt dieselben Bytes ins ZIP und in dessen Hashverzeichnis."""
    archive.writestr(member, data)
    manifest[member] = hashlib.sha256(data).hexdigest()


def build_submission(repo_root, output, *, variant=None):
    """Package actual files; optional profile gets its own entry and outer root."""
    if variant is not None and variant not in VARIANTS:
        raise ValueError(f"Unbekanntes Profil: {variant}")
    repo_root = Path(repo_root).resolve()
    output = Path(output)
    checksum_path = output.with_name(output.name + ".sha256")
    if output.exists() or checksum_path.exists():
        raise FileExistsError(f"Ausgabe existiert bereits: {output} oder {checksum_path}")
    if not repo_root.is_dir():
        raise FileNotFoundError(repo_root)
    if variant is None:
        project_prefix = repo_root.name
        documents_prefix = "Dokumente"
        selected_files = ()
    else:
        outer = f"Schiffe_versenken_{variant}"
        project_prefix = f"{outer}/{repo_root.name}"
        documents_prefix = f"{outer}/Dokumente"
        profile_dir = repo_root / "varianten" / variant
        selected_files = (
            (profile_dir / "start.py", "start.py"),
            (profile_dir / "START.md", "START_HIER.md"),
        )
        for source, _ in selected_files:
            if not source.is_file() or source.is_symlink():
                raise FileNotFoundError(source)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest = {}
    checksum_created = False
    with output.open("xb") as stream:
        try:
            with checksum_path.open("x", encoding="utf-8") as checksum_stream:
                checksum_created = True
                with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                    roots = [(repo_root, project_prefix)]
                    originals = repo_root.parent / "Dokumente"
                    if originals.is_dir():
                        roots.append((originals, documents_prefix))
                    for root, prefix in roots:
                        for path, relative in _files(root):
                            if path.resolve() in (output.resolve(), checksum_path.resolve()):
                                continue
                            if variant is not None and root == repo_root and relative.as_posix() in (
                                    "start.py", "START_HIER.md", "PROFIL.txt"):
                                continue
                            member = f"{prefix}/{relative.as_posix()}"
                            data = path.read_bytes()
                            _write_member(archive, manifest, member, data)
                    if variant is not None:
                        for source, destination in selected_files:
                            member = f"{project_prefix}/{destination}"
                            data = source.read_bytes()
                            _write_member(archive, manifest, member, data)
                        member = f"{project_prefix}/PROFIL.txt"
                        data = (variant + "\n").encode("utf-8")
                        _write_member(archive, manifest, member, data)
                    status = _submission_status()
                    member = f"{project_prefix}/ABGABESTATUS.md"
                    _write_member(archive, manifest, member, status)
                    archive.writestr("SHA256SUMS.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
                stream.flush()
                with output.open("rb") as archive_stream:
                    digest = hashlib.file_digest(archive_stream, "sha256").hexdigest()
                checksum_stream.write(f"{digest}  {output.name}\n")
        except BaseException:
            # Only remove the newly-created incomplete archive, never old evidence.
            stream.close()
            output.unlink(missing_ok=True)
            if checksum_created:
                checksum_path.unlink(missing_ok=True)
            raise
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Neues ZIP; Standard zeitgestempelt unter dist/")
    parser.add_argument("--variant", choices=VARIANTS,
                        help="Profilpaket mit eigenem Einstieg und START_HIER.md")
    args = parser.parse_args()
    default = ROOT / "dist" / ("Schiffe_versenken_" + (args.variant + "_" if args.variant else "")
                               + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ") + ".zip")
    try:
        path = build_submission(ROOT, args.output or default, variant=args.variant)
    except OSError as exc:
        parser.exit(1, f"Abgabepaket konnte nicht erstellt werden: {exc}\n")
    print(path)
    print(path.with_name(path.name + ".sha256"))


if __name__ == "__main__":
    main()
