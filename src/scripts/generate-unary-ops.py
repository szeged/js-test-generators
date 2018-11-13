#!/usr/bin/env python
import sys
import os
import settings
import random
path = os.path.join(settings.TEMPLATE_DIR)
sys.path.append(path)
import validate
from constants import _constants
from parse_args import parse_args
from generator_base import Generator
from utils import write_file
from utils import Messages

class Unary_Operator_Generator(Generator):

    class _InnerValues():
        # The maximum and minimum values of numbers
        min_max = {'min': _constants.min, 'max': _constants.max}
        # The file name of the generated tests
        generated_filename = '''unary-ops-{NUMBER}.js'''
        # The number of false values generated for each tests
        false_values_count = 5
        # The count of test case type
        test_case_type_count = 2
        # The count of test case type for typeof operator
        test_case_type_count_typeof = 3
        # The pairs of test- and expected values for ! operator
        logical_not_test_values = {
            "0": False,
            "1": True,
            "-1": True,
            "''": False,
            "'true'": True,
            "'false'": True,
            "true": True,
            "false": False,
            "undefined": False,
            "null": False
        }
        unique_type_of_testtype = -1
        # The following lists are sublists of unary operators
        unary_plus_and_negation = ["+", "-"]
        increment_and_decrement = ["++", "--"]
        logical_and_bitwise_not = ["!", "~"]
        typeof_delete_and_void = ["typeof", "delete", "void"]
        # The unary operators used in this script
        unary_operators = (unary_plus_and_negation + increment_and_decrement +
                          logical_and_bitwise_not + typeof_delete_and_void)

    def concat_list_elements(self, list):
        return ''.join(map(str, list))
    # Creates the operation's string
    def create_operation(self, op, count, random_test_case_type):
        # At these operators the operations base is the 'operator''Variable name'
        if op not in self._InnerValues.typeof_delete_and_void:
            operation = "%s%s" % (op,
                                  self.TEST_VALUE_VAR_NAME.format(NUMBER = ""))
            # These operators need for loop to test
            if op in (self._InnerValues.increment_and_decrement +
                      self._InnerValues.logical_and_bitwise_not):
                # These operators needs declaration
                if op in self._InnerValues.logical_and_bitwise_not:
                    operation = self.create_declarations_string(
                                     self.create_declarations_dict(
                                          operation,
                                          self.TEST_VALUE_VAR_NAME))
                else:
                    operation = "%s;\n" % (operation)
                operation = ("for (i = 0; i < %d; i++) {\n%s}\n" % (count, operation))
            else:
                # negative hexadecimal numbers cannot be converted, so the test case
                # check it's type instead
                if isinstance(self.expected_value, str):
                    operation = "%s" % (self.create_declarations_string(
                                             self.create_declarations_dict(
                                                  "typeof(%s)" % (operation),
                                                  self.TEST_VALUE_VAR_NAME)))
                else:
                    operation = "%s" % (self.create_declarations_string(
                                             self.create_declarations_dict(
                                                  operation,
                                                  self.TEST_VALUE_VAR_NAME)))
        elif op == "typeof":
            operation = "%s" % (self.create_declarations_string(
                                      self.create_declarations_dict(
                                           "%s(%s)" % (op,self.TEST_VALUE_VAR_NAME.format(NUMBER = "")),
                                           self.TEST_VALUE_VAR_NAME)))
            if random_test_case_type == self._InnerValues.unique_type_of_testtype:
                operation = "delete %s;\n%s" % (self.TEST_VALUE_VAR_NAME.format(NUMBER = ""), operation)
        # Deletes an array element or a variable
        elif op == "delete":
            if random_test_case_type % self._InnerValues.test_case_type_count:
                operation = "%s" % (self.create_declarations_string(
                                         self.create_declarations_dict(
                                              "%s %s[%d]" % (op, self.TEST_VALUE_VAR_NAME.format(NUMBER = ""),
                                                             random.randint(0, count - 1)),
                                              self.TEST_VALUE_VAR_NAME)))
            else:
                operation = "%s" % (self.create_declarations_string(
                                         self.create_declarations_dict(
                                              "%s %s" % (op, self.TEST_VALUE_VAR_NAME.format(NUMBER = "")),
                                              self.TEST_VALUE_VAR_NAME)))
        elif op == "void":
            operation = "%s" % (self.create_declarations_string(
                                     self.create_declarations_dict(
                                          "typeof(%s %s())" % (op, self.TEST_VALUE_VAR_NAME.format(NUMBER = "")),
                                          self.TEST_VALUE_VAR_NAME)))
        return operation

     # Appends test_case to file output
    def append_test_case(self):
        self.file_output.append(self.test_case)
        self.test_case = ""

    # Adjust file_write_settings based on options
    def configure_settings(self, options):
        return settings.file_write_settings(
            self._InnerValues.generated_filename,
            options.output,
            validate.validate_numeric,
            _constants.test_case_in_a_file)

    # Adds Unique test cases for some operators
    def add_unique_test_cases(self, op):
        if op in self._InnerValues.unary_plus_and_negation:
            # Step is used for test value here
            for step in ["true","false","null"]:
                self.test_value = step
                self.expected_value = step == "true"
                if op == "-":
                    self.expected_value = -self.expected_value
                self.expected_value = int(self.expected_value)
                false_values = self.generate_false_numbers(self.expected_value,
                                                           self._InnerValues.false_values_count,
                                                           self._InnerValues.min_max)
                # The false value is the opposite of expected_value here
                false_values.append(int(step != "true"))
                # Count and random_test_case_type parameters is not used here
                self.create_test_case_string(op, false_values, 0, 0)
        # Examines the type of a deleted variable
        elif op == "typeof":
            self.test_value = random.randint(_constants.min, _constants.max)
            self.expected_value = "'undefined'"
            false_values = []
            false_values.append("'string'")
            false_values.append("'number'")
            false_values.append("'object'")
            # Count parameter is not used here
            self.create_test_case_string(op,
                                         false_values,
                                         self._InnerValues.unique_type_of_testtype,
                                         0)

    # Creates test- and expected value
    def specify_test_and_expected_value(self, op, random_test_case_type, count):
        # For The operators except these three operators the base of the test value
        # is a random integer between _constants.min and -max
        if op not in self._InnerValues.logical_and_bitwise_not + ["delete"]:
            self.test_value = random.randint(_constants.min, _constants.max)
            # If the operator is unary plus or unary negation, the test value is
            # tested with hexadecimal form too
            if op in self._InnerValues.unary_plus_and_negation:
                self.expected_value = self.test_value
                if random_test_case_type % self._InnerValues.test_case_type_count:
                    self.test_value = "'%s'" %(str(hex(self.test_value)))
                    # negative hexadecimal numbers cannot be converted, so the test case
                    # check it's type instead
                    if self.expected_value < 0:
                        self.expected_value = "'number'"
                else:
                    self.test_value = ("'%s'" %(str(self.test_value)))
            elif op == "++":
                self.expected_value = self.test_value + count
            elif op == "--":
                self.expected_value = self.test_value - count
            # The test- and expected value depends from testtype here
            elif op == "typeof":
                testtype = random_test_case_type % self._InnerValues.test_case_type_count_typeof
                if not testtype:
                    self.test_value = "'%s'" % (self.test_value)
                    self.expected_value = "'string'"
                elif testtype == 1:
                    self.test_value = "{x:%d, y:%d }" % (self.test_value,
                                                         random.randint(_constants.min,
                                                         _constants.max))
                    self.expected_value = "'object'"
                else:
                    self.expected_value = "'number'"
            # At void operator the test value is a function and the xpected value is undefined.
            # Tested with typeof operator
            elif op == 'void':
                self.expected_value = "'undefined'"
                self.test_value = "function() {\nreturn %d\n}" % (self.test_value)
        # At the ! operator the test- and expected values are from a dictionary
        elif op == "!":
            key, value = random.choice(list(self._InnerValues.logical_not_test_values.items()))
            self.test_value = "Boolean(%s)" % (key)
            self.expected_value = value
            for j in range(count):
                self.expected_value = eval("not %s" % (self.expected_value))
        # At the ~ operator the test value is between _constants.bitmin and -bitmax
        elif op == "~":
            self.test_value = random.randint(_constants.bitmin, _constants.bitmax)
            self.expected_value = self.test_value
            for j in range(count):
                self.expected_value = ~self.expected_value
        # At delete operator the expected value is true, and has two testtypes:
        # delete array element or delete a variable
        elif op == "delete":
            self.expected_value = "true"
            if random_test_case_type % self._InnerValues.test_case_type_count:
                self.test_value = []
                for j in range(count):
                    self.test_value.append(random.randint(_constants.min, _constants.max))
                self.test_value = str(self.test_value)
            else:
                self.test_value = random.randint(_constants.min, _constants.max)

    # Creates false values
    def specify_false_values(self, op, random_test_case_type):
        false_values = []
        # For these operators the false values are random integers between _constants.min and -max
        if op in (self._InnerValues.unary_plus_and_negation +
                  self._InnerValues.increment_and_decrement):
            if isinstance(self.expected_value, str):
                false_values.append("'string'")
                false_values.append("'object'")
                false_values.append("'undefined'")
            else:
                false_values = self.generate_false_numbers(self.expected_value,
                    self._InnerValues.false_values_count,
                    self._InnerValues.min_max)
                if op == "-":
                    false_values.append(self.expected_value)
                    self.expected_value = -self.expected_value
        else:
            if op == "!":
            # For Logical not operator the false value is not expected value
                false_values.append(str(not self.expected_value).lower())
                self.expected_value = str(self.expected_value).lower()
            elif op == "~":
            # For bitwise not operator the false value is ~expected value
                false_values.append(~self.expected_value)
            elif op == "typeof":
            # For typeof operator the false values depends on testtype
                testtype = random_test_case_type % self._InnerValues.test_case_type_count_typeof
                false_values.append("'undefined'")
                if not testtype:
                    false_values.append("'number'")
                    false_values.append("'object'")
                elif testtype == 1:
                    false_values.append("'string'")
                    false_values.append("'number'")
                else:
                    false_values.append("'string'")
                    false_values.append("'object'")
            elif op == "delete":
            # At delete operator we examine if delete was succesful
                false_values.append("'false'")
            elif op == "void":
            # At void operator the test function returns with number,
            # and we examine it's type, so the false value is 'number'
                false_values.append("'number'")
        return false_values

    # Creates the string of the test case
    def create_test_case_string(self, op, false_values, random_test_case_type, count):
        self.test_case = self.concat_list_elements(
                              # creates the declaration of test value
                              [self.create_declarations_string(
                                    self.create_declarations_dict(self.test_value,
                                                                  self.TEST_VALUE_VAR_NAME)),
                               # creates the declaration of expected value
                               self.create_declarations_string(
                                    self.create_declarations_dict(self.expected_value,
                                                                  self.EXPECTED_VAR_NAME)),
                               # creates the declaration of false_values
                               self.create_declarations_string(
                                    self.create_declarations_dict(false_values,
                                                                  self.FALSE_RESULT_VAR_NAME)),
                               # Add the operation to the test case
                               self.create_operation(op, count, random_test_case_type),
                               # Add the function_call to the test case
                               self.create_function_call(self.TEST_VALUE_VAR_NAME.format(NUMBER = ""),
                                                         self.EXPECTED_VAR_NAME.format(NUMBER = ""),
                                                         self.create_false_numbers_array_string(len(false_values)),
                                                         validate.validate_numeric_header),
                                                    "\n\n"])
        self.append_test_case() # Appends the test case to file_output

    def generate(self, options): # Generate tests for unary operators
        random.seed(options.seed)
        self.debug("%s\n" % (Messages.generating), options)
        for op in options.test_cases:
            self.add_unique_test_cases(op)
            for i in range(options.test_count):
                count = random.randint(1, options.operand_count)
                random_test_case_type = random.randint(_constants.min, _constants.max)
                self.specify_test_and_expected_value(op, random_test_case_type, count)
                false_values = self.specify_false_values(op, random_test_case_type)
                self.create_test_case_string(op, false_values, random_test_case_type, count)
        write_file(self.configure_settings(options), self.file_output)
        self.debug("%s" % (Messages.done), options)

TestGenerator = Unary_Operator_Generator()
TestGenerator.generate(parse_args(Unary_Operator_Generator._InnerValues.unary_operators))
