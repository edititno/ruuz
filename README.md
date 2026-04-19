# Ruuz — Contextual Commerce Engine

Ruuz is a contextual commerce platform that dynamically adapts Shopify storefronts based on real-time environmental signals. Instead of showing every visitor the same static page, Ruuz reads weather, UV index, air quality, pollen levels, public holidays, national news, stock market sentiment, sunrise/sunset timing, and local time to serve the most relevant products, messaging, imagery, and calls-to-action — all using the merchant's own assets, images, and collections.

**Core thesis:** Ruuz doesn't decide WHO the customer is. It decides WHAT MOMENT the customer is in. The persona stays the same. The context changes.

## Live Demo

The Ruuz Context API is deployed and live at:
**https://web-production-2b083.up.railway.app**

- API root: `/`
- Main context endpoint: `/context?lat=38.9072&lon=-77.0369&country=US`
- Auto-generated API docs: `/docs`

## Ruuz System View

The **Ruuz System View** is a React-based dashboard that visualizes the Ruuz Context API in real time. It renders six live signal cards (weather, UV, air quality, pollen, news, and market) in a 3×2 grid, a hero strip showing the current mood and time of day, and an editorial AI copy preview section that mirrors what the Ruuz engine would render on a storefront. All data is pulled from the Context API in a single request.

Built with **Vite 6**, **React 18**, **Tailwind CSS v4**, and **lucide-react**. The design system uses **Palette 2 (Lapis and Turquoise)**: warm ivory background, midnight navy text, and accents in lapis blue, Persian turquoise, and aged gold. The wordmark pairs lowercase `ruuz` in serif with Persian script روز in aged gold.

### Run locally

    cd system-view
    npm install
    npm run dev

The dev server runs at `http://localhost:5173/`.

## What It Does

When a customer visits a Ruuz-powered store, the engine collects environmental signals and adapts the entire storefront in real time:

- **Announcement banner** — contextual messaging with tiered UV alerts, air quality warnings, pollen alerts, holiday greetings, low-visibility warnings, and market sentiment cues
- **Hero section** — image, headline, and subheadline swap based on weather + time of day, with optional AI-generated copy unique to every visit
- **Featured collection** — warm-weather products when sunny, waterproof gear when raining
- **Pull quote** — brand messaging adapts to match the current context
- **Media sections** — editorial images and copy change to match the mood
- **CTA buttons** — dynamically linked to the relevant collection

All transitions happen instantly on page load.

## How It Works

Ruuz collects multiple environmental signals and combines them to determine what to show. The system has two layers: a FastAPI backend that collects all signals and generates AI-powered copy from a single endpoint, and a client-side JavaScript engine that applies the context to the storefront.

**Backend signals (FastAPI):**

1. **Weather** (OpenWeatherMap) — current conditions, temperature, humidity, wind
2. **UV index** (Open-Meteo) — real-time UV radiation level
3. **Air quality** (OpenWeatherMap) — air pollution index
4. **Pollen** (Open-Meteo) — grass, birch, and ragweed levels
5. **Sunrise/sunset** (OpenWeatherMap) — daylight status and golden hour detection
6. **Public holidays** (Nager.Date) — holiday detection for 100+ countries
7. **News** (GNews) — top national headlines
8. **Stock market** (Alpha Vantage) — S&P 500 price, change, and consumer sentiment
9. **AI copy generation** (OpenAI GPT-4o-mini) — unique headlines, subheadlines, announcements, and pull quotes generated per visit

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
10. News → context for AI copy generation
11. AI copy generation → unique headlines and messaging based on all signals

## Sections Adapted

| Section | What Changes |
|---------|-------------|
| Announcement bar | Weather messaging, UV alerts, air quality warnings, pollen alerts, holiday greetings, low-visibility warnings, market sentiment cues |
| Hero | Image, AI-generated headline and subheadline, CTA button |
| Featured collection | Sunshine Picks or Rainy Day Essentials |
| Pull quote | AI-generated brand copy matching current context |
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

*These are the default fallback headlines. When AI generation is enabled, every visit receives a unique headline based on all context signals.*

**Alert overrides** (take priority over mood messaging)

| Condition | Banner Message |
|-----------|---------------|
| UV index 3-5 | Moderate UV — sunscreen recommended |
| UV index 6-7 | High UV — protect your skin |
| UV index 8-10 | Very high UV — sun protection essential |
| UV index 11+ | Extreme UV — avoid outdoor exposure |
| Air quality Poor/Very Poor | Air quality alert — consider indoor workouts |
| High pollen | High pollen today — allergy-friendly gear recommended |
| Before sunrise / after sunset | Low visibility — reflective gear recommended |
| Holiday detected | Happy [holiday name] — celebrate with our latest picks |
| Stock market drop 2%+ | Market downturn — check out our value picks |
| Multiple triggers | All messages shown together |

## Tech Stack

