# database.py
import streamlit as st
import pandas as pd
import sqlite3

# Database setup
db_file = "weather_data.db"
conn = sqlite3.connect(db_file, check_same_thread=False)
c = conn.cursor()

# Drop the table if it exists (only do this if you can afford to lose data)
# c.execute('DROP TABLE IF EXISTS current_weather')

# Create tables if they don't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS current_weather (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT,
        date TEXT,
        temperature REAL,
        humidity REAL,
        dew_point REAL,
        precipitation REAL,
        wind_speed REAL,
        conditions TEXT,
        UNIQUE(city, date)
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS forecast_weather (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT,
        date TEXT,
        temp_max REAL,
        temp_min REAL,
        humidity REAL,
        conditions TEXT,
        feels_like REAL,
        wind REAL,
        wind_direction TEXT,
        icon TEXT,
        UNIQUE(city, date)
    )
''')

conn.commit()

def save_current_weather(city, weather_data):
    today_date = pd.Timestamp.today().strftime('%Y-%m-%d')
    c.execute('''
        INSERT INTO current_weather (city, date, temperature, humidity, dew_point, precipitation, wind_speed, conditions)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(city, date) DO UPDATE SET 
            temperature = excluded.temperature,
            humidity = excluded.humidity,
            dew_point = excluded.dew_point,
            precipitation = excluded.precipitation,
            wind_speed = excluded.wind_speed,
            conditions = excluded.conditions
    ''', (city, today_date, weather_data['Temperature (°C)'], weather_data['Humidity (%)'], 
        weather_data['Dew Point (°C)'], weather_data['Precipitation (mm)'], 
        weather_data['Wind Speed (km/h)'], weather_data['Conditions']))
    conn.commit()


def save_forecast_weather(city, forecast_data):
    for day in forecast_data:
        c.execute('''INSERT OR IGNORE INTO forecast_weather (city, date, temp_max, temp_min, humidity, conditions, feels_like, wind, wind_direction, icon)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (city, day['Date'], day['Tempmax'], day['Tempmin'], day['Humidity'], day['Conditions'], day['Feelslike'], day['Wind'],
                   day['Wind Direction'], day['icon']))
    conn.commit()

def get_weather_data():
    current_df = pd.read_sql_query("SELECT date, city, temperature, humidity, dew_point, precipitation, wind_speed, conditions FROM current_weather", conn)
    forecast_df = pd.read_sql_query("SELECT date, city, temp_max, temp_min, humidity, feels_like, wind, wind_direction, conditions FROM forecast_weather", conn)
    return current_df, forecast_df

def download_csv(df, filename):
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(label=f"Download {filename}", data=csv, file_name=filename, mime='text/csv')

def display_weather_tables():
    current_df, forecast_df = get_weather_data()
    
    with st.expander("📌 Current Weather Data"):
        st.dataframe(current_df)
        download_csv(current_df, "current_weather.csv")
    
    with st.expander("📅 7-Day Forecast Data"):
        st.dataframe(forecast_df)
        download_csv(forecast_df, "forecast_weather.csv")
        
# Database setup
# mydb= mysql.connector.connect(host= 'localhost', user= 'root', password= '1234', database= 'weather_database')
# mycourse= mydb.cursor()

# # mycourse.execute("CREATE DATABASE IF NOT EXISTS weather_database")

# # Drop the table if it exists (only do this if you can afford to lose data)
# # mycourse.execute('DROP TABLE IF EXISTS current_weather')
# # mycourse.execute('DROP TABLE IF EXISTS forecast_weather')

# # Create tables if they don't exist
# mycourse.execute('''
#     CREATE TABLE IF NOT EXISTS current_weather (
#         id INT AUTO_INCREMENT PRIMARY KEY,
#         city VARCHAR(200),
#         date DATE,
#         temperature FLOAT,
#         humidity FLOAT,
#         dew_point FLOAT,
#         precipitation FLOAT,
#         wind_speed FLOAT,
#         conditions TEXT,
#         UNIQUE(city, date)
#     )
# ''')

