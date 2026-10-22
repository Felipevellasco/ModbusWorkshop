from servidormodbus import ServidorMODBUS


def main():
    s = ServidorMODBUS('localhost',502)
    s.run()

if __name__ == "__main__":
    main()
