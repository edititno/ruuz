# Ruuz Context API v4.0
# FastAPI backend — all context signals + AI-generated headlines
# Signals: weather, UV, air quality, pollen, holidays, news, stock market, sunrise/sunset
# AI: OpenAI generates unique headlines based on all signals

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from datetime import datetime
from openai import OpenAI

app = FastAPI(title='Ruuz Context API', version='4.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)

# API Keys — loaded from environment variables (Railway or local)
import os
OPENWEATHER_KEY = os.environ.get('OPENWEATHER_KEY', '')
GNEWS_KEY = os.environ.get('GNEWS_KEY', '')
ALPHAVANTAGE_KEY = os.environ.get('ALPHAVANTAGE_KEY', '')
OPENAI_KEY = os.environ.get('OPENAI_KEY', '')

openai_client = OpenAI(api_key=OPENAI_KEY)

# Caches
holiday_cache = {}
news_cache = {}
stock_cache = {}

def get_time_of_day():
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return 'morning'
    elif 12 <= hour < 17:
        return 'afternoon'
    return 'evening'

def get_mood(weather_code):
    if weather_code in [800, 801, 802]:
        return 'sunny'
    return 'rainy'

def get_uv_alert(uv):
    if uv >= 11:
        return 'extreme'
    elif uv >= 8:
        return 'very-high'
    elif uv >= 6:
        return 'high'
    elif uv >= 3:
        return 'moderate'
    return 'low'

def get_air_alert(aqi):
    if aqi >= 4:
        return 'poor'
    return 'good'

def get_pollen_level(code):
    if code >= 4:
        return 'very-high'
    elif code >= 3:
        return 'high'
    elif code >= 2:
        return 'moderate'
    elif code >= 1:
        return 'low'
    return 'none'

def get_daylight_status(sunrise_ts, sunset_ts):
    now = datetime.now().timestamp()
    if now < sunrise_ts:
        return 'before-sunrise'
    elif now > sunset_ts:
        return 'after-sunset'
    else:
        time_to_sunset = sunset_ts - now
        if time_to_sunset < 3600:
            return 'golden-hour'
        return 'daylight'

def fetch_weather(lat, lon):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_KEY}&units=imperial"
        data = requests.get(url).json()
        if 'weather' in data:
            return {
                'description': data['weather'][0]['description'],
                'code': data['weather'][0]['id'],
                'temp': round(data['main']['temp']),
                'feels_like': round(data['main']['feels_like']),
                'humidity': data['main']['humidity'],
                'wind_speed': round(data['wind']['speed']),
                'sunrise_ts': data['sys']['sunrise'],
                'sunset_ts': data['sys']['sunset'],
                'sunrise': datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M'),
                'sunset': datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M')
            }
    except:
        pass
    return None

