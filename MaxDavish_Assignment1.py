#!/usr/bin/python3
# coding: utf-8

# # Assignment 1
# ### Max Davish: Projects in Programming and Data Science
# 
# The following code will create and populate a database that will query the OpenWeatherMap and CitiBike APIs in order to compare Citibike usage with weather patterns in New York City.

# In[1]:

#Function for getting NYC Weather data:
def getNYCWeather():
    city = "New York"
    key = '097217bc8c67dcadb7f7f7b295429be1'
    import requests
    return requests.get('http://api.openweathermap.org/data/2.5/weather?q={city}&appid={key}'.format(city=city,key=key)).json()


# In[2]:

#Function for getting CitiBike station data:
def getCitiBike():
    import requests
    url = 'http://www.citibikenyc.com/stations/json'
    return requests.get(url).json()["stationBeanList"]
    data = results["stationBeanList"]


# In[3]:

weather_data = getNYCWeather()
weather_data


# In[4]:

citibike_data = getCitiBike()
citibike_data


# In[5]:

#Connection to database:
import MySQLdb as mdb
import sys

con = mdb.connect(host = 'localhost', 
                  user = 'root', 
                  passwd = 'dwdstudent2015', 
                  charset='utf8', use_unicode=True);


# In[6]:

#This code deletes the database if it exists.
#This was a useful cell to have as I designed the database, but now that the code is finished I will comment this part out.
#db_name = 'MaxDavish_CitiBikeWeather'
#create_db_query = "DROP DATABASE IF EXISTS {db}".format(db=db_name)
#cursor = con.cursor()
#cursor.execute(create_db_query)
#cursor.close()


# In[7]:

#Create the database:
db_name = 'MaxDavish_CitiBikeWeather'
create_db_query = "CREATE DATABASE IF NOT EXISTS {db} DEFAULT CHARACTER SET 'utf8'".format(db=db_name)
cursor = con.cursor()
cursor.execute(create_db_query)
cursor.close()


# In[8]:

#Create the table for CitiBike stations (time-invariant):
cursor = con.cursor()
table_name = 'Station'
create_table_query = '''CREATE TABLE IF NOT EXISTS {db}.{table}
                        (Station_ID int,
                        Station_Name varchar(250),
                        Total_Docks int,
                        Latitude float,
                        Longitude float,
                        Address varchar(250),
                        PRIMARY KEY(Station_ID)
                        )'''.format(db=db_name, table=table_name)
cursor.execute(create_table_query)
cursor.close()


# In[9]:

#Create the table for the status of those stations (time_variant data):
cursor = con.cursor()
table_name = 'Station_Status'
create_table_query = '''CREATE TABLE IF NOT EXISTS {db}.{table}
                        (Station_ID int,
                        Timestamp datetime,
                        Available_Docks int,
                        Available_Bikes int,
                        Status_Key int,
                        Status_Value varchar(250),
                        PRIMARY KEY(Station_ID, Timestamp),
                        FOREIGN KEY(Station_ID) REFERENCES {db}.Station(Station_ID)
                        )'''.format(db=db_name, table=table_name)
cursor.execute(create_table_query)
cursor.close()


# In[10]:

#Create the table for the weather data (time-variant):
#We can later join these on days, hours, and minutes. No need for a foreign key connection.
cursor = con.cursor()
table_name = 'Weather_Status'
create_table_query = '''CREATE TABLE IF NOT EXISTS {db}.{table}
                        (Timestamp datetime,
                        Temp float,
                        Description varchar(250),
                        Humidity float,
                        Pressure float,
                        Wind_Speed float,
                        Wind_Degrees float,
                        PRIMARY KEY(Timestamp)
                        )'''.format(db=db_name, table=table_name)
cursor.execute(create_table_query)
cursor.close()


# In[11]:

#Now that the database has been created, we need three separate blocks of code to continually populate the three tables.
#We'll start with the Station Table (although for the most part this table won't need to be updated).
table_name = 'Station'
query_template = '''INSERT IGNORE INTO {db}.{table}(Station_ID, 
                    Station_Name, 
                    Total_Docks, 
                    Latitude, 
                    Longitude, 
                    Address) 
                    VALUES (%s, %s, %s, %s, %s, %s)'''.format(db=db_name, table=table_name)

cursor = con.cursor()

for entry in citibike_data:
    Station_ID = entry["id"]
    Station_Name = entry["stationName"]
    Total_Docks = entry["totalDocks"]
    Latitude = entry["latitude"]
    Longitude = entry["longitude"]
    Address = entry["stAddress1"]
    query_parameters = (Station_ID, Station_Name, Total_Docks, Latitude, Longitude, Address)
    cursor.execute(query_template, query_parameters)

con.commit()
cursor.close()


# In[12]:

#Now the Station_Status Table:
from datetime import date, datetime, timedelta

table_name = 'Station_Status'
query_template = '''INSERT IGNORE INTO {db}.{table}(Station_ID, 
                    Timestamp, 
                    Available_Docks, 
                    Available_Bikes,
                    Status_Key,
                    Status_Value) 
                    VALUES (%s, %s, %s, %s, %s, %s)'''.format(db=db_name, table=table_name)

cursor = con.cursor()

for entry in citibike_data:
    Station_ID = entry["id"]
    Timestamp = datetime.strptime(entry["lastCommunicationTime"],'%Y-%m-%d %I:%M:%S %p')
    Available_Docks = entry["availableDocks"]
    Available_Bikes = entry["availableBikes"]
    Status_Key = entry["statusKey"]
    Status_Value = entry["statusValue"]
    query_parameters = (Station_ID, Timestamp, Available_Docks, Available_Bikes, Status_Key, Status_Value)
    cursor.execute(query_template, query_parameters)

con.commit()
cursor.close()


# In[13]:

#And finally the weather table:
from datetime import date, datetime, timedelta

table_name = 'Weather_Status'
query_template = '''INSERT IGNORE INTO {db}.{table}(Timestamp,
                        Temp,
                        Description,
                        Humidity,
                        Pressure,
                        Wind_Speed,
                        Wind_Degrees) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)'''.format(db=db_name, table=table_name)

cursor = con.cursor()

#Note: We don't need a for loop for this query since we're only adding one row each time.

Timestamp = datetime.now()
Temp = (9/5)*(weather_data["main"]["temp"]-273)+32
#Had to convert from Kelvin to Farenheit.
Description = weather_data["weather"][0]["description"]
Humidity = weather_data["main"]["humidity"]
Pressure = weather_data["main"]["pressure"]
Wind_Speed = weather_data["wind"]["speed"]
Wind_Degrees = weather_data["wind"]["deg"]
query_parameters = (Timestamp, Temp, Description, Humidity, Pressure, Wind_Speed, Wind_Degrees)
cursor.execute(query_template, query_parameters)

con.commit()
cursor.close()


# In[14]:

#We just might want this code later, too:
#def SQLquery(query):
    #cursor = con.cursor()
    #cursor.execute(query)
    #cursor.close()

