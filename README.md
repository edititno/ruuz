# Ruuz — Contextual Commerce Engine

Ruuz is a contextual commerce tool that dynamically adapts Shopify storefronts based on real-time signals like weather conditions and time of day. Instead of showing every visitor the same static storefront, Ruuz reads the environment and serves the most relevant products, messaging, and visuals automatically.

## What It Does

When a customer visits a Ruuz-powered store, the engine detects their location, checks the current weather, and identifies the time of day. Based on those signals, it swaps:

- **Hero imagery** — sunny lifestyle photo vs rainy mood photo
- **Headlines and copy** — tailored to weather + time (e.g., "Start Your Morning Strong" on a clear morning vs "Brave the Evening Downpour" on a rainy night)
- **Featured product collections** — warm-weather gear when it's sunny, waterproof layers when it's raining
- **CTA buttons** — dynamically linked to the relevant collection

All transitions happen instantly on page load with no noticeable delay to the shopper.

## How It Works

Ruuz uses three data inputs to determine what to show:

1. **Browser geolocation** — detects the visitor's coordinates (falls back to a default location if denied)
2. **OpenWeatherMap API** — fetches current weather conditions at that location
3. **Local time** — determines morning, afternoon, or evening for copy variations

A lightweight JavaScript engine processes these inputs and applies the appropriate "mood" (sunny or rainy) combined with the time of day to swap content on the page. The product collections are pre-built in Shopify and rendered server-side using Liquid, with the JavaScript controlling which collection is visible.

## Tech Stack

- **Shopify** — Storefront and product management
- **Shopify Liquid** — Server-side templating for product collections and section rendering
- **JavaScript (Vanilla)** — Client-side context engine handling weather detection, geolocation, and DOM manipulation
- **OpenWeatherMap API** — Real-time weather data
- **CSS** — Responsive styling with smooth transitions between moods
- **Figma** — UI/UX design and mockups

## File Structure

```
ruuz/
├── assets/
│   └── ruuz-context.js        # Context engine — weather detection, time logic, DOM swapping
├── sections/
│   └── ruuz-context.liquid     # Shopify section — hero, collections, product grids
└── README.md
```

## Context Moods

Ruuz currently supports two weather moods, each with three time-of-day variations:

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

## Future Development

- Build as a standalone installable Shopify App using Shopify App Bridge and the Agent SDK
- Add temperature-based thresholds (not just weather codes)
- Add seasonal context (fall/winter collections vs spring/summer)
- Integrate analytics dashboard tracking which mood converts best
- Support additional signals: UV index, wind speed, air quality
- A/B testing between contextual and static storefronts to measure conversion lift

## About

Ruuz was built by Roo as a portfolio project while completing a Master's in Data Analytics (ML focus) at the University of Maryland Global Campus. The project demonstrates product thinking, real-time data integration, and contextual personalization applied to e-commerce.

The name "Ruuz" is inspired by the Farsi word روز (rooz), meaning "day" — reflecting the app's core function of adapting the shopping experience to the conditions of the day.
