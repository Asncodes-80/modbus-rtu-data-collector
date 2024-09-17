# Modbus RTU Data Collector

## Get packages in poetry environment

```sh
poetry update
```

## Run

```sh
poetry run python main.py
```

## Errors

* "comport_issue": There is not any Comport connection to computer
* "modbus_connection_error": "Client can't connect and send request to the
  Modbus Slave at this time"
* "fault": Software fault in modbus response, check python code