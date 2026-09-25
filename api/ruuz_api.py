# Ruuz Context API v4.0
# FastAPI backend — all context signals + AI-generated headlines
# Signals: weather, UV, air quality, pollen, holidays, news, stock market, sunrise/sunset
# AI: Claude generates unique headlines based on all signals

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import requests
from datetime import datetime
import anthropic
from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import json

app = FastAPI(title='Ruuz Context API', version='4.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'https://ruuz.vercel.app',
        'https://ruuz-dev.myshopify.com',
        'http://localhost:5173',
    ],
    allow_methods=['GET'],
    allow_headers=['X-API-Key', 'Content-Type'],
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# API Keys — loaded from environment variables (Railway or local)
import os
OPENWEATHER_KEY = os.environ.get('OPENWEATHER_KEY', '')
GNEWS_KEY = os.environ.get('GNEWS_KEY', '')
ALPHAVANTAGE_KEY = os.environ.get('ALPHAVANTAGE_KEY', '')
ANTHROPIC_KEY = os.environ.get('ANTHROPIC_KEY', '')

claude_client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

# API authentication
RUUZ_API_KEY = os.environ.get('RUUZ_API_KEY', '')
api_key_header = APIKeyHeader(name='X-API-Key', auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)):
    if not RUUZ_API_KEY:
        raise HTTPException(status_code=500, detail='API key not configured on server')
    if api_key != RUUZ_API_KEY:
        raise HTTPException(status_code=401, detail='Invalid or missing API key')
    return api_key

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
    # two-way family the storefront engine keys its assets on
    if weather_code in [800, 801, 802]:
        return 'sunny'
    return 'rainy'

def get_condition(weather_code):
    # six-way read of the sky, from OpenWeather's code ranges
    if weather_code in [800, 801, 802]:
        return 'sunny'
    if weather_code in [803, 804]:
        return 'cloudy'
    if 200 <= weather_code < 300:
        return 'stormy'
    if 300 <= weather_code < 600:
        return 'rainy'
    if 600 <= weather_code < 700:
        return 'snowy'
    if 700 <= weather_code < 800:
        return 'foggy'
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

