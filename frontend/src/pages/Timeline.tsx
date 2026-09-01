import { useEffect, useState, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../services/api'
import type { TimelineEvent } from '../types'
import SectionHeading from '../components/SectionHeading'
import Spinner from '../components/Spinner'

export default function Timeline() {
  const [events, setEvents] = useState<TimelineEvent[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'ALL' | 'TEMPLE' | 'RULER'>('ALL')

  useEffect(() => {
    api.timeline().then(setEvents).catch(() => setEvents([])).finally(() => setLoading(false))
  }, [])

  const shown = useMemo(() => events.filter((e) => filter === 'ALL' || e.type === filter), [events, filter])

  const minYear = events.length ? Math.min(...events.map((e) => parseInt(e.year) || 0)) : 0
  const maxYear = events.length ? Math.max(...events.map((e) => parseInt(e.year) || 0)) : 0

  return (
    <div className="heritage-bg">
      <div className="bg-charcoal py-10 text-ivory">
        <div className="container-page">
          <p className="label-eyebrow text-gold-light">Timeline</p>
          <h1 className="mt-2 font-display text-4xl font-semibold sm:text-5xl">Through the centuries</h1>
          <p className="mt-3 max-w-2xl text-ivory/70">
            Temples and rulers in chronological order, built from verified consecration and accession years.
          </p>
        </div>
      </div>

      <div className="container-page py-10">
        <div className="mb-8 flex gap-2">
          {(['ALL', 'TEMPLE', 'RULER'] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`rounded-sm px-4 py-2 text-sm font-medium transition ${filter === f ? 'bg-gold text-ivory-card' : 'border border-charcoal/15 text-ink/70 hover:border-gold'}`}
            >
              {f === 'ALL' ? 'All' : f === 'TEMPLE' ? 'Temples' : 'Rulers'}
            </button>
          ))}
          {events.length > 0 && (
            <span className="ml-auto self-center text-sm text-stone">{minYear} – {maxYear} CE · {shown.length} entries</span>
          )}
        </div>

        {loading ? <Spinner /> : (
          <ol className="relative ml-3 border-l-2 border-gold/40">
            {shown.map((e, i) => (
              <li key={i} className="mb-8 ml-6">
                <span className="absolute -left-[9px] mt-1.5 h-4 w-4 rounded-full border-2 border-gold bg-ivory" />
                <div className="card-surface p-5">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="font-display text-2xl font-semibold text-gold-dark">{e.year}</span>
                    <span className={`chip ${e.type === 'TEMPLE' ? 'bg-charcoal/80 text-gold-light' : ''}`}>{e.type}</span>
                  </div>
                  <h3 className="mt-1 font-display text-xl font-semibold text-charcoal">{e.title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-ink/80">{e.description}</p>
                  {e.relatedSlug && e.type === 'TEMPLE' && (
                    <Link to={`/temples/${e.relatedSlug}`} className="mt-3 inline-block text-sm font-medium text-gold-dark hover:underline">Temple page →</Link>
                  )}
                  {e.relatedSlug && e.type === 'RULER' && (
                    <Link to={`/inscriptions?ruler=${e.relatedSlug}`} className="mt-3 inline-block text-sm font-medium text-gold-dark hover:underline">Inscriptions →</Link>
                  )}
                </div>
              </li>
            ))}
          </ol>
        )}
      </div>
    </div>
  )
}
