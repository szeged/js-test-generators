#!/usr/bin/env python
import sys
import os
import settings
import random
path = os.path.join(settings.TEMPLATE_DIR)
sys.path.append(path)
import validate
from generator_base import Generator
from constants import _constants
from parse_args import parse_args
from utils import write_file
from utils import Messages

class Function_Call_Generator(Generator):

    class _InnerValues():
        # The name of the variable at the file header with test_function_value
        test_function_variable_name = 'a'
        # The name of the variable at the file header with test_function2_value
        test_function2_variable_name = 'b'
        # Counts how many times the test_function2 called
        recursive_counter = '''c{NUMBER}'''
        # The file name of the generated tests
        generated_filename = '''function-call-{NUMBER}.js'''
        # The number of false values generated for each tests
        false_values_count = 5
        # Minimum arguments
        args_min = 0
        # Maximum arguments
        args_max = 255
        # The number of test cases before new file begins
        test_case_in_a_file = 70
        # The min value of arguments
        argument_min_value = -10000
        # The max value of arguments
        argument_max_value = 10000
        # The following lists are sublists of possible test cases
        args_and_bind = ['args', 'bind']
        call_and_apply = ['call', 'apply']
        # The possible test cases
        test_cases = args_and_bind + call_and_apply + ['recursive']

    def concat_list_elements(self, list):
        return ''.join(map(str, list))

    # Creates the header of the generated files
    def create_file_header(self):
        return self.concat_list_elements([validate.validate_numeric,
                                         validate.test_function,
                                         validate.test_function2,
                                         '\nvar %s = test_function;\n' % (
                                             self._InnerValues.test_function_variable_name),
                                         '\nvar %s = test_function2;\n' % (
                                             self._InnerValues.test_function2_variable_name)])

    # Appends test_case to file output
    def append_test_case(self):
        self.file_output.append(self.test_case)
        self.test_case = ''

    # Adjust file_write_settings based on options
    def configure_settings(self, options):
        return settings.file_write_settings(self._InnerValues.generated_filename,
                                            options.output,
                                            self.create_file_header(),
                                            self._InnerValues.test_case_in_a_file)

    # Creates test's- and expected value's string
    def specify_test_and_expected_value(self, op):
        # specify the number of arguments here
        if op not in self._InnerValues.args_and_bind:
            number_of_args = random.randint(self._InnerValues.args_min,
                                            self._InnerValues.args_max - 1)
        else:
            number_of_args = random.randint(self._InnerValues.args_min,
                                            self._InnerValues.args_max)

        if op != 'recursive':
            self.expected_value = 'true'
            # Writes 1 as argument for number_of_args times
            self.test_value = ''
            for j in range(number_of_args):
                self.test_value += '%d' % (
                    random.randint(self._InnerValues.argument_min_value,
                                   self._InnerValues.argument_max_value))
                if j != number_of_args - 1:
                    self.test_value += ', '
            # Creates the string of the function call
            if op in self._InnerValues.args_and_bind:
                self.test_value = '(%s)' % (self.test_value)
            elif op == 'apply':
                self.test_value = '[%s]' % (self.test_value)

            if op in self._InnerValues.call_and_apply + ['bind']:
                if op in self._InnerValues.call_and_apply:
                    if self.test_value != '':
                        self.test_value = '(this, %s)' % (self.test_value)
                    else:
                        self.test_value = '(this)'
                else:
                    self.test_value = '(this)%s' % (self.test_value)
                self.test_value = '.%s%s' % (op, self.test_value)
            if random.randint(0, 1):
                self.test_value = 'test_function%s' % (self.test_value)
            else:
                self.test_value = '%s%s' % (
                    self._InnerValues.test_function_variable_name,
                    self.test_value)

            if random.randint(0, 1):
                self.test_value = "eval('%s')" % (self.test_value)
        else:
            # The value of the recursive_counter variable is checked here,
            # because the test_function2 increments it
            self.expected_value = number_of_args
            # Calls the function for number_of_args times
            self.test_value = number_of_args * '()'

            if random.randint(0, 1):
                self.test_value = 'test_function2%s;' % (self.test_value)
            else:
                self.test_value = '%s%s' % (
                    self._InnerValues.test_function2_variable_name,
                    self.test_value)

            if random.randint(0, 1):
                self.test_value = "eval('%s');" % (self.test_value)
            self.test_value = '%s%s\n' % (
                self.create_declarations_string(
                    self.create_declarations_dict(
                        0,
                        self._InnerValues.recursive_counter)),
                self.test_value)

    # Creates false values
    def specify_false_values(self, op):
        false_values = []
        if op != 'recursive':
            false_values.append('false')
        else:
            for i in range(self._InnerValues.false_values_count):
                value = random.randint(_constants.min, _constants.max)
                if value != self.expected_value:
                    false_values.append(value)
        return false_values

    # Creates the string of the test case
    def create_test_case_string(self, op):
        list = []
        if op == 'recursive':
            list.append(self.test_value)
            self.test_value = self._InnerValues.recursive_counter.format(NUMBER = '')
        false_values = self.specify_false_values(op)
        list.append(self.create_declarations_string(
                        self.create_declarations_dict(false_values,
                                                      self.FALSE_RESULT_VAR_NAME)))
        list.append(self.create_function_call(self.test_value,
                    self.expected_value,
                    self.create_false_numbers_array_string(len(false_values)),
                    validate.validate_numeric_header))
        self.test_case = self.concat_list_elements(list + ['\n\n'])
        self.append_test_case()

    # Generate tests for function call
    def generate(self, options):
        random.seed(options.seed)
        self.debug(Messages.GENERATING, options)
        for op in options.test_cases:
            for i in range(options.test_count):
                self.specify_test_and_expected_value(op)
                self.create_test_case_string(op)
        write_file(self.configure_settings(options), self.file_output)
        self.debug(Messages.DONE, options)

Test_Generator = Function_Call_Generator()
Test_Generator.generate(parse_args(Function_Call_Generator._InnerValues.test_cases))
