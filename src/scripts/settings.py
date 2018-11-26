#!/usr/bin/env python
from os import path

SCRIPTS_DIR = path.dirname(path.abspath(__file__))
TEMPLATE_DIR = path.normpath(path.join(SCRIPTS_DIR, 'templates'))
PROJECT_DIR = path.normpath(path.join(SCRIPTS_DIR, '..', '..'))
NUMBER_DIR = path.normpath(path.join(PROJECT_DIR, 'src', 'number'))

class file_write_settings():
    def __init__(self, generated_filename, output_dir, file_header, test_cases_in_a_file):
        self.generated_filename = generated_filename # The template of the generated filename
        self.output_dir = output_dir # The output directory
        self.file_header = file_header # The header of the test files
        self.test_cases_in_a_file = test_cases_in_a_file # The number of test cases for each file
