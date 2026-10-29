"""Verify a delivered ZIP independently, including a fresh venv and actual runs.

Writes outside the archive so the archive never claims its own future test result.
"""
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import urllib.parse
import zipfile
import argparse


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--extract', type=Path, required=True)
    parser.add_argument('--expected-tests', type=int, default=101)
    args = parser.parse_args()
    archive_path = args.archive.resolve()
    output = args.output.resolve()
    extract = args.extract.resolve()
    output.mkdir(parents=True, exist_ok=False)
    extract.mkdir(parents=True, exist_ok=False)
    report = dict(started_at=datetime.now().astimezone().isoformat(), archive=str(archive_path), performer='automatisierter Codex-Testlauf (Rolle 3)', result='FAIL')
    try:
        digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
        report['archive_sha256'] = digest
        checksum = archive_path.with_name(archive_path.name + '.sha256').read_text().strip()
        assert checksum == f'{digest}  {archive_path.name}', 'Archive sidecar SHA mismatch'
        with zipfile.ZipFile(archive_path) as archive:
            assert archive.testzip() is None
            names = archive.namelist()
            assert len(names) == len(set(names)), 'Duplicate archive members'
            for name in names:
                path = Path(name)
                assert not path.is_absolute() and '..' not in path.parts, f'Unsafe archive member {name}'
                assert not any(p in ('.git', '.venv', '__pycache__', '.pytest_cache', '.aws', '.ssh') or p.startswith('.env') for p in path.parts), f'Excluded/private member {name}'
                assert not (path.parts[1:2] == ('logs',)), f'Runtime logs included {name}'
            manifest = json.loads(archive.read('SHA256SUMS.json'))
            members = {name for name in names if not name.endswith('/') and name != 'SHA256SUMS.json'}
            assert set(manifest) == members
            for name, wanted in manifest.items():
                assert hashlib.sha256(archive.read(name)).hexdigest() == wanted, name
            roots = [name[:-len('/src/server.py')] for name in members if name.endswith('/src/server.py')]
            assert len(roots) == 1, roots
            prefix = roots[0]
            required = ['README.md', 'REGELN.md', 'PROTOKOLL.md', 'src/board.py', 'src/netz.py', 'src/server.py', 'src/client_gui.py', 'src/play.py', 'src/client.py', 'src/event_log.py', 'tools/run_tests.py', 'tools/build_submission.py', 'bilder/schiff.png', 'bilder/schiff_imagegen_original.png', 'tests/meilenstein_06/test_image.py', 'docs/status/04_rubric_requirements.md', 'docs/report/meine_reflexion.md', 'ABGABESTATUS.md']
            for name in required: assert f'{prefix}/{name}' in members, name
            assert any(name.startswith('Dokumente/') and name.endswith('.docx') for name in members)
            report['manifest_members_verified'] = len(manifest)
            archive.extractall(extract)
        repo = extract / prefix
        broken = []
        original_links = []
        for markdown in repo.rglob('*.md'):
            for match in re.finditer(r'\]\((?:<([^>]+)>|([^\)]+))\)', markdown.read_text(errors='strict')):
                target = next(value for value in match.groups() if value is not None)
                if 'Dokumente/' not in target or '://' in target:
                    continue
                path = markdown.parent / urllib.parse.unquote(target.split('#', 1)[0])
                original_links.append(dict(source=str(markdown.relative_to(repo)), target=target))
                if not path.exists(): broken.append(original_links[-1])
        assert original_links, 'No source-document links found'
        assert not broken, broken
        report['original_document_links_verified'] = len(original_links)
        environment = repo / '.venv'
        subprocess.run([sys.executable, '-m', 'venv', str(environment)], check=True, capture_output=True, text=True, timeout=60)
        python = environment / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python3')
        with (output / 'tests.txt').open('x') as raw:
            result = subprocess.run([str(python), str(repo / 'tools/run_tests.py'), '--require-gui', '--report-json', str(output / 'tests.json')], cwd=extract, stdout=raw, stderr=subprocess.STDOUT, timeout=120)
        assert result.returncode == 0, f'Extracted suite exit {result.returncode}'
        tests = json.loads((output / 'tests.json').read_text())
        assert tests['success']
        assert tests['summary'] == dict(tests_run=args.expected_tests, passed=args.expected_tests, failures=0, errors=0, skipped=0), tests['summary']
        assert len({row['id'] for row in tests['tests']}) == args.expected_tests
        assert tests['gui']['executed'] == tests['gui']['discovered'] == 16 and not tests['gui']['issues']
        report['tests'] = tests['summary']
        report['gui'] = tests['gui']
        report['environment'] = tests['environment']
        script = repo / 'docs/evidence/final_assessment_tests/verify_local.py'
        with (output / 'runtime.txt').open('x') as raw:
            result = subprocess.run([str(python), str(script), '--output', str(output / 'runtime')], cwd=extract, stdout=raw, stderr=subprocess.STDOUT, timeout=60)
        assert result.returncode == 0, f'Extracted runtime smoke exit {result.returncode}'
        runtime = json.loads((output / 'runtime/result.json').read_text())
        assert runtime['result'] == 'PASS' and runtime['attacks'] == 7 and runtime['console_shots'] == 33
        report['runtime'] = runtime
        report['result'] = 'PASS'
    except Exception as exc:
        report['error'] = f'{type(exc).__name__}: {exc}'
        raise
    finally:
        report['finished_at'] = datetime.now().astimezone().isoformat()
        (output / 'result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == '__main__': main()
