# IoT
1. Setup your virtual enviroment, change *VENV* variable in *start_all_sensors.sh* file to your rcfile path. Otherwise you won't be able to run all sensors using one script.  
2. Create main database by running *create_main_database.py*.  
3. Run *start_all_sensors.sh* or start sensors one by one using */Sensors/Sensor<sensor_num>/sensor<sensor_num>.py* script.  
4. Run *aggregator.py* to start receiving data from sensors and storing it in *sensorsdb.db* created previously in step 2.  
5. Run *manager.py* to preview stored data and manage the sensors.  
