#!/bin/bash
set -euo pipefail
ROOT_DIR=$(pwd)
for project in pre_mitigation_dashboard post_mitigation_dashboard; do
  echo "==> Running security suite for $project"
  pushd "$ROOT_DIR/$project" > /dev/null
  ./run_tests.sh
  popd > /dev/null
  echo "==> Completed $project"
  echo
  rm -rf "$ROOT_DIR/$project/.venv" "$ROOT_DIR/$project/.pytest_cache" "$ROOT_DIR/$project/tests/__pycache__"
done
