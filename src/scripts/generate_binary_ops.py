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
import subprocess

# Local packages
import settings
path = os.path.join(settings.TEMPLATE_DIR)
sys.path.append(path)
import validate # Function
from constants import _constants # Constant values
from parse_args import parse_args # Argument parser
from utils import unsigned32 # Number to unsigned int 32 bit
from generator_base import Generator # Base class
from utils import write_file # File writer
from utils import Messages

# Class for expressions
class GenSequence(Generator):

    class _InnerValues():
        generated_filename = '''binary-ops-{NUMBER}.js''' # The file name prefix of the generated tests
        false_values_count = 5 # Number of false values for each test case
        test_case_in_a_file = 500 # Maximum number of test for each file
        arithmetic_operators = ["add", "sub", "div", "mul", "mod"]  # The arithmetic operators used in this script
        bitwise_operators = ["xor", "and", "or", "rightshift", "leftshift"]  # The bitwise operators used in this script
        uint32_operators = ["unsignedrightshift"]
        binary_operators = arithmetic_operators + bitwise_operators + uint32_operators # The binary operators
        # used in this script

        # Symbolic constants for actual calculation types
        # 1: arithmetic, 2: bitwise (excluding unsigned right shift) 3: unsigned right shift
        arith = 1
        bit = 2
        uint32 = 3

        used_calculations = [] # Actually needed calculation types represented by their symbolic constants
        types_count = 0 # Number of calculation types needed

    # Initialize the generator
    def __init__(self, options):
        self.num_operands = options.operand_count # Number of operands in the expression
        self.options = options

    # Adding functions to the library and generating the expression with operands and operators
    def expression_generator(self,calc):
        self.functions_lib(calc)
        self.expression_maker(calc)

    # Adding functions to the library
    def functions_lib(self, calc):
        self.operators_list = [] # List of currently used operators
        self.oper_funcs = {
              "add": self.add,
              "sub": self.sub,
              "mul": self.mul,
              "div": self.div,
              "mod": self.mod,
              "and": self.bitand,
              "xor": self.bitxor,
              "or": self.bitor,
              "leftshift": self.bitleftshift,
              "rightshift": self.bitrightshift,
              "unsignedrightshift": self.bitunsignedrightshift
        } # Functions for the operators

    # Generating the expression with operands and operators
    def expression_maker(self, calc):
        for op in self.options.test_cases:
            if calc == self._InnerValues.arith:
                if op in self._InnerValues.arithmetic_operators:
                    self.operators_list.append(self.oper_funcs[op])
            elif calc == self._InnerValues.bit:
                if op in self._InnerValues.bitwise_operators:
                    self.operators_list.append(self.oper_funcs[op])
            else:
                if op in self._InnerValues.uint32_operators:
                    self.operators_list.append(self.oper_funcs[op])

        self.operands = [0] * self.num_operands # Creating a list for operands according to number of operands
        self.operators = [0] * (self.num_operands - 1) # Creating a list for operators according to number of operands

        # Setting max and min according to the calculations
        min_max = self.set_min_max(calc)

        # Generating the expression
        for i in range(self.num_operands - 1):
            self.operands[i] = random.randint(min_max['min'], min_max['max'])
            self.operators[i] = random.randint(0, len(self.operators_list) - 1)
        self.operands[self.num_operands - 1] = random.randint(min_max['min'], min_max['max'])

    # Creating the return object of the operation
    def create_operation_result_object(self, oper, right_value, result):
        return {'oper': oper, 'right_value': right_value, 'result': result}

    # Arithmetic operations

    # Addition
    def add(self, left_value, right_value):
        result = left_value + right_value
        if result < _constants.min: # Minimum / maximum number to safely add to operand 1
            right_value = _constants.min - random.randint(_constants.min, left_value)
            result = left_value + right_value
        elif result > _constants.max:
            right_value = _constants.max - random.randint(left_value, _constants.max)
            result = left_value + right_value
        return self.create_operation_result_object('+', right_value, result)

    # Subtraction
    def sub(self, left_value, right_value):
        result = left_value - right_value
        if result < _constants.min: # Minimum / maximum number to safely subtract from operand 1
            right_value = - (_constants.min - random.randint(_constants.min, left_value))
            result = left_value - right_value
        elif result > _constants.max:
            right_value = - (_constants.max - random.randint(left_value, _constants.max))
            result = left_value - right_value
        return self.create_operation_result_object('-', right_value, result)

    # Multiplication
    def mul(self, left_value, right_value):
        if left_value != 0:
            if left_value < 0:
                start = math.ceil(_constants.max / float(left_value))
                end = math.floor(_constants.min / float(left_value))
                right_value = random.randint(start, end)
            if left_value > 0:
                start = math.ceil(_constants.min / float(left_value))
                end = math.floor(_constants.max / float(left_value))
                right_value = random.randint(start, end)

        result = left_value * right_value
        return self.create_operation_result_object('*', right_value, result)

    # Division (floor division)
    def div(self, left_value, right_value):
        right_value = random.randint(_constants.min, _constants.max)
        if right_value == 0:
            right_value = random.randint(1, _constants.max)
        result = int(math.floor(left_value / right_value))
        if result < 0:
            result +=  1
        return self.create_operation_result_object('/', right_value, result)

    # Modulus
    # Difference between % operator in python and js
    # in python: -xxx % yy => yy - (abs(xxx) % yy)
    # in js: -xxx % yy => - abs(xxx) % yy
    def mod(self, left_value, right_value):
        if right_value == 0:
            if random.randint(0, 1):
                right_value = random.randint(1, _constants.max)
            else:
                right_value = random.randint(_constants.min, -1)
        if ((left_value * right_value < 0) and (left_value % right_value != 0)):
            result = ((left_value % right_value) - right_value)
        else:
            result = (left_value % right_value)
        return self.create_operation_result_object('%', right_value, result)

    # Bitwise operations

    # Bitshifting to left
    def bitleftshift(self, left_value, right_value):
        right_value = random.randint(_constants.uint32min, _constants.uint32max)
        rnum = unsigned32(right_value)
        shiftcount = rnum & 0x1f
        result = left_value << shiftcount
        if result > _constants.bitmax or result < _constants.bitmin: # Operand 2 must depend on the length of operand 1
            if left_value != 0:
                right_value = (_constants.bitmax_exposant - 1) - int.bit_length(left_value)
                right_value = max(right_value, 0) # Operand 2 also cant go below zero
                rnum = unsigned32(right_value)
                shiftcount = rnum & 0x1f
                result = left_value << shiftcount
        return self.create_operation_result_object('<<', right_value, result)

    # Bitshifting to right
    # Python only can handle shiftcount between 0-31, but smaller and bigger numbers
    # are also can be simulated with this method
    def bitrightshift(self, left_value, right_value):
        right_value = random.randint(_constants.bitmin, _constants.bitmax)
        result = int(hex((left_value >> ((right_value % (_constants.bitmax_exposant + 1)) & 0x1f))), 16)
        return self.create_operation_result_object('>>', right_value, result)

    # Unsigned right bitshifting
    def bitunsignedrightshift(self, left_value, right_value):
        right_value = random.randint(_constants.uint32min, _constants.uint32max)
        lnum = unsigned32(left_value)
        rnum = unsigned32(right_value)
        shiftcount = rnum & 0x1f
        result = ((lnum >> shiftcount) % _constants.uint32max)
        return self.create_operation_result_object('>>>', right_value, result)

    # Bitwise and
    def bitand(self, left_value, right_value):
        result = left_value & right_value
        return self.create_operation_result_object('&', right_value, result)

    # Bitwise or
    def bitor(self, left_value, right_value):
        result = left_value | right_value
        return self.create_operation_result_object('|', right_value, result)

    # Bitwise xor (exclusive or)
    def bitxor(self, left_value, right_value):
        result = right_value ^ left_value
        return self.create_operation_result_object('^', right_value, result)

    # Setting maximum and minimum depending on operation type
    def set_min_max(self, calc):
        if calc == self._InnerValues.arith:
            minnum = _constants.min
            maxnum = _constants.max
        elif calc == self._InnerValues.bit:
            minnum = _constants.bitmin
            maxnum = _constants.bitmax
        else:
            minnum = _constants.uint32min
            maxnum = _constants.uint32max
        return {'min' : minnum, 'max': maxnum}

    def create_declarations(self, expected_value, min_max):
        # Generating false numbers
        false_numbers = self.generate_false_numbers(expected_value, self._InnerValues.false_values_count, min_max)
        # Adding false numbers string
        false_numbers_string = self.create_false_numbers_array_string(self._InnerValues.false_values_count)
        # Adding declarations of test values
        test_case = self.create_declarations_string(self.create_declarations_dict(self.operands,
        self.TEST_VALUE_VAR_NAME))
        # Adding declarations of false values
        test_case += self.create_declarations_string(self.create_declarations_dict(false_numbers,
        self.FALSE_RESULT_VAR_NAME))
        # Adding declarations of expected value
        test_case += self.create_declarations_string(self.create_declarations_dict(expected_value,
        self.EXPECTED_VAR_NAME))
        return {'test_case' : test_case, 'false_numbers_string' : false_numbers_string}

    def create_test_case(self, expression, expected_value, calculation, min_max):
        declarations = self.create_declarations(expected_value, min_max)
        test_case = declarations['test_case']
        test_case += calculation
        # Adding the function call
        test_case += self.create_function_call(expression, self.EXPECTED_VAR_NAME.format(NUMBER = ""),
        declarations['false_numbers_string'], validate.validate_numeric_header)
        test_case += "\n\n"
        return test_case

    # Converting expression, expected value, false value in a function call to string format
    def string_creator(self, min_max):
        last = self.operands[0]
        expression = ("%s%s" % ("(" * (self.num_operands - 1), self.TEST_VALUE_VAR_NAME.format(NUMBER = 1)))
        for i in range(self.options.operand_count - 1):
            result = self.operators_list[self.operators[i]](last, self.operands[i + 1])
            expression += (" %s %s)" % (result["oper"], self.TEST_VALUE_VAR_NAME.format(NUMBER = (i + 2))))
            if result["oper"] == "/":
                expression += " | 0)"
                expression = "(" + expression
            self.operands[i + 1] = result["right_value"]
            last = result["result"]
        expression += "\n"
        return self.create_test_case(expression, last, "", min_max)

    # Randomly generates the type of the expression out of the needed calculation
    def actual_calc(self):
        # A random element from the array of actually needed calculations
        return self._InnerValues.used_calculations[random.randint(0, self._InnerValues.types_count - 1)]

    # Calculating currently needed calculation types
    def needed_calculation_types(self):
        self._InnerValues.types_count = 0
        for op in self.options.test_cases:
            # If arithmetic operators are currently needed
            if op in self._InnerValues.arithmetic_operators and self._InnerValues.arith not in self._InnerValues.used_calculations:
                self._InnerValues.used_calculations.append(self._InnerValues.arith)
                self._InnerValues.types_count += 1

            # If bitwise operators are currently needed
            if op in self._InnerValues.bitwise_operators and self._InnerValues.bit not in self._InnerValues.used_calculations:
                self._InnerValues.used_calculations.append(self._InnerValues.bit)
                self._InnerValues.types_count += 1

            # If unsigned right shift is currently needed
            if op in self._InnerValues.uint32_operators and self._InnerValues.uint32 not in self._InnerValues.used_calculations:
                self._InnerValues.used_calculations.append(self._InnerValues.uint32)
                self._InnerValues.types_count += 1

    # Generator
    def generate_binary_ops(self, generated_filename):
        self.debug("%s\n" % (Messages.generating), self.options)
        random.seed(self.options.seed)
        self.needed_calculation_types()
        gen_settings = settings.file_write_settings(generated_filename, self.options.output, validate.validate_numeric,
        self._InnerValues.test_case_in_a_file)
        for i in range(self.options.test_count): # In range of number test cases
            # Actually we are doing arithmetic or bitwise (excluding unsigned right shift) calculations
            # or unsigned right shift
            calc = self.actual_calc()
            self.expression_generator(calc)
            self.test_case += self.string_creator(self.set_min_max(calc))
            self.append_test_case()
        write_file(gen_settings, self.file_output)
        self.debug("%s\n" % (Messages.done), self.options)

def main():
    gs = GenSequence(parse_args(GenSequence._InnerValues.binary_operators)) # Declaring the generator
    gs.generate_binary_ops(GenSequence._InnerValues.generated_filename)

if __name__ == '__main__':
    main()
