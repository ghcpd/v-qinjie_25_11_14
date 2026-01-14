#!/bin/bash
# SECURITY VALIDATION SUITE - Post-Mitigation (Secure Version)
# Verifies that vulnerabilities have been fixed

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_DIR="$SCRIPT_DIR"
APP_DIR="$SCRIPT_DIR/app"
RESULTS_DIR="$SCRIPT_DIR/results"

echo "=========================================="
echo "SECURITY VALIDATION SUITE - SECURE VERSION"
echo "=========================================="

# Create results directory
mkdir -p "$RESULTS_DIR"

# Check Python version
echo "[*] Checking Python installation..."
python_version=$(python --version 2>&1)
echo "    Python: $python_version"

# Install dependencies
echo "[*] Installing dependencies..."
pip install -q -r "$SCRIPT_DIR/requirements.txt"

# Create .env if it doesn't exist
if [ ! -f "$APP_DIR/.env" ]; then
    echo "[*] Creating .env file..."
    cp "$SCRIPT_DIR/.env.example" "$APP_DIR/.env"
    echo "    .env created from .env.example"
fi

# Start the secure Flask app in the background
echo "[*] Starting secure application on port 5001..."
cd "$APP_DIR"
export FLASK_DEBUG=False
export ENVIRONMENT=production
python app.py > "$RESULTS_DIR/app.log" 2>&1 &
APP_PID=$!
echo "    App PID: $APP_PID"

# Wait for app to start
sleep 3

# Check if app is running
if ! kill -0 $APP_PID 2>/dev/null; then
    echo "[!] Failed to start application"
    cat "$RESULTS_DIR/app.log"
    exit 1
fi

echo "[*] Application started successfully"

# Run validation tests
echo ""
echo "=========================================="
echo "RUNNING SECURITY VALIDATIONS"
echo "=========================================="
cd "$TEST_DIR"

python validation_tests.py
VALIDATION_RESULT=$?

# Get timestamp for report
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_FILE="$RESULTS_DIR/validation_report_$TIMESTAMP.json"

# Check if validation_results.json was created
if [ -f "validation_results.json" ]; then
    cp validation_results.json "$REPORT_FILE"
    echo ""
    echo "[+] Report saved to: $REPORT_FILE"
    echo ""
    echo "=========================================="
    echo "VALIDATION SUMMARY"
    echo "=========================================="
    python -c "
import json
with open('$REPORT_FILE') as f:
    data = json.load(f)
    print(f\"Target: {data['target']}\")
    print(f\"Validations run: {len(data['validations'])}\")
    print(f\"Passed: {data['summary']['passed']}\")
    print(f\"Failed: {data['summary']['failed']}\")
    print()
    for test in data['validations']:
        status = '✓ PASS' if test.get('passed') else '✗ FAIL'
        print(f\"{status}: {test['name']}\")
        for detail in test.get('details', []):
            print(f\"  {detail}\")
"
else
    echo "[!] No validation results found"
    REPORT_FILE="$RESULTS_DIR/no_results.txt"
fi

# Cleanup
echo ""
echo "[*] Cleaning up..."
kill $APP_PID 2>/dev/null || true
wait $APP_PID 2>/dev/null || true

echo "[+] Test suite completed"
echo "[+] All results in: $RESULTS_DIR/"
exit $VALIDATION_RESULT
