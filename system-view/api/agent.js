// Vercel serverless function: proxies the dashboard's requests to Ruuz's
// /agent endpoint. The Ruuz key stays server-side. Coordinates come from
// the query when given, otherwise from Vercel's geolocation headers, so the
// dashboard is about wherever its visitor actually is.
export default async function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  // the visitor's place: explicit query wins, edge geolocation is the default
  const lat = req.query.lat || req.headers['x-vercel-ip-latitude'] || '38.9'
  const lon = req.query.lon || req.headers['x-vercel-ip-longitude'] || '-77.0'
  const country = req.query.country || req.headers['x-vercel-ip-country'] || 'US'
  const city = req.headers['x-vercel-ip-city']
    ? decodeURIComponent(req.headers['x-vercel-ip-city'])
    : null

  // optional: what the store sells, and the visitor's local hour
  const merchant = req.query.merchant || ''
  const hour = req.query.hour || ''

  const params = new URLSearchParams({ lat, lon, country })
  if (merchant) params.set('merchant', merchant.slice(0, 80))
  if (city) params.set('city', city)
  if (hour !== '') params.set('hour', hour)

  const url = `https://web-production-2b083.up.railway.app/agent?${params.toString()}`

  try {
    const response = await fetch(url, {
      headers: { 'X-API-Key': process.env.RUUZ_API_KEY },
    })
    if (!response.ok) {
      return res.status(response.status).json({ error: 'Upstream API error' })
    }
    const data = await response.json()

    // every visitor gets their own answer: nothing shared, nothing cached
    res.setHeader('Cache-Control', 'private, no-store')
    return res.status(200).json({ ...data, city, lat, lon })
  } catch (error) {
    return res.status(500).json({ error: 'Failed to reach the agent' })
  }
}