#!/usr/bin/env python

# Common methods for intent and broadcast.
#
# Copyright (C) 2015 Intel Corporation
# Author: Andreea Brindusa Proca <andreea.brindusa.proca@intel.com>
# Author: Razvan-Costin Ionescu <razvan.ionescu@intel.com>
#
# Licensed under the MIT license, see COPYING.MIT for details

import os
import sys
import re
from commands import *
from datetime import datetime
from threading import Thread


def get_devices_list():
    #returns the list of all DUTs connected
    devices = getoutput("adb devices").split("\n")
    devices_list = []
    index = [i for i in range(len(devices)) if 'List' in devices[i]]
    if len(index) == 0:
        return False

    #devices are found using adb devices command
    #and they can be identified either by IP, or by their serial number
    for ips in devices[index[0] + 1:-1]:
        devices_list.append(ips.split("\t")[0].split(":")[0])

    if not devices_list:
        return False

    return devices_list


def set_logdir(ip, fuzz_type):
    current_dir = os.getcwd()
    new_folder = raw_input('\nDevice ' + ip + \
       ': Insert the name of the logs folder: ')
    if not new_folder:
        time = datetime.now().strftime('%m%d_%H-%M')
        if not os.path.isdir(current_dir + "/LOGS_" + ip + "_" + time + \
            "_" + fuzz_type):
            os.mkdir(current_dir + "/LOGS_" + ip + "_" + time + \
               "_" + fuzz_type)
        new_folder = current_dir + "/LOGS_" + ip + "_" + time + \
           "_" + fuzz_type
    elif(new_folder and not os.path.isdir(new_folder)):
        os.mkdir(new_folder)

    return new_folder


def get_package_list(ip, log_dir, selected_packages):
    lines = []
    if selected_packages == 'all':
        run_inadb(ip, "shell pm list packages > " + log_dir + \
           "/list_packages.txt")
        output = run_inadb(ip, "shell pm list packages")
        if output is not None:
            lines.extend(output.split('\r\n'))
            lines[-1] = lines[-1].replace('\r', '')
    else:
        partial_pks = re.split(r'[, ]+', selected_packages)
        for pkg in partial_pks:
            output = run_inadb(ip, 'shell pm list packages | grep ' + pkg)
            run_inadb(ip, 'shell pm list packages | grep ' + pkg + " >> " +\
               log_dir + '/list_packages.txt')
            if output is not None:
                lines.extend(output.split('\r\n'))
                lines[-1] = lines[-1].replace('\r', '')
    lines = [x for x in lines if x]
    print lines
    return lines


def log_in_logcat(ip, log):
    if "." in ip:
        log_command = "adb -s %s:5555 shell log -p f -t %s" % (ip, str(log))
    else:
        log_command = "adb -s %s shell log -p f -t %s" % (ip, str(log))
    resp_l = getoutput(log_command)
    return resp_l


def save_logcat(ip):
    logcat_cmd = "adb -s %s logcat -v time *:F > logcat_%s" % (ip, ip)
    os.system(logcat_cmd)


def run_inadb(ip, command):
    if not verify_availability(ip):
        return "Unavailable device."

    if ("." in ip):
        output = getoutput('adb -s %s:5555 %s' % (ip, command))
    else:
        output = getoutput('adb -s %s %s' % (ip, command))
    return output


def verify_availability(ip):
    if ("." in ip):
        output = getoutput('adb -s %s:5555 get-state' % (ip))
    else:
        output = getoutput('adb -s %s get-state' % (ip))
    if 'unknown' in output:
        return False
    else:
        return True

'''
def parse_session_logs(session):
    files = filter(os.path.isfile, os.listdir(session))
    files = [f for f in files if f.startswith('e_')]
    intents = []
    for f in files:
        with open(f, 'r') as error_file:
            for line in error_file:
                if line.startswith('F/BIFUZ_'):
                    intents.append(line)
                    break
    return intents
'''


def parse_session_logs(session):
    files = [session + '/' + f for f in os.listdir(session) \
       if f.startswith('e_')]
    intents = []
    for f in files:
    #if logcat -c is not working, you will find the crashy intent
    #at the end of the error file; that is why reversed is used
        for line in reversed(open(f).readlines()):
            if line.startswith('F/BIFUZ_'):
                intents.append(line)
                break
    return intents


def trim_session(session_one, session_two):
    sessions = [session_one, session_two]
    for s in range(len(sessions)):
        if sessions[s][-1] == '/':
            sessions[s] = sessions[s][:-1]
        sessions[s] = sessions[s][sessions[s].rfind('/') + 1:]
    return sessions


def delta_reports(session_one, session_two):
    if not os.path.isdir(session_one) or not os.path.isdir(session_two):
        print "Verify if both fuzzing session exist."
        return False
    else:
        intents_s1 = parse_session_logs(session_one)
        intents_s2 = parse_session_logs(session_two)

    if not intents_s1 and not intents_s2:
        print "None of this sessions have crashed intents. Stop!"
        return True

    if session_one[-1] == '/':
        session_one = session_one[:-1]
    root_path = session_one[:session_one.rfind('/') + 1]

    sessions_name = trim_session(session_one, session_two)
    deltafile = root_path + "delta__" + sessions_name[0] +\
        "__to__" + sessions_name[1]

    with open(deltafile, 'w') as f:
        f.write("Intents that crashed for session one: %s \n" % session_one)
        f.write("\n".join(intents_s1))

        f.write("\nIntents that crashed for session two: %s \n" % session_two)
        f.write("\n".join(intents_s2))
    print "The delta report is stored here: %s" % deltafile
    return True


def reproducibility(intents_f, partial_name, crashed_intent):
    root_index = intents_f.rfind('/all_')
    root_path = intents_f[:root_index + 1]
    all_crashes = []
    before_crash_f = open(root_path + partial_name + ".sh", 'w')
    intents_file = open(intents_f, 'r')
    for line in intents_file:
        before_crash_f.write(line)
        if line.strip() in crashed_intent.strip():
            break
    before_crash_f.close()
    intents_file.close()
    return True
