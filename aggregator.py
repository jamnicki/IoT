from flask import Flask
from flask_restful import Resource, Api, reqparse

import json
import threading
import re
import sqlite3
import datetime
import random

import paho.mqtt.client as mqtt
import tkinter as tk


class Gui:
    def __init__(self, master):
        self.master = master
        master.title('Aggregator received data logger')
        master.resizable(False, False)
        master.geometry('700x100')

        self.frame = tk.Frame(master, bg='lightgray')
        self.sensor1 = tk.Label(self.frame, text='data from Sensor1')
        self.sensor2 = tk.Label(self.frame, text='data from Sensor2')
        self.sensor3 = tk.Label(self.frame, text='data from Sensor3')
        self.sensor4 = tk.Label(self.frame, text='data from Sensor4')
        self.sensor5 = tk.Label(self.frame, text='data from Sensor5')

        self.sensors = [self.sensor1, self.sensor2, self.sensor3, self.sensor4, self.sensor5]

        # LAYOUT
        self.frame.pack()
        for s in self.sensors:
            s.pack()

    def update_preview(self, sensor_num, data_str):
        self.sensors[sensor_num-1].config(text=data_str)
        

app = Flask(__name__)
api = Api(app)
class Aggregator(Resource):
    def get(self):
        # print('')  # line break
        recv_time = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        dbconn = sqlite3.connect('sensorsdb.db')
        conn_cursor = dbconn.cursor()

        parser = reqparse.RequestParser()

        sensors_l = ['Sensor1', 'Sensor2', 'Sensor3', 'Sensor4', 'Sensor5']
        for sensor_arg_name in sensors_l:
            parser.add_argument(sensor_arg_name)

        args = parser.parse_args()

        for sensor_arg_name in sensors_l:
            match = re.search(r'Sensor(\d+)', sensor_arg_name)
            sensor_num = int(match.group(1))
            if args[f'Sensor{sensor_num}']:
                try:
                    sensor_arg = json.loads(args[sensor_arg_name])
                except Exception as e:
                    print(f'Arg{sensor_num} loading exception:', e)

                if sensor_arg_name == 'Sensor1':
                    ROOM_ID = sensor_arg['room_id']
                    NOTED_DATE = sensor_arg['noted_date']
                    TEMP = round(sensor_arg['temp'], 2)
                    METHOD = sensor_arg['method']
                    try:
                        conn_cursor.execute(f"INSERT INTO Sensor1 VALUES ('{recv_time}', '{ROOM_ID}', '{NOTED_DATE}', {TEMP}, '{METHOD}')")
                        dbconn.commit()
                        print("HTTP: ('{}', '{}', '{}', {}, '{}') INSERTED INTO Sensor1".format(recv_time, ROOM_ID, NOTED_DATE, TEMP, METHOD)) 
                    except Exception as e:
                        print('HTTP: Sensor1 data insertion failed:', e)

                elif sensor_arg_name == 'Sensor2':
                    DATE_TIME = sensor_arg['date/time']
                    WIND_SPEED = sensor_arg['wind_speed']
                    WIND_DIRECTION = sensor_arg['wind_direction']
                    METHOD = sensor_arg['method']
                    try:
                        conn_cursor.execute(f"INSERT INTO Sensor2 VALUES ('{recv_time}', '{DATE_TIME}', {WIND_SPEED}, {WIND_DIRECTION}, '{METHOD}')")
                        dbconn.commit()
                        print("HTTP: ('{}', '{}', {}, {}) INSERTED INTO Sensor2".format(recv_time, DATE_TIME, WIND_SPEED, WIND_DIRECTION, METHOD)) 
                    except Exception as e:
                        print('HTTP: Sensor2 data insertion failed:', e)

                elif sensor_arg_name == 'Sensor3':
                    DATE_TIME = sensor_arg['date_time']
                    AIR_PRESSURE = sensor_arg['air_pressure']
                    RH = round(sensor_arg['rh'], 2)
                    METHOD = sensor_arg['method']
                    try:
                        conn_cursor.execute(f"INSERT INTO Sensor3 VALUES ('{recv_time}', '{DATE_TIME}', {AIR_PRESSURE}, {RH}, '{METHOD}')")
                        dbconn.commit()
                        print("HTTP: ('{}', '{}', {}, {}) INSERTED INTO Sensor3".format(recv_time, DATE_TIME, AIR_PRESSURE, RH, METHOD)) 
                    except Exception as e:
                        print('HTTP: Sensor3 data insertion failed:', e)

                elif sensor_arg_name == 'Sensor4':
                    POKEDEX_NUM = sensor_arg['pokedex_num']
                    POKEMON_NAME = sensor_arg['name']
                    POKEMON_CLASS = sensor_arg['class']
                    METHOD = sensor_arg['method']
                    try:
                        conn_cursor.execute(f"INSERT INTO Sensor4 VALUES ('{recv_time}', '{POKEDEX_NUM}', '{POKEMON_NAME}', '{POKEMON_CLASS}', '{METHOD}')")
                        dbconn.commit()
                        print("HTTP: ('{}', '{}', '{}', '{}') INSERTED INTO Sensor4".format(recv_time, POKEDEX_NUM, POKEMON_NAME, POKEMON_CLASS, METHOD))
                    except Exception as e:
                        print('HTTP: Sensor4 data insertion failed:', e)

                elif sensor_arg_name == 'Sensor5':
                    MAC = sensor_arg['mac']
                    LIGHT = sensor_arg['light']
                    MOTION = sensor_arg['motion']
                    METHOD = sensor_arg['method']
                    try:
                        conn_cursor.execute(f"INSERT INTO Sensor5 VALUES ('{recv_time}', '{MAC}', {LIGHT}, {MOTION}, '{METHOD}')")
                        dbconn.commit()
                        print("HTTP: ('{}', '{}', {}, {}) INSERTED INTO Sensor5".format(recv_time, MAC, LIGHT, MOTION, METHOD))                        
                    except Exception as e:
                        print('HTTP: Sensor5 data insertion failed:', e)

                try:
                    gui_obj.update_preview(sensor_num, 'HTTP:    ' + str(sensor_arg))
                except Exception as e:
                    print(f'Arg{sensor_num} gui preview exception', e)

        

            
