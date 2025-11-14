import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List


@dataclass
class HardenedDashboard:
    """Secure version of the dashboard with mitigations in place."""

    real_api_key: str = "sk_live_POSTM-987654321"
    masked_api_key: str = "sk_live_POSTM-***4321"
    log_file: Path = Path(__file__).parent / "logs" / "sanitised.log"
    allowed_log_fields: List[str] = field(default_factory=lambda: ["message", "level"])

    def __post_init__(self) -> None:
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def render_login(self) -> str:
        return (
            "<form action='/login' method='post'>"
            "<input name=\"username\"/><input name=\"password\" type=\"password\"/>"
            "</form>"
        )

    def render_dashboard(self, username: str) -> str:
        issued_at = datetime.utcnow().isoformat()
        html = f"""
        <h1>Welcome {username}</h1>
        <section id='api-key'>{self.masked_api_key}</section>
        <small data-issued='{issued_at}'>Full token never sent to the browser.</small>
        <script>
            const MASKED_KEY = "{self.masked_api_key}";
            localStorage.setItem('dashboardMask', MASKED_KEY);
        </script>
        """
        return html

    def safe_preview(self, content: str) -> str:
        escaped = content.replace("<", "&lt;").replace(">", "&gt;")
        return f"<div class='preview-card'>{escaped}</div>"

    def record_client_log(self, payload: Dict[str, str]) -> Dict[str, str]:
        filtered = {k: payload[k] for k in payload if k in self.allowed_log_fields}
        filtered["received_at"] = datetime.utcnow().isoformat()
        self.log_file.write_text(json.dumps(filtered) + "\n", encoding="utf-8")
        return filtered

    def dump_logs(self) -> str:
        # Hardened build never exposes raw logs.
        return "forbidden"

    def support_trace(self) -> Dict[str, str]:
        return {
            "message": "Diagnostics hidden. Contact support with request id.",
            "request_id": datetime.utcnow().strftime("%Y%m%d%H%M%S"),
        }

    def static_assets(self) -> Dict[str, str]:
        secure_js = (Path(__file__).parent / "static" / "secure.js").read_text(encoding="utf-8")
        return {"secure_js": secure_js}


__all__ = ["HardenedDashboard"]
