#!/usr/bin/env python

# Common methods for intent and broadcast.
#
# Copyright (C) 2015 Intel Corporation
# Author: Andreea Brindusa Proca <andreea.brindusa.proca@intel.com>
# Author: Razvan-Costin Ionescu <razvan.ionescu@intel.com>
# Author: Bogdan Alexandru Ungureanu <bogdanx.a.ungureanu@intel.com>
#
# Licensed under the MIT license, see COPYING.MIT for details

import os
import sys
import re
from commands import *
from datetime import datetime
from threading import Thread
import random
from intent_bifuz import *
import ast
import itertools


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


def string_generator(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def set_logdir(ip, fuzz_type):
    '''
    Create the log directory: serial no of the device, timestamp , intents type.
    Returns the generated name.
    '''

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
    '''
    Get the list of the packages selected by the user.
    '''

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


def get_root_path(intents_file):
    '''
    Get the root path of the intent file.
    Used for running intents from the seed files.
    '''

    if intents_file[-1] == '/':
        intents_file = intents_file[:-1]
    intents_file = intents_file[:intents_file.rfind('/')]
    return intents_file


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
    '''
    Verify the type of the device, send the command and get output.
    '''

    if not verify_availability(ip):
        return "Unavailable device."

    if ("." in ip):
        output = getoutput('adb -s %s:5555 %s' % (ip, command))
    else:
        output = getoutput('adb -s %s %s' % (ip, command))
    return output


def verify_availability(ip):
    '''
    Verify if a device is still available.
    '''

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
    '''
    For every error file collect the line that generated the error.
    Returns a list of crashing intents.
    '''

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
    '''
    Trim the session log directory.
    Used when generating the delta report between 2 running sessions.
    '''

    sessions = [session_one, session_two]
    for s in range(len(sessions)):
        if sessions[s][-1] == '/':
            sessions[s] = sessions[s][:-1]
        sessions[s] = sessions[s][sessions[s].rfind('/') + 1:]
    return sessions


def delta_reports(session_one, session_two):
    '''
    Analyse both sessions and save in a file the unique errors.
    '''

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
    '''
    Save all the intents up to the crashing intent in a seed file.
    '''

    root_path_reproducibility = get_root_path(intents_f)
    root_index = intents_f.rfind('/all_')
    root_path = intents_f[:root_index + 1]
    all_crashes = []
    before_crash_f = open(root_path_reproducibility + "/" + partial_name + ".sh", 'w')
    intents_file = open(intents_f, 'r')
    for line in intents_file:
        before_crash_f.write(line)
        if line.strip() in crashed_intent.strip():
            break
    before_crash_f.close()
    intents_file.close()
    return True


def get_apks_list(ip, apk_names):
    '''
    Get all the apks from the DUT or only the ones selected by the user
    '''

    output = run_inadb(ip, 'shell ls /system/app')
    #output = run_inadb(ip, 'shell ls /system/app')
    apps_list = output.split("\r\n")
    for apk_name in apk_names:
        match_apps = [app for app in apps_list if apk_name.lower in app.lower]


def get_apks(ip, package_name):
    '''
    Get the apk of the application from the device.
    Decode the apk using apktool.
    Get the uris found in the application.
    '''
    # get_apks_list(ip[0])
    command_resp = run_inadb(ip[0], "pull " + "/system/app/" + package_name + ".apk .")
    print command_resp
    if command_resp.startswith("Unavailable device"):
        print command_resp
        return False
    outp_c = getoutput("apktool decode " + package_name + ".apk")
    if not outp_c.startswith('I:'):
        print outp_c
        return False

    provider_uris = []
    provider_content = getoutput("grep -r 'content://' " + package_name)
    provider_content = provider_content.split('\n')
    for line in provider_content:
        pattern = re.search("(content\:\/\/.*)\"", line)
        try:
            uri = pattern.group(1)
            provider_uris.append(uri)
        except:
            continue
    #print list(set(provider_uris))
    return list(set(provider_uris))

def buffer_overflow(ip):
	print "BUFFER OVERFLOW ATTEMPT against BLUETOOTH"
	#function for generating intents of random sizes; it needs adb root access on the device (for the moment)
	rand_int_f = random.randint(-2147483648,2147483647) #flag might be an integer between -2147483648 and 2147483647
	rand_size_a = random.randint(1,131071)
	rand_size_c = random.randint(1,131071)
	rand_size_d = random.randint(1,131071)
	rand_size_ek = random.randint(1,131071)
	rand_size_ev = random.randint(1,131071)
	os.system("touch buffer.sh")

	#packages
	#com.mwr.example.sieve/.MainLoginActivity
	#com.google.android.calendar/com.android.calendar.AllInOneActivity 
	#com.android.bluetooth/.opp.BluetoothOppLauncherActivity
	fileName = "buffer"
	#hardcoded package activity
	pack_act = "com.android.bluetooth/.opp.BluetoothOppLauncherActivity"
	
	with open(fileName,"w") as f:
		f.write("am start -n "+pack_act+" -f "+ str(rand_int_f)+ \
		" -a "+string_generator(rand_size_a)+" -c "+string_generator(rand_size_c)+" -d "+string_generator(rand_size_d) + \
		" -e "+string_generator(rand_size_ek)+" "+string_generator(rand_size_ev))
		#f.write("am start -n com.google.android.calendar/com.android.calendar.AllInOneActivity -a "+string_generator(rand_size_a))
		
	os.system("chmod 777 "+fileName)
	os.system("adb -s %s push "% (ip)+" "+fileName+" /data/data/")
	os.system("adb -s %s shell sh /data/data/buffer"%(ip))

	print str(rand_int_f) + " rand_int_f"
	print str(rand_size_a) + " rand_size_a"
	print str(rand_size_c) + " rand_size_c"
	print str(rand_size_d) + " rand_size_d"
	print str(rand_size_ek) + " rand_size_ek"
	print str(rand_size_ev) + " rand_size_ev"

def parse_string_for_lists(string_input,ip):
    '''
    Function for parsing the template's lines and looking for lists received as parameters
    '''
    output=[]
    if "[" not in string_input:
		#if there is no list in the template
        output.append(string_input)
    else:
		#if there are lists specified within the template
        list_pattern = '\[[^\]]*\]'
        list_strings = re.findall(list_pattern, string_input)
        i = 0
        arg_lists_maping = {}
        string_template = string_input
        arg_lists = []
        for list in list_strings:
            key = '$' + str(i) + '$'
            i += 1
            string_template = string_template.replace(list, key)
            arg_lists_maping[key] = ast.literal_eval(list)
            arg_lists.append(ast.literal_eval(list))
        for element in itertools.product(*arg_lists):
            i = 0
            gen_string = string_template
            for arg in element:
                key = '$' + str(i) + '$'
                i += 1
                gen_string = gen_string.replace(key, arg)
            #print gen_string
            output.append(gen_string)
    return output

def fill_default_values(parameter):
    '''
    Get the standard categories, extra_keys, extra_types,
    flags and actions.
    '''
    global activity_actions
    global categories
    global extra_keys
    global extra_types
    global flags
    
    global path_txt
    path_txt = os.getcwd() + "/txts/"
	
    if parameter=="cat":
        with open(path_txt + "categories.txt") as f:
            categories = f.read().splitlines()
        return categories
        
    elif parameter=="ek":
        with open(path_txt + "extra_keys.txt") as f:
            extra_keys = f.read().splitlines()
        return extra_keys
        
    elif parameter=="et":
        with open(path_txt + "extra_types.txt") as f:
            extra_types = f.read().splitlines()
        return extra_types
        
    elif parameter=="flag":
        with open(path_txt + "flags.txt") as f:
            flags = f.read().splitlines()
        for i in range(len(flags)):
            index_fl = flags[i].index(':')
            if index_fl > 0:
                flags[i] = flags[i][index_fl + 1:]
        return flags
        
    elif parameter=="act":
        with open(path_txt + "activity_actions.txt") as f:
            activity_actions = f.read().splitlines()
        return activity_actions
