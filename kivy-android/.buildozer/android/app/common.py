import kivy
import random
from kivy.app import App
from kivy.core.window import Window
import glob
from jnius import cast
from jnius import autoclass
import os
from commands import *
from utils import *
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from unicodedata import category

Environment=autoclass("android.os.Environment")
PythonActivity = autoclass('org.renpy.android.PythonActivity')
Intent = autoclass('android.content.Intent')
Uri = autoclass('android.net.Uri')
ComponentName=autoclass('android.content.ComponentName')
ActivityInfo= autoclass("android.content.pm.ActivityInfo")
PackageInfo= autoclass("android.content.pm.PackageInfo")
PackageManager= autoclass("android.content.pm.PackageManager")
Cursor=autoclass("android.database.Cursor")


AsyncTask=autoclass("com/example/asynctask/MyAsyncTask")

Environment=autoclass("android.os.Environment");
TimeUnit=autoclass("java.util.concurrent.TimeUnit")
intents=[]
intents_package_names=[]
commands=[]
categories=[]
extra_keys=[]
extra_types=[]
activity_actions=[]
flags=[]
# if os.path.isfile("/data/anr/traces.txt"):
#     with open("/data/anr/traces.txt") as f:
#         content = f.readlines()
#         for command in content:
#             dir=Environment.getExternalStorageDirectory().toString()
#             path=str(dir) + "APP_TRACES.txt"
#             trace_file=open(path,'a')
#             if os.path.isfile(path):
#                 trace_file.write(command)
# else: PythonActivity.toastError("File not found")
# with open(path_txt + "/data/anr/traces.txt") as f:
#         logs = f.read().splitlines() 
#         for i in range(len(logs)):
#             PythonActivity.toastError(logs[i])
#   


path_txt="txts/"

with open(path_txt + "categories.txt") as f:
        categories = f.read().splitlines()

with open(path_txt + "extra_keys.txt") as f:
        extra_keys = f.read().splitlines()

with open(path_txt + "extra_types.txt") as f:
        extra_types = f.read().splitlines()

with open(path_txt + "flags.txt") as f:
        flags = f.read().splitlines()
with open(path_txt + "activity_actions.txt") as f:
        activity_actions = f.read().splitlines()
for i in range(len(flags)):
    index_fl = flags[i].index(':')
    if index_fl > 0:
        flags[i] = flags[i][index_fl+1:]
# get_default_values("/data/local/tmp/txts/",categories,extra_keys,extra_types,flags)


def log_in_logcat(log): 
    log_command = "log -p f -t %s" % (str(log))
    output = getoutput(log_command)

#parse all lines in a seed file and create intents/broadcast arrays
def parse_seed_line_command(command):
        adb_params = command.split(" ");   
        package=adb_params[adb_params.index("-n")+1]
        packageName=package.split("/")
        intents_package_names.append(packageName[1])
        if (command.find('broadcast')>-1):           
            intent_type=0
        else:   
            intent_type=1  
             
            action=adb_params[adb_params.index("-a")+1]
            s=adb_params[adb_params.index("-f")+2]
            flag=int(s, 0)
            category=adb_params[adb_params.index("-c")+1]
            data=Uri.parse(adb_params[adb_params.index("-d")+1])
            extra_type=adb_params[adb_params.index("-e")+1]
            extra_string=adb_params[adb_params.index("-e")+2]
            extra_value=adb_params[adb_params.index("-e")+3]
        
        intent = Intent()
        intent.setComponent(ComponentName(packageName[0],packageName[1]))      
        if (intent_type==0):
            intents.append(intent)
        else:
            intent.setAction(action)
            intent.addCategory(category)
            intent.setData(data)
            intent.setFlags(flag)   
            if extra_type=="boolean":
                if extra_value=="true":
                    intent.putExtra(extra_string, "true")
                else:
                    intent.putExtra(extra_string, "false")
            elif extra_type=="string":
                intent.putExtra(extra_string, extra_value)
            elif extra_type=="int":
                intent.putExtra(extra_string, int(extra_value))
            intents.append(intent)                                               
        return intent_type
 
 
 
            
Builder.load_file("AppLayout.kv")



class Bifuz(FloatLayout):
    Window.clearcolor = (0,1,1,0)
    
    
