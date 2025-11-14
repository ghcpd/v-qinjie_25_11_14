import json
import unittest

from security_suite import REPORT_PATH, SecurityTestSuite


class VulnerableDashboardSuiteTests(unittest.TestCase):
    def test_security_suite_detects_every_issue(self) -> None:
        suite = SecurityTestSuite()
        report = suite.run_all()
        self.assertEqual(report["exploit_success"], len(report["vulnerabilities"]))
        self.assertGreaterEqual(len(report["vulnerabilities"]), 5)

        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
        self.assertTrue(REPORT_PATH.exists())


if __name__ == "__main__":
    unittest.main()
