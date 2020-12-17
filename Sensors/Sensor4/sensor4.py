# DATA SOURCE: https://www.kaggle.com/mrdew25/pokemon-database
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
    app.run(port='5004', debug=True, use_reloader=False)


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

    for _, row in data.iterrows():
        with open('config.json', 'r') as f:
            config = json.load(f)
            f.close()
        
        if config['base']['broadcast_mode']:
            DATA = {
                'pokedex_num': row['Pokedex Number'],
                'name': row['Pokemon Name'],
                'class': row['Classification'],
                'method': config['base']['method']
            }
            if config['base']['method'] == 'http':
                try:
                    r = requests.get(config['http']['address'], data={'Sensor4': json.dumps(DATA)})
                except requests.exceptions.ConnectionError:
                    print('requests.exceptions.ConnectionError [111]')
                except Exception as e:
                    print('\niterating over data\n',e)
            elif config['base']['method'] == 'mqtt':
                CLIENT.publish(TOPIC, json.dumps(DATA))

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
            args = parser.parse_args()

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



