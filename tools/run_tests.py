"""Standardbibliothek-Tests mit optional strenger GUI-Abnahme und JSON-Bericht."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]


def _cases(suite):
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            yield from _cases(test)
        else:
            yield test


class RecordedResult(unittest.TextTestResult):
    """Actual test executions and fixture/subtest events have separate records."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records = []
        self.events = []
        self._running = {}

    def startTest(self, test):
        super().startTest(test)
        row = {"id": test.id(), "status": "running", "duration_seconds": 0, "reason": ""}
        self.records.append(row)
        self._running[id(test)] = (row, time.perf_counter())

    def stopTest(self, test):
        row, start = self._running[id(test)]
        row["duration_seconds"] = time.perf_counter() - start
        super().stopTest(test)

    def _outcome(self, test, status, reason=""):
        active = self._running.get(id(test))
        if active is None:
            self.events.append({"kind": "fixture", "id": test.id(), "status": status, "reason": reason})
        else:
            active[0].update(status=status, reason=reason)

    def addSuccess(self, test):
        super().addSuccess(test)
        self._outcome(test, "passed")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._outcome(test, "failed", self._exc_info_to_string(err, test))

    def addError(self, test, err):
        super().addError(test, err)
        self._outcome(test, "error", self._exc_info_to_string(err, test))

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        if isinstance(test, unittest.case._SubTest):
            self.events.append({"kind": "subtest", "id": test.id(), "parent_id": test.test_case.id(),
                                "status": "skipped", "reason": reason})
            active = self._running.get(id(test.test_case))
            if active and active[0]["status"] in ("running", "passed", "partial_skip"):
                self._outcome(test.test_case, "partial_skip", reason)
            return
        self._outcome(test, "skipped", reason)

    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err)
        self._outcome(test, "expected_failure", self._exc_info_to_string(err, test))

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        self._outcome(test, "unexpected_success", "Expected failure unexpectedly succeeded")

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        status = "passed" if err is None else "failed" if issubclass(err[0], test.failureException) else "error"
        reason = "" if err is None else self._exc_info_to_string(err, subtest)
        self.events.append({"kind": "subtest", "id": subtest.id(), "parent_id": test.id(), "status": status, "reason": reason})
        if err is not None:
            self._outcome(test, status, reason)


def run_suite(suite, *, require_gui=False, report_json=None, selection=None):
    # Reserve output before executing anything. Never overwrite earlier evidence.
    report_stream = Path(report_json).open("x", encoding="utf-8") if report_json is not None else None
    try:
        gui_ids = {test.id() for test in _cases(suite) if getattr(test, "requires_gui", False)}
        started_at = datetime.now(timezone.utc).isoformat()
        start = time.perf_counter()
        result = unittest.TextTestRunner(verbosity=2, resultclass=RecordedResult).run(suite)
        duration = time.perf_counter() - start
        gui_rows = [r for r in result.records if r["id"] in gui_ids]
        executed = sum(r["status"] != "skipped" for r in gui_rows)
        subtest_skips = {e["parent_id"] for e in result.events
                         if e["kind"] == "subtest" and e["status"] == "skipped" and e["parent_id"] in gui_ids}
        skipped = len(gui_ids) - executed + len(subtest_skips)
        issues = []
        if require_gui:
            if not gui_ids:
                issues.append("Keine mit requires_gui markierten GUI-Tests gefunden.")
            if executed != len(gui_ids):
                issues.append("Nicht alle gefundenen GUI-Tests wurden ausgeführt; Skip/Setup-Fehler prüfen.")
            if subtest_skips:
                issues.append("Mindestens ein erforderlicher GUI-Subtest wurde übersprungen.")
            if any(r["status"] != "passed" for r in gui_rows):
                issues.append("Nicht alle erforderlichen GUI-Tests haben bestanden (auch expectedFailure genügt nicht).")
        success = result.wasSuccessful() and not issues
        try:
            import tkinter
            tk_version = str(tkinter.TkVersion)
        except ImportError:
            tk_version = None
        report = {
            "environment": {"python": sys.version, "platform": platform.platform(), "tk": tk_version},
            "selection": selection, "started_at": started_at, "duration_seconds": duration,
            "tests": result.records, "events": result.events,
            "summary": {"tests_run": result.testsRun,
                        "passed": sum(r["status"] == "passed" for r in result.records),
                        "failures": len(result.failures), "errors": len(result.errors), "skipped": len(result.skipped)},
            "gui": {"required": require_gui, "discovered": len(gui_ids), "executed": executed,
                    "skipped": skipped, "issues": issues},
            "success": success,
        }
        if report_stream is not None:
            json.dump(report, report_stream, ensure_ascii=False, indent=2)
            report_stream.write("\n")
        for issue in issues:
            print("GUI-Abnahme fehlgeschlagen:", issue, file=sys.stderr)
        return 0 if success else 1
    finally:
        if report_stream is not None:
            report_stream.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--milestone", choices=("00", "02", "03", "04", "06", "07", "08"))
    parser.add_argument("--require-gui", action="store_true", help="Alle gefundenen GUI-Tests müssen tatsächlich laufen")
    parser.add_argument("--report-json", type=Path, help="Neue JSON-Berichtsdatei (kein Überschreiben)")
    args = parser.parse_args()
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(ROOT / "src"))
    start = ROOT / "tests"
    if args.milestone:
        start /= f"meilenstein_{args.milestone}"
    suite = unittest.defaultTestLoader.discover(str(start), top_level_dir=str(ROOT))
    try:
        return run_suite(suite, require_gui=args.require_gui, report_json=args.report_json, selection=args.milestone or "all")
    except OSError as exc:
        parser.error(f"Bericht konnte nicht neu angelegt werden: {exc}")


if __name__ == "__main__":
    raise SystemExit(main())
