import kivy
import random
from kivy.app import App
from kivy.core.window import Window
import os
from commands import *


from common import Bifuz

class TestApp(App):
    def __init__(self, **kwargs):
        super(TestApp, self).__init__(**kwargs)
        # Setting it up to listen for keyboard events
        Window.bind(on_keyboard=self.onBackBtn)

    def onBackBtn(self, window, key, *args):
        """ To be called whenever user presses Back/Esc Key """
        if key == 27:
            return True
        return False
    def build(self):
        return Bifuz()
    
    def on_pause(self):
      self.on_resume()
      return True
  
    def on_resume(self):
#       output = getoutput('logcat -d')
#       PythonActivity.toastError(output)  
      return True

if __name__ == '__main__':
    TestApp().run()