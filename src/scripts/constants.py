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

class _constants:
    default_test_count = 100    # The default value of --test-count option
    default_seed = 10000        # The default value of random seed
    test_case_in_a_file = 700   # Maximum number of test for each file
    operand_count_max = 11      # The --operand-count option's maximum value
    operand_count_min = 2       # The --operand-count option's minimum value
    max = (1 << 53) - 1         # The max value of random number (See also Number.MAX_SAFE_INTEGER)
    min = - 1 * max             # The min value of random number (See also Number.MIN_SAFE_INTEGER)
    bitmax = (1 << 31) - 1      # The max value of random number for bitwise operations
    bitmin = - bitmax - 1       # The min value of random number for bitwise operations
    uint32max = (1 << 32) - 1   # The max value of random number for unsigned right shift (See also unsigned int 32)
    uint32min = 0               # The min value of random number for unsigned right shift (See also unsigned int 32)
    bitmax_exposant = 31        # Maximum number for safely shifting an integer in python to
                                # be precise for JS 32 bit numbers
