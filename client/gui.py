from pathlib import Path
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import BooleanProperty, StringProperty
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager

from client.clientemodbus import ClienteMODBUS

PROJECT_ROOT = Path(__file__).resolve().parent.parent
Builder.load_file(str(PROJECT_ROOT / "client/dashboard.kv"))


class MainScreen(MDScreen):
    is_connected = BooleanProperty(False)
    read_result = StringProperty("---")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.modbus_client = None
        self._clock_event = None

    def toggle_connection(self, ip: str, port: str):
        if self.is_connected and self.modbus_client:
            if self._clock_event:
                self._clock_event.cancel()
            self.modbus_client.desconectar()
            self.is_connected = False
            return

        self.modbus_client = ClienteMODBUS(server_ip=ip, porta=int(port))
        if self.modbus_client.conectar():
            self.is_connected = True
        else:
            self.read_result = "Falha ao Conectar"

    def executar_leitura(self, *args):
        if not self.is_connected or not self.modbus_client:
            self.read_result = "Não conectado"
            return

        try:
            addr = int(self.ids.reg_address.text)
            tipo = self.ids.modbus_type.text
            resultado = self.modbus_client.ler_dados(tipo, addr)
            self.read_result = str(resultado)
        except ValueError:
            self.read_result = "Endereço Inválido"

    def executar_escrita(self, valor: str):
        if not self.is_connected or not self.modbus_client:
            self.read_result = "Não conectado"
            return

        try:
            addr = int(self.ids.reg_address.text)
            tipo = self.ids.modbus_type.text
            sucesso = self.modbus_client.escrever_dados(tipo, addr, valor)
            if sucesso:
                self.executar_leitura()
        except ValueError:
            self.read_result = "Endereço Inválido"

    def on_cyclic_toggle(self, active: bool):
        if active:
            try:
                intervalo = float(self.ids.scan_interval.text)
            except ValueError:
                intervalo = 1.0

            # Agenda leitura recorrente via Clock
            self._clock_event = Clock.schedule_interval(
                self.executar_leitura, intervalo
            )
        else:
            if self._clock_event:
                self._clock_event.cancel()
                self._clock_event = None


class RootScreenManager(MDScreenManager):
    pass


class MainApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Indigo"

        sm = RootScreenManager()
        sm.add_widget(MainScreen(name="main"))
        return sm
