import { useEffect, useState, useMemo } from 'react'
import { api } from '../services/api'
import type { TempleCard, DynastyDto, DistrictDto } from '../types'
import TempleCardItem from '../components/TempleCardItem'
import SectionHeading from '../components/SectionHeading'
import Spinner from '../components/Spinner'

export default function TempleGallery() {
  const [temples, setTemples] = useState<TempleCard[]>([])
  const [dynasties, setDynasties] = useState<DynastyDto[]>([])
  const [districts, setDistricts] = useState<DistrictDto[]>([])
  const [q, setQ] = useState('')
  const [dynasty, setDynasty] = useState('')
  const [district, setDistrict] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.dynasties().then(setDynasties).catch(() => {})
    api.districts().then(setDistricts).catch(() => {})
  }, [])

  useEffect(() => {
    setLoading(true)
    api.temples(q || undefined, district || undefined, dynasty || undefined)
      .then(setTemples)
      .catch(() => setTemples([]))
      .finally(() => setLoading(false))
  }, [q, dynasty, district])

  const clear = useMemo(() => () => { setQ(''); setDynasty(''); setDistrict('') }, [])
  const hasFilters = q || dynasty || district

  return (
    <div className="heritage-bg">
      <div className="bg-charcoal py-12 text-ivory">
        <div className="container-page">
          <p className="label-eyebrow text-gold-light">Temple Gallery</p>
          <h1 className="mt-2 font-display text-4xl font-semibold sm:text-5xl">Documented temples</h1>
          <p className="mt-3 max-w-2xl text-ivory/70">
            Real temple photographs, verified periods, and inscription counts. Filter by district or dynasty, or search by name.
          </p>
        </div>
      </div>

      <div className="container-page py-10">
        <div className="card-surface mb-8 flex flex-col gap-4 p-4 sm:flex-row sm:items-center">
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search temples…"
            className="w-full rounded-sm border border-charcoal/15 px-4 py-2.5 text-sm focus:border-gold focus:outline-none sm:max-w-xs"
          />
          <select
            value={dynasty}
            onChange={(e) => setDynasty(e.target.value)}
            className="rounded-sm border border-charcoal/15 px-3 py-2.5 text-sm focus:border-gold focus:outline-none"
          >
            <option value="">All dynasties</option>
            {dynasties.map((d) => <option key={d.slug} value={d.slug}>{d.nameEn}</option>)}
          </select>
          <select
            value={district}
            onChange={(e) => setDistrict(e.target.value)}
            className="rounded-sm border border-charcoal/15 px-3 py-2.5 text-sm focus:border-gold focus:outline-none"
          >
            <option value="">All districts</option>
            {districts.map((d) => <option key={d.slug} value={d.slug}>{d.nameEn}</option>)}
          </select>
          {hasFilters && (
            <button onClick={clear} className="ml-auto text-sm font-medium text-gold-dark hover:underline">Clear filters</button>
          )}
        </div>

        {loading ? (
          <Spinner />
        ) : temples.length === 0 ? (
          <p className="py-16 text-center text-ink/60">No temples match your filters.</p>
        ) : (
          <>
            <p className="mb-4 text-sm text-stone">{temples.length} temple{temples.length !== 1 ? 's' : ''} found</p>
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {temples.map((t) => <TempleCardItem key={t.slug} temple={t} />)}
            </div>
          </>
        )}
      </div>
    </div>
  )
}
