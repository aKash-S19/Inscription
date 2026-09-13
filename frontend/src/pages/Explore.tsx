import { useEffect, useState, useMemo, useRef } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { api } from '../services/api'
import type { DynastyDto, RulerDto, DistrictDto, TempleCard } from '../types'
import TempleCardItem from '../components/TempleCardItem'
import SectionHeading from '../components/SectionHeading'
import Spinner from '../components/Spinner'

export default function Explore() {
  const [params, setParams] = useSearchParams()
  const [dynasties, setDynasties] = useState<DynastyDto[]>([])
  const [rulers, setRulers] = useState<RulerDto[]>([])
  const [districts, setDistricts] = useState<DistrictDto[]>([])
  const [temples, setTemples] = useState<TempleCard[]>([])
  const [loading, setLoading] = useState(true)

  const dynasty = params.get('dynasty') ?? ''
  const district = params.get('district') ?? ''

  useEffect(() => {
    api.dynasties().then(setDynasties).catch(() => {})
    api.rulers().then(setRulers).catch(() => {})
    api.districts().then(setDistricts).catch(() => {})
  }, [])

  useEffect(() => {
    setLoading(true)
    api.temples(undefined, district || undefined, dynasty || undefined)
      .then(setTemples).catch(() => setTemples([])).finally(() => setLoading(false))
  }, [dynasty, district])

  const activeDynasty = dynasties.find((d) => d.slug === dynasty)
  const activeDistrict = districts.find((d) => d.slug === district)
  const dynRulers = useMemo(() => rulers.filter((r) => !dynasty || r.dynastySlug === dynasty), [rulers, dynasty])

  const resultsRef = useRef<HTMLDivElement>(null)

  const set = (key: string, value: string) => {
    const next = new URLSearchParams(params)
    if (value) next.set(key, value); else next.delete(key)
    if (key === 'district') next.delete('dynasty'); if (key === 'dynasty') next.delete('district')
    setParams(next)
    
    // Smooth scroll to results
    setTimeout(() => {
      resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }, 100)
  }

  return (
    <div className="heritage-bg">
      <div className="bg-charcoal py-10 text-ivory">
        <div className="container-page">
          <p className="label-eyebrow text-gold-light">Explore</p>
          <h1 className="mt-2 font-english-display tracking-wide text-4xl font-semibold sm:text-5xl">By dynasty & district</h1>
          <p className="mt-3 max-w-2xl text-ivory/70">Browse verified temples and inscriptions through the lens of period and place.</p>
        </div>
      </div>

      <div className="container-page py-10">
        {/* DISTRICT MAP STRIP */}
        <SectionHeading eyebrow="Districts" title="Tamil Nadu districts" />
        <div className="mb-10 flex flex-wrap gap-3">
          {districts.map((d) => (
            <button
              key={d.slug}
              onClick={() => set('district', d.slug)}
              className={`card-surface px-4 py-3 text-left transition hover:border-gold ${district === d.slug ? 'border-gold ring-1 ring-gold/40' : ''}`}
            >
              <span className="font-english-display tracking-wide text-lg font-bold text-ink">{d.nameEn}</span>
              {d.headquarters && <span className="block text-xs font-semibold text-ink/75 mt-1">HQ: {d.headquarters}</span>}
            </button>
          ))}
        </div>

        {/* DYNASTIES */}
        <SectionHeading eyebrow="Dynasties" title="Ruling houses of the Tamil country" />
        <div className="mb-6 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
          {dynasties.map((d) => (
            <button
              key={d.slug}
              onClick={() => set('dynasty', d.slug)}
              className={`card-surface p-5 text-left transition hover:border-gold ${dynasty === d.slug ? 'border-gold ring-1 ring-gold/40' : ''}`}
            >
              <div className="flex items-start gap-4">
                <img src={`/emblems/${d.slug}_emblem.jpg`} alt={`${d.nameEn} emblem`} className="h-16 w-16 rounded-md object-cover border border-gold/15 shrink-0" />
                <div className="flex-1">
                  <div className="flex items-baseline justify-between">
                    <span className="font-tamil-display text-3xl font-medium tracking-wide text-gold-dark" lang="ta">{d.nameTa}</span>
                    {d.startYear && <span className="text-xs text-stone">{d.startYear}–{d.endYear}</span>}
                  </div>
                  <h3 className="mt-1 font-english-display tracking-wide text-xl font-semibold text-charcoal">{d.nameEn}</h3>
                  {d.capital && <p className="text-xs text-stone mt-1">Capital: {d.capital}</p>}
                </div>
              </div>
              <p className="mt-2 line-clamp-3 text-sm text-ink/75">{d.description}</p>
            </button>
          ))}
        </div>


        {/* RESULTS */}
        <div className="tamil-rule my-6 scroll-mt-24" ref={resultsRef} />
        <SectionHeading
          eyebrow="Results"
          title={activeDistrict ? `Temples in ${activeDistrict.nameEn}` : activeDynasty ? `Temples of the ${activeDynasty.nameEn}` : 'All temples'}
          right={loading ? null : <span className="text-sm text-stone">{temples.length} found</span>}
        />
        {loading ? (
          <Spinner />
        ) : temples.length === 0 ? (
          <p className="text-ink/60">No verified temples for this selection.</p>
        ) : (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {temples.map((t, idx) => <TempleCardItem key={t.slug} temple={t} index={idx} />)}
          </div>
        )}

        {(dynasty || district) && (
          <Link to="/explore" className="btn-ghost mt-8">Reset selection</Link>
        )}
      </div>
    </div>
  )
}