def fetch_uv(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=uv_index"
        data = requests.get(url).json()
        if data.get('current') and data['current'].get('uv_index') is not None:
            return round(data['current']['uv_index'], 1)
    except:
        pass
    return 0

def fetch_pollen(lat, lon):
    try:
        url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=grass_pollen,birch_pollen,ragweed_pollen"
        data = requests.get(url).json()
        if data.get('current'):
            grass = data['current'].get('grass_pollen', 0) or 0
            birch = data['current'].get('birch_pollen', 0) or 0
            ragweed = data['current'].get('ragweed_pollen', 0) or 0

            max_pollen = max(grass, birch, ragweed)
            if max_pollen >= 100:
                level = 5
            elif max_pollen >= 50:
                level = 4
            elif max_pollen >= 20:
                level = 3
            elif max_pollen >= 5:
                level = 2
            elif max_pollen > 0:
                level = 1
            else:
                level = 0

            return {
                'grass': round(grass),
                'birch': round(birch),
                'ragweed': round(ragweed),
                'level': level,
                'alert': get_pollen_level(level)
            }
    except:
        pass
    return {'grass': 0, 'birch': 0, 'ragweed': 0, 'level': 0, 'alert': 'none'}

def fetch_air_quality(lat, lon):
    try:
        url = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={OPENWEATHER_KEY}"
        data = requests.get(url).json()
        if data.get('list') and len(data['list']) > 0:
            aqi = data['list'][0]['main']['aqi']
            labels = ['', 'Good', 'Fair', 'Moderate', 'Poor', 'Very Poor']
            return {'index': aqi, 'label': labels[aqi]}
    except:
        pass
    return {'index': 1, 'label': 'Good'}

def fetch_holiday(country):
    today = datetime.now().strftime('%Y-%m-%d')
    cache_key = f"{country}_{today}"

    if cache_key in holiday_cache:
        return holiday_cache[cache_key]

    try:
        year = datetime.now().year
        url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/{country}"
        holidays = requests.get(url).json()

        for holiday in holidays:
            if holiday['date'] == today:
                holiday_cache[cache_key] = holiday['localName']
                return holiday['localName']

        holiday_cache[cache_key] = None
        return None
    except:
        return None

def fetch_news(country):
    today = datetime.now().strftime('%Y-%m-%d')
    cache_key = f"{country}_{today}_{datetime.now().hour}"

    if cache_key in news_cache:
        return news_cache[cache_key]

    try:
        url = f"https://gnews.io/api/v4/top-headlines?country={country.lower()}&lang=en&max=5&apikey={GNEWS_KEY}"
        data = requests.get(url).json()

        if data.get('articles') and len(data['articles']) > 0:
            articles = []
            for article in data['articles']:
                articles.append({
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'source': article.get('source', {}).get('name', ''),
                    'url': article.get('url', ''),
                    'published': article.get('publishedAt', '')
                })
            news_cache[cache_key] = articles
            return articles
    except:
        pass
    return []

def fetch_stock_market():
    cache_key = datetime.now().strftime('%Y-%m-%d_%H')

    if cache_key in stock_cache:
        return stock_cache[cache_key]

    try:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=SPY&apikey={ALPHAVANTAGE_KEY}"
        data = requests.get(url).json()

        if data.get('Global Quote'):
            quote = data['Global Quote']
            price = float(quote.get('05. price', 0))
            change = float(quote.get('09. change', 0))
            change_pct = quote.get('10. change percent', '0%').replace('%', '')

            if float(change_pct) >= 1:
                sentiment = 'bullish'
            elif float(change_pct) <= -1:
                sentiment = 'bearish'
            else:
                sentiment = 'neutral'

            result = {
                'symbol': 'SPY',
                'price': round(price, 2),
                'change': round(change, 2),
                'change_percent': round(float(change_pct), 2),
                'sentiment': sentiment
            }
            stock_cache[cache_key] = result
            return result
    except:
        pass
    return {'symbol': 'SPY', 'price': 0, 'change': 0, 'change_percent': 0, 'sentiment': 'neutral'}

def generate_ai_copy(context):
    try:
        prompt = f"""You are a copywriter for a women's activewear store. Generate storefront copy based on the current context.

Current conditions:
- Weather: {context['weather']['description']}, {context['weather']['temp']}F (feels like {context['weather']['feels_like']}F)
- Mood: {context['mood']}
- Time of day: {context['time_of_day']}
- Daylight: {context['daylight']}
- UV index: {context['uv']['index']} ({context['uv']['alert']})
- Air quality: {context['air_quality']['label']}
- Pollen: {context['pollen']['alert']}
- Holiday: {context['holiday'] or 'none'}
- Top news: {context['news']['top_headline'] or 'none'}
- Stock market: S&P 500 {context['stock_market']['sentiment']} ({context['stock_market']['change_percent']}%)

Generate exactly 4 lines, one per line, no labels, no quotes, no extra text:
Line 1: A short, punchy headline (5-8 words)
Line 2: A subheadline (8-15 words)
Line 3: An announcement banner message (8-15 words)
Line 4: A pull quote about the brand (15-25 words)

Make the copy feel natural, energetic, and relevant to the current conditions. Reference the weather or conditions naturally without being overly literal. If there is a holiday, weave it into at least one line."""

        response = openai_client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=200,
            temperature=0.8
        )

        lines = response.choices[0].message.content.strip().split('\n')
        lines = [line.strip() for line in lines if line.strip()]

        if len(lines) >= 4:
            return {
                'headline': lines[0],
                'subheadline': lines[1],
                'announcement': lines[2],
                'pull_quote': lines[3],
                'generated': True
            }
    except Exception as e:
        print(f"[Ruuz] AI generation error: {e}")

    return {
        'headline': None,
        'subheadline': None,
        'announcement': None,
        'pull_quote': None,
        'generated': False
    }


