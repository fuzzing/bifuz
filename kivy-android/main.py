import kivy
import random
from kivy.app import App
from kivy.core.window import Window
import os
from commands import *
from jnius import autoclass

from common import Bifuz
Environment=autoclass("android.os.Environment")
PythonActivity = autoclass('org.renpy.android.PythonActivity')

class TestApp(App):
    def __init__(self, **kwargs):
        super(TestApp, self).__init__(**kwargs)
        # Setting it up to listen for keyboard events
        Window.bind(on_keyboard=self.onBackBtn)
        dir=Environment.getExternalStorageDirectory().toString()
        if os.path.isdir(str(dir) + "/test/"):
            ok=True
        else:
            os.mkdir(str(dir)+"/test/" )

    def onBackBtn(self, window, key, *args):
        """ To be called whenever user presses Back/Esc Key """
        if key == 27:
            return True
        return False
    def build(self):
        return Bifuz()
    
    def on_pause(self):
      return True
  
    def on_resume(self):
        return True

if __name__ == '__main__':
    TestApp().run()