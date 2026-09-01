import { useEffect, useState, useMemo } from 'react'
import { useSearchParams } from 'react-router-dom'
import { api } from '../services/api'
import type { InscriptionCard, TempleCard, DynastyDto, RulerDto, DistrictDto } from '../types'
import InscriptionCardItem from '../components/InscriptionCardItem'
import SectionHeading from '../components/SectionHeading'
import Spinner from '../components/Spinner'

export default function InscriptionExplorer() {
  const [params, setParams] = useSearchParams()
  const [items, setItems] = useState<InscriptionCard[]>([])
  const [temples, setTemples] = useState<TempleCard[]>([])
  const [dynasties, setDynasties] = useState<DynastyDto[]>([])
  const [rulers, setRulers] = useState<RulerDto[]>([])
  const [districts, setDistricts] = useState<DistrictDto[]>([])
  const [loading, setLoading] = useState(true)

  const q = params.get('q') ?? ''
  const temple = params.get('temple') ?? ''
  const dynasty = params.get('dynasty') ?? ''
  const ruler = params.get('ruler') ?? ''
  const district = params.get('district') ?? ''

  useEffect(() => {
    api.temples().then(setTemples).catch(() => {})
    api.dynasties().then(setDynasties).catch(() => {})
    api.rulers().then(setRulers).catch(() => {})
    api.districts().then(setDistricts).catch(() => {})
  }, [])

  const query = useMemo(() => ({ q: q || undefined, temple: temple || undefined, dynasty: dynasty || undefined, ruler: ruler || undefined, district: district || undefined }), [q, temple, dynasty, ruler, district])

  useEffect(() => {
    setLoading(true)
    api.inscriptions(query)
      .then(setItems)
      .catch(() => setItems([]))
      .finally(() => setLoading(false))
  }, [q, temple, dynasty, ruler, district])

  const set = (key: string, value: string) => {
    const next = new URLSearchParams(params)
    if (value) next.set(key, value); else next.delete(key)
    setParams(next)
  }
  const hasFilters = !!(q || temple || dynasty || ruler || district)

  return (
    <div className="heritage-bg">
      <div className="bg-charcoal py-12 text-ivory">
        <div className="container-page">
          <p className="label-eyebrow text-gold-light">Inscription Explorer</p>
          <h1 className="mt-2 font-display text-4xl font-semibold sm:text-5xl">Reading the kalvettu</h1>
          <p className="mt-3 max-w-2xl text-ivory/70">
            Search inscriptions and filter by temple, dynasty, ruler, or district. Every record keeps its source reference.
          </p>
        </div>
      </div>

      <div className="container-page py-10">
        <div className="card-surface mb-8 flex flex-col gap-4 p-4 lg:flex-row lg:flex-wrap lg:items-end">
          <label className="flex-1 lg:min-w-[220px]">
            <span className="label-eyebrow">Search</span>
            <input
              value={q}
              onChange={(e) => set('q', e.target.value)}
              placeholder="Keyword, reference, or place…"
              className="mt-1 w-full rounded-sm border border-charcoal/15 px-4 py-2.5 text-sm focus:border-gold focus:outline-none"
            />
          </label>
          <Filter label="Temple" value={temple} onChange={(v) => set('temple', v)} options={temples.map((t) => ({ value: t.slug, label: t.nameEn }))} />
          <Filter label="Dynasty" value={dynasty} onChange={(v) => set('dynasty', v)} options={dynasties.map((d) => ({ value: d.slug, label: d.nameEn }))} />
          <Filter label="Ruler" value={ruler} onChange={(v) => set('ruler', v)} options={rulers.map((r) => ({ value: r.slug, label: r.nameEn }))} />
          <Filter label="District" value={district} onChange={(v) => set('district', v)} options={districts.map((d) => ({ value: d.slug, label: d.nameEn }))} />
          {hasFilters && (
            <button onClick={() => setParams({})} className="text-sm font-medium text-gold-dark hover:underline lg:mb-2">Clear</button>
          )}
        </div>

        {loading ? (
          <Spinner />
        ) : items.length === 0 ? (
          <p className="py-16 text-center text-ink/60">No inscriptions match your filters.</p>
        ) : (
          <>
            <p className="mb-4 text-sm text-stone">{items.length} inscription{items.length !== 1 ? 's' : ''} found</p>
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {items.map((i) => <InscriptionCardItem key={i.slug} inscription={i} />)}
            </div>
          </>
        )}
      </div>
    </div>
  )
}

function Filter({ label, value, onChange, options }: { label: string; value: string; onChange: (v: string) => void; options: { value: string; label: string }[] }) {
  return (
    <label className="lg:min-w-[170px]">
      <span className="label-eyebrow">{label}</span>
      <select value={value} onChange={(e) => onChange(e.target.value)} className="mt-1 w-full rounded-sm border border-charcoal/15 px-3 py-2.5 text-sm focus:border-gold focus:outline-none">
        <option value="">All</option>
        {options.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
    </label>
  )
}
