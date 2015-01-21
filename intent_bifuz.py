#!/usr/bin/env python

# Intent bifuz.
#
# Copyright (C) 2015 Intel Corporation
# Author: Andreea Brindusa Proca <andreea.brindusa.proca@intel.com>
# Author: Razvan-Costin Ionescu <razvan.ionescu@intel.com>
#
# Licensed under the MIT license, see COPYING.MIT for details

import os, sys
import re
import pprint
import random, string
import multiprocessing
from common import *


#list with domains used to generate random URIs
domains=[".com",".org",".net",".int",".gov",".mil"]
def generate_random_uri():
    return random.choice(["http","https"])+"://"+str(string_generator(random.randint(10,100)))+random.choice(domains)


def string_generator(size=8, chars=string.ascii_uppercase + string.digits):
      return ''.join(random.choice(chars) for _ in range(size))

