#!/usr/bin/env bash
set -e
# Run pre-mitigation tests
pushd pre_mitigation
./run_test.sh
popd

# Run post-mitigation tests
pushd post_mitigation
./run_test.sh
popd

# Combine reports
python - <<'PY'
import json, os
pre='pre_mitigation/pre_vuln_report.json'
post='post_mitigation/post_mitigation_report.json'
pr=json.load(open(pre)) if os.path.exists(pre) else {}
po=json.load(open(post)) if os.path.exists(post) else {}
report={'pre':pr,'post':po}
print(json.dumps(report, indent=2))
open('combined_report.json','w').write(json.dumps(report, indent=2))
PY

echo 'Combined report written to combined_report.json'
