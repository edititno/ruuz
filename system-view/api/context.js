// Vercel serverless function — proxies requests to Ruuz Context API
// Keeps the RUUZ_API_KEY secret (server-side only)

export default async function handler(req, res) {
  // Only allow GET requests
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  // Extract query parameters
  const { lat, lon, country = 'US', ai = 'true' } = req.query;

  if (!lat || !lon) {
    return res.status(400).json({ error: 'Missing required parameters: lat, lon' });
  }

  // Build Railway URL
  const railwayUrl = `https://web-production-2b083.up.railway.app/context?lat=${lat}&lon=${lon}&country=${country}&ai=${ai}`;

  try {
    const response = await fetch(railwayUrl, {
      method: 'GET',
      headers: {
        'X-API-Key': process.env.RUUZ_API_KEY,
      },
    });

    if (!response.ok) {
      return res.status(response.status).json({ error: 'Upstream API error' });
    }

    const data = await response.json();

    // Set cache headers — cache for 60 seconds to reduce load
    res.setHeader('Cache-Control', 's-maxage=60, stale-while-revalidate=30');

    return res.status(200).json(data);
  } catch (error) {
    console.error('Proxy error:', error);
    return res.status(500).json({ error: 'Failed to fetch context' });
  }
}