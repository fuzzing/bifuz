
import os, sys
import re
import pprint
import shutil
import random, string
from commands import *
from jnius import autoclass
Environment=autoclass("android.os.Environment");
PythonActivity = autoclass('org.renpy.android.PythonActivity')

#list with domains used to generate random URIs
domains=[".com",".org",".net",".int",".gov",".mil"]
def generate_random_uri():
    return random.choice(["http","https"])+"://"+str(string_generator(random.randint(10,100)))+random.choice(domains)


def string_generator(size=8, chars=string.ascii_uppercase + string.digits):
      return ''.join(random.choice(chars) for _ in range(size))


def parse_broadcast_logcat(log_filename):
    path=Environment.getExternalStorageDirectory() + log_filename
    with open(path, 'r') as logcat:
        error = False
        package_name = ''
        new_name = ''
        for line in logcat:
            if line.startswith('BIFUZ'):
                m = re.search("BIFUZ_.* -n (.*)\/.*\.(.*\..*)", line)
                try:
                    package_name = m.group(1)
                    broadcast_to = m.group(2).strip()
                    crashed_intent = line
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
        os.remove(path)
        return True
    if package_name and new_name:
        new_name = re.sub('\W+','',new_name)
        partial_name =  broadcast_to + "." + new_name
        new_filename = root_path + "/e_" +  partial_name + ".txt"
        os.rename(log_filename, new_filename)
        reproducibility(generated_intents_file, partial_name, crashed_intent)
    return True


def seed_entry(log_filename,command,type):
    dir=Environment.getExternalStorageDirectory().toString()
    path=str(dir) + "/test/all_"+ type +"_"+log_filename+ ".sh"
    all_runs_path=str(dir) + "/test/all_"+ type + ".sh"
    if os.path.isdir(str(dir) + "/test/"):
        seedfile=open(path,'a')
        all_runs_seedfile=open(all_runs_path,'a')
    else:
        os.mkdir(str(dir)+"/test/" )
        seedfile=open(path,'a')
        all_runs_seedfile=open(all_runs_path,'a')
    if (os.path.isfile(path)):
        seedfile.write("adb shell " + command + "\n")
        seedfile.close()
        all_runs_seedfile.write("adb shell " + command + "\n")
        all_runs_seedfile.close()
#         shutil.copyfile(path, new_filename)
#         output = getoutput('adb push ' + path + ' /data/local/tmp/test/ ')
           
#         with open(path, 'r') as logcat: 
#             
#             for line in logcat:
#                 PythonActivity.toastError(line)
#         new_filename="/data/local/tmp/test/" + log_filename + ".sh"
#         try:
#             seedfile=open(new_filename,'a')
#             if seedfile:
#                 PythonActivity.toastError("Seedfile corect")      
#                 for line in logcat:
#                     if line.startswith('BIFUZ_'):
#                         seedfile.write(line)
#                 seedfile.close()   
#                 PythonActivity.toastError(" DONE ")     
#         except:
#                 PythonActivity.toastError(" ERROR ")  
#                 m = re.search("BIFUZ_.* -n (.*)\/.*\.(.*\..*)", line)
#                 try:
#                     package_name = m.group(1)
#                     broadcast_to = m.group(2).strip()
#                     crashed_intent = line
#                 except:
#                     pass
#             elif "Caused" in line:
#                 error = True
#                 m = re.search(".* Caused by\: (.*)\:.*", line)
#                 try:
#                     new_name = m.group(1)
#                 except:
#                     pass
#     if not error:
#         os.remove(path)
#         return True
#     if package_name and new_name:
#         new_name = re.sub('\W+','',new_name)
#         partial_name =  broadcast_to + "." + new_name
#         new_filename = root_path + "/e_" +  partial_name + ".txt"
#         os.rename(log_filename, new_filename)
#         reproducibility(generated_intents_file, partial_name, crashed_intent)
#     return True
