#!/usr/bin/env python
import sys
from os import path
import argparse
import json
import settings
from constants import _constants

def parse_args(test_cases):
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-cases", help = "List of test case(s) to generate", nargs = '+',
        default = test_cases, choices = test_cases)
    parser.add_argument("--test-count", help = "Number of tests to generate", type = int, default = _constants.default_test_count)
    parser.add_argument("--output", help = "Output directory", default = settings.NUMBER_DIR)
    parser.add_argument("--operand-count", help = "Maximum number of operands",
        type = int, choices = range(_constants.operand_count_min, _constants.operand_count_max), default = _constants.operand_count_max)
    parser.add_argument("--seed", help = "Seed value used while generating random number", type = int, default = _constants.default_seed)
    parser.add_argument("-q", help = "Does not print any output", action='store_true')

    if len(sys.argv) <= 1:
        parser.print_help()
        sys.exit(1)

    script_args = parser.parse_args()

    return script_args
