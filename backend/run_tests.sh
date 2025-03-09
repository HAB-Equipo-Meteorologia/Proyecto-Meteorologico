#!/bin/bash

echo "Running tests..."

set -e

set -o allexport
source .env
set +o allexport

export TEST_ENV=true

LOG_FILE="logs/tests.log"

PYTHONPATH=$(pwd):$(pwd)/src
export PYTHONPATH

echo "Running pytest..." >> "$LOG_FILE" 2>&1
pytest --cov=src --cov-report=term-missing "tests" | tee -a "$LOG_FILE" 2>&1

if [ "${PIPESTATUS[0]}" -ne 0 ]; then
  echo "Tests failed! Check $LOG_FILE for more details."
  unset TEST_ENV
  exit 1
else
  echo "Tests passed!"
fi

unset TEST_ENV

exit $?