# mycourse.execute('''
#     CREATE TABLE IF NOT EXISTS forecast_weather (
#         id INT AUTO_INCREMENT PRIMARY KEY,
#         city VARCHAR(200),
#         date DATE,
#         temp_max FLOAT,
#         temp_min FLOAT,
#         humidity FLOAT,
#         conditions TEXT,
#         feels_like FLOAT,
#         wind FLOAT,
#         wind_direction TEXT,
#         UNIQUE(city, date)
#     )
# ''')

# mydb.commit()

# def save_current_weather(city, weather_data):
#     today_date = pd.Timestamp.today().strftime('%Y-%m-%d')
    
#     query='''
#         INSERT INTO current_weather (city, date, temperature, humidity, dew_point, precipitation, wind_speed, conditions)
#         VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
#         ON DUPLICATE KEY UPDATE
#             temperature = VALUES(temperature),
#             humidity = VALUES(humidity),
#             dew_point = VALUES(dew_point),
#             precipitation = VALUES(precipitation),
#             wind_speed = VALUES(wind_speed),
#             conditions = VALUES(conditions)
#     '''
    
#     cursor= mydb.cursor()
#     cursor.execute(query, (city, today_date,  weather_data['Temperature (°C)'], weather_data['Humidity (%)'], 
#                       weather_data['Dew Point (°C)'], weather_data['Precipitation (mm)'], 
#                       weather_data['Wind Speed (km/h)'], weather_data['Conditions']))
#     mydb.commit()
#     cursor.close()

# def save_forecast_weather(city, forecast_data):
#     cursor= mydb.cursor()
    
#     for day in forecast_data:
#         query= '''
#                 INSERT INTO forecast_weather (city, date, temp_max, temp_min, humidity, conditions, feels_like, wind, wind_direction)
#                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
#                 ON DUPLICATE KEY UPDATE 
#                 temp_max = VALUES(temp_max),
#                 temp_min = VALUES(temp_min),
#                 humidity = VALUES(humidity),
#                 conditions = VALUES(conditions),
#                 feels_like = VALUES(feels_like),
#                 wind = VALUES(wind),
#                 wind_direction = VALUES(wind_direction) 
#                 '''
                
#         cursor.execute(query, (city, day['Date'], day['Tempmax'], day['Tempmin'], day['Humidity'], day['Conditions'], day['Feelslike'], day['Wind'],
#                    day['Wind Direction']))
#     mydb.commit()
#     cursor.close()

# def get_weather_data():
#     cursor= mydb.cursor(dictionary= True)  # Dictionary cursor returns results as dictionaries

#     cursor.execute("SELECT date, city, temperature, humidity, dew_point, precipitation, wind_speed, conditions FROM current_weather")
#     current_weather_records= cursor.fetchall()

#     cursor.execute("SELECT date, city, temp_max, temp_min, humidity, feels_like, wind, wind_direction, conditions FROM forecast_weather")
#     forecast_weather_records= cursor.fetchall()

#     cursor.close()

#     # Convert fetched data to Pandas DataFrame
#     current_df= pd.DataFrame(current_weather_records)
#     forecast_df= pd.DataFrame(forecast_weather_records)
#     return current_df, forecast_df

# def download_csv(df, filename):
#     csv = df.to_csv(index=False).encode('utf-8')
#     st.download_button(label=f"Download {filename}", data=csv, file_name=filename, mime='text/csv')

# def display_weather_tables():
#     current_df, forecast_df = get_weather_data()
    
#     with st.expander("📌 Current Weather Data"):
#         st.dataframe(current_df)
#         download_csv(current_df, "current_weather.csv")
    
#     with st.expander("📅 7-Day Forecast Data"):
#         st.dataframe(forecast_df)
#         download_csv(forecast_df, "forecast_weather.csv")

