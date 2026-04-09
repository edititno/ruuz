# Ruuz — Contextual Commerce Engine

Ruuz is a contextual commerce platform that dynamically adapts Shopify storefronts based on real-time environmental signals. Instead of showing every visitor the same static page, Ruuz reads weather, UV index, air quality, pollen levels, public holidays, national news, stock market sentiment, sunrise/sunset timing, and local time to serve the most relevant products, messaging, imagery, and calls-to-action — all using the merchant's own assets, images, and collections.

**Core thesis:** Ruuz doesn't decide WHO the customer is. It decides WHAT MOMENT the customer is in. The persona stays the same. The context changes.

## What It Does

When a customer visits a Ruuz-powered store, the engine collects environmental signals and adapts the entire storefront in real time:

- **Announcement banner** — contextual messaging with tiered UV alerts, air quality warnings, pollen alerts, holiday greetings, low-visibility warnings, and market sentiment cues
- **Hero section** — image, headline, and subheadline swap based on weather + time of day
- **Featured collection** — warm-weather products when sunny, waterproof gear when raining
- **Pull quote** — brand messaging adapts to match the current context
- **Media sections** — editorial images and copy change to match the mood
- **CTA buttons** — dynamically linked to the relevant collection

All transitions happen instantly on page load.

## How It Works

Ruuz collects multiple environmental signals and combines them to determine what to show. The system has two layers: a FastAPI backend that collects all signals from a single endpoint, and a client-side JavaScript engine that applies the context to the storefront.

**Backend signals (FastAPI):**

1. **Weather** (OpenWeatherMap) — current conditions, temperature, humidity, wind
2. **UV index** (Open-Meteo) — real-time ultraviolet radiation level
3. **Air quality** (OpenWeatherMap) — air pollution index
4. **Pollen** (Open-Meteo) — grass, birch, and ragweed levels
5. **Sunrise/sunset** (OpenWeatherMap) — daylight status and golden hour detection
6. **Public holidays** (Nager.Date) — holiday detection for 100+ countries
7. **News** (GNews) — top national headlines
8. **Stock market** (Alpha Vantage) — S&P 500 price, change, and consumer sentiment

**Client-side signals:**

1. **Browser geolocation** — visitor's coordinates (most accurate)
2. **IP geolocation** (ipapi.co) — fallback that detects city with no browser permission
3. **Local time** — morning, afternoon, or evening copy variations

The backend processes all signals into a single JSON response. The engine applies a "mood" (sunny or rainy) combined with time of day, and layers on alerts for UV, air quality, pollen, low visibility, holidays, and market conditions.

**Signal priority chain:**
1. Browser geolocation → IP geolocation → default coordinates
2. Weather → mood determination
3. UV index → tiered alerts (moderate through extreme)
4. Air quality → alert if Poor or Very Poor
5. Pollen → alert if high
6. Daylight → reflective gear alert if dark
7. Holiday → banner override
8. Stock market → sentiment-based messaging if significant move
9. Time of day → copy variation

## Sections Adapted

| Section | What Changes |
|---------|-------------|
| Announcement bar | Weather-specific messaging, UV and air quality alerts |
| Hero | Image, headline, subheadline, CTA button |
| Featured collection | Sunshine Picks or Rainy Day Essentials |
| Pull quote | Brand copy matching current context |
| Media with text | Images, headings, body copy, button links |

## Context Moods

**Sunny mood** (clear skies, light clouds)

| Time | Headline | Subheadline |
|------|----------|-------------|
| Morning | Start Your Morning Strong | Lightweight gear to power your sunrise session |
| Afternoon | Crush Your Afternoon Session | Breathable layers for peak-heat training |
| Evening | End the Day Right | Comfortable fits for your sunset cooldown |

**Rainy mood** (rain, snow, fog, heavy clouds, storms)

| Time | Headline | Subheadline |
|------|----------|-------------|
| Morning | Own the Morning Storm | Waterproof layers to start the day right |
| Afternoon | Train Through the Rain | Stay dry and focused all afternoon |
| Evening | Brave the Evening Downpour | Reflective, waterproof gear for after-dark runs |

**Alert overrides** (take priority over mood messaging)

