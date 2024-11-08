import json, os, platform, socket
from datetime import datetime

from bitstring import BitArray
from get_nic import getnic
from pymodbus.client import ModbusSerialClient


def dev_info() -> dict:
    return {
        "name": socket.gethostname(),
        # "nicInterfaces": getnic.ipaddr(getnic.interfaces()),
        # "platform": platform.platform(),
        # "architecture": platform.architecture(),
        "machine": platform.machine(),
        # "pythonVersion": platform.python_version(),
    }


def get_serial_comport():
    """Only returns comport type tty USB ports."""

    import serial.tools.list_ports

    COMPORT_NAME: str = "STM32 Virtual ComPort"

    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports if port.product == COMPORT_NAME]


def single_byte(v):
    # Extract first and second Bytes
    first_byte, second_byte = (v >> 8) & 0xFF, v & 0xFF
    return [f"{first_byte:#04x}", f"{second_byte:#04x}"]


def parse_data(data: list, slave_id: str, port_name: str):
    """Parses Modbus data into human readable form.

    Args:
        data (list): raw Modbus data from HEXADECIMAL system
        slave_id (str): It's float between hardware modules I/O ports
        port_name (str): USB port name like `/dev/tty/ACM0` as the comport type

    Returns:
        dict: final information of every PSIM device gathered through Modbus.

    Sample:
    ```json
    {
        "timestamp": 1726560300,
        "slave": {
            "id": "1",
            "port": "/dev/ttyACM0"
        },
        "host": {
            "architecture": ["64bit", "ELF"],
            "machine": "x86_64",
            "name": "hostname",
            "nicInterfaces": {
                "eno1": {
                "HWaddr": "ac:22:0b:c8:c1:10",
                "inet4": "172.16.24.134/24",
                "inet6": "fe80::adda:8a65:1e4:c6ed/64",
                "state": "UP"
                }
            },
            "platform": "Linux-6.8.12-3-MANJARO-x86_64-with-glibc2.39",
            "pythonVersion": "3.12.4"
        },
        "digital": [1, 0, 1, 0],
        "temperature": [12, 13, 14, 15],
        "humidity": [14, 15, 16, 17],
        "analog": [1234.0, 3456.0, 4567.0, 5854.0],
        "output": {
        "led": [0, 1, 0, 1],
        "relay": [1, 0, 1, 0]
        }
    }
    ```
    """
    input = [
        [int(single_byte(v)[0], 16), int(single_byte(v)[1], 16)] for v in data[0:6]
    ]
    # Previous version we got only integer value.
    # analog = [int(hex(v), 16) for v in data[6:10]]
    analog = [float(v) / 10 for v in data[6:10]]
    output = [BitArray(hex=hex(v)).bin for v in data[10:]]

    return {
        "timestamp": int(datetime.now().timestamp()),
        "slave": {"id": str(slave_id), "port": port_name},
        "host": dev_info(),
        "digital": [item for sublist in input[0:2] for item in sublist],
        "temperature": [item for sublist in input[2:4] for item in sublist],
        "humidity": [item for sublist in input[4:6] for item in sublist],
        "analog": analog,
        "output": {
            "led": [output[0][i] for i in range(len(output[0]))],
            "relay": [output[1][i] for i in range(len(output[1]))],
        },
    }


def modbus_connect(port: str):
    """Modbus connection

    Args:
        port (str): Comport USB tty
    """
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
            return {}

    client.close()


def save_file(data, file_name):
    log_directory = "/var/log/psim"

    # Create the directory if it doesn't exist
    try:
        os.makedirs(log_directory, exist_ok=True)
    except OSError as e:
        print(f"Error creating directory: {e}")

    json_file_path = os.path.join(log_directory, file_name)

    # Open the JSON file for reading and writing
    try:
        with open(json_file_path, "r+") as file:
            try:
                previous_data = json.load(file)
            except json.JSONDecodeError:
                previous_data = []

            previous_data.append(data)

            # Moves cursor to the beginning of the file to overwrite
            file.seek(0)
            json.dump(previous_data, file, indent=3, sort_keys=True)
            file.truncate()
    except FileNotFoundError:
        # If the file does not exist, create it and write the data
        with open(json_file_path, "w") as file:
            json.dump([data], file, indent=3, sort_keys=True)


def main():
    ports: list[str] = get_serial_comport()

    if len(ports) == 0:
        save_file(
            {
                "timestamp": int(datetime.now().timestamp()),
                "host": dev_info(),
                "comport_issue": "Serial comport list is empty.",
            },
            "errors.json",
        )
    else:
        for port in ports:
            data = modbus_connect(port)

            if data == {}:
                save_file(
                    {
                        "timestamp": int(datetime.now().timestamp()),
                        "host": dev_info(),
                        "modbus_connection_error": "Could't connect to the Modbus Slave",
                    },
                    "errors.json",
                )
            elif data.get("response", "") != "":
                save_file(
                    {
                        "timestamp": int(datetime.now().timestamp()),
                        "host": dev_info(),
                        "fault": data["response"],
                    },
                    "errors.json",
                )
            else:
                save_file(data, "modbus_data.json")


if __name__ == "__main__":
    main()
