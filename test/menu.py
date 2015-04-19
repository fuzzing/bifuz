import kivy
import random
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
import re
red = [1,0,0,1]
green = [0,1,0,1]
blue =  [0,0,1,1]
purple = [1,0,1,1]

########################################################################
class HBoxLayoutExample(App):
    """
    Horizontally oriented BoxLayout example class
    """

    #----------------------------------------------------------------------
    def build(self):
        """
        Horizontal BoxLayout example
        """
        colors = [red, green, blue, purple]
        layout = BoxLayout(padding=10,background_color=random.choice(colors))
        

        for i in range(5):
            btn = Button(text="Button #%s" % (i+1),on_press=self.auth)
            
            layout.add_widget(btn)
        return layout
    
    def auth(self,button):
       # if self.username == "Hendricko":
        popup = Popup(title="success",
            content=Label(text="Howdy !"),
            size=(100, 100),
            size_hint=(0.3, 0.3),
            auto_dismiss=True)
        popup.open()
        
if __name__ == "__main__":
    app = HBoxLayoutExample()
    #app = VBoxLayoutExample()
    #app.setOrientation(orient="vertical")
    app.run()
