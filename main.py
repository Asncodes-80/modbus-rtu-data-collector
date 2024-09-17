import json
from datetime import datetime

from pymodbus.client import ModbusSerialClient
from bitstring import BitArray


def get_serial_comport():
    import serial.tools.list_ports

    COMPORT_NAME: str = "STM32 Virtual ComPort"

    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports if port.product == COMPORT_NAME]


def single_byte(v):
    # Extract first and second Bytes
    first_byte, second_byte = (v >> 8) & 0xFF, v & 0xFF
    return [f"{first_byte:#04x}", f"{second_byte:#04x}"]


def parse_data(data: list, slave_id: str, port_name: str):
    input = [
        [int(single_byte(v)[0], 16), int(single_byte(v)[1], 16)] for v in data[0:6]
    ]
    analog = [int(hex(v), 16) for v in data[6:10]]
    output = [BitArray(hex=hex(v)).bin for v in data[10:]]

    return {
        "slave": {"id": str(slave_id), "port": port_name},
        "timestamp": int(datetime.now().replace(second=0, microsecond=0).timestamp()),
        "digital": [item for sublist in input[0:2] for item in sublist],
        "temperature": [item for sublist in input[3:5] for item in sublist],
        "humidity": [item for sublist in input[4:6] for item in sublist],
        "analog": analog,
        "output": {
            "led": {i: output[0][i] for i in range(len(output[0]))},
            "relay": {i: output[1][i] for i in range(len(output[1]))},
        },
    }


def modbus_connect(port: str):
    slave_id: list[int] = [1, 2, 3]

    client = ModbusSerialClient(
        port=port,
        baudrate=9600,
        timeout=10,
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
                return parse_data(response.registers, slave, port)
            else:
                return {"response": response}
        else:
            # Modbus connection error
            client.close()
            return {}

    client.close()


def main():
    ports: list[str] = get_serial_comport()

    if len(ports) == 0:
        print(json.dumps({"comport_issue": "Serial comport list is empty."}))
    else:
        for port in ports:
            data = modbus_connect(port)

            if data == {}:
                print(
                    json.dumps(
                        {
                            "modbus_connection_error": "Could't connect to the Modbus Slave"
                        }
                    )
                )
            elif data.get("response", "") != "":
                print(json.dumps({"fault": data["response"]}))
            else:
                with open("data.json", "r+") as file:
                    try:
                        previous_data = json.load(file)
                    except json.JSONDecodeError:
                        previous_data = []

                    previous_data.append(
                        data,
                    )
                    # Moves cursor to the beginning of the file to overwrite
                    file.seek(0)
                    json.dump(previous_data, file, indent=3, sort_keys=True)
                    file.truncate()


main()
