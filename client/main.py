from client.clientemodbus import ClienteMODBUS


def main():
    c = ClienteMODBUS("localhost", 51020)
    c.atendimento()


if __name__ == "__main__":
    main()
