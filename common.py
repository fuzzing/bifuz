#!/usr/bin/env python

# Common methods for intent and broadcast.
#
# Copyright (C) 2015 Intel Corporation
# Author: Andreea Brindusa Proca <andreea.brindusa.proca@intel.com>
# Author: Razvan-Costin Ionescu <razvan.ionescu@intel.com>
#
# Licensed under the MIT license, see COPYING.MIT for details

import os, sys
import re
from commands import *
from datetime import datetime
from threading import Thread

def get_devices_list():
    #returns the list of all DUTs connected
    devices = getoutput("adb devices").split("\n")
    devices_list = []

    #devices are found using adb devices command and they can be identified either by IP, or by their serial number
    for ips in devices[1:-1]:
        devices_list.append(ips.split("\t")[0].split(":")[0])

    if not devices_list:
        return False

    return devices_list



def log_in_logcat(ip, log):
    if "." in ip:
        log_command="adb -s %s:5555 shell log -p f -t %s"%(ip, str(log))
    else:
        log_command="adb -s %s shell log -p f -t %s"%(ip, str(log))
    os.system(log_command)


def save_logcat(ip):
    logcat_cmd = "adb -s %s logcat -v time *:F > logcat_%s"%(ip, ip)
    os.system(logcat_cmd)

