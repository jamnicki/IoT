import sqlite3

dbconn = sqlite3.connect('sensorsdb.db')
conn_cursor = dbconn.cursor()

for i in range(1, 6):
    conn_cursor.execute(f"DELETE FROM Sensor{i}")

dbconn.commit()
dbconn.close()