#!/usr/bin/env python

# Intent bifuz.
#
# Copyright (C) 2015 Intel Corporation
# Author: Andreea Brindusa Proca <andreea.brindusa.proca@intel.com>
# Author: Razvan-Costin Ionescu <razvan.ionescu@intel.com>
#
# Licensed under the MIT license, see COPYING.MIT for details

import os
import sys
import re
import pprint
import random
import string
import multiprocessing
from common import *


#list with domains used to generate random URIs
domains = [".com", ".org", ".net", ".int", ".gov", ".mil"]


def generate_random_uri():
    return random.choice(["http", "https"]) + "://" + \
       str(string_generator(random.randint(10, 100))) + random.choice(domains)


def string_generator(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def get_default_values():
    '''
    Get the standard categories, extra_keys, extra_types,
    flags and actions.
    '''

    global categories
    global extra_keys
    global extra_types
    global activity_actions
    global flags

    with open(path_txt + "categories.txt") as f:
        categories = f.read().splitlines()

    with open(path_txt + "extra_keys.txt") as f:
        extra_keys = f.read().splitlines()

    with open(path_txt + "extra_types.txt") as f:
        extra_types = f.read().splitlines()

    with open(path_txt + "flags.txt") as f:
        flags = f.read().splitlines()
    for i in range(len(flags)):
        index_fl = flags[i].index(':')
        if index_fl > 0:
            flags[i] = flags[i][index_fl + 1:]

    with open(path_txt + "activity_actions.txt") as f:
        activity_actions = f.read().splitlines()

    return True


def parse_logcat(ip, log_filename):
    '''
    Parse logcat to collect errors after running an intent.
    In case of errors, call method to generate seed file.
    '''

    root_index = log_filename.rfind('/')
    root_path = log_filename[:root_index]
    created_logfiles = {}
    with open(log_filename, 'r') as logcat:
        error = False
        package_name = ''
        new_name = ''
        for line in logcat:
            if line.startswith('F/BIFUZ'):
                m = re.search("F/BIFUZ_.* -n .*\.(.*)/.*\.(.*) -f", line)
                try:
                    package_name = m.group(1)
                    activity = m.group(2).strip()
                except:
                    pass
            elif "Caused" in line:
                error = True
                m = re.search(".* Caused by\: (.*)\:.*", line)
                try:
                    new_name = m.group(1)
                except:
                    pass

    if not error:
        os.remove(log_filename)
        return True
    if package_name and new_name:
        new_filename = re.sub('\W+', '', new_name)
        new_filename = root_path + "/e_" + activity + "." + new_name
        if new_filename in created_logfiles.keys():
            created_logfiles[new_filename] += 1
        else:
            created_logfiles[new_filename] = 1
        os.rename(log_filename, new_filename + "_" + \
           str(created_logfiles[new_filename]) + ".txt")
    return True


def populate_activity():
    '''
    If empty fields in dumpsys, populate with the standard values.
    '''

    get_default_values()
    for k_pk in activity_map.keys():
        for actv in activity_map[k_pk].keys():
            if len(activity_map[k_pk].get(actv, {})) == 0:
                activity_map[k_pk][actv] = dict([(x, categories) \
                   for x in activity_actions])
            else:
                for intent in activity_map[k_pk][actv].keys():
                    if len(activity_map[k_pk][actv][intent]) == 0:
                        activity_map[k_pk][actv][intent] = categories
    return True


def get_info(data, line):
    '''
    Select a part from dumpsys to collect the needed info.
    Call the method that will parse it.
    '''

    actv_index = data.find("Activity Resolver Table")
    data_actv = data[actv_index:]

    data_actv = data_actv.split("\r\n")
    activity_end = 0

    for i in range(len(data_actv) - 1):
        if data_actv[i] == '' and data_actv[i + 1] == \
           data_actv[i + 1].lstrip():
            activity_end = i
            data_actv = data_actv[:i]
            break

    activity_map[line] = {}

    # get activites
    parse_dumpsys(data_actv, line)
    #pp.pprint(activity_map)

    return True


def parse_dumpsys(data, line):
    '''
    Parse dumpsys and get parameters like: activity, category if found.
    '''

    act_ctg = {}
    part_line = ''
    for i in range(1, len(data)):
        pk_re = re.search("\d+\w+\s(" + line + "\S*)", data[i])
        try:
            part_line = pk_re.group(1).strip()

            part_line = part_line.replace('/.', '.')
            index_sl = part_line.find('/')
            if index_sl != -1:
                part_line = part_line[index_sl + 1:]

            if part_line not in activity_map[line].keys():
                act_ctg = {}
        except:
            act_re = re.search("Action: \"(.*)\".*", data[i])
            try:
                act = act_re.group(1).strip()
                if not act in act_ctg.keys():
                    act_ctg[act] = []
            except:
                catg_re = re.search("Category: \"(.*)\".*", data[i])
                try:
                    catg = catg_re.group(1).strip()
                    if not catg in act_ctg[act]:
                        act_ctg[act].append(catg)
                except:
                    continue

        if part_line in activity_map[line].keys():
            activity_map[line][part_line] = act_ctg
        else:
            activity_map[line].update({part_line: act_ctg})
    populate_activity()
    return True


def collect_info(ip, log_dir, selected_packages):
    '''
    Save the dumpsys of every selected package.
    '''

    lines = get_package_list(ip, log_dir, selected_packages)
    if not lines:
        log_in_logcat(ip, 'BIFUZ_INTENT no valid packages. STOP!')
        sys.exit(1)

    global activity_map
    activity_map = {}

    for line in lines:
        line = line.replace("package:", "")
        cmnd = "shell dumpsys package %s > %s/package_%s.txt"\
           % (line, log_dir, line)
        print cmnd

        run_resp = run_inadb(ip, cmnd)
        if run_resp.startswith('error'):
            continue

        with open(log_dir + "/package_" + line + ".txt", 'r') as outfile:
            data = outfile.read()
            get_info(data, line)
    return create_run_file(ip, log_dir)


def create_run_file(ip, log_dir):
    '''
    Create intents using the collected data.
    '''

    if ("." in ip):
        run_cmnd = 'adb -s %s:5555' % (ip)
    else:
        run_cmnd = 'adb -s %s' % (ip)

    with open(log_dir + '/all_intent_' + ip + '.sh', 'w') as f:
        for k_pkg in activity_map.keys():
            for actv in activity_map[k_pkg].keys():
                for intent in activity_map[k_pkg][actv].keys():
                    for categ in activity_map[k_pkg][actv][intent]:
                        for flag in flags:
                            for extra_type in extra_types:
                                if extra_type == "boolean":
                                    ev = str(random.choice([True, False]))
                                elif extra_type == "string":
                                    ev = string_generator(random.randint(10, \
                                       100))
                                else:
                                    ev = str(random.randint(10, 100))
                                for extra_key in extra_keys:
                                    f.write(run_cmnd + ' shell am start -a ' +\
                                       intent + ' -c ' + categ + ' -n ' + \
                                       k_pkg + '/' + actv + ' -f ' + flag  \
                                       + ' -d ' + generate_random_uri() + \
                                       ' -e ' + extra_type + ' ' + \
                                       extra_key + ' ' + ev + '\n')
    return True


def start_intent_fuzzer(ip, log_dir, generated_intents_file=None):
    '''
    Start running intents.
    Verify if errors are found.
    '''

    if generated_intents_file is None:
        generated_intents_file = log_dir + '/all_intent_' + ip + '.sh'

    if not os.path.isfile(generated_intents_file):
        print "The intent calls were not generated!"
        return False

    with open(generated_intents_file, 'r') as f:
        run_inadb(ip, "logcat -c")
        i = 0
        for line in f:
            # clean logcat
            log_in_logcat(ip, 'BIFUZ_INTENT ' + line.strip())
            os.system(line.strip())

            log_filename = "%s/testfile_%s_%d.txt" % (log_dir, ip, i)
            run_result = run_inadb(ip, 'logcat -d > ' + log_filename)
            if run_result == "Unavailable device.":
                print "Unavailable device: " + ip + ". Stop."
                return False

            resp_parse = parse_logcat(ip, log_filename)
            if not resp_parse:
                print "Device not found: " + ip + ". Stop!"
                return False

            run_inadb(ip, "logcat -c")
            i = i + 1
    res = getoutput("rm " + log_dir + "/package_*")
    return True


def generate_fuzzed_intent(devices_list, selected_packages):
    '''
    Collect data and run on every device the generated intents.
    '''

    global pp
    pp = pprint.PrettyPrinter(indent=4)

    global path_txt
    path_txt = os.getcwd() + "/txts/"

    #devices_list = get_devices_list()
    if not devices_list:
        print "*ERROR* unavailable devices"
        sys.exit(1)

    ip = devices_list[0]

    map_logdirs = {}
    for h in devices_list:
        log_dir = set_logdir(h, "intent")
        map_logdirs[h] = log_dir

    jobs = []
    for h in devices_list:
        log_dir = map_logdirs[h]
        t = multiprocessing.Process(target=collect_info, \
           args=(h, log_dir, selected_packages,))
        t.start()
        jobs.append(t)

    for b in jobs:
        b.join()

    jobs = []
    for h in devices_list:
        log_dir = map_logdirs[h]
        t = multiprocessing.Process(target=start_intent_fuzzer, \
           args=(h, log_dir))
        t.start()
        jobs.append(t)

    for b in jobs:
        b.join()


'''

adb -s <DEVICE ID> shell am start
-a <action - fuzzable>
-c <category - fuzzable>
-n <package>/<activity> -> fixed
-f 0x00400000 -> fixed int -> range: -2147483648 - 2147483647
-d <data-uri> - fuzzable
-e <extra key - fuzzable> <extra value(s) - fuzzable>

'''

def parse_template(templateFile):
    with open(templateFile) as tf:
        lines = tf.readlines()
    
    action_tem = lines[1]
    category_tem = lines[2]
    data_uri_tem = lines[3]
    e_key_tem = lines[4]
    e_val_tem = lines[5]
    if action_tem.strip().split()[1]=="fuzz":
		rand_size_a = random.randint(1,131071) #1, 131071
		action_fuzz = string_generator(rand_size_a)
#		print action_fuzz
    else:
        action_fuzz = action_tem.strip().split()[2]
#       print "Action is not fuzzed"+str(action_tem.split(" "))
        
    if category_tem.strip().split()[1]=="fuzz":
		rand_size_c = random.randint(1,131071) #1, 131071
		category_fuzz = string_generator(rand_size_c)
#		print category_fuzz
    else:
        category_fuzz = category_tem.strip().split()[2]
#       print "Category is not fuzzed"+str(category_tem.split(" "))
        
    if data_uri_tem.strip().split()[1]=="fuzz":
		rand_size_d = random.randint(1,131071) #1, 131071
		data_uri_fuzz = string_generator(rand_size_d)
#		print data_uri_fuzz
    else:
        data_uri_fuzz = data_uri_tem.strip().split()[2]
#       print "Data URI is not fuzzed"+str(data_uri_tem.split(" "))
        
    if e_key_tem.strip().split()[1]=="fuzz":
		rand_size_ek = random.randint(1,131071) #1, 131071
		e_key_fuzz = string_generator(rand_size_ek)
#		print e_key_fuzz
    else:
        e_key_fuzz = e_key_tem.strip().split()[2]
#       print "Extra Key is not fuzzed"+str(e_key_tem.split(" "))
        
    if e_val_tem.strip().split()[1]=="fuzz":
		rand_size_ev = random.randint(1,131071) #1, 131071
		e_val_fuzz = string_generator(rand_size_ev)
#		print e_val_fuzz
    else:
        e_val_fuzz = e_val_tem.strip().split()[2]
#       print "Extra value is not fuzzed"+str(e_val_tem.split(" "))
        
    return str("-a "+action_fuzz+" -c "+category_fuzz+" -d "+data_uri_fuzz+" -e "+e_key_fuzz+" "+e_val_fuzz)
