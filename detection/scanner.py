import re
from typing import List, Dict


def detect_plaintext_api_key(html: str) -> Dict[str, str]:
    match = re.search(r"<strong>Live API Key:</strong>\s*<span>([^<]+)</span>", html, re.IGNORECASE)
    if match:
        displayed = match.group(1).strip()
        if displayed and "*" not in displayed:
            return {
                "id": "plaintext-api-key",
                "description": "API key is rendered in plaintext on the page.",
                "detail": displayed,
            }
    return {}


def detect_embedded_secrets(html: str) -> Dict[str, str]:
    secrets = []
    if "const API_KEY" in html:
        secrets.append("API_KEY defined in client-side script")
    if "const ADMIN_TOKEN" in html:
        secrets.append("ADMIN_TOKEN defined in client-side script")
    if secrets:
        return {
            "id": "embedded-secrets",
            "description": "Secrets are hard-coded in JavaScript and can be read by anyone inspecting the page.",
            "detail": "; ".join(secrets),
        }
    return {}


def detect_unsafe_execution(html: str) -> Dict[str, str]:
    if "eval(" in html:
        return {
            "id": "unsafe-execution",
            "description": "Client-side eval() is called on user-supplied payloads.",
            "detail": "eval() usage found which may execute attacker-controlled input.",
        }
    return {}


def detect_debug_leak(html: str) -> Dict[str, str]:
    if "Traceback" in html or "debug info" in html.lower():
        return {
            "id": "debug-leak",
            "description": "Internal debug information is exposed directly in the UI.",
            "detail": "Traceback or debug info text found on the page.",
        }
    return {}


def detect_sensitive_logging(html: str) -> Dict[str, str]:
    if "console.log" in html:
        return {
            "id": "sensitive-logging",
            "description": "Console logs emit sensitive secrets or debugging information.",
            "detail": "console.log() calls exist in the inline scripts.",
        }
    return {}


def scan_dashboard(html: str) -> List[Dict[str, str]]:
    findings = []
    for detector in (
        detect_plaintext_api_key,
        detect_embedded_secrets,
        detect_unsafe_execution,
        detect_debug_leak,
        detect_sensitive_logging,
    ):
        result = detector(html)
        if result:
            findings.append(result)
    return findings
