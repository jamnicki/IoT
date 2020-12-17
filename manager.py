import requests
import json
import threading
import time
import sqlite3
import datetime
import re
import urllib3

import tkinter as tk

from PIL import Image, ImageTk
from queue import Queue
from objects import Manager
from tkinter import messagebox


def GUI_MAINLOOP(q1, q2, q3):
    global gui_is_working
    
    gui_is_working = True

    root = tk.Tk()
    gui_obj = Manager(root)
    q1.put(gui_obj)
    q2.put(gui_obj)
    q3.put(gui_obj)
    root.mainloop()

    gui_is_working = False


def sensors_data_update_from_db(q1):
    gui_obj = q1.get()
    dbconn = sqlite3.connect('sensorsdb.db')
    while gui_is_working:
        curr_time = datetime.datetime.utcnow() + datetime.timedelta(hours=1)

        tables = ['Sensor1', 'Sensor2', 'Sensor3', 'Sensor4', 'Sensor5']
        for i in range(len(tables)):
            sensor_name = tables[i]
            conn_cursor = dbconn.cursor()
            last_record = conn_cursor.execute(f'SELECT * FROM {tables[i]} ORDER BY recv_time DESC LIMIT 1').fetchall()
            for attribute in last_record:
                if sensor_name == 'Sensor1':
                    gui_obj.sensor1_update(room_id=attribute[1], noted_date=attribute[2], temp=attribute[3], method=attribute[4])
                elif sensor_name == 'Sensor2':
                    gui_obj.sensor2_update(date_time=attribute[1], wind_speed=attribute[2], wind_direction=attribute[3], method=attribute[4])
                elif sensor_name == 'Sensor3':
                    gui_obj.sensor3_update(date_time=attribute[1], air_pressure=attribute[2], rh=attribute[3], method=attribute[4])
                elif sensor_name == 'Sensor4':
                    gui_obj.sensor4_update(pokedex_num=attribute[1], name=attribute[2], poke_class=attribute[3], method=attribute[4])
                elif sensor_name == 'Sensor5':
                    gui_obj.sensor5_update(mac=attribute[1], light=attribute[2], motion=attribute[3], method=attribute[4])

        time.sleep(1)
    conn_cursor.close()
    dbconn.close()


def sensors_status_listener(q2):
    gui_obj = q2.get()
    while gui_is_working:
        time.sleep(1)
        status1 = gui_obj.check_sensor_status(sensor_name='Sensor1')
        status2 = gui_obj.check_sensor_status(sensor_name='Sensor2')
        status3 = gui_obj.check_sensor_status(sensor_name='Sensor3')
        status4 = gui_obj.check_sensor_status(sensor_name='Sensor4')
        status5 = gui_obj.check_sensor_status(sensor_name='Sensor5')

        if status1 == 'working':
            gui_obj.sensor1_running_indicator_update(status1)
        else:
            gui_obj.sensor1_running_indicator_update(status1)
        
        if status2 == 'working':
            gui_obj.sensor2_running_indicator_update(status2)
        else:
            gui_obj.sensor2_running_indicator_update(status2)

        if status3 == 'working':
            gui_obj.sensor3_running_indicator_update(status3)
        else:
            gui_obj.sensor3_running_indicator_update(status3)

        if status4 == 'working':
            gui_obj.sensor4_running_indicator_update(status4)
        else:
            gui_obj.sensor4_running_indicator_update(status4)

        if status5 == 'working':
            gui_obj.sensor5_running_indicator_update(status5)
        else:
            gui_obj.sensor5_running_indicator_update(status5)


def data_error_listener(q3):
    gui_obj = q3.get()
    recent_temp_error = 0
    recent_rh_error = 0
    while gui_is_working:
        DATA = {
            'call': 'check_temp_error'
        }
        try:
            r_for_check_temp_error = requests.post(f'http://127.0.0.1:5001/', data={"Manager": json.dumps(DATA)})
            temp_error = float(r_for_check_temp_error.text)
            if temp_error != recent_temp_error and recent_temp_error != 0:
                gui_obj.open_messagebox(title='Sensor1', message=f'High temperature difference! ({temp_error})')
            recent_temp_error = temp_error
        except requests.exceptions.ConnectionError:
            print('requests.exceptions.ConnectionError [111]')
        except Exception as e:
            print('\data_error_listener\n',e)
        
        DATA = {
            'call': 'check_rh_error'
        }
        try:
            r_for_check_rh_error = requests.post(f'http://127.0.0.1:5003/', data={"Manager": json.dumps(DATA)})
            rh_error = float(r_for_check_rh_error.text)
            print(rh_error)
            if rh_error != recent_rh_error and recent_rh_error != 0:
                gui_obj.open_messagebox(title='Sensor3', message=f'High humidity difference! ({rh_error})')
            recent_rh_error = rh_error
        except requests.exceptions.ConnectionError:
            print('requests.exceptions.ConnectionError [111]')
        except Exception as e:
            print('\data_error_listener\n',e)
        
        time.sleep(0.1)




if __name__ == '__main__':
    queue1 = Queue()
    queue2 = Queue()
    queue3 = Queue()

    thread1 = threading.Thread(target=GUI_MAINLOOP, args=(queue1, queue2, queue3)).start()
    thread2 = threading.Thread(target=sensors_data_update_from_db, args=(queue1,)).start()
    thread3 = threading.Thread(target=sensors_status_listener, args=(queue2,)).start()
    thread4 = threading.Thread(target=data_error_listener, args=(queue3,)).start()





