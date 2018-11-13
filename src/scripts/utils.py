#!/usr/bin/env python
import os
from constants import _constants
from colors import _bcolors

def write_file(settings, content):
    file_count = 1
    output_dir = os.path.abspath(settings.output_dir)
    test_case_count = 0
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    while test_case_count != len(content):
        filename = settings.generated_filename.format(NUMBER = file_count)
        file_to_open = os.path.join(output_dir, filename)
        with open(file_to_open, "w") as file:
            file.write("%s\n" % (settings.file_header))
            for i in range(test_case_count, len(content)):
                file.write("%s" % (content[i]))
                test_case_count += 1
                if not test_case_count % settings.test_cases_in_a_file:
                    break
        file_count += 1

def unsigned32(signed):
    return signed % 0x100000000

class Messages:
    generating = "%sGenerating tests%s" % (_bcolors.okblue, _bcolors.endc)
    done = "%sDone%s" %(_bcolors.okblue, _bcolors.endc)
