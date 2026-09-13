import { useEffect, useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../services/api'
import type { TempleCard, DynastyDto, DistrictDto } from '../types'
import TempleCardItem from '../components/TempleCardItem'
import SectionHeading from '../components/SectionHeading'
import Spinner from '../components/Spinner'

export default function TempleGallery() {
  const navigate = useNavigate()
  const [temples, setTemples] = useState<TempleCard[]>([])
  const [dynasties, setDynasties] = useState<DynastyDto[]>([])
  const [districts, setDistricts] = useState<DistrictDto[]>([])
  const [q, setQ] = useState('')
  const [dynasty, setDynasty] = useState('')
  const [district, setDistrict] = useState('')
  const [loading, setLoading] = useState(true)

  // AI Live Ingestion State
  const [wikiQuery, setWikiQuery] = useState('')
  const [isFetchingWiki, setIsFetchingWiki] = useState(false)
  const [wikiError, setWikiError] = useState<string | null>(null)
  const [wikiSuccess, setWikiSuccess] = useState<string | null>(null)

  const handleFetchFromWiki = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!wikiQuery.trim() || isFetchingWiki) return
    setIsFetchingWiki(true)
    setWikiError(null)
    setWikiSuccess(null)

    try {
      const res = await api.fetchTempleFromWiki(wikiQuery.trim())
      setWikiSuccess(`Successfully synthesized & verified ${res.temple.nameEn}! Opening record…`)
      setTimeout(() => {
        navigate(`/temples/${res.temple.slug}`)
      }, 1000)
    } catch (err: any) {
      setWikiError(err.message || 'Could not fetch temple data from Wikipedia. Please check spelling or try a Wikipedia link.')
    } finally {
      setIsFetchingWiki(false)
    }
  }

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
          <h1 className="mt-2 font-english-display tracking-wide text-4xl font-semibold sm:text-5xl">Documented temples</h1>
          <p className="mt-3 max-w-2xl text-ivory/70">
            Real temple photographs, verified periods, and inscription counts. Filter by district or dynasty, or search by name.
          </p>
        </div>
      </div>

      <div className="container-page py-10">
        {/* AI INTERNET INGESTION CARD */}
        <div className="card-surface mb-8 border border-gold/30 p-5 bg-gradient-to-r from-ivory via-ivory to-gold/5">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <span className="h-2.5 w-2.5 rounded-full bg-gold animate-pulse" />
              <h3 className="font-english-display tracking-wide text-lg font-semibold text-charcoal">AI Live Internet Ingestion</h3>
              <span className="rounded-full bg-gold/15 px-2.5 py-0.5 text-xs font-semibold text-gold-dark">Wikipedia &amp; Wikimedia Commons</span>
            </div>
            <span className="text-xs text-stone">Real data &middot; Zero hardcoding</span>
          </div>
          <p className="mt-1.5 text-sm text-ink/75">
            Discover any temple not yet featured. Enter any temple name or Wikipedia URL - KALVETTU AI will dynamically fetch live facts from the web, extract architectural details, and generate engaging plain-language histories.
          </p>
          <form onSubmit={handleFetchFromWiki} className="mt-4 flex flex-col sm:flex-row gap-3">
            <input
              value={wikiQuery}
              onChange={(e) => setWikiQuery(e.target.value)}
              placeholder="e.g. Vadapalani Murugan Temple, Parthasarathy Temple, or Wikipedia link..."
              className="flex-1 rounded-sm border border-charcoal/20 px-4 py-2.5 text-sm focus:border-gold focus:outline-none bg-white"
              disabled={isFetchingWiki}
            />
            <button
              type="submit"
              disabled={isFetchingWiki || !wikiQuery.trim()}
              className="btn-gold whitespace-nowrap flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {isFetchingWiki ? (
                <>
                  <span className="h-3.5 w-3.5 rounded-full border-2 border-ivory border-t-transparent animate-spin" />
                  <span>Fetching with AI…</span>
                </>
              ) : (
                <span>Fetch from Wikipedia (AI)</span>
              )}
            </button>
          </form>

          {isFetchingWiki && (
            <div className="mt-3 flex items-center gap-2 text-xs text-gold-dark">
              <span className="h-2 w-2 rounded-full bg-gold animate-ping" />
              <span>Querying Wikipedia REST API &middot; Synthesizing history with AI &middot; Extracting stone epigraphs…</span>
            </div>
          )}
          {wikiError && (
            <p className="mt-3 text-xs text-red-600 bg-red-50 p-2.5 rounded border border-red-200">{wikiError}</p>
          )}
          {wikiSuccess && (
            <p className="mt-3 text-xs text-green-700 bg-green-50 p-2.5 rounded border border-green-200">{wikiSuccess}</p>
          )}
        </div>
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
          <div className="py-16 text-center">
            <p className="font-english-display tracking-wide text-xl font-medium text-charcoal">No verified temple record found in the Kalvettu archive.</p>
            <p className="mt-2 text-sm text-stone">Try an alternate spelling or browse temples by district.</p>
          </div>
        ) : (
          <>
            <p className="mb-4 text-sm text-stone">{temples.length} temple{temples.length !== 1 ? 's' : ''} found</p>
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {temples.map((t, idx) => <TempleCardItem key={t.slug} temple={t} index={idx} />)}
            </div>
          </>
        )}
      </div>
    </div>
  )
}
