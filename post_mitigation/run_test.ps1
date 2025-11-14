# Run post-mitigation tests (PowerShell)
python -m pip install -r requirements.txt
python -m playwright install
Start-Process -NoNewWindow -FilePath python -ArgumentList 'app.py'
Start-Sleep -Seconds 2
python -m pytest -q
