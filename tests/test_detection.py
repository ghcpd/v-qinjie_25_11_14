import unittest

from detection.exploit import extract_api_key, exploit_eval_injection
from detection.scanner import scan_dashboard
from secure_dashboard.dashboard import SecureDashboard
from vulnerable_dashboard.dashboard import VulnerableDashboard


class DetectionTests(unittest.TestCase):
    def test_vulnerable_dashboard_reports_findings(self):
        html = VulnerableDashboard().render_dashboard()
        findings = scan_dashboard(html)
        ids = {finding["id"] for finding in findings}
        self.assertIn("plaintext-api-key", ids)
        self.assertIn("embedded-secrets", ids)
        self.assertIn("unsafe-execution", ids)
        self.assertIn("debug-leak", ids)
        self.assertIn("sensitive-logging", ids)

        exploit = extract_api_key(html)
        self.assertEqual(exploit["status"], "success")
        self.assertIn("VULN-SECRET-KEY", exploit["result"])

        eval_exploit = exploit_eval_injection(html)
        self.assertEqual(eval_exploit["status"], "success")

    def test_secure_dashboard_hides_secrets(self):
        html = SecureDashboard().render_dashboard()
        findings = scan_dashboard(html)
        self.assertEqual(findings, [])

        exploit = extract_api_key(html)
        self.assertNotEqual(exploit["status"], "success")

        eval_exploit = exploit_eval_injection(html)
        self.assertEqual(eval_exploit["status"], "failure")

    def test_scan_report_structure(self):
        html = VulnerableDashboard().render_dashboard()
        findings = scan_dashboard(html)
        for finding in findings:
            self.assertIn("id", finding)
            self.assertIn("description", finding)
            self.assertIn("detail", finding)

    def test_logging_snippet_presence(self):
        html = VulnerableDashboard().render_dashboard()
        self.assertGreaterEqual(html.count("console.log"), 1)


if __name__ == "__main__":
    unittest.main()
