from pathlib import Path
from kivy.config import Config
from kivy.utils import platform
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from kivy.lang import Builder

PROJECT_ROOT = Path(__file__).resolve().parent.parent
Builder.load_file(str(PROJECT_ROOT / "client/dashboard.kv"))

if platform == "linux":
    options = Config.options("input")
    for option in options:
        if Config.get("input", option) == "probesysfs":
            Config.remove_option("input", option)


class MainScreen(MDScreen):
    def handle_button_click(self):
        print("Botão pressionado")


class RootScreenManager(MDScreenManager):
    pass


class MainApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Indigo"

        sm = RootScreenManager()
        sm.add_widget(MainScreen(name="main"))
        return sm
