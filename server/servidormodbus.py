from dataclasses import dataclass
from enum import IntEnum
import random
import struct
from time import sleep

from pyModbusTCP.server import DataBank, ModbusServer


class ModbusType(IntEnum):
    COIL = 0
    DISCRETE_INPUT = 1
    INPUT_REGISTER = 2
    HOLDING_REGISTER = 3


@dataclass
class ModbusConfig:
    offset: int
    size: int = 1
    objType: type = int
    multiplier: float = 1.0


MODBUS_TABLES = {
    ModbusType.COIL: {
        "MASTER ENABLE": ModbusConfig(offset=0, objType=bool),
        "PUMP ENABLE": ModbusConfig(offset=1, objType=bool),
        "HEATER ENABLE": ModbusConfig(offset=2, objType=bool),
    },
    ModbusType.HOLDING_REGISTER: {
        "HEATER SETPOINT": ModbusConfig(offset=0, multiplier=100.0),
        "PUMP SETPOINT": ModbusConfig(offset=1, multiplier=100.0),
    },
    ModbusType.INPUT_REGISTER: {
        "PUMP FLOW": ModbusConfig(offset=0, multiplier=100.0),
        "OUTPUT TEMP": ModbusConfig(offset=1, multiplier=100.0),
        "INPUT TEMP": ModbusConfig(offset=2, multiplier=100.0),
        "INPUT VOLTAGE": ModbusConfig(offset=3, size=2, objType=float),
        "POWER": ModbusConfig(offset=5, size=2, objType=float),
        "CAPACITY": ModbusConfig(offset=7, size=2, objType=float),
    },
}


class ServidorMODBUS:
    """
    Classe Servidor Modbus
    """

    def __init__(self, host_ip, port):
        self._db = DataBank()
        self._server = ModbusServer(
            host=host_ip, port=port, no_block=True, data_bank=self._db
        )
        self._clp = CLP(self._db)

    def print_table_snapshot(self):
        """Itera por todas as tabelas e exibe os valores atuais formatados."""
        print("==================================================")
        print("Tabela MODBUS")

        for table_type, registers in MODBUS_TABLES.items():
            print(f"\n--- {table_type.name} ---")
            for name, cfg in registers.items():
                val = self._clp.get_val(name)
                if cfg.objType is float:
                    display_val = f"{val:.2f}"
                else:
                    display_val = str(val)
                print(f"  [{cfg.offset:>2}] {name:<16}: {display_val}")

    def run(self):
        try:
            self._server.start()
            print("Servidor MODBUS em execução")
            while True:
                self._clp.loop()
                self.print_table_snapshot()
                sleep(0.3)
        except Exception as e:
            print("Erro: ", e)
        finally:
            self._server.stop()
            print("Servidor MODBUS finalizado.")


class CLP:
    """
    Simulador de CLP com lógica proporcional (P)
    """

    def __init__(self, bank: DataBank) -> None:
        self._db = bank

        # Mapeamento reverso para busca rápida de configurações por nome
        self._map: dict[str, tuple[ModbusType, ModbusConfig]] = {}
        for table_type, regs in MODBUS_TABLES.items():
            for name, cfg in regs.items():
                self._map[name] = (table_type, cfg)

        self._curr_temp = 20.0  # Temp. ambiente (20°C)
        self._curr_flow = 0.0  # Fluxo atual da bomba (L/min)
        self._curr_capacity = 10.0  # Nível do reservatório (%)
        self._input_temp = 20.0  # Temp. de entrada constante (20°C)

        self._init_defaults()

    def get_val(self, name: str):
        """Lê e decodifica um valor da tabela Modbus."""
        table_type, cfg = self._map[name]

        if table_type == ModbusType.COIL:
            res = self._db.get_coils(cfg.offset, cfg.size)
            return res[0] if res else False

        elif table_type == ModbusType.HOLDING_REGISTER:
            res = self._db.get_holding_registers(cfg.offset, cfg.size)
            return (res[0] / cfg.multiplier) if res else 0.0

        elif table_type == ModbusType.INPUT_REGISTER:
            res = self._db.get_input_registers(cfg.offset, cfg.size)
            if not res:
                return 0.0
            if cfg.objType is float and cfg.size == 2:
                raw_bytes = struct.pack(">HH", res[0], res[1])
                return struct.unpack(">f", raw_bytes)[0]
            return res[0] / cfg.multiplier

        return None

    def set_val(self, name: str, value):
        """Codifica e escreve um valor na tabela Modbus."""
        table_type, cfg = self._map[name]

        if table_type == ModbusType.COIL:
            self._db.set_coils(cfg.offset, [bool(value)])

        elif table_type == ModbusType.HOLDING_REGISTER:
            self._db.set_holding_registers(cfg.offset, [int(value * cfg.multiplier)])

        elif table_type == ModbusType.INPUT_REGISTER:
            if cfg.objType is float and cfg.size == 2:
                raw_bytes = struct.pack(">f", float(value))
                reg1, reg2 = struct.unpack(">HH", raw_bytes)
                self._db.set_input_registers(cfg.offset, [reg1, reg2])
            else:
                self._db.set_input_registers(cfg.offset, [int(value * cfg.multiplier)])

    def _init_defaults(self):
        """Inicializa valores padrões do CLP."""
        # self.set_val("MASTER ENABLE", True)
        # self.set_val("PUMP ENABLE", True)
        # self.set_val("HEATER ENABLE", True)
        self.set_val("HEATER SETPOINT", 50.0)
        self.set_val("PUMP SETPOINT", 30.0)
        self.set_val("INPUT TEMP", self._input_temp)

    def loop(self):
        """Executado periodicamente para simular a física do sistema."""
        master_en = self.get_val("MASTER ENABLE")
        pump_en = self.get_val("PUMP ENABLE")
        heater_en = self.get_val("HEATER ENABLE")

        heater_sp = self.get_val("HEATER SETPOINT")
        pump_sp = self.get_val("PUMP SETPOINT")

        if heater_sp is None or pump_sp is None:
            return

        input_voltage = (
            random.randrange(int(0.93 * 220), int(1.10 * 220)) if master_en else 0.0
        )

        if master_en:
            if heater_en:
                error_temp = heater_sp - self._curr_temp
                self._curr_temp += 0.15 * error_temp
            else:
                self._curr_temp -= 0.1 * (self._curr_temp - self._input_temp)

            if pump_en:
                error_flow = pump_sp - self._curr_flow
                self._curr_flow += 0.3 * error_flow
            else:
                self._curr_flow *= 0.5

            self._curr_capacity = max(
                0.0, min(100.0, self._curr_capacity + (self._curr_flow * 0.05) - 0.2)
            )

            power = (2400.0 if heater_en else 0.0) + (
                self._curr_flow * 20.0 if pump_en else 0.0
            )
        else:
            self._curr_temp -= 0.1 * (self._curr_temp - self._input_temp)
            self._curr_flow = 0.0
            power = 0.0

        self.set_val("PUMP FLOW", self._curr_flow)
        self.set_val("OUTPUT TEMP", self._curr_temp)
        self.set_val("INPUT VOLTAGE", input_voltage)
        self.set_val("POWER", power)
        self.set_val("CAPACITY", self._curr_capacity)
