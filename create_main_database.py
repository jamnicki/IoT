import sqlite3


conn = sqlite3.connect("sensorsdb.db")
c = conn.cursor()

c.execute("""CREATE TABLE Sensor1
             (recv_time TEXT, room_id TEXT, noted_date TEXT, temp REAL, method TEXT)""")

c.execute("""CREATE TABLE Sensor2
             (recv_time TEXT, date_time TEXT, wind_speed REAL, wind_direction REAL, method TEXT)""")

c.execute("""CREATE TABLE Sensor3
             (recv_time TEXT, date_time TEXT, air_pressure REAL, rh REAL, method TEXT)""")

c.execute("""CREATE TABLE Sensor4
             (recv_time TEXT, pokedex_num INTEGER, name TEXT, class real, method TEXT)""")

c.execute("""CREATE TABLE Sensor5
             (recv_time TEXT, mac TEXT, light TEXT, motion TEXT, method TEXT)""")

conn.commit()
conn.close()