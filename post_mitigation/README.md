Post-Mitigation Secure UI Project

This project contains the patched web dashboard with mitigations for the previously simulated vulnerabilities:
- No API key embedded in frontend JS.
- API key is masked in UI and ephemeral tokens are used for API calls.
- File preview sanitizes HTML via bleach.
- Debug route requires X-ADMIN header.
- Secrets are not logged.

How to run:
- Install requirements: python -m pip install -r requirements.txt
- Install Playwright browsers: python -m playwright install
- Run tests: ./run_test.sh (or run_test.ps1 on Windows)

The tests will start the Flask app and run checks to validate mitigations.