#  
# #  Generate Broadcast Intent calls
#  

     #get all packages and activities for Broadcast
    def get_all_Broadcast_packages(self):
        arrayList=[]
        mypackList=[]
        pm = PythonActivity.mActivity.getPackageManager()
        mypackList=pm.getInstalledPackages(PackageManager.GET_RECEIVERS).toArray()  
        for pack in mypackList:
            arrayList.append(pack.packageName)
        filename="all_"+ "broadcast.sh"
        
        self.s1.values.append(filename) 
        self.s41.values = arrayList              
        self.s41.bind(text=self.generate_intents_Receivers)
             
        
    def generate_intents_Receivers(self,spinner,text):
        PackListReceiver=[]
        receivers=[]
        pm = PythonActivity.mActivity.getPackageManager()
        PackListReceiver=pm.getPackageInfo(text, PackageManager.GET_RECEIVERS).receivers
        
        if (PackListReceiver is not None):
            for pack in PackListReceiver:
                packageName=text
                packageClass=pack.name
                command=' am broadcast -n ' + packageName +'/' + packageClass
                seed_entry(text,command,"broadcast")
                PythonActivity.toastError('BIFUZ_BROADCAST ' + command)
                task=AsyncTask(PythonActivity.mActivity) 
                task.execute("broadcast",packageName,packageClass,command)
                receivers.append(packageClass)
            filename="all_"+ "broadcast" +"_"+text+ ".sh"
            if (filename in self.s1.values):
                filename="all_"+ "broadcast" +"_"+text+ ".sh"
            else:
                self.s1.values.append(filename)  
        else:           
            PythonActivity.toastError("No receivers found for this app")         
    
#     
# # Generate Fuzzed Intent calls  
#      
    #get all Broadcast packages
    def get_all_Activities_packages(self):
        arrayList=[]
        mypackList=[]
        pm = PythonActivity.mActivity.getPackageManager()
        mypackList=pm.getInstalledPackages(PackageManager.GET_ACTIVITIES).toArray()       
        for pack in mypackList:
            arrayList.append(pack.packageName)
        filename="all_"+ "intent.sh"
        if (filename in self.s1.values==False):
                self.s1.values.append(filename) 
        self.s31.values = arrayList              
        self.s31.bind(text=self.generate_intents_Activities)        
          
     #get all packages and activities
    def generate_intents_Activities(self,spinner, text):
        PackListActivities=[]
        activities=[]
        pm = PythonActivity.mActivity.getPackageManager()
        PackListActivities=pm.getPackageInfo(text, PackageManager.GET_ACTIVITIES).activities 
        if (PackListActivities is not None):
            for pack in PackListActivities:
                packageName=text
                packageClass=pack.name
                activities.append(packageClass)
                cat=random.choice(categories);
                flag=random.choice(flags);
                e_key=random.choice(extra_keys);
                e_type=random.choice(extra_types);
                act=random.choice(activity_actions);
                data=generate_random_uri()
                if e_type == "boolean":
                    ev = str(random.choice([True,False]))
                elif e_type == "string":
                    ev = string_generator(random.randint(10,100))
                else:
                    ev = str(random.randint(10,100))
                command=' am start -a ' + act + ' -c ' + cat + ' -n ' + packageName +'/' + packageClass + ' -f '  + flag + ' -d ' + data +' -e ' + e_type +' '+ e_key + ' ' + ev
                seed_entry(text,command,"intent")
                PythonActivity.toastError('BIFUZ_INTENT ' + command)      
                task=AsyncTask(PythonActivity.mActivity) 
                task.execute("intent",packageName,packageClass,act,cat,flag,data,e_type,e_key,ev,command)
            filename="all_"+ "intent" +"_"+text+ ".sh"
            if (filename in self.s1.values):
                filename="all_"+ "intent" +"_"+text+ ".sh"
            else:
                self.s1.values.append(filename)   
        else: 
            PythonActivity.toastError("No activities found for this app") 
    
       
    
#     
# # Run existing generated intents from file
#     
    
    #get all seed files
    def parse_directory(self):
            seed_files = []
            path="/sdcard/test/"
            for filename in glob.glob(os.path.join(path, '*.sh')):
                file_path=filename.split("/sdcard/test/")
                seed_files.append(file_path[1])
            self.s1.values = seed_files
            self.s1.bind(text=self.show_selected_value)
    
    def show_selected_value(self,spinner, text):
        file_path='/sdcard/test/'+text
        del intents[:]
        del intents_package_names[:]
        del commands[:]
        if file_path:
            with open(file_path) as f:
                content = f.readlines()
                for command in content:
                    c=command.split('am',1) 
                    c[1]="am "+ c[1]
                    commands.append(c[1])
                    self.intent_type=parse_seed_line_command(command)
        self.s2.values=intents_package_names
        self.s2.values.insert(0, "Test All")
        self.s2.bind(text=self.run_intents)
                   
    def run_intents(self,spinner, text):
#         output = getoutput("logcat -c") 
#         if test all
        if (text.find('Test All')>-1):
            if (self.intent_type==0):
                log_filename = "/sdcard/log_Broadcast_all.txt"
                for int in intents:
                    log_in_logcat('BIFUZ_BROADCAST ' )                   
                    PythonActivity.toastError("BROADCAST \n" + str(intents_package_names[intents.index(int)]))
                    PythonActivity.mActivity.sendBroadcast(intents[intents.index(int)])                      
            else:
#                 output = getoutput("logcat -c")  
                for int in intents:
                    PythonActivity.toastError("Fuzzing \n" + str(intents_package_names[intents.index(int)]))
                    PythonActivity.mActivity.startActivity(intents[intents.index(int)])
                log_filename = "/sdcard/log_fuzz_all.txt"
