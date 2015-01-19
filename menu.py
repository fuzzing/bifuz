#!/usr/bin/env python

# Menu of the BIFUZ project.
#
# Copyright (C) 2015 Intel Corporation
# Author: Andreea Brindusa Proca <andreea.brindusa.proca@intel.com>
# Author: Razvan-Costin Ionescu <razvan.ionescu@intel.com>
#
# Licensed under the MIT license, see COPYING.MIT for details

import os
import re
from intent_bifuz import *
from broadcast_bifuz import *


def print_menu():
    os.system("clear")
    k=15
    print("\n");
    print((k-4)*" "+(2*k+2)*"=")
    print(k*" "+"###   #  ####  #  #  ####");
    print(k*" "+"#  #  #  #     #  #    ##");
    print(k*" "+"###   #  ####  #  #   ## ");
    print(k*" "+"#  #  #  #     #  #  #   ");
    print(k*" "+"###   #  #     ####  ####");
    print((k-4)*" "+(2*k+2)*"=")
    print("\n\n");
    print(k/2*" "+"Select one option from below\n")
    print(k/2*" "+"1. Select Devices Under Test")
    print(k/2*" "+"2. Generate Broadcast Intent calls for the DUT(s)")
    print(k/2*" "+"3. Generate Fuzzed Intent calls")
    print(k/2*" "+"4. Generate a delta report between 2 fuzzing sessions")
    print(k/2*" "+"5. (Future) Generate apks for specific Intent calls")
    print(k/2*" "+"Q. Quit")
    print("\n\n");


if __name__ == '__main__':
    print_menu()
    choice = str(raw_input("Insert your choice:    "));
    loop = True
    devices_list = []
    while loop:
        if (choice=="1"):
            print("\nYou have selected option 1. Select Devices Under Test")

            devices_list = get_devices_list()
            if not devices_list:
                print "*ERROR* unavailable devices"
                loop = False
                continue

            for i in range(len(devices_list)):
                print str(i+1) + ". " + devices_list[i]

            duts = str(raw_input("Select the DUT number or type 'all':    "))
            if duts is not 'all':
                duts_list = re.split(r'[,. ]+', duts)
                devices_list = [devices_list[int(x)-1] for x in duts_list if int(x) > 0 and int(x) <= len(devices_list)]

            print_menu()
            if len(devices_list) > 0:
                print ("Selected DUT(s): " + ', '.join(devices_list))
            choice = str(raw_input("Insert your choice:    "))
        elif (choice=="2"):
            if len(devices_list) == 0:
                devices_list = get_devices_list()
                if devices_list is not False:
                    devices_list = [devices_list[0]]

            print("\nGenerate broadcast intent calls for the following DUT(s): " + ', '.join(devices_list if devices_list else 'Stop. Unavailable DUT'))

            if not devices_list:
                loop = False
                continue

            packages = str(raw_input("Insert the packages wanted or type 'all' for all packages:    "))
            if not packages:
                print_menu()
            else:
                generate_broadcast_intent(devices_list, packages.strip())
                loop = False
        elif (choice=="3"):
            if len(devices_list) == 0:
                devices_list = get_devices_list()
                if devices_list is not False:
                    devices_list = [devices_list[0]]

            print("\nGenerate fuzzed intent calls for the following DUT(s): " + ''.join(devices_list[0] if devices_list else 'Stop. Unavailable DUT'))
            if not devices_list:
                loop = False
                continue

            packages = str(raw_input("Insert the packages wanted or type 'all' for all packages:    "))
            if not packages:
                print_menu()
            else:
                generate_fuzzed_intent(devices_list, packages.strip())
                loop = False
        elif (choice=="4"):
            print("\nYou have selected option 4. Generate a delta report between 2 fuzzing sessions")
            loop = False
        elif (choice=="5"):
            print("\nYou have selected option 5. (Future) Generate apks for specific Intent calls")
            loop = False
        elif (str(choice) in ['q','Q']):
            print("\nThank you for using BIFUZ!")
            loop = False
        elif (choice !=""):
            print("\nYour option is invalid. Please type any number between 1 and 5, or Q for Quit")
            choice = str(raw_input("Insert your choice:    "))
