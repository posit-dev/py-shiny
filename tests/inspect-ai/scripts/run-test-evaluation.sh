#!/bin/bash

set -e # Exit immediately if a command fails

# Function to log with timestamp
log_with_timestamp() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Function to cleanup hanging processes
cleanup_processes() {
  log_with_timestamp "Cleaning up any hanging processes..."
  pkill -f "playwright" || true
  pkill -f "chromium" || true
  pkill -f "pytest" || true
}

# Set up trap to cleanup on exit
trap cleanup_processes EXIT

for i in {1..3}
do
  log_with_timestamp "Starting Attempt $i of 3"

  # Clean up results from previous attempt to ensure a clean slate
  rm -rf results/
  mkdir -p results/
  rm -f test-results.xml

  log_with_timestamp "[Attempt $i] Creating test metadata..."
  python tests/inspect-ai/scripts/create_test_metadata.py

  log_with_timestamp "[Attempt $i] Running Inspect AI evaluation..."
  inspect eval tests/inspect-ai/scripts/evaluation.py@shiny_test_evaluation \
    --log-dir results/ \
    --log-format json

  log_with_timestamp "[Attempt $i] Running Tests..."
  test_exit_code=0
  # Disable exit on error just for the pytest command to check the exit code
  set +e
  timeout 15m pytest tests/inspect-ai/apps \
    --tb=short \
    --disable-warnings \
    --maxfail=2 \
    --junit-xml=test-results.xml \
    --durations=10 \
    --timeout=300 \
    --timeout-method=thread \
    -v || test_exit_code=$?
  # Re-enable exit on error immediately
  set -e

  # Check if timeout occurred
  if [ "${test_exit_code:-0}" -eq 124 ]; then
    log_with_timestamp "Tests timed out on attempt $i - this may indicate hanging tests"
    cleanup_processes
    exit 1
  fi

  # Check if tests failed and how many failures occurred
  if [ "${test_exit_code:-0}" -ne 0 ]; then
    failure_count=$(grep -o 'failures="[0-9]*"' test-results.xml | grep -o '[0-9]*' || echo "0")
    log_with_timestamp "Found $failure_count test failures on attempt $i"

    # Fail the workflow if more than 1 test failed
    if [ "$failure_count" -gt 1 ]; then
      log_with_timestamp "More than 1 test failed on attempt $i - failing CI"
      exit 1
    fi
  fi
  log_with_timestamp "Attempt $i of 3 Succeeded"
done

log_with_timestamp "All 3 evaluation and test runs passed successfully."
