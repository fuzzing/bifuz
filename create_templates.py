#!/usr/bin/env python

# Module for generating all possible raw templates
#
# Copyright (C) 2015 Intel Corporation
# Author: Andreea Brindusa Proca <andreea.brindusa.proca@intel.com>
# Author: Razvan-Costin Ionescu <razvan.ionescu@intel.com>
#
# Licensed under the MIT license, see COPYING.MIT for details

import os

'''
Sample of a raw template 

#Do not add lines to this template; possible options for each item: fuzz, nofuzz; if nofuzz, then a list is expected
action 
category 
data_uri 
e_key 
e_val 
flag
'''

current_path = os.getcwd()
path_to_templates = current_path+"/templates"

with open(path_to_templates+"/raw.tem", 'r') as f:
	raw = f.readlines()
	
#there are 6 possible parameters, so 2^6 = 64 possible templates
for nr in range(64):
	index = bin(nr)[2:].zfill(6)
	if index[0]=="0":
		a_status = "nofuzz"
	else:
		a_status = "fuzz"
	if index[1]=="0":
		c_status = "nofuzz"
	else:
		c_status = "fuzz"
	if index[2]=="0":
		duri_status = "nofuzz"
	else:
		duri_status = "fuzz"
	if index[3]=="0":
		ek_status = "nofuzz"
	else:
		ek_status = "fuzz"
	if index[4]=="0":
		ev_status = "nofuzz"
	else:
		ev_status = "fuzz"
		
	if index[5]=="0":
		flag_status = "nofuzz"
	else:
		flag_status = "fuzz"
	
	with open(path_to_templates+"/tem_%s.tem"%index,'w') as t:
		t.write(raw[0])
		t.write(raw[1].replace("action", "action "+a_status))
		t.write(raw[2].replace("category", "category "+c_status))
		t.write(raw[3].replace("data_uri", "data_uri "+duri_status))
		t.write(raw[4].replace("e_key", "e_key "+ek_status))
		t.write(raw[5].replace("e_val", "e_val "+ev_status))
		t.write(raw[6].replace("flag", "flag "+flag_status))

print "All raw templates have been generated"


#session0 folder contains the tem_111111.tem file - with 0 0s in its name
#session1 folder contains the tem_011111.tem, tem_101111.tem, tem_110111.tem and so on up to tem_111110.tem file - with 1 0s in its name
#...
#session6 folder contains the tem_000000.tem - with 6 0s in its name

ok=True
for session in range(7):
	if os.path.isdir("session_%s"%(str(session))):
		print "Folder session_%s was already created. Please remove it first"%(str(session))
		ok=False
		break
	os.mkdir("session_%s"%(str(session)))
	for i in range(64):
		#myStr will keep the index of the file converted in binary: e.g. 000000
		myStr = str(bin(i)[2:].zfill(6))
		if myStr.count("0") == session:
			os.system("cp templates/tem_%s.tem session_%s"%(myStr,session))
if ok:
	print("All testing session folders have been created")
