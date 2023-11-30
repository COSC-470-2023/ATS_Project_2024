#!/bin/bash

# list of unittest scripts, to test more scripts add their path to the list
unittest_scripts=("company_statements_UnitTest.py" "realtime_stocks_UnitTest.py")

# run unittest code and print results
run_unittest() 
{
  script_name=$1
  python "$script_name"
  # $? is an env var that holds the exit code of the last run command
  exit_code=$?
  if [ $exit_code -eq 0 ]; then
    echo "$script_name passed successfully."
  else
    echo "$script_name failed."
    exit 1
  fi
}

# iterate over scripts and run each
for script in "${unittest_scripts[@]}"; do
  run_unittest "$script"
done

echo "All scripts passed successfully."
exit 0