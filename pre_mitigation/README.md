Pre-Mitigation Vulnerable UI Project

This project simulates a vulnerable web dashboard that exposes API keys, stores secrets client-side, allows unsafe file previews that enable XSS, logs secrets, and exposes debug information.

How to run:
- Install requirements: python -m pip install -r requirements.txt
- Install Playwright browsers: python -m playwright install
- Run tests: ./run_test.sh (or run_test.ps1 on Windows)

The tests will start the Flask app and run checks for vulnerabilities. A simple file preview XSS and API key exfiltration exploit is shown in tests.
