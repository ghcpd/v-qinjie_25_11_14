import os
import sys
import subprocess
import time
import json

ROOT = os.getcwd()
VULN_DIR = os.path.join(ROOT, 'vulnerable')
PATCHED_DIR = os.path.join(ROOT, 'patched')

def run_app_tests(app_dir, run_script, port, env_python=None):
    # Start server in background and run pytest for app
    print(f'Running tests for {app_dir}...')
    prev_dir = os.getcwd()
    os.chdir(app_dir)
    try:
        # Start app server
        server_proc = subprocess.Popen([sys.executable, 'app.py'])
        print('Started server pid', server_proc.pid)
        # Wait for start
        time.sleep(1.2)
        # Run pytest inside app dir
        pytest_proc = subprocess.run(['pytest', '-q'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        print(pytest_proc.stdout)
        # Kill server
        server_proc.kill()
        server_proc.wait()
        return pytest_proc.returncode
    finally:
        os.chdir(prev_dir)


if __name__ == '__main__':
    os.environ['PYTHONUNBUFFERED'] = '1'
    # create venv and install dependencies for both apps
    print('Installing dependencies...')
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', os.path.join(VULN_DIR, 'requirements.txt')])
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', os.path.join(PATCHED_DIR, 'requirements.txt')])

    rc1 = run_app_tests(VULN_DIR, 'scripts/run_tests.sh', 5000)
    rc2 = run_app_tests(PATCHED_DIR, 'scripts/run_tests.sh', 5001)

    # Collect exploit reports
    vuln_report_path = os.path.join(VULN_DIR, 'exploit_result.json')
    patched_report_path = os.path.join(PATCHED_DIR, 'exploit_result.json')
    report = {
        'vulnerable': None,
        'patched': None,
        'summary': {}
    }
    if os.path.exists(vuln_report_path):
        report['vulnerable'] = json.load(open(vuln_report_path))
    else:
        report['vulnerable'] = {'error': 'no report generated'}
    if os.path.exists(patched_report_path):
        report['patched'] = json.load(open(patched_report_path))
    else:
        report['patched'] = {'error': 'no report generated'}

    # Compare exploit success
    vuln_success = report['vulnerable'].get('exploit_success') if report['vulnerable'] else True
    patched_success = report['patched'].get('exploit_success') if report['patched'] else True
    report['summary']['vulnerability_exploited'] = bool(vuln_success)
    report['summary']['patched_exploit_failed'] = not bool(patched_success)

    with open('security_report.json', 'w') as fh:
        json.dump(report, fh, indent=2)

    print('Security report generated at security_report.json')

    if rc1 != 0 or rc2 != 0:
        print('Some tests failed')
        sys.exit(1)
    print('All tests passed')
