#!/bin/bash
VENV="./myvenv/bin/activate"

gnome-terminal \
--tab -e "bash --rcfile $VENV -ci 'cd Sensors/Sensor1; python3 sensor1.py; exec bash'" \
--tab -e "bash --rcfile $VENV -ci 'cd Sensors/Sensor2; python3 sensor2.py; exec bash'" \
--tab -e "bash --rcfile $VENV -ci 'cd Sensors/Sensor3; python3 sensor3.py; exec bash'" \
--tab -e "bash --rcfile $VENV -ci 'cd Sensors/Sensor4; python3 sensor4.py; exec bash'" \
--tab -e "bash --rcfile $VENV -ci 'cd Sensors/Sensor5; python3 sensor5.py; exec bash'" 
