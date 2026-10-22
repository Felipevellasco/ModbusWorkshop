from time import sleep

from pymodbus.client import ModbusTcpClient

# Importa as tabelas do servidor como fonte única de verdade
from server.servidormodbus import MODBUS_TABLES, ModbusType


class ClienteMODBUS:
    """
    Classe Cliente MODBUS orientada às variáveis configuradas no MODBUS_TABLES
    """

    def __init__(self, server_ip, porta, scan_time=1):
        self._cliente = ModbusTcpClient(host=server_ip, port=porta)
        self._scan_time = scan_time

        self._map = {}
        for table_type, registers in MODBUS_TABLES.items():
            for name, cfg in registers.items():
                self._map[name] = (table_type, cfg)

    def atendimento(self):
        self._cliente.connect()
        try:
            atendimento = True
            while atendimento:
                sel = input(
                    "\nDeseja realizar uma ação? (1- Leitura | 2- Escrita | 3- Configurar Varredura | 4- Sair): "
                )

                if sel == "1":
                    nome = self._selecionar_variavel(apenas_escrita=False)
                    if not nome:
                        continue

                    nvezes = int(
                        input("Digite o número de vezes que deseja ler: ") or 1
                    )
                    for i in range(nvezes):
                        val = self.ler_por_nome(nome)
                        print(f"[{i + 1}] {nome}: {val}")
                        if i < nvezes - 1:
                            sleep(self._scan_time)

                elif sel == "2":
                    nome = self._selecionar_variavel(apenas_escrita=True)
                    if not nome:
                        continue

                    _, cfg = self._map[nome]
                    raw_val = input(f"Digite o novo valor para {nome}: ")
                    if cfg.objType is bool:
                        valor = raw_val.lower() in ("1", "true", "t", "sim", "s", "on")
                    else:
                        valor = cfg.objType(raw_val)

                    ok = self.escrever_por_nome(nome, valor)
                    print(
                        "Escrita realizada com sucesso!" if ok else "Falha na escrita."
                    )

                elif sel == "3":
                    scant = input("Digite o tempo de varredura [s]: ")
                    self._scan_time = float(scant)

                elif sel == "4":
                    atendimento = False
                else:
                    print("Opção inválida.")
        except Exception as e:
            print("Erro no atendimento: ", e)
        finally:
            self._cliente.close()

    def _selecionar_variavel(self, apenas_escrita=False) -> str | None:
        """Exibe um menu numérico com as variáveis disponíveis."""
        opcoes = []
        for name, (table_type, cfg) in self._map.items():
            if apenas_escrita and table_type not in (
                ModbusType.COIL,
                ModbusType.HOLDING_REGISTER,
            ):
                continue
            opcoes.append(name)

        if not opcoes:
            print("Nenhuma variável disponível para esta operação.")
            return None

        print("\nVariáveis Disponíveis:")
        for idx, name in enumerate(opcoes, 1):
            table_type, cfg = self._map[name]
            print(f"  {idx} - {name} ({table_type.name})")

        escolha = input("\nEscolha o número da variável: ")
        try:
            idx = int(escolha) - 1
            if 0 <= idx < len(opcoes):
                return opcoes[idx]
        except ValueError:
            pass

        print("Seleção inválida.")
        return None

    def ler_por_nome(self, name: str):
        """Lê o registrador com base no mapeamento do MODBUS_TABLES."""
        table_type, cfg = self._map[name]

        if table_type == ModbusType.COIL:
            resp = self._cliente.read_coils(
                address=cfg.offset, count=cfg.size, device_id=1
            )
            if resp and not resp.isError():
                return resp.bits[0]

        elif table_type == ModbusType.HOLDING_REGISTER:
            resp = self._cliente.read_holding_registers(
                address=cfg.offset, count=cfg.size, device_id=1
            )
            if resp and not resp.isError():
                return resp.registers[0] / cfg.multiplier

        elif table_type == ModbusType.INPUT_REGISTER:
            resp = self._cliente.read_input_registers(
                address=cfg.offset, count=cfg.size, device_id=1
            )
            if resp and not resp.isError():
                if cfg.objType is float and cfg.size == 2:
                    return self._cliente.convert_from_registers(
                        resp.registers, self._cliente.DATATYPE.FLOAT32
                    )
                return resp.registers[0] / cfg.multiplier

        return None

    def escrever_por_nome(self, name: str, valor) -> bool:
        """Escreve na variável aplicando a escala ou empacotamento correto."""
        table_type, cfg = self._map[name]

        if table_type == ModbusType.COIL:
            resp = self._cliente.write_coil(
                address=cfg.offset, value=bool(valor), device_id=1
            )
            return bool(resp and not resp.isError())

        elif table_type == ModbusType.HOLDING_REGISTER:
            if cfg.objType is float and cfg.size == 2:
                payload = self._cliente.convert_to_registers(
                    float(valor), self._cliente.DATATYPE.FLOAT32
                )
                resp = self._cliente.write_registers(
                    address=cfg.offset, values=payload, device_id=1
                )
            else:
                raw_val = int(valor * cfg.multiplier)
                resp = self._cliente.write_register(
                    address=cfg.offset, value=raw_val, device_id=1
                )
            return bool(resp and not resp.isError())

        return False
