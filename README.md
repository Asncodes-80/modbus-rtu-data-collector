# Modbus RTU Data Collector

## Get packages in poetry environment

```sh
poetry update
```

## Run

During client configurations, you should set `$USER` Read-Write permission to
`/var/log` directory.

NOTE: find logs at `/var/log/psim`.

```sh
sudo chmod o+w /var/log
```

### Manual

```sh
poetry run python main.py
```

### Auto Startup with Parallel Machine to Machine

```sh
pm2 startup
```

#### Run as Background Service

Run the following command to make the `psim.sh` script executable.

```sh
chmod +x psim.sh
```

```sh
pm2 start ./psim.sh
```

#### Check Service is Run

```sh
pm2 list
```

#### Save service

```sh
pm2 save
```

## Errors

* "comport_issue": There is not any Comport connection to computer
* "modbus_connection_error": "Client can't connect and send request to the
  Modbus Slave at this time"
* "fault": Software fault in modbus response, check python code