Patched Demo App

This app demonstrates mitigations for the vulnerabilities in the vulnerable app:
- No API keys embedded in client-side JS
- Masked API key displayed in UI; full key isn't available without extra server-side auth checks
- Uploaded HTML content is sanitized to remove script tags and event handlers using Bleach
- The preview UI uses text rendering that prevents script execution
- No client-side logging of sensitive data

Usage:
- Start the app: python app.py
- Access http://127.0.0.1:5001/login
- Login and use the dashboard to upload a malicious HTML payload which should be sanitized and not cause exfiltration
- Tests will verify that exploit no longer works and produce patched/exploit_result.json
