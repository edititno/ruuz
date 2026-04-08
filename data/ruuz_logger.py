# Ruuz Data Logger v2.0
# Collects weather, UV index, and air quality data for 10 cities
# Saves everything to a CSV file

import requests
import csv
import os
from datetime import datetime

# Your OpenWeatherMap API key
API_KEY = 'YOUR_OPENWEATHERMAP_API_KEY'

# Cities to check
CITIES = [
    {'name': 'Washington DC', 'lat': 38.9072, 'lon': -77.0369},
    {'name': 'New York', 'lat': 40.7128, 'lon': -74.0060},
    {'name': 'Los Angeles', 'lat': 34.0522, 'lon': -118.2437},
    {'name': 'Chicago', 'lat': 41.8781, 'lon': -87.6298},
    {'name': 'Miami', 'lat': 25.7617, 'lon': -80.1918},
    {'name': 'Seattle', 'lat': 47.6062, 'lon': -122.3321},
    {'name': 'Denver', 'lat': 39.7392, 'lon': -104.9903},
    {'name': 'Atlanta', 'lat': 33.7490, 'lon': -84.3880},
    {'name': 'Boston', 'lat': 42.3601, 'lon': -71.0589},
    {'name': 'Phoenix', 'lat': 33.4484, 'lon': -112.0740}
]

CSV_FILE = 'ruuz_data.csv'

AQI_LABELS = ['', 'Good', 'Fair', 'Moderate', 'Poor', 'Very Poor']

def get_time_of_day():
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return 'morning'
    elif 12 <= hour < 17:
        return 'afternoon'
    else:
        return 'evening'

def get_mood(weather_code):
    if weather_code in [800, 801, 802]:
        return 'sunny'
    return 'rainy'

def get_uv_alert(uv):
    if uv >= 6:
        return 'high'
    return 'normal'

def get_air_alert(aqi):
    if aqi >= 4:
        return 'poor'
    return 'good'

def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={city['lat']}&lon={city['lon']}&appid={API_KEY}&units=imperial"
    try:
        response = requests.get(url)
        data = response.json()
        if 'weather' in data and len(data['weather']) > 0:
            return data
        else:
            print(f"  Weather error for {city['name']}: {data.get('message', 'Unknown')}")
            return None
    except Exception as e:
        print(f"  Weather error for {city['name']}: {e}")
        return None

def get_uv(city):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={city['lat']}&longitude={city['lon']}&current=uv_index"
    try:
        response = requests.get(url)
        data = response.json()
        if data.get('current') and data['current'].get('uv_index') is not None:
            return data['current']['uv_index']
        return 0
    except:
        return 0

def get_air_quality(city):
    url = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={city['lat']}&lon={city['lon']}&appid={API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        if data.get('list') and len(data['list']) > 0:
            return data['list'][0]['main']['aqi']
        return 1
    except:
        return 1

def collect_city_data(city):
    weather_data = get_weather(city)
    if not weather_data:
        return None

    uv = get_uv(city)
    aqi = get_air_quality(city)
    weather_code = weather_data['weather'][0]['id']

    result = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'city': city['name'],
        'lat': city['lat'],
        'lon': city['lon'],
        'weather': weather_data['weather'][0]['description'],
        'weather_code': weather_code,
        'temp': round(weather_data['main']['temp']),
        'feels_like': round(weather_data['main']['feels_like']),
        'humidity': weather_data['main']['humidity'],
        'wind_speed': round(weather_data['wind']['speed']),
        'sunrise': datetime.fromtimestamp(weather_data['sys']['sunrise']).strftime('%H:%M'),
        'sunset': datetime.fromtimestamp(weather_data['sys']['sunset']).strftime('%H:%M'),
        'uv_index': round(uv, 1),
        'uv_alert': get_uv_alert(uv),
        'air_quality': aqi,
        'air_quality_label': AQI_LABELS[aqi],
        'air_alert': get_air_alert(aqi),
        'time_of_day': get_time_of_day(),
        'mood': get_mood(weather_code)
    }
    return result

def save_to_csv(results):
    file_exists = os.path.exists(CSV_FILE)
    
    with open(CSV_FILE, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        if not file_exists:
            writer.writeheader()
        for result in results:
            writer.writerow(result)

def main():
    print('=== Ruuz Data Logger v2.0 ===')
    print(f'Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'Checking weather, UV, and air quality for {len(CITIES)} cities...')
    print()

    results = []

    for city in CITIES:
        data = collect_city_data(city)
        if data:
            results.append(data)
            uv_flag = ' [HIGH UV]' if data['uv_alert'] == 'high' else ''
            air_flag = ' [POOR AIR]' if data['air_alert'] == 'poor' else ''
            print(f"  {data['city']}: {data['weather']} | {data['temp']}F | UV: {data['uv_index']} | Air: {data['air_quality_label']} | Mood: {data['mood']}{uv_flag}{air_flag}")

    if results:
        save_to_csv(results)
        print()
        print(f'Saved {len(results)} records to {CSV_FILE}')
        print(f'Total records in file: {sum(1 for line in open(CSV_FILE)) - 1}')
    else:
        print('No data collected.')

    print()
    print('=== Done ===')

if __name__ == '__main__':
    main()
