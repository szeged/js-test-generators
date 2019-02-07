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
import sys
import argparse
import collections
import random
import math

# Local packages
import settings
path = os.path.join(settings.TEMPLATE_DIR)
sys.path.append(path)
import validate # Function
from constants import _constants # Constant values
from parse_args import parse_args # Argument parser
from utils import unsigned32
from generator_base import Generator
from generate_binary_ops import GenSequence

# Class for expressions
class GenerateAssignments(GenSequence):

    # Initialize the generator
    def __init__(self, options):
        self.num_operands = options.operand_count # Number of operands in the expression
        self.options = options
        self._InnerValues.generated_filename = '''assignments-{NUMBER}.js'''
        self._InnerValues.arithmetic_operators.append("assign")
        self._InnerValues.binary_operators.append("assign")

    # Generating the expression with operands and operators
    def expression_generator(self, calc):
        self.functions_lib(calc)
        self.oper_funcs["assign"] = self.assign
        self.expression_maker(calc)

    # Arithmetic calculations not included in base class

    # Assignment
    def assign(self, left_value, right_value):
        return {'oper': '=', 'right_value': right_value, 'result': right_value}

    # Converting expression, expected value, false value in a function call to string format
    def string_creator(self, min_max):
        last = self.operands[0]
        calculation = ""
        expression = self.TEST_VALUE_VAR_NAME.format(NUMBER = 1)
        for i in range(self.options.operand_count - 1):
            result = self.operators_list[self.operators[i]](last, self.operands[i + 1])
            # If the operator is assignment, we do not need to add another
            calculation += ("%s %s%s %s;\n" % (self.TEST_VALUE_VAR_NAME.format(NUMBER = 1), result["oper"],
            "" if (result["oper"] == "=") else "=", self.TEST_VALUE_VAR_NAME.format(NUMBER = (i + 2))))
            if result["oper"] == "/":
                calculation += "%s |= 0; " % (self.TEST_VALUE_VAR_NAME.format(NUMBER = 1))
            self.operands[i + 1] = result["right_value"]
            last = result["result"]
        return self.create_test_case(expression, last, calculation, min_max)

def main():
    ga = GenerateAssignments(parse_args(GenerateAssignments._InnerValues.binary_operators)) # Declaring the generator
    ga.generate_binary_ops(GenerateAssignments._InnerValues.generated_filename)

if __name__ == '__main__':
    main()
