
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

