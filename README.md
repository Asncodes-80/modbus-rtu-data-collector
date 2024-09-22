# Modbus RTU Data Collector

## Get packages in poetry environment

```sh
poetry update
```

## Run

During client configurations, you should set `$USER` Read-Write permission to
`/var/log` directory.

```sh
sudo chmod o+w /var/log
```

### Manual

```sh
poetry run python main.py
```

### Cronjob

Run the following command to make the `psim.sh` script executable.

```sh
chmod +x psim.sh
```

```sh
crontab -e
```

In cronjob:

```ini
@reboot /home/$USER/Development/modbus-rtu-data-collector/psim.sh
```

Run the `psim.sh` in the Background:

```sh
nohup /home/$USER/Development/modbus-rtu-data-collector/psim.sh &
```

## Errors

* "comport_issue": There is not any Comport connection to computer
* "modbus_connection_error": "Client can't connect and send request to the
  Modbus Slave at this time"
* "fault": Software fault in modbus response, check python code