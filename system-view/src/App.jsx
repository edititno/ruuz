import { useState, useEffect } from 'react'
import SignalCard from './components/SignalCard'

// the visitor's local hour, sent along so the agent knows morning from evening
const localHour = () => new Date().getHours()

// the agent's chosen tools, rendered as a chain of chips
function Trace({ tools, rounds }) {
  if (!tools || tools.length === 0) {
    return <p className="text-xs uppercase tracking-wider text-[#1e2a44]/50">wrote without fetching anything</p>
  }
  return (
    <div className="flex flex-wrap items-center gap-2">
      {tools.map((t, i) => (
        <span key={i} className="flex items-center gap-2">
          <span className="text-xs uppercase tracking-wider px-2.5 py-1 rounded-full bg-[#2a5a8a]/10 text-[#2a5a8a]">
            {t.replace('get_', '')}
          </span>
          {i < tools.length - 1 && <span className="text-[#c29a3e]">→</span>}
        </span>
      ))}
      <span className="text-xs uppercase tracking-wider text-[#1e2a44]/50 ml-2">
        {rounds} {rounds === 1 ? 'round' : 'rounds'} · chosen by the model
      </span>
    </div>
  )
}

function App() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const [moment, setMoment] = useState(null)      // the agent's line about now
  const [merchant, setMerchant] = useState('')     // what the visitor types
  const [asked, setAsked] = useState(null)         // the agent's answer for it
  const [asking, setAsking] = useState(false)

  useEffect(() => {
    // the six signals, for wherever the visitor is
    fetch('/api/context')
      .then((r) => { if (!r.ok) throw new Error(`Backend returned ${r.status}`); return r.json() })
      .then((json) => { setData(json); setLoading(false) })
      .catch((err) => { setError(err.message); setLoading(false) })

    // the agent reads the moment, in parallel
    fetch(`/api/agent?hour=${localHour()}`)
      .then((r) => (r.ok ? r.json() : null))
      .then((json) => setMoment(json || { copy: null }))
      .catch(() => setMoment({ copy: null }))
  }, [])

  const ask = () => {
    const m = merchant.trim()
    if (!m || asking) return
    setAsking(true)
    setAsked(null)
    fetch(`/api/agent?merchant=${encodeURIComponent(m)}&hour=${localHour()}`)
      .then((r) => (r.ok ? r.json() : null))
      .then((json) => { setAsked(json || { copy: null }); setAsking(false) })
      .catch(() => { setAsked({ copy: null }); setAsking(false) })
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-[#f8f5ed] text-[#1e2a44] flex items-center justify-center font-serif">
        <p className="text-lg tracking-wide">Reading your moment...</p>
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

  const place = data.city || 'Your location'

  return (
    <div className="min-h-screen bg-[#f8f5ed] text-[#1e2a44] font-serif">
      {/* Header */}
      <header className="border-b border-[#1e2a44]/10 px-8 py-5 flex items-center justify-between">
        <div className="flex items-baseline gap-3">
          <h1 className="text-2xl tracking-tight lowercase">ruuz</h1>
          <span className="text-sm text-[#c29a3e]" lang="fa">روز</span>
        </div>
        <div className="text-xs uppercase tracking-[0.2em] text-[#1e2a44]/60">
          Context Intelligence · System View
        </div>
      </header>

      {/* Hero strip: the visitor's own sky */}
      <section className="px-8 py-10 border-b border-[#1e2a44]/10">
        <p className="text-xs uppercase tracking-[0.25em] text-[#2a5a8a] mb-3">{place}</p>
        <h2 className="text-4xl md:text-5xl font-light mb-2">
          {data.weather?.temp}°F, {data.weather?.description}
        </h2>
        <p className="text-[#1e2a44]/70">
          Sky: <span className="text-[#2a5a8a]">{data.condition || data.mood}</span>
          {' · '}Time: <span className="text-[#2a5a8a]">{data.time_of_day}</span>
          {' · '}S&P: <span className="text-[#2a5a8a]">${data.stock_market?.price}</span>{' '}
          <span className="text-[#c29a3e]">({data.stock_market?.sentiment})</span>
        </p>
      </section>

      {/* This moment: the agent's reading of now */}
      <section className="px-8 py-14 border-b border-[#1e2a44]/10 bg-[#f3efe3]">
        <div className="max-w-3xl mx-auto">
          <h3 className="text-xs uppercase tracking-[0.25em] text-[#1e2a44]/60 mb-6">This moment, read by the agent</h3>
          {moment === null ? (
            <p className="text-2xl font-light italic text-[#1e2a44]/50">reading the sky...</p>
          ) : moment.copy ? (
            <>
              <p className="text-3xl md:text-4xl font-light leading-snug mb-6">{moment.copy}</p>
              <Trace tools={moment.tools_used} rounds={moment.rounds} />
            </>
          ) : (
            <p className="text-lg font-light text-[#1e2a44]/50">the agent is unavailable right now</p>
          )}
        </div>
      </section>

      {/* Live signals: everything the agent could have used */}
      <section className="px-8 py-10">
        <h3 className="text-xs uppercase tracking-[0.25em] text-[#1e2a44]/60 mb-6">
          Live Signals · what the agent can see
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          <SignalCard
            type="weather"
            title="Weather"
            value={`${data.weather?.temp}°F`}
            detail={`Feels ${data.weather?.feels_like}° · ${data.weather?.humidity}% humidity · ${data.weather?.description}`}
          />
          <SignalCard
            type="uv"
            title="UV Index"
            value={data.uv?.index}
            detail={`Sunrise ${data.weather?.sunrise} · Sunset ${data.weather?.sunset}`}
            alert={data.uv?.alert}
          />
          <SignalCard
            type="air"
            title="Air Quality"
            value={data.air_quality?.label}
            detail={`AQI level ${data.air_quality?.index} of 5`}
            alert={data.air_quality?.alert}
          />
          <SignalCard
            type="pollen"
            title="Pollen"
            value={data.pollen?.alert === 'none' ? 'None' : `Level ${data.pollen?.level}`}
            detail={`Grass ${data.pollen?.grass} · Birch ${data.pollen?.birch} · Ragweed ${data.pollen?.ragweed}`}
            alert={data.pollen?.alert}
          />
          <SignalCard
            type="news"
            title="Top News"
            value={`${data.news?.article_count} stories`}
            detail={`${data.news?.top_headline} · ${data.news?.source}`}
          />
          <SignalCard
            type="market"
            title={data.stock_market?.symbol}
            value={`$${data.stock_market?.price}`}
            detail={`${data.stock_market?.change >= 0 ? '+' : ''}${data.stock_market?.change} (${data.stock_market?.change_percent}%)`}
            alert={data.stock_market?.sentiment}
            trend={data.stock_market?.change > 0 ? 'up' : data.stock_market?.change < 0 ? 'down' : 'flat'}
          />
        </div>
      </section>

      {/* Ask the agent: watch it choose */}
      <section className="px-8 py-16 border-t border-[#1e2a44]/10 bg-[#f3efe3]">
        <div className="max-w-3xl mx-auto">
          <h3 className="text-xs uppercase tracking-[0.25em] text-[#1e2a44]/60 mb-3">Ask the agent</h3>
          <p className="text-[#1e2a44]/70 mb-8 max-w-2xl">
            Tell it what a store sells. It decides which of the signals above matter for
            this moment, fetches only those, and writes one line. The chips show its choices.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 mb-10">
            <input
              value={merchant}
              onChange={(e) => setMerchant(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && ask()}
              placeholder="sunscreen, umbrellas, luxury watches, coffee..."
              className="flex-1 bg-white/70 border border-[#1e2a44]/15 rounded-full px-5 py-3 outline-none focus:border-[#2a5a8a]"
            />
            <button
              onClick={ask}
              disabled={asking || !merchant.trim()}
              className="rounded-full px-6 py-3 bg-[#1e2a44] text-[#f8f5ed] uppercase text-xs tracking-[0.2em] disabled:opacity-40"
            >
              {asking ? 'thinking' : 'ask'}
            </button>
          </div>
          {asking && <p className="text-lg font-light italic text-[#1e2a44]/50">choosing its signals...</p>}
          {asked && asked.copy && (
            <>
              <p className="text-2xl md:text-3xl font-light leading-snug mb-5">{asked.copy}</p>
              <Trace tools={asked.tools_used} rounds={asked.rounds} />
            </>
          )}
          {asked && !asked.copy && !asking && (
            <p className="text-lg font-light text-[#1e2a44]/50">the agent is unavailable right now</p>
          )}
        </div>
      </section>

      {/* Footer */}
      <footer className="px-8 py-6 border-t border-[#1e2a44]/10 text-xs text-[#1e2a44]/50 flex justify-between">
        <span>Ruuz · context intelligence platform</span>
        <span>Signals refreshed {data.timestamp}</span>
      </footer>
    </div>
  )
}

export default App