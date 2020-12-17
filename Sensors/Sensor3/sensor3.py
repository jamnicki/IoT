# DATA SOURCE: https://www.kaggle.com/pankrzysiu/weather-archive-jena
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
    app.run(port='5003', debug=True, use_reloader=False)


def broadcast():
    with open('config.json', 'r') as f:
        config = json.load(f)
        f.close()

        data = pd.read_csv(config['base']['data_source'])
        sample = data.head()

        
    BROKER = config['mqtt']['address']
    CLIENT = mqtt.Client('SENSOR3')
    TOPIC = config['mqtt']['topic']

    CLIENT.connect(BROKER)
    CLIENT.loop_start()

    extra_rh_iteration = 0
    recent_rh = 0
    for _, row in data.iterrows():
        with open('config.json', 'r') as f:
            config = json.load(f)
            f.close()
        
        if config['base']['broadcast_mode']:
            extra_rh = extra_rh_iteration * 1.1
            DATA = {
                'date_time': row['Date Time'],
                'air_pressure': round(row['p (mbar)'], 2),
                'rh': row['rh (%)'] + extra_rh,
                'method': config['base']['method']
            }
            if config['base']['method'] == 'http':
                try:
                    r = requests.get(config['http']['address'], data={'Sensor3': json.dumps(DATA)})
                except requests.exceptions.ConnectionError:
                    print('requests.exceptions.ConnectionError [111]')
                except Exception as e:
                    print('\niterating over data\n',e)
            elif config['base']['method'] == 'mqtt':
                CLIENT.publish(TOPIC, json.dumps(DATA))
            
            ######### RH CONTROL COMPONENT ###########

            if DATA['rh'] < 60 and config['components']['humidifier']['running'] == 1:
                extra_rh_iteration += 1
            elif DATA['rh'] > 60:
                extra_rh_iteration -= 1
            elif extra_rh_iteration > 2 and config['components']['humidifier']['running'] == 0:
                extra_rh_iteration -= 3
            elif extra_rh_iteration > 0 and config['components']['humidifier']['running'] == 0:
                extra_rh_iteration -= 1

            ############################################

            ######## ANOMALIES HANDLER #################

            if DATA['rh'] < 50:
                config['components']['humidifier']['running'] = 1
                with open("config.json", "w") as jsonFile:
                    json.dump(config, jsonFile)
                    jsonFile.close()
                print('! Humidity is too low !')

            if DATA['rh'] > 70:
                config['components']['humidifier']['running'] = 0
                with open("config.json", "w") as jsonFile:
                    json.dump(config, jsonFile)
                    jsonFile.close()
                print('! Humidity is too high !')

            rh_diff = DATA['rh'] - recent_rh
            if abs(rh_diff) > (0.15 * DATA['rh']):
                config['components']['humidifier']['rh_error'] = round(rh_diff, 2)
                with open("config.json", "w") as jsonFile:
                    json.dump(config, jsonFile)
                    jsonFile.close()
                print(f'High Humidity difference! ({round(rh_diff, 2)})')

            recent_rh = DATA['rh']

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
            parser.add_argument('Humidifier')
            args = parser.parse_args()

            if args['Humidifier']:
                heater_arg = json.loads(args['Humidifier'])
                with open('config.json', 'r') as f:
                        config = json.load(f)
                        f.close()

                if heater_arg['command'] == 1:
                    config['components']['humidifier']['running'] = 1
                elif heater_arg['command'] == 0:
                    config['components']['humidifier']['running'] = 0

                with open("config.json", "w") as jsonFile:
                    json.dump(config, jsonFile)
                    jsonFile.close()

            if args['Manager']:
                manager_arg = json.loads(args['Manager'])
                with open('config.json', 'r') as f:
                        config = json.load(f)
                        f.close()
            
                print(config['base']['broadcast_mode'])
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
                elif manager_arg['call'] == 'check_rh_error':
                    return config['components']['humidifier']['rh_error']
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


