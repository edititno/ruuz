import { Cloud, Sun, Wind, Flower2, Newspaper, TrendingUp, TrendingDown, Minus } from 'lucide-react'

const ICONS = {
  weather: Cloud,
  uv: Sun,
  air: Wind,
  pollen: Flower2,
  news: Newspaper,
  market: TrendingUp,
}

const ALERT_STYLES = {
  low: 'bg-[#3ea6a6]/15 text-[#2a5a8a]',
  good: 'bg-[#3ea6a6]/15 text-[#2a5a8a]',
  none: 'bg-[#3ea6a6]/15 text-[#2a5a8a]',
  moderate: 'bg-[#c29a3e]/20 text-[#8a6a1f]',
  high: 'bg-[#c29a3e]/25 text-[#8a6a1f]',
  neutral: 'bg-[#2a5a8a]/10 text-[#2a5a8a]',
  bullish: 'bg-[#3ea6a6]/20 text-[#1e5a5a]',
  bearish: 'bg-[#c29a3e]/25 text-[#8a6a1f]',
}

function SignalCard({ type, title, value, detail, alert, trend }) {
  const Icon = type === 'market' && trend === 'down' ? TrendingDown
             : type === 'market' && trend === 'flat' ? Minus
             : ICONS[type]

  const alertClass = ALERT_STYLES[alert?.toLowerCase()] || ALERT_STYLES.neutral

  return (
    <div className="bg-white/60 border border-[#1e2a44]/10 rounded-2xl p-5 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-200">
      <div className="flex items-start justify-between mb-3">
        <Icon className="w-6 h-6 text-[#2a5a8a]" strokeWidth={1.75} />
        {alert && (
          <span className={`text-xs font-medium px-2 py-0.5 rounded-full uppercase tracking-wide ${alertClass}`}>
            {alert}
          </span>
        )}
      </div>
      <h3 className="text-xs uppercase tracking-wider text-[#1e2a44]/60 mb-1">{title}</h3>
      <p className="text-2xl font-semibold text-[#1e2a44] leading-tight mb-1">{value}</p>
      {detail && <p className="text-sm text-[#1e2a44]/70 leading-snug">{detail}</p>}
    </div>
  )
}

export default SignalCard