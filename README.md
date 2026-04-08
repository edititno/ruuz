# Ruuz — Contextual Commerce Engine

Ruuz is a contextual commerce platform that dynamically adapts Shopify storefronts based on real-time environmental signals. Instead of showing every visitor the same static storefront, Ruuz reads the weather, time of day, and location to serve the most relevant products, messaging, imagery, and calls-to-action automatically.

**Core thesis:** Ruuz doesn't decide WHO the customer is. It decides WHAT MOMENT the customer is in. The persona stays the same. The context changes.

## What It Does

When a customer visits a Ruuz-powered store, the engine collects environmental signals and adapts the entire storefront in real time:

- **Announcement banner** — contextual messaging
- **Hero section** — image, headline, and subheadline swap based on weather + time of day
- **Featured collection** — warm-weather products when sunny, waterproof gear when raining
- **Pull quote** — brand messaging adapts to match the current context
- **Media sections** — editorial images and copy change to match the mood
- **CTA buttons** — dynamically linked to the relevant collection

All transitions happen instantly on page load.

## How It Works

Ruuz uses three data inputs to determine what to show:

1. **Browser geolocation** — detects the visitor's coordinates (falls back to a default location if denied)
2. **OpenWeatherMap API** — fetches current weather conditions at that location
3. **Local time** — determines morning, afternoon, or evening for copy variations

The engine processes these inputs and applies a "mood" (sunny or rainy) combined with the time of day. This creates 6 unique storefront states, each with its own headline, subheadline, announcement, pull quote, editorial copy, images, and featured collection.

## Sections Adapted

| Section | What Changes |
|---------|-------------|
| Announcement bar | Weather-specific messaging |
| Hero | Image, headline, subheadline, CTA button |
| Featured collection | Sunshine Picks or Rainy Day Essentials |
| Pull quote | Brand copy matching current context |
| Media with text (x2) | Images, headings, body copy, button links |

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

## Tech Stack

- **Shopify** — Storefront and product management
- **Shopify Liquid** — Server-side templating for the rainy day collection section
- **JavaScript (Vanilla)** — Client-side context engine handling weather detection, geolocation, time logic, and full DOM manipulation across 7 page sections
- **Python** — Data collection logger and SQL database loader
- **SQLite** — Relational database for weather and context data
- **SQL** — Queries for mood distribution, temperature analysis, and city-level insights
- **Pandas** — Data analysis and manipulation
- **Streamlit** — Interactive analytics dashboard
- **OpenWeatherMap API** — Real-time weather data
- **ipapi.co** — IP-based geolocation fallback (no browser permission needed)
- **Open-Meteo API** — UV index data (free, no key required)
- **OpenWeatherMap Air Pollution API** — Air quality index data
- **HTML/CSS** — Responsive rainy collection layout
- **Figma** — UI/UX design and mockups

## File Structure

```
ruuz/
├── assets/
│   └── ruuz-context.js          # Context engine v0.4
├── data/
│   ├── ruuz_dashboard.py        # Streamlit analytics dashboard
│   ├── ruuz_data_sample.csv     # Sample weather data output
│   ├── ruuz_db.py               # SQLite database loader + SQL queries
│   └── ruuz_logger.py           # Python data logger (10 cities)
├── sections/
│   └── ruuz-rainy.liquid         # Hidden rainy day collection
└── README.md
```
## Product Vision

Ruuz is designed as a proof of concept for a broader contextual commerce platform.

**Signal expansion:** Temperature thresholds, UV index, air quality index, IP geolocation, public holidays, sunrise/sunset, local and national news, and stock market sentiment.

**Merchant experience:** Zero-config mode that works with existing collections immediately. Smart auto-tagging using ML-powered product classification. Data quality scoring with actionable readiness assessments. Merchant dashboard for mapping triggers to collections.

**Tiered model:** Free tier with 2 mood mappings and basic signals. Pro tier with unlimited moods, all signals, analytics dashboard, and auto-tagging. Enterprise tier with multi-store support, custom APIs, and A/B testing.

**Ethics and data practices:** Geolocation data minimized to city-level and not stored beyond session. Algorithmic transparency with optional personalization badge. Product diversity safeguards to prevent geographic filter bubbles. GDPR-compliant data handling. Privacy disclosure generator for merchants.

## About

Ruuz was built as part of a portfolio project while completing a Master's in Data Analytics (ML focus). The project demonstrates product thinking, real-time data integration, contextual personalization, UX design, and ethical considerations applied to e-commerce.

The name "Ruuz" is inspired by the Farsi word روز (rooz), meaning "day" — reflecting the engine's core function of adapting the shopping experience to the conditions of the day.
