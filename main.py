from datetime import datetime

from pymodbus.client import ModbusSerialClient
from bitstring import BitArray


def get_serial_comport():
    import serial.tools.list_ports

    COMPORT_NAME: str = "STM32 Virtual ComPort"

    ports = serial.tools.list_ports.comports()
    com_set = set(
        [port.device if port.product == COMPORT_NAME else None for port in ports]
    )

    return list(com_set)[1:]


def single_byte(v):
    # Extract first and second Bytes
    first_byte, second_byte = (v >> 8) & 0xFF, v & 0xFF
    return [f"{first_byte:#04x}", f"{second_byte:#04x}"]


def parse_data(data: list):
    input = [single_byte(v) for v in data[0:6]]
    analog = [hex(v) for v in data[6:10]]
    output = [BitArray(hex=hex(v)).bin[4:] for v in data[10:]]

    return {
        "timestamp": datetime.now().timestamp(),
        "digital": input[0:2],
        "temp": input[3:5],
        "humidity": input[4:6],
        "analog": analog,
        "output": {"led": output[0], "relay": output[1]},
    }


def modbus_connect(port: str):
    slave_id: list[int] = [1, 2, 3]

    client = ModbusSerialClient(
        port=port,
        baudrate=9600,
        timeout=3,
        parity="N",
        stopbits=1,
        bytesize=8,
    )

    for slave in slave_id:
        if client.connect():
            response = client.read_holding_registers(
                slave=slave, address=0x28, count=0x0C
            )

            if not response.isError():
                return parse_data(response.registers)
            else:
                return {"response": response}

        else:
            return {}


def main():
    ports: list[int] = get_serial_comport()
    if len(ports) == 0:
        print("Serial comport list is empty.")
    else:
        for port in ports:
            data = modbus_connect(port)

            if data == {}:
                print("Could't connect to the Modbus Slave")
            elif data.get("response", "") != "":
                print(data["response"])
            else:
                print(data)


main()
