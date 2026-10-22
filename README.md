# Atividade 4 - Informática Industrial

Será simulado o estado de um aquecedor com reservatório, que contém uma bomba e um elemento resistivo, ambos controláveis.

## Organização de endereços

Utilizando Modbus, vamos controlar os seguintes parâmetros:

### Coil

Os registradores abaixo descrevem o controle direto dos parâmetros do equipamento.

| #   | Nome/Descrição                                             | Endereço | Tipo | Multiplicador | Permissão |
| --- | ---------------------------------------------------------- | -------- | ---- | ------------- | --------- |
| 1   | **MASTER ENABLE**: Habilita o funcionamento do equipamento | 1        | bool | 1             | R/W       |
| 2   | **PUMP ENABLE**: Habilita o funcionamento da bomba         | 2        | bool | 1             | R/W       |
| 3   | **HEATER ENABLE**: Habilita o funcionamento do aquecedor   | 3        | bool | 1             | R/W       |

### Holding Registers

Os registradores abaixo descrevem o controle dos parâmetros do equipamento.

| #   | Nome/Descrição                                     | Endereço | Tipo   | Multiplicador | Permissão |
| --- | -------------------------------------------------- | -------- | ------ | ------------- | --------- |
| 4   | **HEATER SETPOINT**: Temperatura alvo do aquecedor | 40001    | uint16 | 100           | R/W       |
| 5   | **PUMP SETPOINT**: Fluxo alvo da bomba             | 40002    | uint16 | 100           | R/W       |

### Input Registers

Os registradores abaixo descrevem os dados de entrada e funcionamento do equipamento.

| #   | Nome/Descrição                                          | Endereço | Tipo    | Multiplicador | Permissão |
| --- | ------------------------------------------------------- | -------- | ------- | ------------- | --------- |
| 6   | **PUMP FLOW**: Fluxo atual da bomba                     | 30001    | uint16  | 100           | R         |
| 7   | **OUTPUT TEMP**: Temperatura do fluido na saída         | 30002    | uint16  | 100           | R         |
| 8   | **INPUT TEMP**: Temperatura do fluido na entrada        | 30003    | uint16  | 100           | R         |
| 9   | **INPUT VOLTAGE**: Tensão de alimentação do equipamento | 30004    | float32 | 1             | R         |
| 10  | **POWER**: Potência ativa consumida pelo equipamento    | 30006    | float32 | 1             | R         |
| 11  | **CAPACITY**: Capacidade consumida do tanque            | 30008    | float32 | 1             | R         |
