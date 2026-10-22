import random
from time import sleep

from pyModbusTCP.server import DataHandler, ModbusServer, DataBank


class ServidorMODBUS:
    """
    Classe Servidor Modbus
    """

    def __init__(self, host_ip, port):
        """
        Construtor
        """
        self._db = DataBank()
        self._server = ModbusServer(
            host=host_ip, port=port, no_block=True, data_bank=self._db
        )

    def run(self):
        """
        Execução do servidor Modbus
        """
        try:
            self._server.start()
            print("Servidor MODBUS em execução")
            while True:
                self._db.set_holding_registers(
                    0, [random.randrange(int(0.95 * 400), int(1.05 * 400))]
                )

                coils = self._db.get_coils(0, 3)
                holding_regs = self._db.get_holding_registers(0, 2)
                input_regs = self._db.get_input_registers(0, 3)

                print("======================")
                print("Tabela MODBUS")
                print(f"Coils (1..3): {coils}")
                print(f"Holding Registers (40001..40002): {holding_regs}")
                print(f"Input Registers (30001..30003): {input_regs}")
                sleep(1)
        except Exception as e:
            print("Erro: ", e)
        finally:
            self._server.stop()
            print("Servidor MODBUS finalizado.")


class CLP:
    def __init__(self, bank: DataBank) -> None:
        self._db: DataBank
        self._addr: dict[str, int] = {
            "MASTER ENABLE": 1,  # Coil, bool
            "PUMP ENABLE": 2,  # Coil, bool
            "HEATER ENABLE": 3,  # Coil, bool
            "HEATER SETPOINT": 1,  # Holding, uint16 * 100
            "PUMP SETPOINT": 2,  # Holding, uint16 * 100
            "PUMP FLOW": 1,  # Input, uint16 * 100
            "OUTPUT TEMP": 2,  # Input, uint16 * 100
            "INPUT TEMP": 3,  # Input, uint16 * 100
            "INPUT VOLTAGE": 4,  # Input, float32
            "POWER": 6,  # Input, float32
            "CAPACITY": 8,  # Input, float32
        }

    def loop(self):
        pass
