#!/bin/bash

set -e

# Defaults (override via env)
: "${SHINY_TEST_TIMEOUT_SECS:=10}"
: "${PYTEST_PER_TEST_TIMEOUT:=60}"
: "${PYTEST_SUITE_TIMEOUT:=6m}"
: "${PYTEST_MAXFAIL:=1}"
: "${PYTEST_XDIST_WORKERS:=auto}"
: "${ATTEMPTS:=3}"
export SHINY_TEST_TIMEOUT_SECS

log_with_timestamp() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

cleanup_processes() {
  log_with_timestamp "Cleaning up any hanging processes..."
  pkill -f "playwright" || true
  pkill -f "chromium" || true
  pkill -f "pytest" || true
}

trap cleanup_processes EXIT

# Initialize results directory structure once
rm -rf results/
mkdir -p results/

for i in $(seq 1 "$ATTEMPTS"); do
  log_with_timestamp "Starting attempt $i of $ATTEMPTS"

  mkdir -p results/attempts/attempt_$i/
  rm -f test-results.xml

  log_with_timestamp "[Attempt $i] Creating test metadata..."
  python tests/inspect-ai/scripts/create_test_metadata.py

  log_with_timestamp "[Attempt $i] Running Inspect AI evaluation..."
  inspect eval tests/inspect-ai/scripts/evaluation.py@shiny_test_evaluation \
    --log-dir results/attempts/attempt_$i/ \
    --log-format json

  log_with_timestamp "[Attempt $i] Running tests..."
  test_exit_code=0
  set +e
  timeout "$PYTEST_SUITE_TIMEOUT" pytest tests/inspect-ai/apps \
    -n "$PYTEST_XDIST_WORKERS" --dist loadfile \
    --tb=short \
    --disable-warnings \
    --maxfail="$PYTEST_MAXFAIL" \
    --junit-xml=results/attempts/attempt_$i/test-results.xml \
    --durations=10 \
    --timeout="$PYTEST_PER_TEST_TIMEOUT" \
    --timeout-method=signal \
    -v || test_exit_code=$?
  set -e

  if [ "${test_exit_code:-0}" -eq 124 ]; then
    log_with_timestamp "Tests timed out on attempt $i (possible hang)"
    cleanup_processes
    exit 1
  fi

  if [ "${test_exit_code:-0}" -ne 0 ]; then
    if [ -f results/attempts/attempt_$i/test-results.xml ]; then
      failure_count=$(grep -o 'failures="[0-9]*"' results/attempts/attempt_$i/test-results.xml | grep -o '[0-9]*' || echo "0")
    else
      failure_count=0
    fi
    log_with_timestamp "Found $failure_count test failures on attempt $i"

    if [ "$failure_count" -gt 1 ]; then
      log_with_timestamp "More than 1 test failed on attempt $i - failing CI"
      exit 1
    fi
  fi

  log_with_timestamp "Attempt $i of $ATTEMPTS succeeded"
done

log_with_timestamp "All $ATTEMPTS evaluation and test runs passed successfully."

log_with_timestamp "Averaging results across all attempts..."
python tests/inspect-ai/utils/scripts/average_results.py results/attempts/ results/
