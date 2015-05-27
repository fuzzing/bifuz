import kivy
import random
from kivy.app import App
from kivy.core.window import Window
import glob
from jnius import cast
from jnius import autoclass
import os
from commands import *
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
PythonActivity = autoclass('org.renpy.android.PythonActivity')
Intent = autoclass('android.content.Intent')
Uri = autoclass('android.net.Uri')
ComponentName=autoclass('android.content.ComponentName')
ActivityInfo= autoclass("android.content.pm.ActivityInfo")
PackageInfo= autoclass("android.content.pm.PackageInfo")
PackageManager= autoclass("android.content.pm.PackageManager")
Cursor=autoclass("android.database.Cursor")
AsyncTask=autoclass("com/example/asynctask/MyAsyncTask")
intents=[]
intents_package_names=[]
commands=[]


def log_in_logcat(log): 
    log_command = "log -p f -t %s" % (str(log))
    resp_l = getoutput(log_command)
    return resp_l

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
                output = getoutput("logcat -c")
#                 log_in_logcat('BIFUZ_BROADCAST ' + ' am broadcast -n ' + packageName +'/' + packageClass)
#                 
                task=AsyncTask(PythonActivity.mActivity) 
                task.execute("broadcastseed",packageName,packageClass)
                
#                 output = getoutput('logcat -d')
#                 PythonActivity.toastError(output)  

                receivers.append(packageClass)
            self.s42.values = receivers  
        else: 
            PythonActivity.toastError("No receivers found for this app")         
#         self.s41.bind(text=self.generate_intents)  
    
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
                PythonActivity.toastError(packageClass)  
                activities.append(packageClass)
                
                log_in_logcat('BIFUZ_BROADCAST ' + ' am start -n ' + packageName +'/' + packageClass)
                
                task=AsyncTask(PythonActivity.mActivity) 
                task.execute("intentseed",packageName,packageClass)
               
#                 output = getoutput('logcat -d')
#                 PythonActivity.toastError(output)  
#             self.s32.values = activities     
        else: 
            PythonActivity.toastError("No activities found for this app")         
#         self.s41.bind(text=self.generate_intents)            
    
       
    
#     
# # Run existing generated intents from file
#     
    
    #get all seed files
    def parse_directory(self):
            seed_files = []
            path="/data/local/tmp/test/"
            for filename in glob.glob(os.path.join(path, '*.sh')):
                file_path=filename.split("/data/local/tmp/test/")
                seed_files.append(file_path[1])
            self.s1.values = seed_files
            self.s1.bind(text=self.show_selected_value)
    
    def show_selected_value(self,spinner, text):
        file_path='/data/local/tmp/test/'+text
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
        output = getoutput("logcat -c") 
#         if test all
        if (text.find('Test All')>-1):
            if (self.intent_type==0):
                log_in_logcat('BIFUZ_BROADCAST ' )
                log_filename = "/sdcard/log_Broadcast_all.txt"
                for int in intents:                   
                    PythonActivity.toastError("BROADCAST \n" + str(intents_package_names[intents.index(int)]))
                    PythonActivity.mActivity.sendBroadcast(intents[intents.index(int)])              
                run_result = getoutput("logcat -d >> " + log_filename )
                PythonActivity.toastError(run_result)          
            else:
                output = getoutput("logcat -c")  
                for int in intents:
                    PythonActivity.toastError("Fuzzing \n" + str(intents_package_names[intents.index(int)]))
                    PythonActivity.mActivity.startActivity(intents[intents.index(int)])
                log_filename = "/sdcard/log_fuzz_all.txt"
                run_result = getoutput("logcat -d > " + log_filename )
                PythonActivity.toastError(run_result)     
        else:          
            index=intents_package_names.index(text)
            PythonActivity.toastError(text)
            if (self.intent_type==0):
                output = getoutput("logcat -c")
                log_in_logcat('BIFUZ_BROADCAST ' + commands[index].strip())
                i=intents[index]
                task=AsyncTask(PythonActivity.mActivity) 
                task.execute("broadcastseed",str(i.getComponent().getPackageName()),str(i.getComponent().getClassName()))

#                 log_filename = "/sdcard/log_B.txt"
#                 run_result = getoutput("logcat -d > " + log_filename )    
#                 output = getoutput('logcat -d')
#                 PythonActivity.toastError(output)  
            else:
                output = getoutput("logcat -c")
                log_in_logcat('BIFUZ_INTENT ' + commands[index].strip())   
                i=intents[index]
                task=AsyncTask(PythonActivity.mActivity) 
                task.execute("intentseed",str(i.getComponent().getPackageName()),str(i.getComponent().getClassName()))
         
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
                paths=pack.pathPermissions
                providers.append(string)
        self.s52.values = providers              
        self.s52.bind(text=self.sql_operations)  
         
    def sql_operations(self,spinner,text):
        am = PythonActivity.mActivity
        s='content://com.mwr.example.sieve.DBContentProvider/Passwords/'
        cursor = am.getContentResolver().query(Uri.parse(s),None,None,None,None)
        contentResolver=am.getContentResolver().getPersistedUriPermissions().toArray()
        if (contentResolver is not None):
            for path in contentResolver:
                p=path.getUri().getString()
                PythonActivity.toastError(str(p))
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
                   
                   row_values=row_values + " " + str(value)
                   c+=1
               
               r+=1
               cursor.moveToNext()
               row_values=row_values+ "\n"
            PythonActivity.toastError(row_values)

        
            
#  