api.add_resource(Aggregator, '/')


def on_message(client, userdata, message):
    dbconn = sqlite3.connect('sensorsdb.db')
    conn_cursor = dbconn.cursor()
    recv_time = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    match = re.search(r'Sensor(\d+)', message.topic)
    SENSOR_NUM = int(match.group(1))
    SENSOR_NAME = match.group(0)
    decoded_msg = message.payload.decode('utf-8')
    data = json.loads(decoded_msg)

    if SENSOR_NAME == 'Sensor1':
        ROOM_ID = data['room_id']
        NOTED_DATE = data['noted_date']
        TEMP = round(data['temp'], 2)
        METHOD = data['method']
        try:
            conn_cursor.execute(f"INSERT INTO Sensor1 VALUES ('{recv_time}', '{ROOM_ID}', '{NOTED_DATE}', {TEMP}, '{METHOD}')")
            dbconn.commit()
            print("MQTT: ('{}', '{}', '{}', {}) INSERTED INTO Sensor1".format(recv_time, ROOM_ID, NOTED_DATE, TEMP, METHOD)) 
        except Exception as e:
            print('MQTT: Sensor1 data insertion failed:', e)

    elif SENSOR_NAME == 'Sensor2':
        DATE_TIME = data['date/time']
        WIND_SPEED = data['wind_speed']
        WIND_DIRECTION = data['wind_direction']
        METHOD = data['method']
        try:
            conn_cursor.execute(f"INSERT INTO Sensor2 VALUES ('{recv_time}', '{DATE_TIME}', {WIND_SPEED}, {WIND_DIRECTION}, '{METHOD}')")
            dbconn.commit()
            print("MQTT: ('{}', '{}', {}, {}) INSERTED INTO Sensor2".format(recv_time, DATE_TIME, WIND_SPEED, WIND_DIRECTION, METHOD)) 
        except Exception as e:
            print('MQTT: Sensor2 data insertion failed:', e)

    elif SENSOR_NAME == 'Sensor3':
        DATE_TIME = data['date_time']
        AIR_PRESSURE = data['air_pressure']
        RH = round(data['rh'], 2)
        METHOD = data['method']
        try:
            conn_cursor.execute(f"INSERT INTO Sensor3 VALUES ('{recv_time}', '{DATE_TIME}', {AIR_PRESSURE}, {RH}, '{METHOD}')")
            dbconn.commit()
            print("MQTT: ('{}', '{}', {}, {}) INSERTED INTO Sensor3".format(recv_time, DATE_TIME, AIR_PRESSURE, RH, METHOD)) 
        except Exception as e:
            print('MQTT: Sensor3 data insertion failed:', e)

    elif SENSOR_NAME == 'Sensor4':
        POKEDEX_NUM = data['pokedex_num']
        POKEMON_NAME = data['name']
        POKEMON_CLASS = data['class']
        METHOD = data['method']
        try:
            conn_cursor.execute(f"INSERT INTO Sensor4 VALUES ('{recv_time}', '{POKEDEX_NUM}', '{POKEMON_NAME}', '{POKEMON_CLASS}', '{METHOD}')")
            dbconn.commit()
            print("MQTT: ('{}', '{}', '{}', '{}') INSERTED INTO Sensor4".format(recv_time, POKEDEX_NUM, POKEMON_NAME, POKEMON_CLASS, METHOD))
        except Exception as e:
            print('MQTT: Sensor4 data insertion failed:', e)

    elif SENSOR_NAME == 'Sensor5':
        MAC = data['mac']
        LIGHT = data['light']
        MOTION = data['motion']
        METHOD = data['method']
        try:
            conn_cursor.execute(f"INSERT INTO Sensor5 VALUES ('{recv_time}', '{MAC}', {LIGHT}, {MOTION}, '{METHOD}')")
            dbconn.commit()
            print("MQTT: ('{}', '{}', {}, {}) INSERTED INTO Sensor5".format(recv_time, MAC, LIGHT, MOTION, METHOD))                        
        except Exception as e:
            print('MQTT: Sensor5 data insertion failed:', e)



    gui_obj.update_preview(sensor_num=SENSOR_NUM, data_str='MQTT:    ' + str(data))


def sub_loop(CLIENT, topic):
    CLIENT.loop_start()
    CLIENT.subscribe(topic)


def run_flask():
    app.run(port='5000', debug=True, use_reloader=False)


def GUI_MAINLOOP():

    global gui_obj

    root = tk.Tk()
    gui_obj = Gui(root)
    root.mainloop()


if __name__ == '__main__':

    '''
    INNE BROKERY:
        test.mosquitto.org
        broker.hivemq.com
        mqtt.eclipse.org
        mqtt.fluux.io
        broker.emqx.io
    '''

    thread1 = threading.Thread(target=run_flask).start()
    thread3 = threading.Thread(target=GUI_MAINLOOP).start()

    BROKER = 'broker.hivemq.com'
    CLIENT = mqtt.Client('APK3')
    CLIENT.on_message = on_message
    CLIENT.connect(BROKER)

    thread2 = threading.Thread(target=sub_loop, args=(CLIENT, 'w61psWyytw084seq/Sensors/#')).start()