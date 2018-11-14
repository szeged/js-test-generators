#!/usr/bin/env python

validate_numeric = '''
function validate_numeric(test_value, expected_result, false_results) {
    var radix = 2 + Math.abs(expected_result % 35);
    assert(test_value === expected_result);
    assert(test_value.toString(radix) === expected_result.toString(radix));
    for (var i in false_results) {
        radix = 2 + Math.abs(false_results[i] % 35);
        assert(test_value !== false_results[i]);
        assert(test_value.toString(radix) !== false_results[i].toString(radix));
    }
}
'''

validate_numeric_header = '''validate_numeric({EXPRESSION}, {EXPECTED_RESULT}, {FALSE_VALUES});'''
