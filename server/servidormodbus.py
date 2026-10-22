import random, struct
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
        self._clp = CLP(self._db)

    def run(self):
        """
        Execução do servidor Modbus
        """
        try:
            self._server.start()
            print("Servidor MODBUS em execução")
            while True:
                self._clp.loop()

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
    """
    Simulador de CLP com lógica proporcional (P)
    """

    def __init__(self, bank: DataBank) -> None:
        self._db = bank
        self._addr = {
            "MASTER ENABLE": 0,  # Coil, bool
            "PUMP ENABLE": 1,  # Coil, bool
            "HEATER ENABLE": 2,  # Coil, bool
            "HEATER SETPOINT": 0,  # Holding, uint16 * 100
            "PUMP SETPOINT": 1,  # Holding, uint16 * 100
            "PUMP FLOW": 0,  # Input, uint16 * 100
            "OUTPUT TEMP": 1,  # Input, uint16 * 100
            "INPUT TEMP": 2,  # Input, uint16 * 100
            "INPUT VOLTAGE": 3,  # Input, float32
            "POWER": 5,  # Input, float32
            "CAPACITY": 7,  # Input, float32
        }

        self._curr_temp = 20.0  # Temp. ambiente (20°C)
        self._curr_flow = 0.0  # Fluxo atual da bomba (L/min)
        self._curr_capacity = 10.0  # Nível do reservatório (%)
        self._input_temp = 20.0  # Temp. de entrada constante (20°C)

        # Configurar valores iniciais no DataBank
        self._init_defaults()

    def _init_defaults(self):
        """Inicializa valores padrões de setpoints e lecturas fixas."""
        # Configurar Setpoint do Aquecedor (ex: 50.0 °C -> 5000 com multiplicador x100)
        self._db.set_holding_registers(self._addr["HEATER_SETPOINT"], [5000])
        # Configurar Setpoint da Bomba (ex: 30.0 L/min -> 3000 com multiplicador x100)
        self._db.set_holding_registers(self._addr["PUMP_SETPOINT"], [3000])
        # Temp de entrada (20.0 °C -> 2000)
        self._db.set_input_registers(
            self._addr["INPUT_TEMP"], [int(self._input_temp * 100)]
        )

    def _write_float32(self, address: int, value: float):
        """Auxiliar para converter float32 em 2 registradores de 16-bit (Big-Endian)."""
        raw_bytes = struct.pack(">f", value)
        reg1, reg2 = struct.unpack(">HH", raw_bytes)
        self._db.set_input_registers(address, [reg1, reg2])

    def loop(self):
        """
        Executado periodicamente para simular a física do sistema
        """
        # Lê as coils e verifica o que deve ser ativado/desativado.
        coils = self._db.get_coils(0, 3) or [False, False, False]
        master_en = coils[self._addr["MASTER_ENABLE"]]
        pump_en = coils[self._addr["PUMP_ENABLE"]]
        heater_en = coils[self._addr["HEATER_ENABLE"]]

        # Lê setpoints
        holdings = self._db.get_holding_registers(0, 2) or [0, 0]
        heater_sp = holdings[self._addr["HEATER_SETPOINT"]] / 100.0
        pump_sp = holdings[self._addr["PUMP_SETPOINT"]] / 100.0

        # Tensão de alimentação (220V se ligado, 0V se desligado)
        input_voltage = (
            random.randrange(int(0.93 * 220), int(1.1 * 220)) if master_en else 0.0
        )

        # Simula a dinâmica do sistema usando um controlador P
        if master_en:
            if heater_en:
                error_temp = heater_sp - self._curr_temp
                kp_temp = 0.15
                self._curr_temp += kp_temp * error_temp
            else:
                # Decaimento natural para a temperatura ambiente (20°C)
                self._curr_temp -= 0.1 * (self._curr_temp - self._input_temp)

            if pump_en:
                error_flow = pump_sp - self._curr_flow
                kp_flow = 0.3
                self._curr_flow += kp_flow * error_flow
            else:
                self._curr_flow *= 0.5  # Parada da bomba

            # A capacidade varia proporcionalmente ao fluxo da bomba
            self._curr_capacity = max(
                0.0, min(100.0, self._curr_capacity + (self._curr_flow * 0.05) - 0.2)
            )

            # Potência ativa simples baseada nos atuadores ligados (Watts)
            power = (2400.0 if heater_en else 0.0) + (
                self._curr_flow * 20.0 if pump_en else 0.0
            )
        else:
            # Equipamento Desligado (Master Enable Off)
            self._curr_temp -= 0.1 * (self._curr_temp - self._input_temp)
            self._curr_flow = 0.0
            power = 0.0

        self._db.set_input_registers(
            self._addr["PUMP_FLOW"], [int(self._curr_flow * 100)]
        )
        self._db.set_input_registers(
            self._addr["OUTPUT_TEMP"], [int(self._curr_temp * 100)]
        )
        self._write_float32(self._addr["INPUT_VOLTAGE"], input_voltage)
        self._write_float32(self._addr["POWER"], power)
        self._write_float32(self._addr["CAPACITY"], self._curr_capacity)
