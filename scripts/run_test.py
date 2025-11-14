"""
Runs vulnerability detection, exploit validation, and patch verification, and
exports a structured JSON report covering exposed secrets, exploit proofs, and regression outcomes.
"""

import io
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import unittest

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from detection.exploit import exploit_eval_injection, extract_api_key, list_detected_loggers
from detection.scanner import scan_dashboard
from secure_dashboard.dashboard import SecureDashboard
from vulnerable_dashboard.dashboard import VulnerableDashboard


def collect_findings(html: str) -> List[Dict[str, Any]]:
    return scan_dashboard(html)


def collect_exploit_logs(html: str) -> List[Dict[str, Any]]:
    return [
        extract_api_key(html),
        exploit_eval_injection(html),
        {"target": "Client loggers", "method": "Log inspection", "result": list_detected_loggers(html), "status": "info"},
    ]


def run_regression_tests() -> Dict[str, Any]:
    loader = unittest.TestLoader()
    module = __import__("tests.test_detection", fromlist=["DetectionTests"])
    suite = loader.loadTestsFromModule(module)
    stream = io.StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=0)
    result = runner.run(suite)
    status = "pass" if result.wasSuccessful() else "fail"
    return {
        "name": "tests.test_detection",
        "status": status,
        "details": {
            "testsRun": result.testsRun,
            "failures": len(result.failures),
            "errors": len(result.errors),
        },
        "description": "Validates detection/exploit helpers for both dashboard versions.",
    }


def build_report() -> Dict[str, Any]:
    vulnerable_html = VulnerableDashboard().render_dashboard()
    secure_html = SecureDashboard().render_dashboard()

    vulnerable_block = {
        "vulnerabilities": collect_findings(vulnerable_html),
        "exploit_logs": collect_exploit_logs(vulnerable_html),
        "summary": "Sensitive secrets appear in HTML/JS, and unsafe eval paths are present.",
    }

    secure_block = {
        "vulnerabilities": collect_findings(secure_html),
        "exploit_logs": collect_exploit_logs(secure_html),
        "summary": "Secrets are masked, scripts avoid eval, and debugger data is hidden.",
    }

    report = {
        "vulnerable_dashboard": vulnerable_block,
        "secure_dashboard": secure_block,
        "patch_verification": {
            "description": "Mask API keys, remove embedded secrets, and sanitize preview execution.",
            "status": "verified" if not secure_block["vulnerabilities"] else "failed",
        },
        "regression_tests": run_regression_tests(),
    }
    return report


def main():
    report = build_report()
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    out_path = reports_dir / "security_test_report.json"
    with out_path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
