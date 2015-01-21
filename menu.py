#!/usr/bin/env python
import os

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
	choice = str(raw_input("Insert your choice:    "))
	loop = True
	while loop:
		if (choice=="1"):
			print("You have selected option 1. Select Devices Under Test")
			loop = False
		elif (choice=="2"):
			print("You have selected option 2. Generate Broadcast Intent calls for the DUT(s)")
			loop = False
		elif (choice=="3"):
			print("You have selected option 3. Generate Fuzzed Intent calls")
			loop = False
		elif (choice=="4"):
			print("You have selected option 4. Generate a delta report between 2 fuzzing sessions")
			loop = False
		elif (choice=="5"):
			print("You have selected option 5. (Future) Generate apks for specific Intent calls")
			loop = False
		elif (str(choice) in ['q','Q']):
			print("Thank you for using BIFUZ!")
			loop = False
		elif (choice !=""):
			print("Your option is invalid. Please type any number between 1 and 5, or Q for Quit")
			choice = str(raw_input("Insert your choice:    "))