# ---- Agentic mode: the toolbox ----
# Each entry describes one capability to Claude in the Anthropic tool-use
# format: a name, a plain-English description (this is what Claude reads to
# decide), and a JSON schema of the arguments it must supply.
AGENT_TOOLS = [
    {
        "name": "get_weather",
        "description": "Current weather for the shopper's location: temperature, conditions, sunrise and sunset times. Useful for almost any storefront moment.",
        "input_schema": {
            "type": "object",
            "properties": {
                "lat": {"type": "number", "description": "latitude"},
                "lon": {"type": "number", "description": "longitude"},
            },
            "required": ["lat", "lon"],
        },
    },
    {
        "name": "get_uv",
        "description": "UV index at the location. Worth fetching for daytime, outdoor, skincare, or sun-related products.",
        "input_schema": {
            "type": "object",
            "properties": {
                "lat": {"type": "number"},
                "lon": {"type": "number"},
            },
            "required": ["lat", "lon"],
        },
    },
    {
        "name": "get_air_quality",
        "description": "Air quality index at the location. Relevant for outdoor activity, fitness, and health-adjacent products.",
        "input_schema": {
            "type": "object",
            "properties": {
                "lat": {"type": "number"},
                "lon": {"type": "number"},
            },
            "required": ["lat", "lon"],
        },
    },
    {
        "name": "get_pollen",
        "description": "Pollen level at the location. Relevant for allergies, outdoor time, and seasonal products.",
        "input_schema": {
            "type": "object",
            "properties": {
                "lat": {"type": "number"},
                "lon": {"type": "number"},
            },
            "required": ["lat", "lon"],
        },
    },
    {
        "name": "get_holiday",
        "description": "Whether today is a public holiday in the shopper's country. Worth checking for gifting, celebration, or closure-related messaging.",
        "input_schema": {
            "type": "object",
            "properties": {
                "country": {"type": "string", "description": "two-letter country code, e.g. US"},
            },
            "required": ["country"],
        },
    },
    {
        "name": "get_market",
        "description": "Today's S&P 500 movement and sentiment. Only relevant for finance-adjacent, luxury, or big-ticket contexts.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
]

# maps a tool name Claude requests to the real function that answers it;
# doubling as the allowlist: a name not in this dict cannot be executed
AGENT_TOOL_RUNNERS = {
    "get_weather": lambda a: fetch_weather(a["lat"], a["lon"]),
    "get_uv": lambda a: fetch_uv(a["lat"], a["lon"]),
    "get_air_quality": lambda a: fetch_air_quality(a["lat"], a["lon"]),
    "get_pollen": lambda a: fetch_pollen(a["lat"], a["lon"]),
    "get_holiday": lambda a: fetch_holiday(a["country"]),
    "get_market": lambda a: fetch_stock_market(),
}

# ---- Agentic mode: the loop ----
# Instead of the pipeline (fetch everything, then write), here Claude is given
# the tools and decides what it needs. It may call tools, read results, call
# more, and only writes when it judges it has enough. This is the agentic
# pattern: the model directs the work; this function is just the hands.
def run_agent(lat, lon, country, merchant=None, city=None, hour=None):
    # two voices: a storefront line when a merchant is given,
    # a line about the moment itself when nothing is being sold
    if merchant:
        system = (
            "You write one short, vivid storefront line for a contextual-commerce "
            "platform. You have tools that report the shopper's live conditions. "
            "Call ONLY the tools this moment actually needs, then write. Do not "
            "call a tool whose signal wouldn't change the copy. Keep the final "
            "line under 20 words, concrete, no emojis, plain text only: no markdown, no dashes."
        )
    else:
        system = (
            "You write one short, vivid line about what it is like to be in this "
            "place at this moment: the sky, the hour, the air, the day. You have "
            "tools that report live conditions. Call ONLY the tools that matter "
            "for this moment, then write. Keep the final line under 25 words, "
            "concrete, plain text only: no markdown, no dashes, no emojis."
        )

    # the visitor's local hour, if the client sent it; the server clock otherwise
    if hour is None:
        tod = get_time_of_day()
    else:
        tod = 'morning' if 5 <= hour < 12 else 'afternoon' if 12 <= hour < 17 else 'evening'

    place = city or f"lat {lat}, lon {lon}"
    situation = f"Place: {place} (lat {lat}, lon {lon}, country {country}). Local time: {tod}."
    if merchant:
        situation += f" The store sells: {merchant}."

    # the running transcript Claude and the loop pass back and forth
    messages = [{"role": "user", "content": situation}]
    trace = []          # which tools were chosen, in order: our observability
    MAX_ROUNDS = 5      # guardrail: the loop can never run forever

    for _ in range(MAX_ROUNDS):
        resp = claude_client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=400,
            system=system,
            tools=AGENT_TOOLS,
            messages=messages,
        )

        # Claude signals it wants tools by stopping with reason "tool_use"
        if resp.stop_reason == "tool_use":
            # record Claude's turn verbatim so the next call has full context
            messages.append({"role": "assistant", "content": resp.content})

            tool_results = []
            for block in resp.content:
                if block.type == "tool_use":
                    trace.append(block.name)
                    runner = AGENT_TOOL_RUNNERS.get(block.name)
                    # allowlist enforcement: unknown name = refused, not run
                    if runner is None:
                        out = {"error": f"unknown tool {block.name}"}
                    else:
                        try:
                            out = runner(block.input)
                        except Exception as e:
                            out = {"error": str(e)}
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(out),
                    })
            # hand every tool's answer back to Claude for the next round
            messages.append({"role": "user", "content": tool_results})
            continue

        # any other stop reason means Claude is done and wrote its line
        text = "".join(b.text for b in resp.content if b.type == "text").strip()
        return {"copy": text, "tools_used": trace, "rounds": len(trace)}

    # safety net: hit the round cap without a final answer
    return {"copy": None, "tools_used": trace, "rounds": len(trace), "note": "max rounds reached"}

