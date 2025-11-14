import os
import time
import json
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

BASE_URL = 'http://127.0.0.1:5001'

# Helper to ensure server is up

def wait_for_server(timeout=5):
    for _ in range(timeout * 5):
        try:
            requests.get(BASE_URL)
            return True
        except Exception:
            time.sleep(0.2)
    raise RuntimeError('Server not running')


def test_secret_masked_in_dashboard():
    wait_for_server()
    s = requests.Session()
    s.post(BASE_URL + '/login', data={'username': 'user1'})
    r = s.get(BASE_URL + '/dashboard')
    assert 'SENSITIVE_API_KEY_patched_DEF456' not in r.text
    assert 'API Key: [HIDDEN]' in r.text or 'API Key: S' in r.text


def test_no_secret_in_client_js():
    wait_for_server()
    r = requests.get(BASE_URL + '/static/js/client.js')
    assert 'SENSITIVE_API_KEY_patched_DEF456' not in r.text
    assert 'console.log' not in r.text or 'API_KEY' not in r.text


def write_json_report(report_path, report):
    with open(report_path, 'w', encoding='utf-8') as fh:
        json.dump(report, fh, indent=2)


def test_upload_preview_sanitized_and_no_exfiltration():
    wait_for_server()
    # Start Selenium headless as a victim
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    report = {
        'vulnerability': 'Sanitized preview should not execute uploaded scripts',
        'exploit_steps': [],
        'expected': 'Uploaded scripts should be removed and no token exfiltration occur',
        'actual': '',
        'exploit_success': False
    }
    try:
        driver.get(BASE_URL + '/login')
        report['exploit_steps'].append('Login as victim')
        driver.find_element(By.NAME, 'username').send_keys('victim')
        driver.find_element(By.CSS_SELECTOR, 'button[type=submit]').click()
        time.sleep(0.8)
        assert 'Patched Dashboard' in driver.page_source
        report['exploit_steps'].append('Open patched dashboard')
        # Upload the previously malicious payload
        malicious = "<script>new Image().src=\'/exfiltrate?token=\' + encodeURIComponent(document.getElementById('api-key').innerText);</script>"
        report['exploit_steps'].append('Upload malicious HTML file')
        files = {'file': ('malicious.html', malicious)}
        s = requests.Session()
        s.post(BASE_URL + '/login', data={'username': 'u'})
        # Reset any previous exfiltrations
        s.post(BASE_URL + '/reset-exfiltrations')
        r = s.post(BASE_URL + '/upload', files=files)
        assert r.status_code == 200
        filename = r.json()['filename']
        # Open the preview page - sanitized so script should not execute
        driver.get(BASE_URL + '/preview/' + filename)
        time.sleep(0.5)  # Wait for any script execution (shouldn't run)
        r = requests.get(BASE_URL + '/exfiltrations')
        data = r.json()
        report['actual'] = {'exfiltrated': data}
        success = any('SENSITIVE_API_KEY_patched_DEF456' in (e.get('token') or '') for e in data)
        report['exploit_success'] = success
        write_json_report('patched/exploit_result.json', report)
        assert not success
    finally:
        driver.quit()


def test_debug_info_denied():
    wait_for_server()
    s = requests.Session()
    s.post(BASE_URL + '/login', data={'username': 'u'})
    r = s.get(BASE_URL + '/debug-info')
    assert r.status_code == 403


if __name__ == '__main__':
    print('Patched app tests')
