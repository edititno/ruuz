# Ruuz: Context Intelligence Platform

Ruuz is a context intelligence platform: an API that reads the live environmental, economic, and cultural signals around a person (weather, UV, air quality, pollen, sunrise and sunset, public holidays, news, market sentiment, local time) and turns them into a picture of the moment they are in, plus AI-written copy for that moment.

**Two production consumers run on it today:**

- **Contextual commerce for Shopify** (the first vertical): storefronts that adapt in real time, serving the most relevant products, messaging, imagery, and calls-to-action using the merchant's own assets.
- **[mystillmornings.com](https://www.mystillmornings.com)**: a live site whose 3D instrument sets its light by each visitor's real sunrise and sunset and engraves their readings, all served by Ruuz through a server-side call.

The same signal engine and LLM orchestration layer can power adjacent markets including ad bidding, dynamic pricing, travel, and logistics.

**Core thesis:** Ruuz doesn't decide WHO the customer is. It decides WHAT MOMENT the customer is in. The persona stays the same. The context changes.

## Live Demo

**Ruuz Context API (backend, live):**
**<https://web-production-2b083.up.railway.app>**

* API root: `/`
* Pipeline endpoint: `/context?lat=38.9072&lon=-77.0369&country=US`
* Agentic endpoint: `/agent?lat=38.9072&lon=-77.0369&country=US&merchant=sunscreen`
* Auto-generated API docs: `/docs`

All data endpoints require an `X-API-Key` header.

**Ruuz System View (dashboard, live):**
**<https://ruuz.mystillmornings.com>**

The visitor's own signals, the agent's reading of their moment, and an interactive console where anyone can watch the agent choose.

## What It Does (Shopify vertical)

When a customer visits a Ruuz-powered store, the engine collects environmental signals and adapts the entire storefront in real time:

- **Announcement banner**: contextual messaging with tiered UV alerts, air quality warnings, pollen alerts, holiday greetings, low-visibility warnings, and market sentiment cues
- **Hero section**: image, headline, and subheadline swap based on weather and time of day, with optional AI-generated copy unique to every visit
- **Featured collection**: warm-weather products when sunny, waterproof gear when raining
- **Pull quote**: brand messaging adapts to match the current context
- **Media sections**: editorial images and copy change to match the mood
- **CTA buttons**: dynamically linked to the relevant collection
- **Agentic copy**: given what the merchant sells, Claude decides which live signals the moment needs, fetches only those, and writes from them (see Two Ways to Write Copy)

All transitions happen instantly on page load.

## Agentic Mode

Ruuz runs an agent in production: Claude decides which live signals a moment needs, calls them as tools, and writes from what it gathered. The endpoint is `/agent`, the loop is hand-built on the Anthropic tool-use API, and every response returns the trace of what the agent chose. You can watch it work at [ruuz.mystillmornings.com](https://ruuz.mystillmornings.com).

Ruuz produces AI copy in two modes, and they answer different questions.

**Pipeline mode (`/context`)** is deterministic: the backend fetches every signal, assembles them into one prompt, and Claude writes. The developer decides what the model sees.

**Agentic mode (`/agent`)** inverts that. Claude is handed a toolbox of six signal functions (weather, UV, air quality, pollen, holiday, market) described in the Anthropic tool-use format, plus the shopper's location and what the merchant sells. The model decides which signals this moment needs, the backend executes only those calls, results are returned to the model, and it loops until it judges it has enough to write. The model decides what it needs.

Two calls made minutes apart from the same coordinates on an overcast Washington evening:

| Merchant | Tools the model chose | Rounds | Output |
|---|---|---|---|
| sunscreen and outdoor gear | get_weather, get_uv, get_pollen | 3 | "Overcast won't stop rays. Grab SPF before heading out." |
| luxury watches | get_market | 1 | "Timeless precision, regardless of market moments." |

No rule maps merchants to signals. The selection is the model's judgment, and every response returns the trace (`tools_used`, `rounds`) so that judgment is observable per request.

**Guardrails:** a hard cap of five tool rounds per request, an allowlist so the model can only invoke the six declared tools, per-request tracing for observability, a tighter rate limit than the pipeline endpoint (agent calls spend real tokens), and the same API-key gate as every other endpoint. Signal failures are returned to the model as errors rather than crashing the request.

```
GET /agent?lat=38.9&lon=-77.0&country=US&merchant=luxury%20watches
X-API-Key: <key>
```

```json
{ "source": "agent", "model": "claude-haiku-4-5", "copy": "...", "tools_used": ["get_market"], "rounds": 1 }
```

## How It Works

Ruuz collects multiple environmental signals and combines them to determine what to show. The system has two layers: a FastAPI backend that serves context signals and AI copy, and a client-side JavaScript engine that applies the context to the storefront.

**Backend signals (FastAPI):**

1. **Weather** (OpenWeatherMap): current conditions, temperature, humidity, wind, place name, and a six-way sky condition (sunny, cloudy, rainy, stormy, snowy, foggy) alongside the two-way mood the storefront engine keys on
2. **UV index** (Open-Meteo): real-time UV radiation level
3. **Air quality** (OpenWeatherMap): air pollution index
4. **Pollen** (Open-Meteo): grass, birch, and ragweed levels
5. **Sunrise/sunset** (OpenWeatherMap): daylight status and golden hour detection, exposed as unix timestamps so clients can render local time
6. **Public holidays** (Nager.Date): holiday detection for 100+ countries
7. **News** (GNews): top national headlines
8. **Stock market** (Alpha Vantage): S&P 500 price, change, and consumer sentiment
9. **AI copy generation, pipeline mode** (Claude, claude-haiku-4-5): unique headlines, subheadlines, announcements, and pull quotes generated per visit from all signals
10. **AI copy generation, agentic mode** (Claude tool use): the model selects and calls the signal functions it judges relevant, then writes

**Client-side signals:**

1. **Browser geolocation**: visitor's coordinates (most accurate)
2. **IP geolocation** (ipapi.co): fallback that detects city with no browser permission
3. **Local time**: morning, afternoon, or evening copy variations

In pipeline mode the backend processes all signals into a single JSON response. The engine applies a "mood" (sunny or rainy) combined with time of day, and layers on alerts for UV, air quality, pollen, low visibility, holidays, and market conditions.

**Signal priority chain (pipeline mode):**
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

In agentic mode there is no fixed chain: the model sets the priority per request, and the returned trace records the order it chose.

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

*These are the default fallback headlines. When AI generation is enabled, every visit receives a unique headline based on context signals.*

**Alert overrides** (take priority over mood messaging)

| Condition | Banner Message |
|-----------|---------------|
| UV index 3-5 | Moderate UV, sunscreen recommended |
| UV index 6-7 | High UV, protect your skin |
| UV index 8-10 | Very high UV, sun protection essential |
| UV index 11+ | Extreme UV, avoid outdoor exposure |
| Air quality Poor/Very Poor | Air quality alert, consider indoor workouts |
| High pollen | High pollen today, allergy-friendly gear recommended |
| Before sunrise / after sunset | Low visibility, reflective gear recommended |
| Holiday detected | Happy [holiday name], celebrate with our latest picks |
| Stock market drop 2%+ | Market downturn, check out our value picks |
| Multiple triggers | All messages shown together |

## Security and Operations

- **Keys never touch code.** Every credential (signal APIs, Anthropic, the Ruuz API key) is read from environment variables on Railway.
- **Fail-closed authentication.** Every data endpoint requires `X-API-Key`; if the server-side key is missing the gate refuses everyone rather than admitting everyone.
- **Rate limiting** per client IP on every endpoint (slowapi), tighter on `/agent` because agent calls spend tokens.
- **Agent guardrails:** bounded iterations, tool allowlist, per-request trace.
- **Dependency hygiene:** Dependabot alerts, security updates, and malware alerts enabled; secret scanning with push protection on the repository.
- **Graceful degradation:** consumers treat a null or failed response as "use local defaults," so a signal outage never breaks a storefront.

## Ruuz System View

The **Ruuz System View** at [ruuz.mystillmornings.com](https://ruuz.mystillmornings.com) is a React dashboard that puts the platform in front of a person. It has four parts:

- **The visitor's own sky:** location from the network (labeled approximate), with an opt-in button that asks the browser for precise coordinates; nothing is stored either way. Temperature, conditions, the six-way sky condition (sunny, cloudy, rainy, stormy, snowy, foggy), time of day, and market sentiment.
- **This moment, read by the agent:** on load, the agentic endpoint writes one line about being in this place at this hour, and shows the tools it chose to get there.
- **Live signals:** six cards (weather, UV, air quality, pollen, news, market), everything the agent can see.
- **Ask the agent:** a console. Type what a store sells; the agent decides which signals matter, fetches only those, writes one line, and the chips show its choices in order. In production this line is delivered by the agent's API straight into a storefront, rewritten for every visitor.

The dashboard reaches Ruuz through two small Vercel serverless functions (`system-view/api/context.js` and `system-view/api/agent.js`) that hold the API key server-side and pass the visitor's coordinates through, so no key ever reaches the browser.

Built with **Vite 6**, **React 18**, **Tailwind CSS v4**, and **lucide-react**. The design system uses **Palette 2 (Lapis and Turquoise)**: warm ivory background, midnight navy text, and accents in lapis blue, turquoise, and aged gold. The wordmark pairs lowercase `ruuz` in serif with روز in aged gold.

### Run locally

```
cd system-view
npm install
npm run dev
```

The dev server runs at `http://localhost:5173/`.

## Tech Stack

- **Shopify**: storefront and product management
- **Shopify Liquid**: server-side templating for the rainy day collection section
- **JavaScript (Vanilla)**: client-side context engine handling weather detection, geolocation, time logic, and full DOM manipulation across 7 page sections
- **React 18**: component library for the Ruuz System View dashboard
- **Vite 6**: build tool and dev server for the System View
- **Tailwind CSS v4**: utility-first styling framework for the System View
- **lucide-react**: icon library used throughout the System View
- **Python**: backend, data collection logger, and SQL database loader
- **FastAPI**: Python backend API serving context signals and both copy modes
- **slowapi**: per-IP rate limiting on every endpoint
- **Railway**: cloud platform hosting the FastAPI backend with auto-deploy from the GitHub main branch
- **Vercel**: cloud platform hosting the Ruuz System View dashboard at ruuz.mystillmornings.com, with auto-deploy from the GitHub main branch and serverless proxy functions that keep the API key server-side
- **Claude API (claude-haiku-4-5)**: AI-generated headlines, subheadlines, and copy in pipeline mode
- **Anthropic tool use (Messages API)**: the agentic mode, where Claude selects and calls signal functions through a declared toolbox and a bounded agent loop
- **SQLite**: relational database for weather and context data
- **SQL**: queries for mood distribution, temperature analysis, UV tracking, air quality, and city-level insights
- **Pandas**: data analysis and manipulation
- **Streamlit**: two local analytics apps: `data/ruuz_streamlit.py` for charts, alert tables, and data explorer; `quality/ruuz_streamlit.py` for data quality scoring across 16 checks
- **OpenWeatherMap API**: real-time weather data and sunrise/sunset timing
- **OpenWeatherMap Air Pollution API**: air quality index data
- **Open-Meteo API**: UV index and pollen data (free, no key required)
- **ipapi.co**: IP-based geolocation fallback (no browser permission needed)
- **Nager.Date API**: public holiday detection for 100+ countries (free, no key required)
- **GNews API**: real-time national news headlines
- **Alpha Vantage API**: stock market data and consumer sentiment signals
- **HTML/CSS**: responsive rainy collection layout
- **Figma**: UI/UX design and mockups

## File Structure

    ruuz/
    ├── api/
    │   └── ruuz_api.py          # signal fetchers, pipeline mode (/context), agentic mode (/agent: toolbox, agent loop)
    ├── assets/
    │   └── ruuz-context.js      # client-side context engine
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
    │   ├── api/
    │   │   ├── context.js       # serverless proxy to /context (key stays server-side)
    │   │   └── agent.js         # serverless proxy to /agent
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

Ruuz is a context intelligence platform. The first deployed application is **contextual commerce for Shopify**, with signal expansion and platform hardening underway to support adjacent verticals (ad bidding, dynamic pricing, travel, logistics).

**Signal expansion (completed):** Weather, UV index, air quality, pollen, IP geolocation, public holidays, sunrise/sunset timing, national news, and stock market sentiment.

**Signal expansion (in progress):** Economic context (FRED API, VIX, BLS regional indicators), local events (Eventbrite, Ticketmaster), expanded trend data (Google Trends, Reddit), and hyper-local news. Each new signal becomes both a pipeline input and a tool the agent can choose.

**Merchant experience:** Zero-config mode that works with existing collections and assets immediately. Smart auto-tagging using ML-powered product classification that scans titles, descriptions, and tags to suggest context mappings. **Data quality scoring (completed)**: a free Python tool that analyzes Shopify product exports and generates a weighted readiness score across 16 checks spanning critical fields (images, descriptions, pricing), high-importance fields (SKUs, inventory, SEO, tags), medium-importance fields (shipping weight, compare-at price), and minor fields (barcodes, categorization, duplicates). Merchants get an actionable report with specific items to fix, prioritized by impact. Merchant dashboard for mapping triggers to collections without touching code.

**LLM-powered content (completed):** Dynamic headline and copy generation using the Claude API (claude-haiku-4-5). The backend sends all context signals to the LLM, which generates a unique headline, subheadline, announcement, and pull quote for every visit. No two customers see the same copy.

**Agentic signal selection (completed):** The `/agent` endpoint hands Claude the signal functions as tools and lets it decide which ones a merchant's moment needs, with bounded iteration, an allowlist, and per-request tracing. This is the platform's orchestration layer going forward: new capabilities are added as tools, and the model composes them.

**AI brand voice via RAG (next):** Brand-voice awareness becomes one more tool in the agent's toolbox. Merchant product descriptions, About page, marketing emails, and social media copy are indexed in a vector database (pgvector) and exposed as a `get_brand_voice` tool that retrieves the most relevant passages at generation time. The agent decides when brand context matters and pulls it, producing on-brand copy without model fine-tuning. This extends to auto-generating product descriptions, collection copy, and email subject lines based on real-time context.

**Evaluation and monitoring (next):** Agent traces (`tools_used`, `rounds`, output) are already returned per request; the next step logs them and scores outputs against rules (length, tone, banned claims, signal relevance) so quality is measured continuously rather than assumed.

**Tiered model:** Free tier with 2 mood mappings, basic weather and time signals, and the data quality scoring tool. Pro tier with unlimited moods, all signals, analytics dashboard, auto-tagging, and LLM-generated content. Enterprise tier with multi-store support, custom API integrations, and A/B testing to validate contextual commerce performance against static storefronts.

**A/B testing:** Contextual commerce and A/B testing work together. A/B testing validates whether contextual adaptation actually improves conversion rates by showing 50% of visitors the Ruuz-adapted storefront and 50% the default static page, then comparing results. This is how merchants prove ROI.

**Ethics and data practices:** Environmental, economic, and cultural data (weather, UV, air quality, market indicators per region) is stored for analytics and model training. This is not personal data. Visitor session data is stored in anonymized form (city, mood served, collection shown, click-through) for merchant analytics dashboards. No personally identifiable information is collected or stored. Algorithmic transparency with optional "personalized for your local context" badge. Product diversity safeguards to prevent geographic filter bubbles. GDPR-compliant data handling. Privacy disclosure generator for merchants.

## About

Ruuz was built as a project while completing a Master's in Applied AI. The project demonstrates product thinking, real-time API integration, contextual personalization, full-stack development, data pipeline engineering, generative and agentic AI in production (LLM copy generation and a tool-using agent loop with guardrails), security practices for a live service, and ethical considerations applied to e-commerce.

The name Ruuz means day (روز, rooz), reflecting the engine's core function of adapting an experience to the conditions of the day.
