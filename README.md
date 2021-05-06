# Internet of things course project
It's an internet of things devices manager with a graphical user interface. Every sensor is an individual local webserver. The action of a sensor emitting data is simulated by iterating over pandas dataframes. Each sensor handles various requests such as turn on/off, turn on/off additional acctuators, change config, etc. Aggregator, also a webserver, is constantly receving the data and then aggregates it into the database. Sensors and aggregator communicate over http protocol or specified mqtt broker. Manager fetches sensors data from the database and display it in gui.

<img src="https://user-images.githubusercontent.com/56606076/117352890-caceea80-aeaf-11eb-9b85-3ba3bee64f2f.gif" width=643, height=551>

# Usage
1. Setup your virtual enviroment, change ***VENV*** variable in ***start_all_sensors.sh*** file to your rcfile path. Otherwise you won't be able to run all sensors using one script.
2. Create main database by running ***create_main_database.py***.
3. Run ***start_all_sensors.sh*** or start sensors one by one using ***/Sensors/Sensor<sensor_num>/sensor<sensor_num>.py*** script.
4. Run ***aggregator.py*** to start receiving data from sensors and storing it in ***sensorsdb.db*** created previously in step 2.
5. Run ***manager.py*** to preview stored data and manage the sensors.
