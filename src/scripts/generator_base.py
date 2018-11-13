#!/usr/bin/env python

# Copyright JS Foundation and other contributors, http://js.foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import argparse
import random
import math
import sys

# Local packages
import settings
path = os.path.join(settings.TEMPLATE_DIR)
sys.path.append(path)
import validate # Function
from constants import _constants

# Generator base class, other generator classes will intherit from this class
class Generator:
    TEST_VALUE_VAR_NAME = '''t{NUMBER}'''    # The name of the test variable(s) in the .js files
    EXPECTED_VAR_NAME = '''e{NUMBER}'''  # The name of the expected variable in the .js files
    FALSE_RESULT_VAR_NAME = '''f{NUMBER}'''  # The name of the false variable(s) in the .js files
    test_case = "" # Actual test case with validate function call
    file_output = [] # All the test cases generated (without function definition)

    # Printing debug messages (-q: quiet)
    def debug(self, message, options):
        if not options.q:
            print(message)

    # Appends test_case to file output
    def append_test_case(self):
        self.file_output.append(self.test_case)
        self.test_case = ""

    # Generate a random false value
    def generate_false_value(self, expected_value, min_max):
        # Random number which must not be equal with the expected value
        LESS_OR_MORE = random.randint(0, 1)
        if ((LESS_OR_MORE and expected_value != min_max['max']) or expected_value == min_max['min']):
            return random.randint(int(expected_value + 1), min_max['max'])
        return random.randint(min_max['min'], int(expected_value - 1))

    # Generating false values into an array
    def generate_false_numbers(self, expected_value, false_values_count, min_max):
        false_values = []
        for j in range(false_values_count):
            false_values.append(self.generate_false_value(expected_value, min_max))
        return false_values

    # Stringify an array of false values
    def create_false_numbers_array_string(self, false_values_count):
        return ('[%s]'% ', '.join([self.FALSE_RESULT_VAR_NAME.format(NUMBER = i) for i in range(1,
        false_values_count + 1)]))

    # Stringify a declaration dictionary
    def create_declarations_string(self, declarations_dictionary):
        declaration_string = ""
        for key, value in declarations_dictionary.items():  # For E.g.: a0 = 38473837;
             declaration_string += "%s = %s;\n" % (str(key), str(value))
        return declaration_string

    # Create a dictionary from the from the given value(s)
    def create_declarations_dict(self, values, var_name):
        declarations_dictionary = {}
        if isinstance(values, list):
            for i in range(1, len(values) + 1):
                declarations_dictionary[var_name.format(NUMBER = i)] = values[i - 1]
        else:
            declarations_dictionary[var_name.format(NUMBER = "")] = values
        return declarations_dictionary

    # Construct a test case.
    def create_function_call(self, test_value, expected_value, false_values, function):
        function_call = function.format(
            EXPRESSION = str(test_value),
            EXPECTED_RESULT = str(expected_value),
            FALSE_VALUES = str(false_values))
        return function_call
