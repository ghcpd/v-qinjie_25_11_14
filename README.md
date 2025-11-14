# UI Security Simulation Suite

This repository hosts a pair of Python-based simulations that demonstrate how UI security flaws manifest and how they can be fixed. The two directories represent:

- `vulnerable_dashboard`: a pre-mitigation version of a dashboard that leaks secrets through its UI layer.
- `secure_dashboard`: a mitigated version that fixes the leaks and unsafe behaviors.

Each project exposes a simple API key dashboard, a file preview component, and client-side scripts that can either expose or protect sensitive data. The detection logic, exploit validations, and regression checks live under `detection/`, `tests/`, and `scripts/`.

## Running the suite

1. Create the environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Run the automated analysis (detection + verification):
   ```bash
   ./run_test.sh
   ```
   This generates `reports/security_test_report.json` which contains vulnerability reports, exploit logs, and patch verification results in JSON format.

3. For a guided test workflow, inspect `templates/security_report_template.json`.

## Structure

- `detection/` – Shared scanners and exploit extractors.
- `vulnerable_dashboard/` – Unsafe UI implementation.
- `secure_dashboard/` – Hardened UI implementation.
- `scripts/run_test.py` – Runs the detection/exploit/verification pipeline and writes JSON output.
- `tests/` – `unittest`-based suites that assert detection and mitigation behavior.

## Environment

- `requirements.txt` – Python dependencies.
- `Dockerfile` – Defines a reproducible container for running the suite.
- `run_test.sh` – One-click script that executes `scripts/run_test.py`.
