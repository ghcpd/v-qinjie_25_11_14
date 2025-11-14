import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List


@dataclass
class VulnerableDashboard:
    """Simulates an intentionally vulnerable dashboard UI workflow."""

    leaked_api_key: str = "sk_live_PREM-123456789"
    debug_config: Dict[str, str] = field(
        default_factory=lambda: {
            "db_host": "debug-db.internal",
            "db_password": "postgres-dev-password",
            "feature_flags": ["unsafe_preview", "log_secrets"],
            "build": "pre-mitigation",
        }
    )
    log_file: Path = Path(__file__).parent / "logs" / "client.log"

    def __post_init__(self) -> None:
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def render_login(self) -> str:
        return (
            "<form action='/login' method='post'>"
            "<input name=\"username\"/><input name=\"password\" type=\"password\"/>"
            "</form>"
        )

    def render_dashboard(self, username: str, debug: bool = False) -> str:
        debug_blob = json.dumps(self.debug_config, indent=2)
        stack_trace = (
            "Traceback (simulated line 42): api_key lookup failed"
            if debug
            else "Hidden"
        )
        html = f"""
        <h1>Welcome {username}</h1>
        <section id='api-key'>{self.leaked_api_key}</section>
        <pre id='debug'>{debug_blob}</pre>
        <p id='stack'>{stack_trace}</p>
        <script>
            const USER_API_KEY = "{self.leaked_api_key}";
            sessionStorage.setItem('apiKey', USER_API_KEY);
            console.log('Debug dump', {debug_blob});
        </script>
        """
        return html

    def unsafe_preview(self, content: str) -> str:
        # No sanitisation applied; payload is reflected directly.
        return f"<div class='preview-card'>{content}</div>"

    def record_client_log(self, payload: Dict[str, str]) -> Dict[str, str]:
        entry = {
            "message": payload.get("message", ""),
            "apiKey": payload.get("apiKey"),
            "received_at": datetime.utcnow().isoformat(),
        }
        with self.log_file.open("a", encoding="utf-8") as handler:
            handler.write(json.dumps(entry) + "\n")
        return entry

    def dump_logs(self) -> str:
        if not self.log_file.exists():
            return ""
        return self.log_file.read_text(encoding="utf-8")

    def support_trace(self) -> Dict[str, object]:
        return {
            "config": self.debug_config,
            "api_key": self.leaked_api_key,
            "stack": "Traceback: failing function leaked_api_key",
        }

    def static_assets(self) -> Dict[str, str]:
        leaky_js = (Path(__file__).parent / "static" / "leaky.js").read_text(encoding="utf-8")
        return {"leaky_js": leaky_js}


__all__: List[str] = ["VulnerableDashboard"]
