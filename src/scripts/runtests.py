#!/usr/bin/env python
import sys
import os
import argparse
import subprocess
import re
import glob
import settings
from colors import _bcolors

def convert_if_int(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ convert_if_int(c) for c in re.split('(\d+)', text) ]

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-q", help = "only shows the final stats", action='store_true')
    parser.add_argument("--test-folder", help = "the folder of the tests to run", default = settings.NUMBER_DIR)
    parser.add_argument("--engine-location", help = "the location of javascript engine", required = True, default = "")

    if len(sys.argv) <= 1:
        parser.print_help()
        sys.exit(1)

    script_args = parser.parse_args()

    return script_args

def debug(message, options):
    if (not options.q):
      print(message)

def run_tests(options):
    test_count = 0 # The count of tests run
    fail_count = 0 # The count of failed tests
    pass_count = 0 # The count of passed tests
    os.chdir(options.test_folder)
    test_files = glob.glob("*.js") # Files to test

    if (not test_files):
        sys.exit(10)

    test_files.sort(key = natural_keys)

    debug("%s\nTest\t\t\tExit code\n%s" % (_bcolors.okblue, _bcolors.endc), options)

    for filename in test_files:
        test_file = os.path.join(options.test_folder, filename)
        p = subprocess.Popen([options.engine_location, test_file], stderr = open(os.devnull, 'w'))
        p.communicate()
        test_count += 1
        if (not p.returncode):
            color = _bcolors.okgreen
            pass_count += 1
        else:
            color = _bcolors.fail
            fail_count += 1
        debug("%s%s   \t%d%s" % (color , filename, p.returncode, _bcolors.endc), options)


    pass_percentage = (pass_count * 100.0) / test_count
    fail_percentage = (fail_count * 100.0) / test_count

    print("\n%sPASS:\t%d\t%f %%%s" % (_bcolors.okgreen, pass_count, pass_percentage, _bcolors.endc))
    print("%sFAIL:\t%d\t%f %%%s" % (_bcolors.fail, fail_count, fail_percentage, _bcolors.endc))

run_tests(get_arguments())
