# Ruuz Data Logger v1.0
# Calls OpenWeatherMap API for multiple cities
# Saves weather data + what mood Ruuz would serve to a CSV file

import requests
import csv
import os
from datetime import datetime

# OpenWeatherMap API key 
API_KEY = 'YOUR_OPENWEATHERMAP_API_KEY'

# Cities to check weather for
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

# File where data will be saved
CSV_FILE = 'ruuz_data.csv'

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

def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={city['lat']}&lon={city['lon']}&appid={API_KEY}&units=imperial"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if 'weather' in data and len(data['weather']) > 0:
            weather_code = data['weather'][0]['id']
            
            result = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'city': city['name'],
                'lat': city['lat'],
                'lon': city['lon'],
                'weather': data['weather'][0]['description'],
                'weather_code': weather_code,
                'temp': round(data['main']['temp']),
                'feels_like': round(data['main']['feels_like']),
                'humidity': data['main']['humidity'],
                'wind_speed': round(data['wind']['speed']),
                'sunrise': datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M'),
                'sunset': datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M'),
                'time_of_day': get_time_of_day(),
                'mood': get_mood(weather_code)
            }
            return result
        else:
            print(f"  Error for {city['name']}: {data.get('message', 'Unknown error')}")
            return None
            
    except Exception as e:
        print(f"  Error for {city['name']}: {e}")
        return None

def save_to_csv(results):
    file_exists = os.path.exists(CSV_FILE)
    
    with open(CSV_FILE, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        
        if not file_exists:
            writer.writeheader()
        
        for result in results:
            writer.writerow(result)

def main():
    print('=== Ruuz Data Logger v1.0 ===')
    print(f'Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'Checking weather for {len(CITIES)} cities...')
    print()
    
    results = []
    
    for city in CITIES:
        weather = get_weather(city)
        if weather:
            results.append(weather)
            print(f"  {weather['city']}: {weather['weather']} | {weather['temp']}F | Mood: {weather['mood']}")
    
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
