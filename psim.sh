#!/bin/bash
while true; do
    poretry run python /home/$USER/Development/modbus-rtu-data-collector/main.py
    sleep 3
done