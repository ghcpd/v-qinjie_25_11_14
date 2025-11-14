import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from app import VulnerableDashboard

REPORT_PATH = Path(__file__).parent / "reports" / "latest_vulnerability_report.json"


class SecurityTestSuite:
    """Runs exploit-style assertions against the vulnerable dashboard."""

    def __init__(self) -> None:
        self.dashboard = VulnerableDashboard()
        self.metadata: Dict[str, str] = {
            "project": "pre_mitigation_dashboard",
            "generated_at": datetime.utcnow().isoformat(),
        }

    def _record(self, name: str, description: str, success: bool, evidence: str) -> Dict[str, str]:
        severity = "high" if success else "info"
        status = "exploited" if success else "not_reproduced"
        return {
            "name": name,
            "description": description,
            "severity": severity,
            "status": status,
            "evidence": evidence,
        }

    def _check_api_key_exposure(self) -> Dict[str, str]:
        html = self.dashboard.render_dashboard("attacker", debug=True)
        leaked = self.dashboard.leaked_api_key in html
        snippet = html.split("\n")[0:4]
        return self._record(
            name="UI API key leak",
            description="Dashboard renders secret API key directly in DOM and scripts.",
            success=leaked,
            evidence="\n".join(snippet),
        )

    def _check_static_secret(self) -> Dict[str, str]:
        assets = self.dashboard.static_assets()
        leaky_js = assets["leaky_js"]
        success = "HARDCODED_ADMIN_TOKEN" in leaky_js
        return self._record(
            name="Hardcoded admin token in JS",
            description="Static asset contains admin token and eval helper.",
            success=success,
            evidence=leaky_js.strip().splitlines()[0],
        )

    def _check_preview_rce(self) -> Dict[str, str]:
        payload = "<img src=x onerror=alert('pwned')>"
        html = self.dashboard.unsafe_preview(payload)
        success = payload in html
        return self._record(
            name="Unsafe file preview",
            description="Preview response reflects attacker HTML/JS without escaping.",
            success=success,
            evidence=html,
        )

    def _check_client_log_leak(self) -> Dict[str, str]:
        secret = "session=steal-me"
        self.dashboard.record_client_log({"message": "exfil", "apiKey": secret})
        log_dump = self.dashboard.dump_logs()
        success = secret in log_dump
        return self._record(
            name="Client log disclosure",
            description="Attacker can retrieve prior client logs with embedded secrets.",
            success=success,
            evidence=log_dump,
        )

    def _check_debug_endpoint(self) -> Dict[str, str]:
        trace = self.dashboard.support_trace()
        success = trace.get("api_key") == self.dashboard.leaked_api_key
        return self._record(
            name="Debug trace reveals secrets",
            description="Support diagnostics return API keys and DB passwords.",
            success=success,
            evidence=json.dumps(trace),
        )

    def run_all(self) -> Dict[str, object]:
        findings = [
            self._check_api_key_exposure(),
            self._check_static_secret(),
            self._check_preview_rce(),
            self._check_client_log_leak(),
            self._check_debug_endpoint(),
        ]
        report = {
            **self.metadata,
            "vulnerabilities": findings,
            "exploit_success": sum(1 for item in findings if item["status"] == "exploited"),
        }
        return report

    def write_report(self, path: Path = REPORT_PATH) -> Path:
        report = self.run_all()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        return path


__all__ = ["SecurityTestSuite", "REPORT_PATH"]
