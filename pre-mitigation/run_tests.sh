#!/bin/bash
# VULNERABILITY TEST SUITE - Pre-Mitigation (Vulnerable Version)
# Demonstrates how to run exploit tests and generate JSON reports

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_DIR="$SCRIPT_DIR"
APP_DIR="$SCRIPT_DIR/app"
RESULTS_DIR="$SCRIPT_DIR/results"

echo "=========================================="
echo "VULNERABILITY TEST SUITE - VULNERABLE VERSION"
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

# Start the vulnerable Flask app in the background
echo "[*] Starting vulnerable application on port 5000..."
cd "$APP_DIR"
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

# Run exploit tests
echo ""
echo "=========================================="
echo "RUNNING EXPLOIT TESTS"
echo "=========================================="
cd "$TEST_DIR"

python exploit_tests.py
EXPLOIT_RESULT=$?

# Get timestamp for report
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_FILE="$RESULTS_DIR/vulnerability_report_$TIMESTAMP.json"

# Check if exploit_results.json was created
if [ -f "exploit_results.json" ]; then
    cp exploit_results.json "$REPORT_FILE"
    echo ""
    echo "[+] Report saved to: $REPORT_FILE"
    echo ""
    echo "=========================================="
    echo "SUMMARY"
    echo "=========================================="
    python -c "
import json
with open('$REPORT_FILE') as f:
    data = json.load(f)
    print(f\"Target: {data['target']}\")
    print(f\"Exploits run: {len(data['exploits'])}\")
    successful = sum(1 for e in data['exploits'] if e.get('success'))
    print(f\"Successful exploits: {successful}\")
    print()
    for exploit in data['exploits']:
        status = '✓ SUCCESS' if exploit.get('success') else '✗ FAILED'
        print(f\"{status}: {exploit['name']}\")
        if exploit.get('evidence'):
            print(f\"  Evidence: {exploit['evidence']}\")
"
else
    echo "[!] No exploit results found"
    REPORT_FILE="$RESULTS_DIR/no_results.txt"
fi

# Cleanup
echo ""
echo "[*] Cleaning up..."
kill $APP_PID 2>/dev/null || true
wait $APP_PID 2>/dev/null || true

echo "[+] Test suite completed"
echo "[+] All results in: $RESULTS_DIR/"
exit $EXPLOIT_RESULT
