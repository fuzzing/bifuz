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


def set_logdir(ip, fuzz_type):
    current_dir = os.getcwd()
    new_folder=raw_input('\nDevice ' + ip + ': Insert the name of the logs folder: ')
    if not new_folder:
        time = datetime.now().strftime('%m%d_%H-%M')
        if not os.path.isdir(current_dir +  "/LOGS_" + ip + "_" + time + "_" + fuzz_type):
            os.mkdir(current_dir +  "/LOGS_" + ip + "_" + time + "_" + fuzz_type)
        new_folder = current_dir +  "/LOGS_" + ip + "_" + time  + "_" + fuzz_type
    elif(new_folder and not os.path.isdir(new_folder)):
        os.mkdir(new_folder)

    return new_folder


def get_package_list(ip, log_dir, selected_packages):
    lines = []
    if selected_packages == 'all':
        run_inadb(ip, "shell pm list packages > " + log_dir + "/list_packages.txt")
        output = run_inadb(ip, "shell pm list packages")
        if output is not None:
            lines.extend(output.split('\r\n'))
            lines[-1] = lines[-1].replace('\r', '')
    else:
        partial_pks = re.split(r'[,. ]+', selected_packages)
        for pkg in partial_pks:
            output = run_inadb(ip, 'shell pm list packages | grep ' + pkg)
            run_inadb(ip, 'shell pm list packages | grep ' + pkg + " >> " +  log_dir + '/list_packages.txt')
            if output is not None:
                lines.extend(output.split('\r\n'))
                lines[-1] = lines[-1].replace('\r', '')
    lines = [x for x in lines if x]
    print lines
    return lines


def log_in_logcat(ip, log):
    if "." in ip:
        log_command="adb -s %s:5555 shell log -p f -t %s"%(ip, str(log))
    else:
        log_command="adb -s %s shell log -p f -t %s"%(ip, str(log))
    os.system(log_command)


def save_logcat(ip):
    logcat_cmd = "adb -s %s logcat -v time *:F > logcat_%s"%(ip, ip)
    os.system(logcat_cmd)


def run_inadb(ip, command):
    if not verify_availability(ip):
        return "Unavailable device."
    if ("." in ip):
        output = getoutput('adb -s %s:5555 %s'%(ip, command))
    else:
        output = getoutput('adb -s %s %s'%(ip, command))
    return output


def verify_availability(ip):
    if ("." in ip):
        output = getoutput('adb -s %s:5555 get-state'%(ip))
    else:
        output = getoutput('adb -s %s get-state'%(ip))
    if 'unknown' in output:
        return False
    else:
        return True


def create_thrs(func_name, devices_list):
    threadlist=[]
    for h in devices_list:
        log_dir = set_logdir(h)
        t=Thread(target=func_name, args=(h, log_dir,))
        t.start()
        threadlist.append(t)

    for b in threadlist:
        b.join()
