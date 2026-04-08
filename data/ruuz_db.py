# Ruuz Database & SQL Queries v1.0
# Loads CSV data into a SQLite database and runs queries

import sqlite3
import csv
import os

# Database file (will be created in this folder)
DB_FILE = 'ruuz.db'
CSV_FILE = 'ruuz_data.csv'

def create_database():
    """Create the database and load CSV data into it"""
    
    # Connect to database (creates it if it doesn't exist)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create the table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            city TEXT,
            lat REAL,
            lon REAL,
            weather TEXT,
            weather_code INTEGER,
            temp INTEGER,
            feels_like INTEGER,
            humidity INTEGER,
            wind_speed INTEGER,
            sunrise TEXT,
            sunset TEXT,
            time_of_day TEXT,
            mood TEXT
        )
    ''')
    
    # Clear old data so we don't duplicate
    cursor.execute('DELETE FROM weather_logs')
    
    # Load CSV data
    with open(CSV_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute('''
                INSERT INTO weather_logs 
                (timestamp, city, lat, lon, weather, weather_code, temp, feels_like, humidity, wind_speed, sunrise, sunset, time_of_day, mood)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['timestamp'],
                row['city'],
                float(row['lat']),
                float(row['lon']),
                row['weather'],
                int(row['weather_code']),
                int(row['temp']),
                int(row['feels_like']),
                int(row['humidity']),
                int(row['wind_speed']),
                row['sunrise'],
                row['sunset'],
                row['time_of_day'],
                row['mood']
            ))
    
    conn.commit()
    
    # Count records
    cursor.execute('SELECT COUNT(*) FROM weather_logs')
    count = cursor.fetchone()[0]
    print(f'Loaded {count} records into database')
    print()
    
    return conn

def run_queries(conn):
    """Run SQL queries against the data"""
    cursor = conn.cursor()
    
    # QUERY 1: How many records per mood?
    print('=== QUERY 1: Records by Mood ===')
    print('SQL: SELECT mood, COUNT(*) FROM weather_logs GROUP BY mood')
    print()
    cursor.execute('SELECT mood, COUNT(*) as count FROM weather_logs GROUP BY mood')
    for row in cursor.fetchall():
        print(f'  {row[0]}: {row[1]} records')
    print()
    
    # QUERY 2: Average temperature by mood
    print('=== QUERY 2: Average Temperature by Mood ===')
    print('SQL: SELECT mood, ROUND(AVG(temp)) FROM weather_logs GROUP BY mood')
    print()
    cursor.execute('SELECT mood, ROUND(AVG(temp)) as avg_temp FROM weather_logs GROUP BY mood')
    for row in cursor.fetchall():
        print(f'  {row[0]}: {row[1]}F average')
    print()
    
    # QUERY 3: Which cities had rainy mood?
    print('=== QUERY 3: Cities with Rainy Mood ===')
    print('SQL: SELECT DISTINCT city, weather, temp FROM weather_logs WHERE mood = "rainy"')
    print()
    cursor.execute('SELECT DISTINCT city, weather, temp FROM weather_logs WHERE mood = "rainy"')
    for row in cursor.fetchall():
        print(f'  {row[0]}: {row[1]} | {row[2]}F')
    print()
    
    # QUERY 4: Hottest and coldest cities
    print('=== QUERY 4: Temperature Extremes ===')
    print('SQL: SELECT city, MAX(temp), MIN(temp) FROM weather_logs GROUP BY city ORDER BY MAX(temp) DESC')
    print()
    cursor.execute('SELECT city, MAX(temp) as max_temp, MIN(temp) as min_temp FROM weather_logs GROUP BY city ORDER BY max_temp DESC')
    for row in cursor.fetchall():
        print(f'  {row[0]}: High {row[1]}F / Low {row[2]}F')
    print()
    
    # QUERY 5: Mood distribution by city
    print('=== QUERY 5: Mood Distribution by City ===')
    print('SQL: SELECT city, mood, COUNT(*) FROM weather_logs GROUP BY city, mood ORDER BY city')
    print()
    cursor.execute('SELECT city, mood, COUNT(*) as count FROM weather_logs GROUP BY city, mood ORDER BY city')
    for row in cursor.fetchall():
        print(f'  {row[0]}: {row[1]} ({row[2]}x)')
    print()
    
    # QUERY 6: Average humidity by mood
    print('=== QUERY 6: Average Humidity by Mood ===')
    print('SQL: SELECT mood, ROUND(AVG(humidity)) FROM weather_logs GROUP BY mood')
    print()
    cursor.execute('SELECT mood, ROUND(AVG(humidity)) as avg_humidity FROM weather_logs GROUP BY mood')
    for row in cursor.fetchall():
        print(f'  {row[0]}: {row[1]}% average humidity')
    print()

def main():
    print('=== Ruuz Database & SQL Queries v1.0 ===')
    print()
    
    if not os.path.exists(CSV_FILE):
        print(f'Error: {CSV_FILE} not found. Run ruuz_logger.py first to collect data.')
        return
    
    conn = create_database()
    run_queries(conn)
    conn.close()
    
    print(f'Database saved as {DB_FILE}')
    print('=== Done ===')

if __name__ == '__main__':
    main()
