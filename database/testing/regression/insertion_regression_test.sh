#!/bin/bash

# function to compare actual and expected outputs
compare_outputs() 
{
    actual_output="$1"
    expected_output="$2"

    if cmp -s "$actual_output" "$expected_output"; then
        echo "Test passed: $actual_output matches $expected_output"
    else
        echo "Test failed: "
    fi
}

# run tests
run_tests()
{
    test_program="$1"
    expected_output="$2"
    output_file="results_$test_program.txt"

    ./"$test_program" > "$output_file"
    compare_outputs "$output_file" "$expected_output"
}