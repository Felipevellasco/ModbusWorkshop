# Atividade 4 - Informática Industrial

Este projeto implementa uma simulação de um aquecedor, que contém um reservatório e uma bomba que podem ser controladas
pelo usuário. Para configurar o sistema, basta utilizar a interface Modbus disponível no arquivo `client.py`.

## Sumário

- [Atividade 4 - Informática Industrial](#atividade-4---informática-industrial)
  - [TLDR](#tldr)
  - [Organização](#organização)
  - [Instalação e configuração](#instalação-e-configuração)
  - [Executando o código](#executando-o-código)
  - [Organização de endereços](#organização-de-endereços)
    - [Coil](#coil)
    - [Holding Registers](#holding-registers)
    - [Input Registers](#input-registers)
  - [Créditos](#créditos)

## TL;DR

Para executar o código, basta abrir um terminal para cada um dos comandos abaixo:

```bash
run-server # terminal 1, executa o servidor modbus (simulação da CLP)

run-client # terminal 2, executa o cliente (supervisor)
```

## Organização

O repositório contém os seguintes arquivos e diretórios:

```
/
├── client/
│   ├── clientemodbus.py
│   └── main.py
├── pyproject.toml
├── README.md
├── server/
│   ├── main.py
│   └── servidormodbus.py
└── uv.lock
```

## Instalação e configuração

Para executar o projeto, é necessário baixar as dependências listadas em `pyproject.toml`. Para isso, você pode utilizar
os seguintes comandos:

```bash
# Utilizando o UV
uv venv
uv pip install -e .

# Utilizando o python padrão
python -m venv .venv

## Para Linux ou MacOS (Bash)
source ./.venv/bin/activate
## Para Windows (PowerShell ou CMD)
.\.venv\Scripts\activate

pip install -e .
```

Adicionalmente, também é incluso um arquivo do `direnv` para simplificar a gestão do ambiente virtual. Para habilitar o
ambiente virtual automaticamente ao navegar até a pasta com a interface de comando, basta executar:

```bash
cat .envrc # Sempre inspecione a script antes de executar!

direnv allow
```

Dessa forma, você não precisará digitar `source ./.venv/bin/activate` neste repositório.

## Executando o código

Para executar o servidor e o cliente, são disponibilizados dois atalhos rápidos através do `pyproject.toml`:

```bash
run-server # Executa o servidor na janela selecionada; deve ser executado antes do cliente

run-client # Abre uma sessão do cliente conectada ao Modbus TCP
```

O programa aberto utilizando `run-client` fornece uma interface TUI que pode ser utilizada para ler e escrever dados
utilizando o protocolo Modbus TCP disponibilizado pelo servidor. Também é possível ler um dado N vezes contínuas
selecionando uma repetição de N medidas.  
Caso seja necessário configurar um delay específico, digite 3 no menu da interface para selecionar o delta t entre
medições.  
O servidor e o cliente ambos executam na porta `51020`, que substitui a porta original `502` do serviço. Esta
modificação foi feita pois em sistemas Linux, as portas inferiores a `1000` são portas acessíveis apenas ao _super
user_ (administrador).

## Organização de endereços

Utilizando Modbus, é possível controlar os seguintes parâmetros:

### Coil

Os registradores abaixo descrevem o controle direto dos parâmetros do equipamento.

| #   | Nome/Descrição                                             | Endereço | Tipo | Multiplicador | Permissão |
| --- | ---------------------------------------------------------- | -------- | ---- | ------------- | --------- |
| 1   | **MASTER ENABLE**: Habilita o funcionamento do equipamento | 1        | bool | 1             | R/W       |
| 2   | **PUMP ENABLE**: Habilita o funcionamento da bomba         | 2        | bool | 1             | R/W       |
| 3   | **HEATER ENABLE**: Habilita o funcionamento do aquecedor   | 3        | bool | 1             | R/W       |

### Holding Registers

Os registradores abaixo descrevem o controle dos parâmetros do equipamento.

| #   | Nome/Descrição                                          | Endereço | Tipo   | Multiplicador | Permissão |
| --- | ------------------------------------------------------- | -------- | ------ | ------------- | --------- |
| 4   | **HEATER SETPOINT** (°C): Temperatura alvo do aquecedor | 40001    | uint16 | 100           | R/W       |
| 5   | **PUMP SETPOINT** (L/min): Fluxo alvo da bomba          | 40002    | uint16 | 100           | R/W       |

### Input Registers

Os registradores abaixo descrevem os dados de entrada e funcionamento do equipamento.

| #   | Nome/Descrição                                              | Endereço | Tipo    | Multiplicador | Permissão |
| --- | ----------------------------------------------------------- | -------- | ------- | ------------- | --------- |
| 6   | **PUMP FLOW** (L/min): Fluxo atual da bomba                 | 30001    | uint16  | 100           | R         |
| 7   | **OUTPUT TEMP** (°C): Temperatura do fluido na saída        | 30002    | uint16  | 100           | R         |
| 8   | **INPUT TEMP** (°C): Temperatura do fluido na entrada       | 30003    | uint16  | 100           | R         |
| 9   | **INPUT VOLTAGE** (V): Tensão de alimentação do equipamento | 30004    | float32 | 1             | R         |
| 10  | **POWER** (W): Potência ativa consumida pelo equipamento    | 30006    | float32 | 1             | R         |
| 11  | **CAPACITY** (%): Capacidade consumida do tanque            | 30008    | float32 | 1             | R         |

Nota: o código utiliza indexação de base 0, o que significa que as portas possuem um offset N - 1. Exemplos:

| Nome        | Endereço | Índice no código |
| ----------- | -------- | ---------------- |
| PUMP FLOW   | 30001    | 0                |
| OUTPUT TEMP | 30002    | 1                |
| INPUT TEMP  | 30003    | 2                |

Adicionalmente, os registradores do tipo `float32` utilizam dois registradores `uint16` consecutivos, com formatação
_big endian_.

## Créditos

Autor: `Felipe Freesz Vellasco`
e-mail: `vellasco.felipe@estudante.ufjf.br`
