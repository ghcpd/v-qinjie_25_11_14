import json, os

pre_file='pre_mitigation/pre_vuln_report.json'
post_file='post_mitigation/post_mitigation_report.json'
pre = json.load(open(pre_file)) if os.path.exists(pre_file) else {}
post = json.load(open(post_file)) if os.path.exists(post_file) else {}

report = {
    'summary': 'UI Security Report - Pre/Post mitigation comparison',
    'pre_mitigation': pre,
    'post_mitigation': post,
    'vulnerabilities': []
}

# Map certain findings to report entries (basic mapping)
for v in pre.get('vulnerabilities', []):
    name = v.get('test')
    status = v.get('status')
    patched = False
    for v2 in post.get('vulnerabilities', []):
        if v2.get('test') == name or v2.get('test').startswith(name.split('_')[0]):
            patched = (v2.get('status') == 'passed')
            break
    report['vulnerabilities'].append({'test': name, 'pre_status': status, 'post_patched': patched})

open('security_report.json', 'w').write(json.dumps(report, indent=2))
print('security_report.json written')
