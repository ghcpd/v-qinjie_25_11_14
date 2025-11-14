import json
import os

VULN = 'vulnerable/exploit_result.json'
PATCHED = 'patched/exploit_result.json'
PATCH_SUMMARY = 'patched/PATCH_SUMMARY.md'
OUT = 'security_report.json'

report = {
    'vulnerability': None,
    'exploit': None,
    'patched': None,
}

if os.path.exists(VULN):
    vuln = json.load(open(VULN))
    report['vulnerability'] = {
        'description': vuln.get('vulnerability'),
        'exploit_steps': vuln.get('exploit_steps'),
        'expected': vuln.get('expected'),
        'actual': vuln.get('actual'),
        'exploit_success': vuln.get('exploit_success')
    }
else:
    report['vulnerability'] = {'error': 'no vulnerable exploit report'}

if os.path.exists(PATCHED):
    patched = json.load(open(PATCHED))
    report['patched'] = {
        'description': patched.get('vulnerability'),
        'exploit_steps': patched.get('exploit_steps'),
        'expected': patched.get('expected'),
        'actual': patched.get('actual'),
        'exploit_success': patched.get('exploit_success')
    }
else:
    report['patched'] = {'error': 'no patched exploit report'}

if os.path.exists(PATCH_SUMMARY):
    report['patch_summary'] = open(PATCH_SUMMARY).read()

json.dump(report, open(OUT, 'w'), indent=2)
print('Created report at', OUT)
