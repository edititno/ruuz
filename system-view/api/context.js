// Vercel serverless function: proxies requests to the Ruuz Context API.
// Keeps the RUUZ_API_KEY secret (server-side only). Coordinates come from
// the query when given, otherwise from Vercel's geolocation headers.
export default async function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  const lat = req.query.lat || req.headers['x-vercel-ip-latitude'] || '38.9'
  const lon = req.query.lon || req.headers['x-vercel-ip-longitude'] || '-77.0'
  const country = req.query.country || req.headers['x-vercel-ip-country'] || 'US'
  const city = req.headers['x-vercel-ip-city']
    ? decodeURIComponent(req.headers['x-vercel-ip-city'])
    : null

  // the dashboard shows signals, not pipeline copy: ai stays off unless asked
  const ai = req.query.ai || 'false'

  const railwayUrl = `https://web-production-2b083.up.railway.app/context?lat=${lat}&lon=${lon}&country=${country}&ai=${ai}`

  try {
    const response = await fetch(railwayUrl, {
      headers: { 'X-API-Key': process.env.RUUZ_API_KEY },
    })
    if (!response.ok) {
      return res.status(response.status).json({ error: 'Upstream API error' })
    }
    const data = await response.json()

    // per-visitor answer, never shared through a cache
    res.setHeader('Cache-Control', 'private, no-store')
    return res.status(200).json({ ...data, city })
  } catch (error) {
    console.error('Proxy error:', error)
    return res.status(500).json({ error: 'Failed to fetch context' })
  }
}