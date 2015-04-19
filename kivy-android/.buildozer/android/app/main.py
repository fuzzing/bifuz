import kivy
import random
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.base import runTouchApp
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
import glob
from jnius import cast
from jnius import autoclass
import os


PythonActivity = autoclass('org.renpy.android.PythonActivity')
Intent = autoclass('android.content.Intent')
String = autoclass('java.lang.String')
toaster = autoclass("android.widget.Toast")
Uri = autoclass('android.net.Uri')
ComponentName=autoclass('android.content.ComponentName')


red = [1,0,0,0]
green = [0,1,0,1]
blue =  [193/255,205/255,193/255,1]
purple = [1,0,0.7,1]
intents=[]
intents_package_names=[]

#get all seed files
def parse_directory(path):
        seed_files = []
        for filename in glob.glob(os.path.join(path, '*.sh')):
            file_path=filename.split("/data/local/tmp/test/")
            seed_files.append(file_path[1]);
        return seed_files
    
#parse all lines in a seed file and create intents/broadcast arrays
def parse_intent_command(command):
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
            
     
            

########################################################################
class AppLayout(App):
    #----------------------------------------------------------------------
    
    def build(self):
        """
        APP LAYOUT
        """
        Window.clearcolor = (0,1,1,0)
        colors = [red, green, blue, purple]
        title=Label(
            text="[color=520415][b]Bifuz[/b][/color]",
            font_size='50sp', markup=True,
            size_hint=(.7, 0.3),
            pos_hint={'center_x': .5, 'center_y': .5})
        self.layout = BoxLayout(orientation='vertical',spacing=40)
        self.layout.add_widget(title)
        self.layout.orientation='vertical'
        seed_file=parse_directory("/data/local/tmp/test")    
        if not seed_file:
            seed_file=('red','green')
        self.seedSpinner = Spinner(
            text='Select seed file',
            values=seed_file,
            size_hint=(0.7, 0.2),
            pos_hint={'center_x': .5, 'center_y': .5},
            background_color=purple)
        self.seedSpinner.bind(text=self.show_selected_value)
        self.layout.add_widget(self.seedSpinner)    
        self.packageSpinner = Spinner(
            text='Select package',
            values=(''),
            size_hint=(0.7, 0.2),
            pos_hint={'center_x': .5, 'center_y': .5},
            background_color=purple,
            multiline=True)
        self.layout.add_widget(self.packageSpinner)

        return self.layout
    
    #show all the intents/broadcast when a seed file is selected
    def show_selected_value(self,spinner, text):
        file_path='/data/local/tmp/test/'+text
#         PythonActivity.toastError(spinner)
        if file_path:
            with open(file_path) as f:
                content = f.readlines()
                for command in content:
                    self.intent_type=parse_intent_command(command)
        self.layout.remove_widget(self.packageSpinner)
        self.packageSpinner = Spinner(
            text='Select package',
            values=(intents_package_names),
            size_hint=(0.7, 0.2),
            pos_hint={'center_x': .5, 'center_y': .5},
            background_color=purple,
            multiline=True)
        self.packageSpinner.bind(text=self.run_intents)
      
        self.layout.add_widget(self.packageSpinner)
        return self.layout
                        
                    
                    
    def run_intents(self,spinner, text):
        index=intents_package_names.index(text)
        if (self.intent_type==0):
            PythonActivity.toastError("BROADCAST")
            PythonActivity.mActivity.sendBroadcast(intents[index])
        else:
            PythonActivity.toastError("FUZZING")
            PythonActivity.mActivity.startActivity(intents[index])
        
    
            
        
if __name__ == "__main__":
    app = AppLayout()
    app.run()
