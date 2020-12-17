import sqlite3

dbconn = sqlite3.connect('sensorsdb.db')
conn_cursor = dbconn.cursor()

conn_cursor.execute("DROP TABLE Sensor5")
conn_cursor.execute("DROP TABLE Sensor4")
conn_cursor.execute("DROP TABLE Sensor3")
conn_cursor.execute("DROP TABLE Sensor2")
conn_cursor.execute("DROP TABLE Sensor1")

dbconn.commit()
dbconn.close()