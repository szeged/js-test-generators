#!/usr/bin/env python3

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
import sys
import argparse
import collections
import random
import subprocess

# Local packages
import settings
path = os.path.join(settings.TEMPLATE_DIR)
sys.path.append(path)
import validate # Function
from constants import _constants # Constant values
from parse_args import parse_args # Argument parser
from generator_base import Generator # Base class
from utils import write_file # File writer
from generate_binary_ops import GenSequence # Operation result object
from utils import Messages # Messages

# Class for relational and equality expressions
class GenRelationAndEquality(Generator):

    class _InnerValues():
        generated_filename = '''relation-equality-ops-{NUMBER}.js''' # The file name prefix of the generated
        relational_and_equality_operators = ["EQ", "NE", "SE", "SN", "LT", "LE", "GT", "GE"]
        # Special values which need to be handled differently than numbers or strings
        special_values =  ["undefined", "null", "NaN", "true", "false"]

    # Initialize the generator
    def __init__(self, options):
        self.num_operands = options.operand_count # Number of operands in the expression
        self.options = options

    def expression_generator(self):
        self.functions_lib()
        self.expression_builder()

    # Libary of operator functions
    def functions_lib(self):
        self.operators_list = [] # List of currently used operators
        self.oper_funcs = {}
        for oper in self._InnerValues.relational_and_equality_operators:
            self.oper_funcs[oper] = getattr(self, oper)

    # Handler for operand generating
    def percentage(self, opts, i):
      sum = 0
      for elem in opts:
        sum += elem[0]
        if i <= sum:
          break;
        if sum >= 100:
          break
      return elem[1]

    # Generating the expression with operands and operators
    def expression_builder(self):
        for op in self.options.test_cases:
            self.operators_list.append(self.oper_funcs[op])

        self.operands = [0] * self.num_operands # Creating a list for the operands
        self.operators = [0] * (self.num_operands - 1) # Creating a list for the operators

        # Generating the expression
        for i in range(self.num_operands - 1):
            options = [
            [40, self._InnerValues.special_values[random.randint(0, len(self._InnerValues.special_values) - 1)]],
            [10, str(random.randint(_constants.min, _constants.max))],
            [50, random.randint(_constants.min, _constants.max)],
            ]
            self.operands[i] = self.percentage(options, random.randint(0, 100))
            self.operators[i] = random.randint(0, len(self.operators_list) - 1)
        self.operands[self.num_operands - 1] = self.percentage(options, random.randint(0, 100))

    # Convert python boolean values to fit js
    def convert_true_false_to_lowercase_string(self, value):
        return "true" if value else "false";

    # Add commas to the value if it is meant to be a string in the test case
    def add_coma_if_string(self, value):
        if value not in self._InnerValues.special_values and isinstance(value, str):
            value = "'%s'" % (value)
        return value

    # A helper function for special cases in equality
    def eq_helper_special_cases(self, values):
        special_cases = [["undefined", "undefined"], ["null", "null"], ["undefined", "null"],
        ["null", "undefined"], ["true", "true"], ["false", "false"]]
        return values in special_cases

    # ES v5.1 11.8. - 11.9. (except 11.8.6. and 11.8.7.)
    # Relational and equality operators

    # Equality operators

    # ES v5.1 11.9.3
    # Equality
    def EQ(self, left_value, right_value):
        # If one of the values is NaN return false
        if (left_value == "NaN" or right_value == "NaN"):
            return GenSequence.create_operation_result_object(self ,'==', right_value, "false")

        # Cases where it should return true
        elif self.eq_helper_special_cases([left_value, right_value]):
            return GenSequence.create_operation_result_object(self ,'==', right_value, "true")

        # If it does not match the cases above and values are not undefined or null
        elif left_value not in ["undefined", "null"] and right_value not in ["undefined", "null"]:
            # Converting values
            left_converted = int({"true": 1, "false": 0}.get(left_value, left_value))
            right_converted = int({"true": 1, "false": 0}.get(right_value, right_value))
            result = self.convert_true_false_to_lowercase_string(left_converted == right_converted)
            return GenSequence.create_operation_result_object(self, '==', right_value, result)
        return GenSequence.create_operation_result_object(self, '==', right_value, "false")

    # ES v5.1 11.9.2.
    # Not equality
    def NE(self, left_value, right_value):
        result = "true" if self.EQ(left_value, right_value)['result'] == "false" else "false"
        return GenSequence.create_operation_result_object(self, '!=', right_value, result)

    # ES v5.1 11.9.4
    # Strict equality
    def SE(self, left_value, right_value):
        # If one of the values is NaN return false
        if (left_value == "NaN" or right_value == "NaN"):
            return GenSequence.create_operation_result_object(self ,'===', right_value, "false")
        result = self.convert_true_false_to_lowercase_string(left_value == right_value)
        return GenSequence.create_operation_result_object(self, '===', right_value, result)

    # ES v5.1 11.9.5.
    # Strict not equality
    def SN(self, left_value, right_value):
        result = "true" if self.SE(left_value, right_value)['result'] == "false" else "false"
        return GenSequence.create_operation_result_object(self, '!==', right_value, result)

    # Relational operators

    # ES v5.1 11.8.5
    # Less than operator
    def LT(self, left_value, right_value):
        # If one of the values is NaN return false
        if left_value in ["NaN", "undefined"] or right_value in ["NaN", "undefined"]:
            return GenSequence.create_operation_result_object(self ,'<', right_value, "false")
        # To convert null, true, and false
        # if its not null, true or false, dont do anything
        left_converted = {"null": 0, "false": 0, "true": 1}.get(left_value, left_value)
        right_converted = {"null": 0, "false": 0, "true": 1}.get(right_value, right_value)
        if (isinstance(left_converted, str) and isinstance(right_converted, str)):
            result = self.convert_true_false_to_lowercase_string(left_converted < right_converted)
        else:
            result = self.convert_true_false_to_lowercase_string(int(left_converted) < int(right_converted))
        return GenSequence.create_operation_result_object(self, '<', right_value, result)

    # ES v5.1 11.8.2
    # Greater than operator
    def GT(self, left_value, right_value):
        if "NaN" in [left_value, right_value]:
            return GenSequence.create_operation_result_object(self ,'>', right_value, "false")
        result = self.LT(right_value, left_value)['result']
        return GenSequence.create_operation_result_object(self, '>', right_value, result)

    # ES v5.1 11.8.3.
    # Less than or equal operator
    def LE(self, left_value, right_value):
        if left_value in ["NaN", "undefined"] or right_value in ["NaN", "undefined"]:
            return GenSequence.create_operation_result_object(self ,'<=', right_value, "false")
        result = "true" if self.LT(right_value, left_value)['result'] == "false" else "false"
        return GenSequence.create_operation_result_object(self, '<=', right_value, result)

    # ES v5.1 11.8.4.
    # Greater than or equal operator
    def GE(self, left_value, right_value):
        if left_value in ["NaN", "undefined"] or right_value in ["NaN", "undefined"]:
            return GenSequence.create_operation_result_object(self ,'>=', right_value, "false")
        result = "true" if self.LT(left_value, right_value)['result'] == "false" else "false"
        return GenSequence.create_operation_result_object(self, '>=', right_value, result)

    # Declaration creater function
    def create_declarations(self, expected_value):
        # Adding false boolean string
        false_boolean_string = self.create_false_boolean_string(expected_value)
        # Adding commas if value is meant to be a string
        for i in range(len(self.operands)):
            self.operands[i] = self.add_coma_if_string(self.operands[i])
        # Adding declarations of test values
        test_case = self.create_declarations_string(self.create_declarations_dict(self.operands,
        self.TEST_VALUE_VAR_NAME))
        # Adding declarations of false value
        test_case += self.create_declarations_string(self.create_declarations_dict(false_boolean_string,
        self.FALSE_RESULT_VAR_NAME))
        # Adding declarations of expected value
        test_case += self.create_declarations_string(self.create_declarations_dict(expected_value,
        self.EXPECTED_VAR_NAME))
        return test_case

    # Converting expression, expected value, false value in a function call to string format
    def string_creator(self):
        self.expression_generator()
        last = self.operands[0]
        expression = "%s%s" % ("(" * (self.num_operands - 1), self.TEST_VALUE_VAR_NAME.format(NUMBER = (1)))
        for i in range(self.options.operand_count - 1):
            result = self.operators_list[self.operators[i]](last, self.operands[i + 1])
            expression += (" %s %s)" % (result["oper"], self.TEST_VALUE_VAR_NAME.format(NUMBER = (i + 2))))
            self.operands[i + 1] = result["right_value"]
            last = result["result"]
        expression += "\n"
        test_case = self.create_declarations(last)
        # Adding the function call
        test_case += self.create_function_call(expression, self.EXPECTED_VAR_NAME.format(NUMBER = ""),
        self.FALSE_RESULT_VAR_NAME.format(NUMBER = ""), validate.validate_boolean_header)
        test_case += "\n\n"
        return test_case

    # Relational and equality operator test generator function
    def generate_relational_and_equality_ops(self, options):
        random.seed(self.options.seed)
        self.debug(Messages.generating, self.options)
        gen_settings = settings.file_write_settings(self._InnerValues.generated_filename, self.options.output, validate.validate_boolean,
        _constants.test_case_in_a_file)
        for i in range(self.options.test_count): # In range of number test cases
            self.test_case += self.string_creator()
            self.append_test_case()
        write_file(gen_settings, self.file_output)
        self.debug(Messages.done, self.options)

if __name__ == '__main__':
    gre = GenRelationAndEquality(parse_args(GenRelationAndEquality._InnerValues.relational_and_equality_operators)) # Declaring the generator
    gre.generate_relational_and_equality_ops(GenSequence._InnerValues.generated_filename)
