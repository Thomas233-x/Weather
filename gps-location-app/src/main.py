import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from gps_provider import GPSProvider

class MainApp(App):
    def build(self):
        self.gps_provider = GPSProvider()
        layout = BoxLayout(orientation='vertical')
        # Additional UI components can be added here
        return layout

if __name__ == '__main__':
    MainApp().run()