#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

# list of unittest scripts, to test more scripts add their path to the list
unittest_scripts=("company_statements_insert_UnitTest" "realtime_stock_insert_UnitTest")

# flag to silence python output by default
VERBOSE_MODE=false

# run unittest code and print results
run_unittest() 
{
  script_name=$1
  if [ "$VERBOSE_MODE" = true ]; then
    python3 -m "tests.database.$script_name"
  else
    python3 -m "tests.database.$script_name" > /dev/null 2>&1
  fi
  # $? is an env var that holds the exit code of the last run command
  exit_code=$?
  if [ $exit_code -eq 0 ]; then
    echo "Regression: $script_name passed successfully."
  else
    echo "Regression: $script_name failed."
  fi
}

# check for verbose mode option
while [[ $# -gt 0 ]]; do
  case "$1" in
    --verbose | -v )
      VERBOSE_MODE=true
      shift
      ;;
    * )
      shift
      ;;
  esac
done

# iterate over scripts and run each
for script in "${unittest_scripts[@]}"; do
  run_unittest "$script"
done

echo "Regression: All unit tests completed."
exit 0
