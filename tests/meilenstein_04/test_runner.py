"""Observable runner outcomes using small real unittest suites, never recursive discovery."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from tools import run_tests


class RunnerTests(unittest.TestCase):
    def run_controlled(self, case, *, strict=False):
        self.assertTrue(callable(getattr(run_tests, 'run_suite', None)), 'Shared strict/report runner is missing')
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        report = Path(directory.name) / 'result.json'
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(case)
        with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
            code = run_tests.run_suite(suite, require_gui=strict, report_json=report, selection='controlled')
        return code, json.loads(report.read_text())

    def test_success_report_identifies_real_test_and_environment(self):
        class Passing(unittest.TestCase):
            def test_ok(self): self.assertEqual(2 + 3, 5)
        code, report = self.run_controlled(Passing)
        self.assertEqual(code, 0)
        self.assertTrue(report['success'])
        self.assertEqual(report['summary'], dict(tests_run=1, passed=1, failures=0, errors=0, skipped=0))
        self.assertEqual(report['selection'], 'controlled')
        self.assertTrue(report['environment']['python'])
        self.assertTrue(report['environment']['platform'])
        self.assertIn('tk', report['environment'])
        self.assertGreaterEqual(report['duration_seconds'], 0)
        self.assertTrue(report['started_at'])
        self.assertEqual(len(report['tests']), 1)
        self.assertTrue(report['tests'][0]['id'].endswith('Passing.test_ok'))
        self.assertEqual(report['tests'][0]['status'], 'passed')
        self.assertGreaterEqual(report['tests'][0]['duration_seconds'], 0)

    def test_assertion_failure_returns_failure_and_keeps_reason(self):
        class Failing(unittest.TestCase):
            def test_bad(self): self.fail('controlled failure evidence')
        code, report = self.run_controlled(Failing)
        self.assertNotEqual(code, 0)
        self.assertFalse(report['success'])
        self.assertEqual(report['summary']['failures'], 1)
        self.assertEqual(report['tests'][0]['status'], 'failed')
        self.assertIn('controlled failure evidence', report['tests'][0]['reason'])

    def test_normal_mode_reports_skip_but_strict_mode_rejects_it(self):
        class SkippedGui(unittest.TestCase):
            requires_gui = True
            @unittest.skip('display deliberately unavailable')
            def test_display(self): pass
        code, report = self.run_controlled(SkippedGui)
        self.assertEqual(code, 0)
        self.assertEqual(report['summary']['skipped'], 1)
        code, report = self.run_controlled(SkippedGui, strict=True)
        self.assertNotEqual(code, 0)
        self.assertFalse(report['success'])
        self.assertTrue(report['gui']['issues'])
        self.assertIn('display deliberately unavailable', report['tests'][0]['reason'])

    def test_strict_mode_accepts_executed_marked_test(self):
        class AvailableGui(unittest.TestCase):
            requires_gui = True
            def test_display(self): pass
        code, report = self.run_controlled(AvailableGui, strict=True)
        self.assertEqual(code, 0)
        self.assertTrue(report['success'])
        self.assertEqual(report['gui']['discovered'], 1)
        self.assertEqual(report['gui']['executed'], 1)
        self.assertEqual(report['gui']['issues'], [])

    def test_strict_mode_rejects_gui_subtest_skip(self):
        class PartialGui(unittest.TestCase):
            requires_gui = True
            def test_display(self):
                with self.subTest(screen='required'):
                    self.skipTest('required image check skipped')
        code, report = self.run_controlled(PartialGui, strict=True)
        self.assertNotEqual(code, 0)
        self.assertFalse(report['success'])
        self.assertEqual(report['summary']['tests_run'], 1)
        self.assertEqual(report['summary']['skipped'], 1)
        self.assertNotEqual(report['tests'][0]['status'], 'running', 'Completed test with skipped subtest needs an honest final outcome')
        self.assertTrue(report['gui']['issues'])

    def test_strict_mode_requires_passing_gui_not_expected_failure(self):
        class ExpectedBrokenGui(unittest.TestCase):
            requires_gui = True
            @unittest.expectedFailure
            def test_display(self): self.fail('known missing display behavior')
        code, report = self.run_controlled(ExpectedBrokenGui, strict=True)
        self.assertNotEqual(code, 0)
        self.assertFalse(report['success'])
        self.assertEqual(report['tests'][0]['status'], 'expected_failure')
        self.assertTrue(report['gui']['issues'])

    def test_strict_mode_rejects_suite_with_no_gui_tests(self):
        class ConsoleOnly(unittest.TestCase):
            def test_ok(self): pass
        code, report = self.run_controlled(ConsoleOnly, strict=True)
        self.assertNotEqual(code, 0)
        self.assertEqual(report['gui']['discovered'], 0)
        self.assertFalse(report['success'])

    def test_class_skip_does_not_invent_executed_test_records(self):
        class MissingDisplay(unittest.TestCase):
            requires_gui = True
            @classmethod
            def setUpClass(cls): raise unittest.SkipTest('class display probe failed')
            def test_one(self): pass
            def test_two(self): pass
        code, report = self.run_controlled(MissingDisplay, strict=True)
        self.assertNotEqual(code, 0)
        self.assertEqual(report['summary']['tests_run'], 0)
        self.assertEqual(report['tests'], [])
        self.assertEqual(report['gui']['discovered'], 2)
        self.assertEqual(report['gui']['executed'], 0)
        self.assertTrue(any('class display probe failed' in str(e) for e in report['events']))

    def test_subtest_and_class_error_are_failures_without_fake_test_totals(self):
        class BadSubtest(unittest.TestCase):
            def test_table(self):
                for value in (1, 2):
                    with self.subTest(value=value): self.assertEqual(value, 1)
        code, report = self.run_controlled(BadSubtest)
        self.assertNotEqual(code, 0)
        self.assertEqual(report['summary']['tests_run'], 1)
        self.assertEqual(report['summary']['passed'], 0)
        self.assertEqual(report['summary']['failures'], 1)
        self.assertEqual(len(report['tests']), 1)
        self.assertTrue(report['events'])
        class BrokenSetup(unittest.TestCase):
            @classmethod
            def setUpClass(cls): raise RuntimeError('setup exploded')
            def test_never(self): pass
        code, report = self.run_controlled(BrokenSetup)
        self.assertNotEqual(code, 0)
        self.assertEqual(report['summary']['tests_run'], 0)
        self.assertEqual(report['summary']['errors'], 1)
        self.assertEqual(report['tests'], [])
        self.assertIn('setup exploded', str(report['events']))

    def test_existing_report_is_refused_before_running_suite(self):
        self.assertTrue(callable(getattr(run_tests, 'run_suite', None)), 'Shared strict/report runner is missing')
        ran = []
        class Sentinel(unittest.TestCase):
            def test_no(self): ran.append(True)
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / 'old.json'
            report.write_bytes(b'original evidence\n')
            try:
                code = run_tests.run_suite(unittest.defaultTestLoader.loadTestsFromTestCase(Sentinel), report_json=report)
            except FileExistsError:
                code = 1
            self.assertNotEqual(code, 0)
            self.assertEqual(report.read_bytes(), b'original evidence\n')
            self.assertEqual(ran, [])