#         for one selected line 
        else:          
            index=intents_package_names.index(text)
            if (self.intent_type==0):
#                 output = getoutput("logcat -c")
                adb_params = commands[index].split(" "); 
                package=adb_params[adb_params.index("-n")+1]
                packageName=package.split("/")
                command=' am broadcast -n ' + package
                log_in_logcat('BIFUZ_INTENT ' + command) 
                task=AsyncTask(PythonActivity.mActivity) 
                task.execute("broadcast",packageName[0],packageName[1])

#                 log_filename = "/sdcard/log_B.txt"
#                 run_result = getoutput("logcat -d > " + log_filename )    
#                 output = getoutput('logcat -d')
#                 PythonActivity.toastError(output)  
            else:
#                 output = getoutput("logcat -c")          
                adb_params = commands[index].split(" "); 
                package=adb_params[adb_params.index("-n")+1]
                packageName=package.split("/")
                action=adb_params[adb_params.index("-a")+1]
                flag=adb_params[adb_params.index("-f")+2]
                category=adb_params[adb_params.index("-c")+1]
                data=adb_params[adb_params.index("-d")+1]
                extra_type=adb_params[adb_params.index("-e")+1]
                extra_string=adb_params[adb_params.index("-e")+2]
                extra_value=adb_params[adb_params.index("-e")+3]
                task=AsyncTask(PythonActivity.mActivity) 
                command=' am start -a ' + action + ' -c ' + category + ' -n ' + package + ' -f '  + flag + ' -d ' + data +' -e ' + extra_type +' '+ extra_string + ' ' + extra_value
                PythonActivity.toastError(command)  
                log_in_logcat('BIFUZ_INTENT ' + command)   
#                 task.execute("intent",packageName[0],packageName[1],action,category,flag,data,extra_type,extra_string,extra_value)
#          
#                 log_filename = "/sdcard/log_"+text+".txt"
#                 run_result = getoutput("logcat -d > " + log_filename )
#                 output = getoutput('logcat -d')
#                 PythonActivity.toastError(output)  
                
                
                
#  
# #  SQL injections for specific apk


     #get all packages and activities for Broadcast
    def get_all_Providers_packages(self):
        arrayList=[]
        mypackList=[]
        pm = PythonActivity.mActivity.getPackageManager()
        mypackList=pm.getInstalledPackages(PackageManager.GET_PROVIDERS).toArray()       
        for pack in mypackList:
            string=pack.packageName
            if (string.find('sieve')>-1):
#             PackListProviders=pm.getPackageInfo(string, PackageManager.GET_PROVIDERS).providers 
#             if (PackListProviders is not None):
                arrayList.append(pack.packageName)
        self.s51.values = arrayList              
        self.s51.bind(text=self.generate_contents_providers)
        
    def generate_contents_providers(self,spinner,text):
        PackListProviders=[]
        providers=[]
        pm = PythonActivity.mActivity.getPackageManager()
        PackListProviders=pm.getPackageInfo(text, PackageManager.GET_PROVIDERS).providers 
        if (PackListProviders is not None):
            for pack in PackListProviders:
                string=pack.authority 
                path_permissions=pack.pathPermissions
                if (path_permissions is not None):
                    for p in path_permissions:
                        perm=str(p.getWritePermission ())
                        if perm is not None:
                            PythonActivity.toastError(perm)
                            path_parts=perm.split("WRITE_")
                            path=path_parts[1]
                            uri_path=path[0].upper() + path[1:].lower()
                            am = PythonActivity.mActivity
    #                         s='content://com.mwr.example.sieve.DBContentProvider/Keys/'
                            s='content://'+string+'/'+uri_path +'/'
                            PythonActivity.toastError(s)
                            providerInfo=am.getContentResolver
                            cursor = am.getContentResolver().query(Uri.parse(s),None,None,None,None)
                            array=cursor.getColumnNames()
                            columns=cursor.getColumnCount()
                            rows=cursor.getCount()     
                            if (cursor.moveToFirst()==True):
                                r=1
                                row_values=""
                                while (r<=rows):
                                   c=1
                                   while (c<columns):
                                       type=cursor.getType(c)
                                       if type == 1:
                                           value=cursor.getInt(c)
                                       elif type == 2:
                                           value=cursor.getFloat(c)
                                       elif type == 3:
                                           value=cursor.getString(c)
                                       elif  type == 4:
                                           value=cursor.getBlob(c)
                                       elif type==0: value=" "
                                       
                                       row_values=row_values + "\n" + str(value)
                                       c+=1              
                                   r+=1
                                   cursor.moveToNext()
                                   row_values=row_values+ "\n"
                                   PythonActivity.toastError(uri_path + ":" + row_values)
                    providers.append(string)
                
                else:   PythonActivity.toastError("no uri_path")
#         self.s52.values = providers              
#         self.s52.bind(text=self.sql_operations)  
   
        
            
#  