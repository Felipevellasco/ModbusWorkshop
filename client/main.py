from clientemodbus import ClienteMODBUS


def main():
    c = ClienteMODBUS("localhost", 502)
    c.atendimento()


if __name__ == "__main__":
    main()
