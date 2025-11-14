Set-StrictMode -Version Latest
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r ..\requirements.txt
Start-Process -NoNewWindow -FilePath python -ArgumentList 'app.py' -PassThru
Start-Sleep -Seconds 1
pytest -q
