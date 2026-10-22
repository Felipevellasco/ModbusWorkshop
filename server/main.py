from server.servidormodbus import ServidorMODBUS


def main():
    s = ServidorMODBUS("localhost", 51020)
    s.run()


if __name__ == "__main__":
    main()
