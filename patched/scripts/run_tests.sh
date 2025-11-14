#!/usr/bin/env bash
set -e
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
# Run patched Flask app in background
python app.py &
APP_PID=$!
echo "Started patched app with PID $APP_PID"
sleep 1
pytest -q
kill $APP_PID
