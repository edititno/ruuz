import { useState, useEffect } from 'react'
import SignalCard from './components/SignalCard'

function App() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch('/api/context?lat=38.9072&lon=-77.0369')
      .then((response) => {
        if (!response.ok) throw new Error(`Backend returned ${response.status}`)
        return response.json()
      })
      .then((json) => {
        console.log('Ruuz data received:', json)
        setData(json)
        setLoading(false)
      })
      .catch((err) => {
        console.error('Ruuz fetch error:', err)
        setError(err.message)
        setLoading(false)
      })
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-[#f8f5ed] text-[#1e2a44] flex items-center justify-center font-serif">
        <p className="text-lg tracking-wide">Loading Ruuz System View...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-[#f8f5ed] text-[#1e2a44] flex items-center justify-center font-serif">
        <div className="max-w-md text-center">
          <h1 className="text-2xl mb-2 text-[#8b2c1a]">Connection error</h1>
          <p className="text-sm">{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#f8f5ed] text-[#1e2a44] font-serif">
      {/* Header */}
      <header className="border-b border-[#1e2a44]/10 px-8 py-5 flex items-center justify-between">
        <div className="flex items-baseline gap-3">
          <h1 className="text-2xl tracking-tight lowercase">ruuz</h1>
          <span className="text-sm text-[#c29a3e]" lang="fa">روز</span>
        </div>
        <div className="text-xs uppercase tracking-[0.2em] text-[#1e2a44]/60">
          Ruuz System View
        </div>
      </header>

      {/* Hero strip */}
      <section className="px-8 py-10 border-b border-[#1e2a44]/10">
        <p className="text-xs uppercase tracking-[0.25em] text-[#2a5a8a] mb-3">
          Washington, DC
        </p>
        <h2 className="text-4xl md:text-5xl font-light mb-2">
          {data.weather.temp}°F, {data.weather.description}
        </h2>
        <p className="text-[#1e2a44]/70">
          Mood: <span className="text-[#2a5a8a]">{data.mood}</span> · Time: <span className="text-[#2a5a8a]">{data.time_of_day}</span> · S&P: <span className="text-[#2a5a8a]">${data.stock_market.price}</span> <span className="text-[#c29a3e]">({data.stock_market.sentiment})</span>
        </p>
      </section>

      {/* Signal cards grid */}
      <section className="px-8 py-10">
        <h3 className="text-xs uppercase tracking-[0.25em] text-[#1e2a44]/60 mb-6">
          Live Signals
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          <SignalCard
            type="weather"
            title="Weather"
            value={`${data.weather.temp}°F`}
            detail={`Feels ${data.weather.feels_like}° · ${data.weather.humidity}% humidity · ${data.weather.description}`}
          />
          <SignalCard
            type="uv"
            title="UV Index"
            value={data.uv.index}
            detail={`Sunrise ${data.weather.sunrise} · Sunset ${data.weather.sunset}`}
            alert={data.uv.alert}
          />
          <SignalCard
            type="air"
            title="Air Quality"
            value={data.air_quality.label}
            detail={`AQI level ${data.air_quality.index} of 5`}
            alert={data.air_quality.alert}
          />
          <SignalCard
            type="pollen"
            title="Pollen"
            value={data.pollen.alert === 'none' ? 'None' : `Level ${data.pollen.level}`}
            detail={`Grass ${data.pollen.grass} · Birch ${data.pollen.birch} · Ragweed ${data.pollen.ragweed}`}
            alert={data.pollen.alert}
          />
          <SignalCard
            type="news"
            title="Top News"
            value={`${data.news.article_count} stories`}
            detail={`${data.news.top_headline} · ${data.news.source}`}
          />
          <SignalCard
            type="market"
            title={data.stock_market.symbol}
            value={`$${data.stock_market.price}`}
            detail={`${data.stock_market.change >= 0 ? '+' : ''}${data.stock_market.change} (${data.stock_market.change_percent}%)`}
            alert={data.stock_market.sentiment}
            trend={data.stock_market.change > 0 ? 'up' : data.stock_market.change < 0 ? 'down' : 'flat'}
          />
        </div>
      </section>

      {/* AI copy preview */}
      <section className="px-8 py-16 border-t border-[#1e2a44]/10 bg-[#f3efe3]">
        <div className="max-w-3xl mx-auto">
          <div className="flex items-center justify-between mb-10">
            <h3 className="text-xs uppercase tracking-[0.25em] text-[#1e2a44]/60">
              AI Storefront Copy
            </h3>
            {data.ai_copy.generated && (
              <span className="text-xs uppercase tracking-wider text-[#c29a3e]">
                ✦ Generated
              </span>
            )}
          </div>

          <p className="text-xs uppercase tracking-[0.3em] text-[#2a5a8a] mb-4">
            {data.ai_copy.ribbon}
          </p>

          <h1 className="text-5xl md:text-6xl font-light leading-[1.05] mb-5 text-[#1e2a44]">
            {data.ai_copy.headline}
          </h1>

          <p className="text-xl md:text-2xl font-light text-[#1e2a44]/75 leading-snug mb-10 max-w-2xl">
            {data.ai_copy.subheadline}
          </p>

          <div className="text-sm uppercase tracking-wider text-[#2a5a8a] mb-12 pb-6 border-b border-[#1e2a44]/15">
            {data.ai_copy.announcement}
          </div>

          <blockquote className="border-l-2 border-[#c29a3e] pl-6 py-2 my-12">
            <p className="text-2xl md:text-3xl font-light italic leading-snug text-[#1e2a44]">
              {data.ai_copy.pull_quote}
            </p>
          </blockquote>

          <div className="grid md:grid-cols-2 gap-10 mt-14 pt-10 border-t border-[#1e2a44]/15">
            <div>
              <h4 className="text-xs uppercase tracking-[0.2em] text-[#c29a3e] mb-3">
                {data.ai_copy.media1_heading}
              </h4>
              <p className="text-base text-[#1e2a44]/80 leading-relaxed">
                {data.ai_copy.media1_text}
              </p>
            </div>
            <div>
              <h4 className="text-xs uppercase tracking-[0.2em] text-[#c29a3e] mb-3">
                {data.ai_copy.media2_heading}
              </h4>
              <p className="text-base text-[#1e2a44]/80 leading-relaxed">
                {data.ai_copy.media2_text}
              </p>
            </div>
          </div>

          <p className="text-xs text-[#1e2a44]/40 mt-14 italic">
            Generated from current signals: {data.mood} mood, {data.time_of_day}, {data.weather.description}
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="px-8 py-6 border-t border-[#1e2a44]/10 text-xs text-[#1e2a44]/50 flex justify-between">
        <span>Ruuz · contextual commerce engine</span>
        <span>Data refreshed {data.timestamp}</span>
      </footer>
    </div>
  )
}

export default App