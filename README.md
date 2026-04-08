Ruuz — Contextual Commerce Engine
Ruuz is a contextual commerce platform that dynamically adapts Shopify storefronts based on real-time environmental signals. Instead of showing every visitor the same static storefront, Ruuz reads the weather, time of day, and location to serve the most relevant products, messaging, imagery, and calls-to-action automatically.
Core thesis: Ruuz doesn't decide WHO the customer is. It decides WHAT MOMENT the customer is in. The persona stays the same. The context changes.
What It Does
When a customer visits a Ruuz-powered store, the engine collects environmental signals and adapts the entire storefront in real time:
Announcement banner — contextual messaging ("Rain today — stay dry with our waterproof collection")
Hero section — image, headline, and subheadline swap based on weather + time of day
Featured collection — warm-weather products when sunny, waterproof gear when raining
Pull quote — brand messaging adapts to match the current context
Media sections — editorial images and copy change to match the mood
CTA buttons — dynamically linked to the relevant collection
All transitions happen instantly on page load with no noticeable delay to the shopper.
How It Works
Ruuz uses three data inputs to determine what to show:
Browser geolocation — detects the visitor's coordinates (falls back to a default location if denied)
OpenWeatherMap API — fetches current weather conditions at that location
Local time — determines morning, afternoon, or evening for copy variations
The engine processes these inputs and applies a "mood" (sunny or rainy) combined with the time of day. This creates 6 unique storefront states (2 moods x 3 time periods), each with its own headline, subheadline, announcement, pull quote, editorial copy, images, and featured collection.
Sections Adapted
Section	What Changes
Announcement bar	Weather-specific messaging
Hero	Image, headline, subheadline, CTA button
Featured collection	Sunshine Picks or Rainy Day Essentials
Pull quote	Brand copy matching current context
Media with text (x2)	Images, headings, body copy, button links
Context Moods
Sunny mood (clear skies, light clouds)
Time	Headline	Subheadline
Morning	Start Your Morning Strong	Lightweight gear to power your sunrise session
Afternoon	Crush Your Afternoon Session	Breathable layers for peak-heat training
Evening	End the Day Right	Comfortable fits for your sunset cooldown
Rainy mood (rain, snow, fog, heavy clouds, storms)
Time	Headline	Subheadline
Morning	Own the Morning Storm	Waterproof layers to start the day right
Afternoon	Train Through the Rain	Stay dry and focused all afternoon
Evening	Brave the Evening Downpour	Reflective, waterproof gear for after-dark runs
Tech Stack
Shopify — Storefront and product management
Shopify Liquid — Server-side templating for the rainy day collection section
JavaScript (Vanilla) — Client-side context engine handling weather detection, geolocation, time logic, and full DOM manipulation across 7 page sections
OpenWeatherMap API — Real-time weather data
HTML/CSS — Responsive rainy collection layout
Figma — UI/UX design and mockups
File Structure
```
ruuz/
├── assets/
│   └── ruuz-context.js          # Context engine v0.4 — weather, time, full page adaptation
├── sections/
│   └── ruuz-rainy.liquid         # Hidden rainy day collection, shown by JS when weather triggers
└── README.md
```
Product Vision
Ruuz is designed as a proof of concept for a broader contextual commerce platform. The full product vision includes:
Signal expansion:
Temperature thresholds (hot / warm / cool / cold)
UV index (promote SPF and protective gear)
Air quality index (suggest indoor workout alternatives)
IP geolocation (location detection without browser permission)
Public holidays (event-driven promotions)
Sunrise/sunset (reflective gear when dark)
Local and national news (event-driven merchandising)
Stock market sentiment (consumer spending signals)
Merchant experience:
Zero-config mode: works with existing collections immediately
Smart auto-tagging: ML-powered product classification by context
Data quality scoring: actionable readiness assessment for merchant catalogs
Merchant dashboard for mapping triggers to collections
Tiered model:
Free: 2 mood mappings, weather + time signals
Pro: unlimited moods, all signals, analytics dashboard, auto-tagging
Enterprise: multi-store, custom APIs, A/B testing
Ethics and data practices:
Geolocation data minimized to city-level, not stored beyond session
Algorithmic transparency: option for "personalized for your local weather" badge
Product diversity safeguards to prevent geographic filter bubbles
GDPR-compliant data handling
Privacy disclosure generator for merchants
About
Ruuz was built as a portfolio project while completing a Master's in Data Analytics (ML focus)s. The project demonstrates product thinking, real-time data integration, contextual personalization, UX design, and ethical considerations applied to e-commerce.
The name "Ruuz" is inspired by the Farsi word روز (rooz), meaning "day" — reflecting the engine's core function of adapting the shopping experience to the conditions of the day.
