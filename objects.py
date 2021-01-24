import re
import requests
import json
import sqlite3
import time

import tkinter as tk
import pandas as pd

from tkinter import messagebox
from tkinter import ttk


class Manager:
    def __init__(self, master):
        self.master = master
        master.title('Sensors manager')
        master.resizable(False, False)

        # SRC
        self.save_data_img = tk.PhotoImage(file='./src/save_to_file.png')
        self.inspect_img = tk.PhotoImage(file='./src/inspect.png')
        self.settings_img = tk.PhotoImage(file='./src/settings.png')
        self.send_command_button = tk.PhotoImage(file='./src/send_command.png')
        self.green_circ_img = tk.PhotoImage(file='./src/green_circle.png')
        self.red_circ_img = tk.PhotoImage(file='./src/red_circle.png')
        self.mqtt_sign_img = tk.PhotoImage(file='./src/MQTT_sign.png')
        self.http_sign_img = tk.PhotoImage(file='./src/HTTP_sign.png')
        self.start_sensor_img = tk.PhotoImage(file='./src/on_icon.png')
        self.stop_sensor_img = tk.PhotoImage(file='./src/off_icon.png')

        # WIDGETS
        self.sensor1_container = tk.Frame(master, highlightbackground='darkgrey', highlightthickness=1, height=200, width=300)
        self.sensor2_container = tk.Frame(master, highlightbackground='darkgrey', highlightthickness=1, height=200, width=300)
        self.sensor3_container = tk.Frame(master, highlightbackground='darkgrey', highlightthickness=1, height=200, width=300)
        self.sensor4_container = tk.Frame(master, highlightbackground='darkgrey', highlightthickness=1, height=200, width=300)
        self.sensor5_container = tk.Frame(master, highlightbackground='darkgrey', highlightthickness=1, height=200, width=300)
        self.acctuators_container = tk.Frame(master, highlightbackground='darkgrey', highlightthickness=1, height=200, width=300)

        self.sensor1_data_preview_container = tk.Frame(self.sensor1_container, bg=self.sensor1_container['bg'], height=100, width=100)
        self.sensor2_data_preview_container = tk.Frame(self.sensor2_container, bg=self.sensor2_container['bg'], height=100, width=100)
        self.sensor3_data_preview_container = tk.Frame(self.sensor3_container, bg=self.sensor3_container['bg'], height=100, width=100)
        self.sensor4_data_preview_container = tk.Frame(self.sensor4_container, bg=self.sensor4_container['bg'], height=100, width=100)
        self.sensor5_data_preview_container = tk.Frame(self.sensor5_container, bg=self.sensor5_container['bg'], height=100, width=100)
        self.sensors_data_preview = [ self.sensor1_data_preview_container,
                                      self.sensor2_data_preview_container,
                                      self.sensor3_data_preview_container,
                                      self.sensor4_data_preview_container,
                                      self.sensor5_data_preview_container ]

        self.sensor1_inspect_button = tk.Button(self.sensor1_container, command=self.open_datapreview1_toplevel_window, borderwidth=0, activebackground=self.sensor1_container['bg'], image=self.inspect_img)

        self.sensor1_settings_button = tk.Button(self.sensor1_container, command=self.open_settings1_toplevel_window,borderwidth=0, activebackground=self.sensor1_container['bg'], image=self.settings_img)
        self.sensor2_settings_button = tk.Button(self.sensor2_container, command=self.open_settings2_toplevel_window,borderwidth=0, activebackground=self.sensor2_container['bg'], image=self.settings_img)
        self.sensor3_settings_button = tk.Button(self.sensor3_container, command=self.open_settings3_toplevel_window,borderwidth=0, activebackground=self.sensor3_container['bg'], image=self.settings_img)
        self.sensor4_settings_button = tk.Button(self.sensor4_container, command=self.open_settings4_toplevel_window,borderwidth=0, activebackground=self.sensor4_container['bg'], image=self.settings_img)
        self.sensor5_settings_button = tk.Button(self.sensor5_container, command=self.open_settings5_toplevel_window,borderwidth=0, activebackground=self.sensor5_container['bg'], image=self.settings_img)

        self.sensor1_title = tk.Label(self.sensor1_container, text='Sensor1', background=self.sensor1_container['bg'])
        self.sensor2_title = tk.Label(self.sensor2_container, text='Sensor2', background=self.sensor2_container['bg'])
        self.sensor3_title = tk.Label(self.sensor3_container, text='Sensor3', background=self.sensor3_container['bg'])
        self.sensor4_title = tk.Label(self.sensor4_container, text='Sensor4', background=self.sensor4_container['bg'])
        self.sensor5_title = tk.Label(self.sensor5_container, text='Sensor5', background=self.sensor5_container['bg'])
        self.sensor_titles = [ self.sensor1_title,
                               self.sensor2_title,
                               self.sensor3_title,
                               self.sensor4_title,
                               self.sensor5_title ]

        self.sensor1_running_indicator = tk.Label(self.sensor1_container, bg=self.sensor1_container['bg'], image=self.red_circ_img)
        self.sensor2_running_indicator = tk.Label(self.sensor2_container, bg=self.sensor2_container['bg'], image=self.red_circ_img)
        self.sensor3_running_indicator = tk.Label(self.sensor3_container, bg=self.sensor3_container['bg'], image=self.red_circ_img)
        self.sensor4_running_indicator = tk.Label(self.sensor4_container, bg=self.sensor4_container['bg'], image=self.red_circ_img)
        self.sensor5_running_indicator = tk.Label(self.sensor5_container, bg=self.sensor5_container['bg'], image=self.red_circ_img)
        self.sensors_indicators = [ self.sensor1_running_indicator,
                                    self.sensor2_running_indicator,
                                    self.sensor3_running_indicator,
                                    self.sensor4_running_indicator,
                                    self.sensor5_running_indicator ]

        self.sensor1_method_label = tk.Label(self.sensor1_container, bg=self.sensor1_container['bg'], image=self.http_sign_img)
        self.sensor2_method_label = tk.Label(self.sensor2_container, bg=self.sensor2_container['bg'], image=self.http_sign_img)
        self.sensor3_method_label = tk.Label(self.sensor3_container, bg=self.sensor3_container['bg'], image=self.http_sign_img)
        self.sensor4_method_label = tk.Label(self.sensor4_container, bg=self.sensor4_container['bg'], image=self.http_sign_img)
        self.sensor5_method_label = tk.Label(self.sensor5_container, bg=self.sensor5_container['bg'], image=self.http_sign_img)

        
        self.sensor1_start_button = tk.Button(self.sensor1_container, activebackground=self.sensor1_container['bg'], borderwidth=0, image=self.start_sensor_img, text='start', command=lambda: self.manage_sensor(sensor_name='Sensor1', call='start'))
        self.sensor1_stop_button = tk.Button(self.sensor1_container, activebackground=self.sensor1_container['bg'], borderwidth=0, image=self.stop_sensor_img, text='stop', command=lambda: self.manage_sensor(sensor_name='Sensor1', call='stop'))
        self.sensor2_start_button = tk.Button(self.sensor2_container, activebackground=self.sensor2_container['bg'], borderwidth=0, image=self.start_sensor_img, text='start', command=lambda: self.manage_sensor(sensor_name='Sensor2', call='start'))
        self.sensor2_stop_button = tk.Button(self.sensor2_container, activebackground=self.sensor2_container['bg'], borderwidth=0, image=self.stop_sensor_img, text='stop', command=lambda: self.manage_sensor(sensor_name='Sensor2', call='stop'))
        self.sensor3_start_button = tk.Button(self.sensor3_container, activebackground=self.sensor3_container['bg'], borderwidth=0, image=self.start_sensor_img, text='start', command=lambda: self.manage_sensor(sensor_name='Sensor3', call='start'))
        self.sensor3_stop_button = tk.Button(self.sensor3_container, activebackground=self.sensor3_container['bg'], borderwidth=0, image=self.stop_sensor_img, text='stop', command=lambda: self.manage_sensor(sensor_name='Sensor3', call='stop'))
        self.sensor4_start_button = tk.Button(self.sensor4_container, activebackground=self.sensor4_container['bg'], borderwidth=0, image=self.start_sensor_img, text='start', command=lambda: self.manage_sensor(sensor_name='Sensor4', call='start'))
        self.sensor4_stop_button = tk.Button(self.sensor4_container, activebackground=self.sensor4_container['bg'], borderwidth=0, image=self.stop_sensor_img, text='stop', command=lambda: self.manage_sensor(sensor_name='Sensor4', call='stop'))
        self.sensor5_start_button = tk.Button(self.sensor5_container, activebackground=self.sensor5_container['bg'], borderwidth=0, image=self.start_sensor_img, text='start', command=lambda: self.manage_sensor(sensor_name='Sensor5', call='start'))
        self.sensor5_stop_button = tk.Button(self.sensor5_container, activebackground=self.sensor5_container['bg'], borderwidth=0, image=self.stop_sensor_img, text='stop', command=lambda: self.manage_sensor(sensor_name='Sensor5', call='stop'))
        self.start_buttons = [ self.sensor1_start_button,
                               self.sensor2_start_button,
                               self.sensor3_start_button,
                               self.sensor4_start_button,
                               self.sensor5_start_button ]
        self.stop_buttons = [ self.sensor1_stop_button,
                              self.sensor2_stop_button,
                              self.sensor3_stop_button,
                              self.sensor4_stop_button,
                              self.sensor5_stop_button ]

        self.sensor1_temp = tk.Label(self.sensor1_data_preview_container, bg=self.sensor1_data_preview_container['bg'], text='Temperature:')
        self.sensor1_temp_value = tk.Label(self.sensor1_data_preview_container, bg=self.sensor1_data_preview_container['bg'], text=' - ')
        self.sensor1_room_id = tk.Label(self.sensor1_data_preview_container, bg=self.sensor1_data_preview_container['bg'], text='Room Id:')
        self.sensor1_room_id_value = tk.Label(self.sensor1_data_preview_container, bg=self.sensor1_data_preview_container['bg'], text=' ----- ')
        self.sensor1_noted_date = tk.Label(self.sensor1_data_preview_container, bg=self.sensor1_data_preview_container['bg'], text='Noted date:')
        self.sensor1_noted_date_value = tk.Label(self.sensor1_data_preview_container, bg=self.sensor1_data_preview_container['bg'], text=' - ')

        self.sensor2_date_time = tk.Label(self.sensor2_data_preview_container, bg=self.sensor2_data_preview_container['bg'], text='Date/Time:')
        self.sensor2_date_time_value = tk.Label(self.sensor2_data_preview_container, bg=self.sensor2_data_preview_container['bg'], text=' - ')
        self.sensor2_wind_speed = tk.Label(self.sensor2_data_preview_container, bg=self.sensor2_data_preview_container['bg'], text='Wind speed:')
        self.sensor2_wind_speed_value = tk.Label(self.sensor2_data_preview_container, bg=self.sensor2_data_preview_container['bg'], text=' ----- ')
        self.sensor2_wind_direction = tk.Label(self.sensor2_data_preview_container, bg=self.sensor2_data_preview_container['bg'], text='Wind direction:')
        self.sensor2_wind_direction_value = tk.Label(self.sensor2_data_preview_container, bg=self.sensor2_data_preview_container['bg'], text=' - ')

        self.sensor3_date_time = tk.Label(self.sensor3_data_preview_container, bg=self.sensor3_data_preview_container['bg'], text='Date/Time:')
        self.sensor3_date_time_value = tk.Label(self.sensor3_data_preview_container, bg=self.sensor3_data_preview_container['bg'], text=' - ')
        self.sensor3_air_pressure = tk.Label(self.sensor3_data_preview_container, bg=self.sensor3_data_preview_container['bg'], text='Air pressure:')
        self.sensor3_air_pressure_value = tk.Label(self.sensor3_data_preview_container, bg=self.sensor3_data_preview_container['bg'], text=' ----- ')
        self.sensor3_rh = tk.Label(self.sensor3_data_preview_container, bg=self.sensor3_data_preview_container['bg'], text='RH:')
        self.sensor3_rh_value = tk.Label(self.sensor3_data_preview_container, bg=self.sensor3_data_preview_container['bg'], text=' - ')

        self.sensor4_pokedex_num = tk.Label(self.sensor4_data_preview_container, bg=self.sensor4_data_preview_container['bg'], text='Pokedex No.:')
        self.sensor4_pokedex_num_value = tk.Label(self.sensor4_data_preview_container, bg=self.sensor4_data_preview_container['bg'], text=' - ')
        self.sensor4_name = tk.Label(self.sensor4_data_preview_container, bg=self.sensor4_data_preview_container['bg'], text='Name:')
        self.sensor4_name_value = tk.Label(self.sensor4_data_preview_container, bg=self.sensor4_data_preview_container['bg'], text=' ----- ')
        self.sensor4_class = tk.Label(self.sensor4_data_preview_container, bg=self.sensor4_data_preview_container['bg'], text='Class:')
        self.sensor4_class_value = tk.Label(self.sensor4_data_preview_container, bg=self.sensor4_data_preview_container['bg'], text=' - ')

        self.sensor5_mac = tk.Label(self.sensor5_data_preview_container, bg=self.sensor5_data_preview_container['bg'], text='dbconnMac:')
        self.sensor5_mac_value = tk.Label(self.sensor5_data_preview_container, bg=self.sensor5_data_preview_container['bg'], text=' - ')
        self.sensor5_light = tk.Label(self.sensor5_data_preview_container, bg=self.sensor5_data_preview_container['bg'], text='Light:')
        self.sensor5_light_value = tk.Label(self.sensor5_data_preview_container, bg=self.sensor5_data_preview_container['bg'], text=' ----- ')
        self.sensor5_motion = tk.Label(self.sensor5_data_preview_container, bg=self.sensor5_data_preview_container['bg'], text='Motion:')
        self.sensor5_motion_value = tk.Label(self.sensor5_data_preview_container, bg=self.sensor5_data_preview_container['bg'], text=' - ')

        self.start_heater_button = tk.Button(self.acctuators_container, text='start_heater', command=lambda: self.manage_heater(command=1))
        self.stop_heater_button = tk.Button(self.acctuators_container, text='stop_heater', command=lambda: self.manage_heater(command=0))
        self.start_humidifier_button = tk.Button(self.acctuators_container, text='start_humidifier', command=lambda: self.manage_humidifier(command=1))
        self.stop_humidifier_button = tk.Button(self.acctuators_container, text='stop_humidifier',command=lambda: self.manage_humidifier(command=0))

        # EMPTY
        self.space_label = tk.Label(self.acctuators_container,
                                    background=self.acctuators_container['bg'])
        
        # LAYOUT
        self.sensor1_container.grid(row=0, column=0)
        self.sensor2_container.grid(row=1, column=0)
        self.sensor3_container.grid(row=2, column=0)
        self.sensor4_container.grid(row=0, column=1)
        self.sensor5_container.grid(row=1, column=1)
        self.acctuators_container.grid(row=2, column=1)

        self.sensor1_inspect_button.place(relx=0.13, rely=0)

        self.sensor1_settings_button.place(relx=0.2, rely=0)
        self.sensor2_settings_button.place(relx=0.2, rely=0)
        self.sensor3_settings_button.place(relx=0.2, rely=0)
        self.sensor4_settings_button.place(relx=0.2, rely=0)
        self.sensor5_settings_button.place(relx=0.2, rely=0)


        for title in self.sensor_titles:
            title.place(relx=0.3, rely=0.01)
        
        for indicator in self.sensors_indicators:
            indicator.place(relx=0.49, rely=0.025)
        
        self.sensor1_method_label.place(relx=0.53, rely=0.04)
        self.sensor2_method_label.place(relx=0.53, rely=0.04)
        self.sensor3_method_label.place(relx=0.53, rely=0.04)
        self.sensor4_method_label.place(relx=0.53, rely=0.04)
        self.sensor5_method_label.place(relx=0.53, rely=0.04)

        for start_button in self.start_buttons:
            start_button.place(relx=0.29, rely=0.13)

        for stop_button in self.stop_buttons:
            stop_button.place(relx=0.44, rely=0.13)
        
        for sensor_data_preview_container in self.sensors_data_preview:
            sensor_data_preview_container.place(relx=0.1, rely=0.35)

        self.sensor1_temp.grid(row=0, column=0, sticky=tk.E)
        self.sensor1_temp_value.grid(row=0, column=1, sticky=tk.W)
        self.sensor1_room_id.grid(row=1, column=0, sticky=tk.E)
        self.sensor1_room_id_value.grid(row=1, column=1, sticky=tk.W)
        self.sensor1_noted_date.grid(row=2, column=0, sticky=tk.E)
        self.sensor1_noted_date_value.grid(row=2, column=1, sticky=tk.W)

        self.sensor2_date_time.grid(row=0, column=0, sticky=tk.E)
        self.sensor2_date_time_value.grid(row=0, column=1, sticky=tk.W)
        self.sensor2_wind_speed.grid(row=1, column=0, sticky=tk.E)
        self.sensor2_wind_speed_value.grid(row=1, column=1, sticky=tk.W)
        self.sensor2_wind_direction.grid(row=2, column=0, sticky=tk.E)
        self.sensor2_wind_direction_value.grid(row=2, column=1, sticky=tk.W)

        self.sensor3_date_time.grid(row=0, column=0, sticky=tk.E)
        self.sensor3_date_time_value.grid(row=0, column=1, sticky=tk.W)
        self.sensor3_air_pressure.grid(row=1, column=0, sticky=tk.E)
        self.sensor3_air_pressure_value.grid(row=1, column=1, sticky=tk.W)
        self.sensor3_rh.grid(row=2, column=0, sticky=tk.E)
        self.sensor3_rh_value.grid(row=2, column=1, sticky=tk.W)

        self.sensor4_pokedex_num.grid(row=0, column=0, sticky=tk.E)
        self.sensor4_pokedex_num_value.grid(row=0, column=1, sticky=tk.W)
        self.sensor4_name.grid(row=1, column=0, sticky=tk.E)
        self.sensor4_name_value.grid(row=1, column=1, sticky=tk.W)
        self.sensor4_class.grid(row=2, column=0, sticky=tk.E)
        self.sensor4_class_value.grid(row=2, column=1, sticky=tk.W)

        self.sensor5_mac.grid(row=0, column=0, sticky=tk.E)
        self.sensor5_mac_value.grid(row=0, column=1, sticky=tk.W)
        self.sensor5_light.grid(row=1, column=0, sticky=tk.E)
        self.sensor5_light_value.grid(row=1, column=1, sticky=tk.W)
        self.sensor5_motion.grid(row=2, column=0, sticky=tk.E)
        self.sensor5_motion_value.grid(row=2, column=1, sticky=tk.W)
        
        self.start_heater_button.pack()
        self.stop_heater_button.pack()
        self.space_label.pack()
        self.start_humidifier_button.pack()
        self.stop_humidifier_button.pack()
    
    def manage_heater(self, command):
        DATA = {
            'command': command
        }

        try:
            requests.post("http://localhost:5001", data={"Heater": json.dumps(DATA)})
        except Exception as e:
            print(e)
    
    def manage_humidifier(self, command):
        DATA = {
            'command': command
        }

        try:
            requests.post("http://localhost:5003", data={"Humidifier": json.dumps(DATA)})
        except Exception as e:
            print(e)

    def open_settings1_toplevel_window(self):
        top = tk.Toplevel()
        top.title('Settings1')
        top.geometry('400x200')
        top.resizable(False, False)

        # WIDGETS
        readme_frame = tk.Frame(top, width=360, height=200)
        readme_content = tk.Message(readme_frame, width=readme_frame['width'], bg=readme_frame['bg'], text='Sensor1 API:\nex.:\n    change_config:send_freq=>1\n    change_config:method=>http')
        send_call_from_settings_button = tk.Button(top, command=lambda: self.send_call_from_settings(sensor_name='Sensor1'), image=self.send_command_button, activebackground=top['bg'], borderwidth=0)
        global settings_entry1 
        settings_entry1 = tk.Entry(top, width=40)

        # LAYOUT
        readme_frame.place(relx=0.05, rely=0.05)
        readme_content.pack()
        settings_entry1.place(relx=0.05, rely=0.85)
        send_call_from_settings_button.place(relx=0.87, rely=0.815)
    
    def open_settings2_toplevel_window(self):
        top = tk.Toplevel()
        top.title('Settings2')
        top.geometry('400x200')
        top.resizable(False, False)

        # WIDGETS
        readme_frame = tk.Frame(top, width=360, height=150)
        readme_content = tk.Message(readme_frame, width=readme_frame['width'], bg=readme_frame['bg'], text='Sensor2 API:\nex.:\n    change_config:send_freq=>1\n    change_config:method=>http')
        send_call_from_settings_button = tk.Button(top, command=lambda: self.send_call_from_settings(sensor_name='Sensor2'), image=self.send_command_button, activebackground=top['bg'], borderwidth=0)
        global settings_entry2
        settings_entry2 = tk.Entry(top, width=40)

        # LAYOUT
        readme_frame.place(relx=0.05, rely=0.05)
        readme_content.pack()
        settings_entry2.place(relx=0.05, rely=0.85)
        send_call_from_settings_button.place(relx=0.87, rely=0.815)
    
    def open_settings3_toplevel_window(self):
        top = tk.Toplevel()
        top.title('Settings3')
        top.geometry('400x200')
        top.resizable(False, False)

        # WIDGETS
        readme_frame = tk.Frame(top, width=360, height=150)
        readme_content = tk.Message(readme_frame, width=readme_frame['width'], bg=readme_frame['bg'], text='Sensor3 API:\nex.:\n    change_config:send_freq=>1\n    change_config:method=>http')
        send_call_from_settings_button = tk.Button(top, command=lambda: self.send_call_from_settings(sensor_name='Sensor3'), image=self.send_command_button, activebackground=top['bg'], borderwidth=0)
        global settings_entry3 
        settings_entry3 = tk.Entry(top, width=40)

        # LAYOUT
        readme_frame.place(relx=0.05, rely=0.05)
        readme_content.pack()
        settings_entry3.place(relx=0.05, rely=0.85)
        send_call_from_settings_button.place(relx=0.87, rely=0.815)

    def open_settings4_toplevel_window(self):
        top = tk.Toplevel()
        top.title('Settings4')
        top.geometry('400x200')
        top.resizable(False, False)

        # WIDGETS
        readme_frame = tk.Frame(top, width=360, height=150)
        readme_content = tk.Message(readme_frame, width=readme_frame['width'], bg=readme_frame['bg'], text='Sensor4 API:\nex.:\n    change_config:send_freq=>1\n    change_config:method=>http')
        send_call_from_settings_button = tk.Button(top, command=lambda: self.send_call_from_settings(sensor_name='Sensor4'), image=self.send_command_button, activebackground=top['bg'], borderwidth=0)
        global settings_entry4 
        settings_entry4 = tk.Entry(top, width=40)

        # LAYOUT
        readme_frame.place(relx=0.05, rely=0.05)
        readme_content.pack()
        settings_entry4.place(relx=0.05, rely=0.85)
        send_call_from_settings_button.place(relx=0.87, rely=0.815)

    def open_settings5_toplevel_window(self):
        top = tk.Toplevel()
        top.title('Settings')
        top.geometry('400x200')
        top.resizable(False, False)

        # WIDGETS
        readme_frame = tk.Frame(top, width=360, height=150)
        readme_content = tk.Message(readme_frame, width=readme_frame['width'], bg=readme_frame['bg'], text='Sensor5 API:\nex.:\n    change_config:send_freq=>1\n    change_config:method=>http')
        send_call_from_settings_button = tk.Button(top, command=lambda: self.send_call_from_settings(sensor_name='Sensor5'), image=self.send_command_button, activebackground=top['bg'], borderwidth=0)
        global settings_entry5 
        settings_entry5 = tk.Entry(top, width=40)

        # LAYOUT
        readme_frame.place(relx=0.05, rely=0.05)
        readme_content.pack()
        settings_entry5.place(relx=0.05, rely=0.85)
        send_call_from_settings_button.place(relx=0.87, rely=0.815)

    def open_datapreview1_toplevel_window(self):
        top = tk.Toplevel()
        top.geometry('1020x400')
        top.resizable(False, False)

        # WIDGETS
        global inspect1_timestamp
        global tree
        tree = ttk.Treeview(top, column=("c1", "c2", "c3", "c4", "c5"), show='headings')
        tree.column("#1")
        tree.heading("#1", text="recv_time")
        tree.column("#2")
        tree.heading("#2", text="room_id")
        tree.column("#3")
        tree.heading("#3", text="noted_date")
        tree.column("#4")
        tree.heading("#4", text="temp")
        tree.column("#5")
        tree.heading("#5", text="method")

        inspect1_timestamp = tk.Entry(top, width=40)
        entry_label = tk.Label(top, text='Timestamp(s):')
        preview_button = tk.Button(top, text='Preview data', command=lambda: self.data_preview(sensor_num=1, timestamp=inspect1_timestamp.get()))
        clear_tree_button = tk.Button(top, text='Clear', command=lambda: self.clear_treeview(tree=tree))
        save_data_button = tk.Button(top, image=self.save_data_img, borderwidth=0, activebackground=top['bg'],
                                     command=lambda: self.save_data_to_csv(sensor_num=1, timestamp=inspect1_timestamp.get()))

        # LAYOUT
        entry_label.place(relx=0.01, rely=0.01)
        inspect1_timestamp.place(relx=0.11, rely=0.01, width=70)
        preview_button.place(relx=0.22, rely=0.01)
        tree.place(relx=0.01, rely=0.1)
        clear_tree_button.place(relx=0.9, rely=0.01)
        save_data_button.place(relx=0.33, rely=0.01)


    def send_call_from_settings(self, sensor_name):
        match = re.search(r'Sensor(\d+)', sensor_name)
        sensor_num = int(match.group(1))

        if sensor_name == 'Sensor1':
            settings_entry = settings_entry1
        elif sensor_name == 'Sensor2':
            settings_entry = settings_entry2
        elif sensor_name == 'Sensor3':
            settings_entry = settings_entry3
        elif sensor_name == 'Sensor4':
            settings_entry = settings_entry4
        elif sensor_name == 'Sensor5':
            settings_entry = settings_entry5

        DATA = {
            'call': settings_entry.get()
        }
        try:
            status = requests.post(f'http://127.0.0.1:500{sensor_num}/', data={"Manager": json.dumps(DATA)})
        except requests.exceptions.ConnectionError:
            print('requests.exceptions.ConnectionError [111]')
        except Exception as e:
            print('\nsend_call_from_settings\n',e)

    def check_sensor_status(self, sensor_name):
        match = re.search(r'Sensor(\d+)', sensor_name)
        sensor_num = int(match.group(1))

        DATA = {
            'call': 'check_status'
        }
        try:
            status = requests.post(f'http://127.0.0.1:500{sensor_num}/', data={"Manager": json.dumps(DATA)})
            if status.text == '"working"\n':
                return 'working'
            elif status.text == '"not working"\n':
                return 'not working'
        except requests.exceptions.ConnectionError:
            print('requests.exceptions.ConnectionError [111]')
            return 'not working'
        except Exception as e:
            print('\ncheck_sensor_status\n',e)
            return 'not working'
    
    def manage_sensor(self, sensor_name, call):
        match = re.search(r'Sensor(\d+)', sensor_name)
        sensor_num = int(match.group(1))
        
        DATA = {
            'call': call # 'start' / 'stop'
        }
        try:
            status = requests.post(f'http://127.0.0.1:500{sensor_num}/', data={"Manager": json.dumps(DATA)})
        except requests.exceptions.ConnectionError:
            print('requests.exceptions.ConnectionError [111]')
    
    def sensor1_running_indicator_update(self, status):
        if status == 'working':
            self.sensor1_running_indicator.config(image=self.green_circ_img)
        elif status == 'not working':
            self.sensor1_running_indicator.config(image=self.red_circ_img)
    
    def sensor2_running_indicator_update(self, status):
        if status == 'working':
            self.sensor2_running_indicator.config(image=self.green_circ_img)
        elif status == 'not working':
            self.sensor2_running_indicator.config(image=self.red_circ_img)

    def sensor3_running_indicator_update(self, status):
        if status == 'working':
            self.sensor3_running_indicator.config(image=self.green_circ_img)
        elif status == 'not working':
            self.sensor3_running_indicator.config(image=self.red_circ_img)

    def sensor4_running_indicator_update(self, status):
        if status == 'working':
            self.sensor4_running_indicator.config(image=self.green_circ_img)
        elif status == 'not working':
            self.sensor4_running_indicator.config(image=self.red_circ_img)

    def sensor5_running_indicator_update(self, status):
        if status == 'working':
            self.sensor5_running_indicator.config(image=self.green_circ_img)
        elif status == 'not working':
            self.sensor5_running_indicator.config(image=self.red_circ_img)

    def sensor1_update(self, room_id, noted_date, temp, method):
        self.sensor1_room_id_value.config(text=str(room_id))
        self.sensor1_noted_date_value.config(text=str(noted_date))
        self.sensor1_temp_value.config(text=str(temp))
        if method == 'mqtt':
            self.sensor1_method_label.config(image=self.mqtt_sign_img)
        elif method == 'http':
            self.sensor1_method_label.config(image=self.http_sign_img)
    
    def sensor2_update(self, date_time, wind_speed, wind_direction, method):
        self.sensor2_date_time_value.config(text=str(date_time))
        self.sensor2_wind_speed_value.config(text=str(wind_speed))
        self.sensor2_wind_direction_value.config(text=str(wind_direction))
        if method == 'mqtt':
            self.sensor2_method_label.config(image=self.mqtt_sign_img)
        elif method == 'http':
            self.sensor2_method_label.config(image=self.http_sign_img)
    
    def sensor3_update(self, date_time, air_pressure, rh, method):
        self.sensor3_date_time_value.config(text=str(date_time))
        self.sensor3_air_pressure_value.config(text=str(air_pressure))
        self.sensor3_rh_value.config(text=str(rh))
        if method == 'mqtt':
            self.sensor3_method_label.config(image=self.mqtt_sign_img)
        elif method == 'http':
            self.sensor3_method_label.config(image=self.http_sign_img)
    
    def sensor4_update(self, pokedex_num, name, poke_class, method):
        self.sensor4_pokedex_num_value.config(text=str(pokedex_num))
        self.sensor4_name_value.config(text=str(name))
        self.sensor4_class_value.config(text=str(poke_class))
        if method == 'mqtt':
            self.sensor4_method_label.config(image=self.mqtt_sign_img)
        elif method == 'http':
            self.sensor4_method_label.config(image=self.http_sign_img)
    
    def sensor5_update(self, mac, light, motion, method):
        self.sensor5_mac_value.config(text=str(mac))
        self.sensor5_light_value.config(text=str(light))
        self.sensor5_motion_value.config(text=str(motion))
        if method == 'mqtt':
            self.sensor5_method_label.config(image=self.mqtt_sign_img)
        elif method == 'http':
            self.sensor5_method_label.config(image=self.http_sign_img)

    def open_messagebox(self, title, message):
        messagebox.showwarning(title, message)

    def data_preview(self, sensor_num, timestamp):
        global tree
        con = sqlite3.connect('sensorsdb.db')
        cur = con.cursor()

        cur.execute(f"""SELECT *
        FROM Sensor{sensor_num}
        WHERE strftime('%s','now', '+1 hour')-strftime('%s', recv_time)<{timestamp}""")
        records = cur.fetchall()
        for record in records:
            print(record)
            tree.insert('', tk.END, values=record)
        con.close()
    
    def save_data_to_csv(self, sensor_num, timestamp):
        con = sqlite3.connect('sensorsdb.db')
        cur = con.cursor()

        cur.execute(f"""SELECT *
        FROM Sensor{sensor_num}
        WHERE strftime('%s','now', '+1 hour')-strftime('%s', recv_time)<{timestamp}""")
        records = cur.fetchall()

        cur.execute(f'PRAGMA table_info(Sensor{sensor_num})')
        table_info = cur.fetchall()
        col_names = [col_info[1] for col_info in table_info]

        df = pd.DataFrame(records, columns=col_names)
        df.to_csv(f'sensor{sensor_num}_last{timestamp}s__{int(time.time())}.csv')

    def clear_treeview(self, tree):
        for i in tree.get_children():
            tree.delete(i)