def generate_ai_copy(context):
    try:
        prompt = f"""You are a copywriter for a women's activewear store. Generate storefront copy based on the current context.

Current conditions:
- Weather: {context['weather']['description']}, {context['weather']['temp']}F (feels like {context['weather']['feels_like']}F)
- Mood: {context['mood']}
- Sky condition: {context['condition']}- Time of day: {context['time_of_day']}
- Daylight: {context['daylight']}
- UV index: {context['uv']['index']} ({context['uv']['alert']})
- Air quality: {context['air_quality']['label']}
- Pollen: {context['pollen']['alert']}
- Holiday: {context['holiday'] or 'none'}
- Top news: {context['news']['top_headline'] or 'none'}
- Stock market: S&P 500 {context['stock_market']['sentiment']} ({context['stock_market']['change_percent']}%)

Generate exactly 9 lines, one per line, no labels, no quotes, no extra text:
Line 1: A short, punchy hero headline (5-8 words)
Line 2: A hero subheadline (8-15 words)
Line 3: An announcement banner message (8-15 words)
Line 4: A pull quote about the brand (15-25 words)
Line 5: Media section 1 heading (3-6 words)
Line 6: Media section 1 description (10-18 words)
Line 7: Media section 2 heading (3-6 words)
Line 8: Media section 2 description (10-18 words)
Line 9: A short ribbon banner message (4-8 words)

Make the copy feel natural, energetic, and relevant to the current conditions. Reference the weather or conditions naturally without being overly literal. If there is a holiday, weave it into at least one line. CRITICAL RULES: Never invent prices, discounts, percentages off, sales, promo codes, or specific dollar amounts. Never mention shipping promotions. The merchant controls all pricing and offers. Stick to lifestyle and product benefit messaging only."""
        
        response = claude_client.messages.create(
            model='claude-haiku-4-5',
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=400
        )

        lines = response.content[0].text.strip().split('\n')
        lines = [line.strip() for line in lines if line.strip()]

        if len(lines) >= 9:
            return {
                'headline': lines[0],
                'subheadline': lines[1],
                'announcement': lines[2],
                'pull_quote': lines[3],
                'media1_heading': lines[4],
                'media1_text': lines[5],
                'media2_heading': lines[6],
                'media2_text': lines[7],
                'ribbon': lines[8],
                'generated': True
            }
    except Exception as e:
        print(f"[Ruuz] AI generation error: {e}")

    return {
        'headline': None,
        'subheadline': None,
        'announcement': None,
        'pull_quote': None,
        'media1_heading': None,
        'media1_text': None,
        'media2_heading': None,
        'media2_text': None,
        'ribbon': None,
        'generated': False
    }


@app.get('/')
def home():
    return {
        'name': 'Ruuz Context API',
        'version': '4.0',
        'signals': ['weather', 'uv_index', 'air_quality', 'pollen', 'holidays', 'news', 'stock_market', 'sunrise_sunset', 'time_of_day'],
        'ai': 'Claude (claude-haiku-4-5) for dynamic headline generation',
        'status': 'running'
    }


@app.get('/context')
@limiter.limit("30/minute")
def get_context(request: Request, lat: float, lon: float, country: str = 'US', ai: bool = True, api_key: str = Depends(verify_api_key)):
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
    condition = 'sunny'
    daylight = 'daylight'
    if weather:
        mood = get_mood(weather['code'])
        condition = get_condition(weather['code'])
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
            'sunset': weather['sunset'],
            'sunrise_ts': weather['sunrise_ts'],
            'sunset_ts': weather['sunset_ts']
        }

    # Build context for AI
    context = {
        'mood': mood,
        'condition': condition,
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

@app.get('/agent')
@limiter.limit("10/minute")
def get_agent(request: Request, lat: float, lon: float, country: str = 'US', merchant: str = None, city: str = None, hour: int = None, api_key: str = Depends(verify_api_key)):
    """
    Agentic endpoint. Unlike /context (which fetches every signal, then writes),
    Claude is handed the toolbox and decides which signals this moment needs.
    Returns the copy plus the trace of tools it chose, in order.
    """
    result = run_agent(lat, lon, country, merchant, city, hour)
    return {'source': 'agent', 'model': 'claude-haiku-4-5', **result}

@app.get('/news')
@limiter.limit("30/minute")
def get_news(request: Request, country: str = 'US', api_key: str = Depends(verify_api_key)):
    """Returns top news headlines for a country."""
    news = fetch_news(country)
    return {
        'country': country,
        'article_count': len(news),
        'articles': news,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


@app.get('/stock')
@limiter.limit("30/minute")
def get_stock(request: Request, api_key: str = Depends(verify_api_key)):
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