@app.get('/')
def home():
    return {
        'name': 'Ruuz Context API',
        'version': '4.0',
        'signals': ['weather', 'uv_index', 'air_quality', 'pollen', 'holidays', 'news', 'stock_market', 'sunrise_sunset', 'time_of_day'],
        'ai': 'OpenAI GPT-4o-mini for dynamic headline generation',
        'status': 'running'
    }


@app.get('/context')
def get_context(lat: float, lon: float, country: str = 'US', ai: bool = True):
    """
    Main endpoint. Returns all context signals + AI-generated copy.
    Set ai=false to skip AI generation and save API costs.
    """

    # Collect all signals
    weather = fetch_weather(lat, lon)
    uv = fetch_uv(lat, lon)
    air = fetch_air_quality(lat, lon)
    pollen = fetch_pollen(lat, lon)
    holiday = fetch_holiday(country)
    news = fetch_news(country)
    stock = fetch_stock_market()
    time_of_day = get_time_of_day()

    # Determine mood
    mood = 'sunny'
    daylight = 'daylight'
    if weather:
        mood = get_mood(weather['code'])
        daylight = get_daylight_status(weather['sunrise_ts'], weather['sunset_ts'])

    # Build alert messages
    alerts = []
    uv_alert = get_uv_alert(uv)
    air_alert = get_air_alert(air['index'])

    if holiday:
        alerts.append(f"Happy {holiday} — celebrate with our latest picks")

    if uv >= 11:
        alerts.append(f"Extreme UV ({round(uv)}) — avoid outdoor exposure")
    elif uv >= 8:
        alerts.append(f"Very high UV ({round(uv)}) — sun protection essential")
    elif uv >= 6:
        alerts.append(f"High UV ({round(uv)}) — protect your skin")
    elif uv >= 3:
        alerts.append(f"Moderate UV ({round(uv)}) — sunscreen recommended")

    if air['index'] >= 4:
        alerts.append("Air quality alert — consider indoor workouts")

    if pollen['level'] >= 4:
        alerts.append("High pollen today — allergy-friendly gear recommended")

    if daylight in ['before-sunrise', 'after-sunset']:
        alerts.append("Low visibility — reflective gear recommended")

    if stock['sentiment'] == 'bearish' and stock['change_percent'] <= -2:
        alerts.append("Market downturn — check out our value picks")

    # Clean weather response
    weather_clean = None
    if weather:
        weather_clean = {
            'description': weather['description'],
            'code': weather['code'],
            'temp': weather['temp'],
            'feels_like': weather['feels_like'],
            'humidity': weather['humidity'],
            'wind_speed': weather['wind_speed'],
            'sunrise': weather['sunrise'],
            'sunset': weather['sunset']
        }

    # Build context for AI
    context = {
        'mood': mood,
        'time_of_day': time_of_day,
        'daylight': daylight,
        'weather': weather_clean or {'description': 'clear sky', 'temp': 70, 'feels_like': 70},
        'uv': {'index': uv, 'alert': uv_alert},
        'air_quality': {'index': air['index'], 'label': air['label'], 'alert': air_alert},
        'pollen': pollen,
        'holiday': holiday,
        'news': {
            'top_headline': news[0]['title'] if len(news) > 0 else None,
            'source': news[0]['source'] if len(news) > 0 else None,
            'article_count': len(news)
        },
        'stock_market': stock,
        'country': country,
        'alerts': alerts,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    # Generate AI copy
    ai_copy = {'generated': False}
    if ai:
        ai_copy = generate_ai_copy(context)

    # Final response
    context['ai_copy'] = ai_copy
    return context


@app.get('/news')
def get_news(country: str = 'US'):
    """Returns top news headlines for a country."""
    news = fetch_news(country)
    return {
        'country': country,
        'article_count': len(news),
        'articles': news,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


@app.get('/stock')
def get_stock():
    """Returns current S&P 500 (SPY) market data and sentiment."""
    stock = fetch_stock_market()
    return {
        'market': stock,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


if __name__ == '__main__':
    import uvicorn
    print('=== Ruuz Context API v4.0 ===')
    print('Starting server on http://localhost:8000')
    print('API docs at http://localhost:8000/docs')
    print()
    uvicorn.run(app, host='0.0.0.0', port=8000)
