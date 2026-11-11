from client.clientemodbus import ClienteMODBUS
from client.gui import MainApp


def cli():
    c = ClienteMODBUS("localhost", 51020)
    c.atendimento()


def gui():
    c = ClienteMODBUS("localhost", 51020)
    MainApp().run()


if __name__ == "__main__":
    cli()