| Condition | Banner Message |
|-----------|---------------|
| UV index 3-5 | Moderate UV — sunscreen recommended |
| UV index 6-7 | High UV — protect your skin |
| UV index 8-10 | Very high UV — sun protection essential |
| UV index 11+ | Extreme UV — avoid outdoor exposure |
| Air quality Poor/Very Poor | Air quality alert — consider indoor workouts |
| Multiple triggers | Both messages shown together |

## Tech Stack

- **Shopify** — Storefront and product management
- **Shopify Liquid** — Server-side templating for the rainy day collection section
- **JavaScript (Vanilla)** — Client-side context engine handling weather detection, geolocation, time logic, and full DOM manipulation across 7 page sections
- **Python** — Data collection logger and SQL database loader
- **FastAPI** — Python backend API serving all context signals from one endpoint
- **OpenAI API (GPT-4o-mini)** — AI-generated headlines, subheadlines, and copy based on real-time context signals
- **SQLite** — Relational database for weather and context data
- **SQL** — Queries for mood distribution, temperature analysis, UV tracking, air quality, and city-level insights
- **Pandas** — Data analysis and manipulation
- **Streamlit** — Interactive analytics dashboard with charts, alert tables, and data explorer
- **OpenWeatherMap API** — Real-time weather data and sunrise/sunset timing
- **OpenWeatherMap Air Pollution API** — Air quality index data
- **Open-Meteo API** — UV index and pollen data (free, no key required)
- **ipapi.co** — IP-based geolocation fallback (no browser permission needed)
- **Nager.Date API** — Public holiday detection for 100+ countries (free, no key required)
- **GNews API** — Real-time national news headlines
- **Alpha Vantage API** — Stock market data and consumer sentiment signals
- **HTML/CSS** — Responsive rainy collection layout
- **Figma** — UI/UX design and mockups

## File Structure

```
ruuz/
├── api/
│   └── ruuz_api.py
├── assets/
│   └── ruuz-context.js
├── data/
│   ├── ruuz_dashboard.py
│   ├── ruuz_data_sample.csv
│   ├── ruuz_db.py
│   └── ruuz_logger.py
├── sections/
│   └── ruuz-rainy.liquid
└── README.md
```
## Product Vision

Ruuz is designed as a proof of concept for a broader contextual commerce platform.

**Signal expansion (completed):** Weather, UV index, air quality, pollen, IP geolocation, public holidays, sunrise/sunset timing, national news, and stock market sentiment. Future additions include local news by city, sports scores, and social media trending topics.

**Merchant experience:** Zero-config mode that works with existing collections and assets immediately. Smart auto-tagging using ML-powered product classification that scans titles, descriptions, and tags to suggest context mappings. Data quality scoring offered as a free tool that gives merchants an actionable readiness report — not just a pass/fail score, but specific items to fix with direct links to each problem in their Shopify admin. Merchant dashboard for mapping triggers to collections without touching code.

**LLM-powered content:** Dynamic headline and copy generation using the Anthropic or OpenAI API, trained on the merchant's existing content style. Instead of rotating through a fixed set of headlines, every visit generates a fresh, context-aware headline that fits the moment.

**Tiered model:** Free tier with 2 mood mappings, basic weather and time signals, and the data quality scoring tool. Pro tier with unlimited moods, all signals, analytics dashboard, auto-tagging, and LLM-generated content. Enterprise tier with multi-store support, custom API integrations, and A/B testing to validate contextual commerce performance against static storefronts.

**A/B testing:** Contextual commerce and A/B testing work together. A/B testing validates whether contextual adaptation actually improves conversion rates by showing 50% of visitors the Ruuz-adapted storefront and 50% the default static page, then comparing results. This is how merchants prove ROI.

**Ethics and data practices:** Environmental data (weather, UV, air quality per city) is stored for analytics and model training — this is not personal data. Visitor session data is stored in anonymized form (city, mood served, collection shown, click-through) for merchant analytics dashboards. No personally identifiable information is collected or stored. Algorithmic transparency with optional "personalized for your local weather" badge. Product diversity safeguards to prevent geographic filter bubbles. GDPR-compliant data handling. Privacy disclosure generator for merchants.

## About

Ruuz was built as a project while completing a Master's in Data Analytics (ML focus). The project demonstrates product thinking, real-time API integration, contextual personalization, full-stack development, data pipeline engineering, and ethical considerations applied to e-commerce.

The name "Ruuz" is inspired by the Farsi word روز (rooz), meaning "day" — reflecting the engine's core function of adapting the shopping experience to the conditions of the day.
