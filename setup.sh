#!/usr/bin/env bash
set -e
python -m pip install --upgrade pip
python -m pip install virtualenv || true
python -m venv venv
. venv/bin/activate
pip install -r pre_mitigation/requirements.txt
python -m playwright install
