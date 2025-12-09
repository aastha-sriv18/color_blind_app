from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
from screens.what_color import WhatColorScreen
from screens.cc_charts import CCChartsScreen
from screens.elec import ElecScreen
from screens.mar_bio import MarBioScreen
from screens.emails import EmailsScreen


KV = '''
MDScreen:

    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "App Name"
            elevation: 2
            pos_hint: {"top": 1}

        # The MDBottomNavigation acts as the ScreenManager
        MDBottomNavigation:
            selected_color_background: "orange"
            text_color_active: "lightgrey"

            # --- TAB 1: Charts ---
            MDBottomNavigationItem:
                name: 'screen_charts'
                text: 'Charts'
                icon: 'chart-bar'
                
                # We simply place the screen class here
                CCChartsScreen:

            # --- TAB 2: Electrical ---
            MDBottomNavigationItem:
                name: 'screen_elec'
                text: 'Electrical'
                icon: 'lightning-bolt' # specific icon names might need checking
                
                ElecScreen:

            # --- TAB 3: Color (The Fix) ---
            MDBottomNavigationItem:
                name: 'screen_color'
                text: 'Color'
                icon: 'eyedropper'
                
                WhatColorScreen:

            # --- TAB 4: Marine Bio ---
            MDBottomNavigationItem:
                name: 'screen_mar_bio'
                text: 'Marine Bio'
                icon: 'fish'
                
                MarBioScreen:

            # --- TAB 5: Emails ---
            MDBottomNavigationItem:
                name: 'screen_emails'
                text: 'Mail'
                icon: 'gmail'
                
                EmailsScreen:
'''

class ColorAssistApp(MDApp):
    def build(self):
        # Load the specific KV file for the color screen
        # Make sure screens/what_color.kv exists
        Builder.load_file("screens/what_color.kv")
        
        # Optional: Set a theme color
        self.theme_cls.primary_palette = "Blue"
        
        return Builder.load_string(KV)


if __name__ == '__main__':
    ColorAssistApp().run()