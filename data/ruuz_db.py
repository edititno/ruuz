# Ruuz Database & SQL Queries v3.0
# Loads CSV data into SQLite with weather, UV, air quality, and holidays

import sqlite3
import csv
import os

DB_FILE = 'ruuz.db'
CSV_FILE = 'ruuz_data.csv'

def create_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('DROP TABLE IF EXISTS weather_logs')

    cursor.execute('''
        CREATE TABLE weather_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            city TEXT,
            country TEXT,
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
            uv_index REAL,
            uv_alert TEXT,
            air_quality INTEGER,
            air_quality_label TEXT,
            air_alert TEXT,
            holiday TEXT,
            time_of_day TEXT,
            mood TEXT
        )
    ''')

    with open(CSV_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute('''
                INSERT INTO weather_logs 
                (timestamp, city, country, lat, lon, weather, weather_code, temp, feels_like, humidity, wind_speed, sunrise, sunset, uv_index, uv_alert, air_quality, air_quality_label, air_alert, holiday, time_of_day, mood)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['timestamp'],
                row['city'],
                row['country'],
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
                float(row['uv_index']),
                row['uv_alert'],
                int(row['air_quality']),
                row['air_quality_label'],
                row['air_alert'],
                row['holiday'],
                row['time_of_day'],
                row['mood']
            ))

    conn.commit()

    cursor.execute('SELECT COUNT(*) FROM weather_logs')
    count = cursor.fetchone()[0]
    print(f'Loaded {count} records into database')
    print()

    return conn

def run_queries(conn):
    cursor = conn.cursor()

    print('=== QUERY 1: Records by Mood ===')
    cursor.execute('SELECT mood, COUNT(*) as count FROM weather_logs GROUP BY mood')
    for row in cursor.fetchall():
        print(f'  {row[0]}: {row[1]} records')
    print()

    print('=== QUERY 2: Average Temperature by Mood ===')
    cursor.execute('SELECT mood, ROUND(AVG(temp)) as avg_temp FROM weather_logs GROUP BY mood')
    for row in cursor.fetchall():
        print(f'  {row[0]}: {row[1]}F average')
    print()

    print('=== QUERY 3: Cities with High UV ===')
    cursor.execute('SELECT city, uv_index, temp, weather FROM weather_logs WHERE uv_alert IN ("high", "very-high", "extreme") ORDER BY uv_index DESC')
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            print(f'  {row[0]}: UV {row[1]} | {row[2]}F | {row[3]}')
    else:
        print('  No high UV records yet')
    print()

    print('=== QUERY 4: Cities with Poor Air Quality ===')
    cursor.execute('SELECT city, air_quality_label, air_quality, temp FROM weather_logs WHERE air_alert = "poor" ORDER BY air_quality DESC')
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            print(f'  {row[0]}: {row[1]} ({row[2]}/5) | {row[3]}F')
    else:
        print('  No poor air quality records yet')
    print()

    print('=== QUERY 5: Average UV Index by City ===')
    cursor.execute('SELECT city, ROUND(AVG(uv_index), 1) as avg_uv FROM weather_logs GROUP BY city ORDER BY avg_uv DESC')
    for row in cursor.fetchall():
        print(f'  {row[0]}: UV {row[1]}')
    print()

    print('=== QUERY 6: Temperature Extremes ===')
    cursor.execute('SELECT city, MAX(temp) as max_temp, MIN(temp) as min_temp FROM weather_logs GROUP BY city ORDER BY max_temp DESC')
    for row in cursor.fetchall():
        print(f'  {row[0]}: High {row[1]}F / Low {row[2]}F')
    print()

    print('=== QUERY 7: Mood Distribution by City ===')
    cursor.execute('SELECT city, mood, COUNT(*) as count FROM weather_logs GROUP BY city, mood ORDER BY city')
    for row in cursor.fetchall():
        print(f'  {row[0]}: {row[1]} ({row[2]}x)')
    print()

    print('=== QUERY 8: Air Quality Distribution ===')
    cursor.execute('SELECT air_quality_label, COUNT(*) as count FROM weather_logs GROUP BY air_quality_label ORDER BY air_quality')
    for row in cursor.fetchall():
        print(f'  {row[0]}: {row[1]} records')
    print()

    print('=== QUERY 9: Average Humidity by Mood ===')
    cursor.execute('SELECT mood, ROUND(AVG(humidity)) as avg_humidity FROM weather_logs GROUP BY mood')
    for row in cursor.fetchall():
        print(f'  {row[0]}: {row[1]}% average humidity')
    print()

    print('=== QUERY 10: UV Alert Distribution ===')
    cursor.execute('SELECT uv_alert, COUNT(*) as count FROM weather_logs GROUP BY uv_alert ORDER BY count DESC')
    for row in cursor.fetchall():
        print(f'  {row[0]}: {row[1]} records')
    print()

    print('=== QUERY 11: Holiday Records ===')
    cursor.execute('SELECT city, holiday, mood, temp FROM weather_logs WHERE holiday != "none"')
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            print(f'  {row[0]}: {row[1]} | {row[2]} | {row[3]}F')
    else:
        print('  No holiday records yet (run logger on a public holiday to capture)')
    print()

    print('=== QUERY 12: Full Alert Summary ===')
    cursor.execute('SELECT city, COUNT(*) as alerts FROM weather_logs WHERE uv_alert IN ("high", "very-high", "extreme") OR air_alert = "poor" OR holiday != "none" GROUP BY city ORDER BY alerts DESC')
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            print(f'  {row[0]}: {row[1]} alert(s)')
    else:
        print('  No alerts triggered yet')
    print()

def main():
    print('=== Ruuz Database & SQL Queries v3.0 ===')
    print()

    if not os.path.exists(CSV_FILE):
        print(f'Error: {CSV_FILE} not found. Run ruuz_logger.py first.')
        return

    conn = create_database()
    run_queries(conn)
    conn.close()

    print(f'Database saved as {DB_FILE}')
    print('=== Done ===')

if __name__ == '__main__':
    main()