- **Shopify** — Storefront and product management
- **Shopify Liquid** — Server-side templating for the rainy day collection section
- **JavaScript (Vanilla)** — Client-side context engine handling weather detection, geolocation, time logic, and full DOM manipulation across 7 page sections
- **React 18** — Component library for the Ruuz System View dashboard
- **Vite 6** — Build tool and dev server for the System View
- **Tailwind CSS v4** — Utility-first styling framework for the System View
- **lucide-react** — Icon library used throughout the System View
- **Python** — Data collection logger and SQL database loader
- **FastAPI** — Python backend API serving all context signals from one endpoint
- **OpenAI API (GPT-4o-mini)** — AI-generated headlines, subheadlines, and copy based on real-time context signals
- **SQLite** — Relational database for weather and context data
- **SQL** — Queries for mood distribution, temperature analysis, UV tracking, air quality, and city-level insights
- **Pandas** — Data analysis and manipulation
- **Streamlit** — Two local analytics apps: `data/ruuz_streamlit.py` for charts, alert tables, and data explorer; `quality/ruuz_streamlit.py` for data quality scoring across 16 checks
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

    ruuz/
    ├── api/
    │   └── ruuz_api.py
    ├── assets/
    │   └── ruuz-context.js
    ├── data/
    │   ├── ruuz_data_sample.csv
    │   ├── ruuz_db.py
    │   ├── ruuz_logger.py
    │   └── ruuz_streamlit.py
    ├── quality/
    │   ├── ruuz_quality.py
    │   └── ruuz_streamlit.py
    ├── sections/
    │   └── ruuz-rainy.liquid
    ├── system-view/
    │   ├── public/
    │   ├── src/
    │   │   ├── assets/
    │   │   ├── components/
    │   │   │   └── SignalCard.jsx
    │   │   ├── App.css
    │   │   ├── App.jsx
    │   │   ├── index.css
    │   │   └── main.jsx
    │   ├── .gitignore
    │   ├── eslint.config.js
    │   ├── index.html
    │   ├── package.json
    │   ├── package-lock.json
    │   └── vite.config.js
    ├── .gitignore
    ├── Procfile
    ├── README.md
    └── requirements.txt

## Product Vision

Ruuz is designed as a proof of concept for a broader contextual commerce platform.

**Signal expansion (completed):** Weather, UV index, air quality, pollen, IP geolocation, public holidays, sunrise/sunset timing, national news, and stock market sentiment. Future additions include local news by city, sports scores, and social media trending topics.

**Merchant experience:** Zero-config mode that works with existing collections and assets immediately. Smart auto-tagging using ML-powered product classification that scans titles, descriptions, and tags to suggest context mappings. **Data quality scoring (completed)** — a free Python tool that analyzes Shopify product exports and generates a weighted readiness score across 16 checks spanning critical fields (images, descriptions, pricing), high-importance fields (SKUs, inventory, SEO, tags), medium-importance fields (shipping weight, compare-at price), and minor fields (barcodes, categorization, duplicates). Merchants get an actionable report with specific items to fix, prioritized by impact. Merchant dashboard for mapping triggers to collections without touching code.

**LLM-powered content (completed):** Dynamic headline and copy generation using the OpenAI API (GPT-4o-mini). The backend sends all context signals to the LLM, which generates a unique headline, subheadline, announcement, and pull quote for every visit. No two customers see the same copy.

**AI brand voice training (future):** The next evolution of AI-generated content trains the LLM on each merchant's actual brand voice by analyzing their existing product descriptions, About page, marketing emails, and social media copy. Generated headlines and messaging will sound like the merchant wrote them, not generic. This also extends to auto-generating product descriptions, collection copy, and email subject lines based on real-time context, reducing the merchant's content workload while keeping their voice consistent across every customer touchpoint.

**Tiered model:** Free tier with 2 mood mappings, basic weather and time signals, and the data quality scoring tool. Pro tier with unlimited moods, all signals, analytics dashboard, auto-tagging, and LLM-generated content. Enterprise tier with multi-store support, custom API integrations, and A/B testing to validate contextual commerce performance against static storefronts.

**A/B testing:** Contextual commerce and A/B testing work together. A/B testing validates whether contextual adaptation actually improves conversion rates by showing 50% of visitors the Ruuz-adapted storefront and 50% the default static page, then comparing results. This is how merchants prove ROI.

**Ethics and data practices:** Environmental data (weather, UV, air quality per city) is stored for analytics and model training — this is not personal data. Visitor session data is stored in anonymized form (city, mood served, collection shown, click-through) for merchant analytics dashboards. No personally identifiable information is collected or stored. Algorithmic transparency with optional "personalized for your local weather" badge. Product diversity safeguards to prevent geographic filter bubbles. GDPR-compliant data handling. Privacy disclosure generator for merchants.

## About

Ruuz was built as a project while completing a Master's in Data Analytics (ML focus). The project demonstrates product thinking, real-time API integration, contextual personalization, full-stack development, data pipeline engineering, AI-powered content generation, and ethical considerations applied to e-commerce.

The name "Ruuz" is inspired by the Farsi word روز (rooz), meaning "day" — reflecting the engine's core function of adapting the shopping experience to the conditions of the day.
