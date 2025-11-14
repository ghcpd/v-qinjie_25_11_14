import json
import unittest

from security_suite import REPORT_PATH, SecurityTestSuite


class HardenedDashboardSuiteTests(unittest.TestCase):
    def test_security_suite_verifies_all_controls(self) -> None:
        suite = SecurityTestSuite()
        report = suite.run_all()
        self.assertEqual(report["verified_controls"], len(report["regression_checks"]))

        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
        self.assertTrue(REPORT_PATH.exists())


if __name__ == "__main__":
    unittest.main()
