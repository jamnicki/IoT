# DATA SOURCE: https://www.kaggle.com/atulanandjha/temperature-readings-iot-devices
import json
import pandas as pd
import requests
import time
import threading
import multiprocessing 
import re

import paho.mqtt.client as mqtt

from flask import Flask
from flask_restful import Resource, Api, reqparse
from queue import Queue


def run_flask():
    app.run(port='5001', debug=True, use_reloader=False)


def broadcast():
    with open('config.json', 'r') as f:
        config = json.load(f)
        f.close()

        data = pd.read_csv(config['base']['data_source'])
        sample = data.head()

        
    BROKER = config['mqtt']['address']
    CLIENT = mqtt.Client('SENSOR1')
    TOPIC = config['mqtt']['topic']

    CLIENT.connect(BROKER)
    CLIENT.loop_start()

    extra_heat_iteration = 0
    recent_temp = 0
    for _, row in data.iterrows():
        with open('config.json', 'r') as f:
            config = json.load(f)
            f.close()
        
        if config['base']['broadcast_mode']:
            extra_heat = extra_heat_iteration * 1.1
            DATA = {
                'room_id': row['room_id/id'],
                'noted_date': row['noted_date'],
                'temp': row['temp'] + extra_heat,
                'method': config['base']['method']
            }
            if config['base']['method'] == 'http':
                try:
                    r = requests.get(config['http']['address'], data={'Sensor1': json.dumps(DATA)})
                except requests.exceptions.ConnectionError:
                    print('requests.exceptions.ConnectionError [111]')
                except Exception as e:
                    print('\niterating over data\n',e)
            elif config['base']['method'] == 'mqtt':
                CLIENT.publish(TOPIC, json.dumps(DATA))

            ######### TEMP CONTROL COMPONENT ###########

            if DATA['temp'] < 55 and config['components']['heater']['running'] == 1:
                extra_heat_iteration += 1
            elif DATA['temp'] > 55:
                extra_heat_iteration -= 1
            elif extra_heat_iteration > 2 and config['components']['heater']['running'] == 0:
                extra_heat_iteration -= 3
            elif extra_heat_iteration > 0 and config['components']['heater']['running'] == 0:
                extra_heat_iteration -= 1

            ############################################

            ######## ANOMALIES HANDLER #################

            if DATA['temp'] < 40:
                config['components']['heater']['running'] = 1
                with open("config.json", "w") as jsonFile:
                    json.dump(config, jsonFile)
                    jsonFile.close()
                print('! Temperature is too low ! Heating up...')

            if DATA['temp'] > 70:
                config['components']['heater']['running'] = 0
                with open("config.json", "w") as jsonFile:
                    json.dump(config, jsonFile)
                    jsonFile.close()
                print('! Temperature is too high ! Turned off the heater.')

            temp_diff = DATA['temp'] - recent_temp
            if abs(temp_diff) > (0.15 * DATA['temp']):
                config['components']['heater']['temp_error'] = round(temp_diff, 2)
                with open("config.json", "w") as jsonFile:
                    json.dump(config, jsonFile)
                    jsonFile.close()
                print(f'High temperature difference! ({round(temp_diff, 2)})')

            recent_temp = DATA['temp']

            ############################################

            time.sleep(config['base']['send_freq'])

        else:
            print("config['base']['broadcast_mode'] = 0 !!!")
            time.sleep(1)

    CLIENT.loop_stop()
    CLIENT.disconnect()


if __name__ == '__main__':

    app = Flask(__name__)
    api = Api(app)
    class Sensor(Resource):
        def post(self):
            parser = reqparse.RequestParser()
            parser.add_argument('Manager')
            parser.add_argument('Heater')
            args = parser.parse_args()

            if args['Heater']:
                heater_arg = json.loads(args['Heater'])
                with open('config.json', 'r') as f:
                        config = json.load(f)
                        f.close()

                if heater_arg['command'] == 1:
                    config['components']['heater']['running'] = 1
                elif heater_arg['command'] == 0:
                    config['components']['heater']['running'] = 0

                with open("config.json", "w") as jsonFile:
                    json.dump(config, jsonFile)
                    jsonFile.close()

            if args['Manager']:
                manager_arg = json.loads(args['Manager'])
                with open('config.json', 'r') as f:
                        config = json.load(f)
                        f.close()
            
                if manager_arg['call'] == 'stop':
                    config['base']['broadcast_mode'] = 0
                    with open("config.json", "w") as jsonFile:
                        json.dump(config, jsonFile)
                        jsonFile.close()
                elif manager_arg['call'] == 'start':
                    config['base']['broadcast_mode'] = 1
                    with open("config.json", "w") as jsonFile:
                        json.dump(config, jsonFile)
                        jsonFile.close()
                elif manager_arg['call'] == 'check_status':
                    if config['base']['broadcast_mode'] == 1:
                        response_msg = 'working'
                    else:
                        response_msg = 'not working'    
                    return response_msg
                elif manager_arg['call'] == 'check_temp_error':
                    return config['components']['heater']['temp_error']
                elif 'change_config:' in manager_arg['call']:
                    change_config_child = re.search(r'(?<=change_config:).*$', manager_arg['call'])
                    if change_config_child:
                        if 'send_freq' in change_config_child[0]:
                            send_freq_match = re.search(r'(?<=send_freq=>)\d+$', manager_arg['call'])
                            if send_freq_match:
                                config['base']['send_freq'] = int(send_freq_match[0])
                                with open("config.json", "w") as jsonFile:
                                    json.dump(config, jsonFile)
                                    jsonFile.close()
                        elif 'method' in change_config_child[0]:
                            method_match = re.search(r'(?<=method=>)\w+$', manager_arg['call'])
                            if method_match:
                                config['base']['method'] = str(method_match[0])
                                with open("config.json", "w") as jsonFile:
                                    json.dump(config, jsonFile)
                                    jsonFile.close()
                    else:
                        print('coś źle byczku')



    api.add_resource(Sensor, '/')

    thread1 = threading.Thread(target=broadcast).start()
    thread2 = threading.Thread(target=run_flask).start()


