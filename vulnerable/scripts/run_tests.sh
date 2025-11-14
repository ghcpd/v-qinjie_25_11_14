#!/usr/bin/env bash
# Simple script to run the vulnerable app and run tests
set -e
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
# Start the Flask app in background
python app.py &
APP_PID=$!
echo "Started vulnerable app with PID $APP_PID"
# Wait for the server to start
sleep 1
pytest -q
# Shutdown
kill $APP_PID
