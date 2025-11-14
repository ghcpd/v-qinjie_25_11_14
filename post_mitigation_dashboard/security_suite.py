import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from app import HardenedDashboard

REPORT_PATH = Path(__file__).parent / "reports" / "latest_patch_report.json"


class SecurityTestSuite:
    """Ensures security controls remain effective after mitigations."""

    def __init__(self) -> None:
        self.dashboard = HardenedDashboard()
        self.metadata: Dict[str, str] = {
            "project": "post_mitigation_dashboard",
            "generated_at": datetime.utcnow().isoformat(),
        }

    def _record(self, name: str, description: str, safe: bool, evidence: str) -> Dict[str, str]:
        return {
            "name": name,
            "description": description,
            "status": "verified" if safe else "regression",
            "evidence": evidence,
            "severity": "info" if safe else "high",
        }

    def _assert_no_plain_api_key(self) -> Dict[str, str]:
        html = self.dashboard.render_dashboard("qa")
        safe = self.dashboard.real_api_key not in html and "***" in html
        return self._record(
            name="API key redaction",
            description="Dashboard masks API keys before rendering.",
            safe=safe,
            evidence="masked" if safe else html,
        )

    def _assert_static_js_clean(self) -> Dict[str, str]:
        assets = self.dashboard.static_assets()
        code = assets["secure_js"]
        safe = "eval(" not in code and "sk_" not in code
        return self._record(
            name="Static assets clean",
            description="Secure JavaScript helper avoids eval and embedded secrets.",
            safe=safe,
            evidence=code.splitlines()[0],
        )

    def _assert_preview_sanitized(self) -> Dict[str, str]:
        payload = "<script>alert('owned')</script>"
        html = self.dashboard.safe_preview(payload)
        safe = payload not in html and "&lt;script&gt;" in html
        return self._record(
            name="Preview escaping",
            description="Preview output escapes user input to prevent script execution.",
            safe=safe,
            evidence=html,
        )

    def _assert_log_dump_blocked(self) -> Dict[str, str]:
        secret_payload = {"message": "ui-loaded", "apiKey": "super-secret"}
        self.dashboard.record_client_log(secret_payload)
        dump = self.dashboard.dump_logs()
        safe = "secret" not in dump and dump == "forbidden"
        return self._record(
            name="Client log access control",
            description="Direct log dump is disabled.",
            safe=safe,
            evidence=dump,
        )

    def _assert_trace_minimal(self) -> Dict[str, str]:
        trace = self.dashboard.support_trace()
        safe = "api_key" not in trace and "config" not in trace
        return self._record(
            name="Trace scrubbing",
            description="Support traces omit secrets and config details.",
            safe=safe,
            evidence=json.dumps(trace),
        )

    def run_all(self) -> Dict[str, object]:
        checks = [
            self._assert_no_plain_api_key(),
            self._assert_static_js_clean(),
            self._assert_preview_sanitized(),
            self._assert_log_dump_blocked(),
            self._assert_trace_minimal(),
        ]
        report = {
            **self.metadata,
            "regression_checks": checks,
            "verified_controls": sum(1 for c in checks if c["status"] == "verified"),
        }
        return report

    def write_report(self, path: Path = REPORT_PATH) -> Path:
        report = self.run_all()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        return path


__all__ = ["SecurityTestSuite", "REPORT_PATH"]
