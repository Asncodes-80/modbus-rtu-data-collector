#!/bin/bash
while true; do
    poetry run python /home/$USER/Development/modbus-rtu-data-collector/main.py
    sleep 3
done