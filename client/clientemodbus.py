from pymodbus.client import ModbusTcpClient


class ClienteMODBUS:
    def __init__(self, server_ip="127.0.0.1", porta=502):
        self.server_ip = server_ip
        self.porta = int(porta)
        self._cliente = None

    def conectar(self) -> bool:
        self._cliente = ModbusTcpClient(host=self.server_ip, port=self.porta)
        return self._cliente.connect()

    def desconectar(self):
        if self._cliente:
            self._cliente.close()
            self._cliente = None

    def is_connected(self) -> bool:
        if not self._cliente:
            raise ValueError("Cliente não instanciado!")

        return self._cliente is not None and self._cliente.connected

    def ler_dados(self, tipo: str, endereco: int) -> str:
        if not self.is_connected():
            return "Erro: Não conectado"
        elif not self._cliente:
            raise ValueError("Cliente não instanciado!")

        try:
            if tipo == "Coil":
                resp = self._cliente.read_coils(address=endereco, count=1)
                if resp and not resp.isError():
                    return str(resp.bits[0])

            elif tipo == "Holding Register":
                resp = self._cliente.read_holding_registers(address=endereco, count=1)
                if resp and not resp.isError():
                    return str(resp.registers[0])

            elif tipo == "Float":
                resp = self._cliente.read_holding_registers(address=endereco, count=2)
                if resp and not resp.isError():
                    val = self._cliente.convert_from_registers(
                        resp.registers, self._cliente.DATATYPE.FLOAT32
                    )
                    return f"{val:.4f}"

            return "Erro de Leitura"
        except Exception as e:
            return f"Erro: {str(e)}"

    def escrever_dados(self, tipo: str, endereco: int, valor_raw: str) -> bool:
        if not self.is_connected():
            return False
        elif not self._cliente:
            raise ValueError("Cliente não instanciado!")

        try:
            if tipo == "Coil":
                val = valor_raw.lower() in ("1", "true", "t", "sim", "s", "on")
                resp = self._cliente.write_coil(address=endereco, value=val)
                return bool(resp and not resp.isError())

            elif tipo == "Holding Register":
                resp = self._cliente.write_register(
                    address=endereco, value=int(valor_raw)
                )
                return bool(resp and not resp.isError())

            elif tipo == "Float":
                payload = self._cliente.convert_to_registers(
                    float(valor_raw), self._cliente.DATATYPE.FLOAT32
                )
                resp = self._cliente.write_registers(address=endereco, values=payload)
                return bool(resp and not resp.isError())

            return False
        except Exception:
            return False
