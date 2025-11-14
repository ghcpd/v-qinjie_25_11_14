#!/bin/bash
set -euo pipefail
python3 -m unittest discover tests -v
python3 - <<'PY'
from security_suite import SecurityTestSuite
path = SecurityTestSuite().write_report()
print(f"Patch verification report stored at {path}")
PY
