// api/sky.js — asks Ruuz for the visitor's context, returns a slim package.
// Runs server-side on Vercel: the Ruuz key lives in env vars, never the browser.
export default async function handler(req, res) {
  try {
    // Vercel geolocates every request and hands us the coordinates as headers.
    // No permission popups. Falls back to DC if the headers are missing.
    const lat = parseFloat(req.headers["x-vercel-ip-latitude"]) || 38.9072
    const lon = parseFloat(req.headers["x-vercel-ip-longitude"]) || -77.0369
    const country = req.headers["x-vercel-ip-country"] || "US"

    // ai=false: signals only, zero Claude spend
    const url = `https://web-production-2b083.up.railway.app/context?lat=${lat}&lon=${lon}&country=${country}&ai=false`
    const r = await fetch(url, { headers: { "X-API-Key": process.env.RUUZ_API_KEY } })
    if (!r.ok) throw new Error("ruuz unavailable")
    const c = await r.json()

    // slim it down to exactly what the instrument needs
    const sky = {
      city: req.headers["x-vercel-ip-city"] ? decodeURIComponent(req.headers["x-vercel-ip-city"]) : null,
      mood: c.mood ?? null,
      time_of_day: c.time_of_day ?? null,
      daylight: c.daylight ?? null,
      sun: { rise_ts: c.weather?.sunrise_ts ?? null, set_ts: c.weather?.sunset_ts ?? null },
      weather: { temp: c.weather?.temp ?? null, description: c.weather?.description ?? null },
      uv: { index: c.uv?.index ?? null, alert: c.uv?.alert ?? null },
      air: c.air_quality?.label ?? null,
      pollen: c.pollen?.alert ?? null,
      holiday: c.holiday ?? null,
      market: { change: c.stock_market?.change_percent ?? null, sentiment: c.stock_market?.sentiment ?? null },
    }

    // cache 10 min at the edge so Ruuz and its signal APIs aren't hammered
    res.setHeader("Cache-Control", "s-maxage=600, stale-while-revalidate=3600")
    res.setHeader("Access-Control-Allow-Origin", "*")
    res.status(200).json({ sky, source: "ruuz" })
  } catch (e) {
    // Ruuz asleep? The site's clock-based sky takes over seamlessly.
    res.status(200).json({ sky: null, source: "fallback" })
  }
}