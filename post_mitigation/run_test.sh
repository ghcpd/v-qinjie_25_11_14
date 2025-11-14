#!/usr/bin/env bash
set -e
python -m pip install -r requirements.txt
python -m playwright install
python app.py &
# give server time to start
sleep 2
pytest -q
