from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.uix.screen import MDScreen

from screens.what_color import WhatColorScreen
from screens.cc_charts import CCChartsScreen
from screens.elec import ElecScreen
from screens.mar_bio import MarBioScreen
from screens.emails import EmailsScreen

#class WhatColorScreen(Screen): pass
#class CCChartsScreen(Screen): pass
#class ElecScreen(Screen): pass
#class MarBioScreen(Screen): pass
#class EmailsScreen(Screen): pass

class MainScreenManager(ScreenManager): pass


KV = '''
MDScreen:

    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "App Name"
            size_hint_y: None
            height: dp(56)
            id: top_bar



        ScreenManager:
            id: screen_manager

            CCChartsScreen:
                name: "cc_charts"

            ElecScreen:
                name: "elec"

            WhatColorScreen:
                name: "what_color"

            MarBioScreen:
                name: "mar_bio"

            EmailsScreen:
                name: "emails"



        MDBottomNavigation:
            #panel_color: "#eeeaea"
            selected_color_background: "orange"
            text_color_active: "lightgrey"

            MDBottomNavigationItem:
                name: 'screen 1'
                text: 'Charts'
                icon: 'chart-bar'
                on_tab_press: screen_manager.current = "cc_charts"

            MDBottomNavigationItem:
                name: 'screen 2'
                text: 'Electrical'
                icon: 'Electrical Services'
                on_tab_press: screen_manager.current = "elec"

            MDBottomNavigationItem:
                name: 'screen 3'
                text: 'Color'
                icon: 'home'
                on_tab_press: screen_manager.current = "what_color"
            
            MDBottomNavigationItem:
                name: 'screen 4'
                text: 'Marine Bio'
                icon: 'Water Ph'
                on_tab_press: screen_manager.current = "mar_bio"

            
            MDBottomNavigationItem:
                name: 'screen 5'
                text: 'Mail'
                icon: 'gmail'
                on_tab_press: screen_manager.current = "emails"
'''

class ColorAssistApp(MDApp):
    def build(self):
        return Builder.load_string(KV)

if __name__ == '__main__':
    ColorAssistApp().run()