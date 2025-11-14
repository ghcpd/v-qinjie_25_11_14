# UI Security Vulnerability Demo (Vulnerable vs Patched)

This workspace contains two demo Flask apps to illustrate UI security issues and how to fix them:

- vulnerable/: Pre-mitigation app demonstrating API key leakage, secrets in JS, unsafe preview that allows XSS and exfiltration
- patched/: Post-mitigation app with masked keys, sanitized preview, and removal of client-side secret leaks

How to run (UNIX):
- Run run_all.py to install dependencies, run both apps and tests, and generate a consolidated JSON report:
  python run_all.py

Security report is stored in security_report.json

The apps are intentionally insecure for learning; do not deploy them in production.
