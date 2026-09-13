import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { api } from '../services/api'
import type { TempleDetail } from '../types'
import ImageWithAttribution from '../components/ImageWithAttribution'
import InscriptionCardItem from '../components/InscriptionCardItem'
import Spinner from '../components/Spinner'
import SectionHeading from '../components/SectionHeading'

type Tab = 'overview' | 'history' | 'architecture' | 'inscriptions' | 'gallery' | 'map' | 'references'

export default function TempleDetails() {
  const { slug } = useParams()
  const [data, setData] = useState<TempleDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [syncing, setSyncing] = useState(false)
  const [tab, setTab] = useState<Tab>('overview')
  const [activeImg, setActiveImg] = useState(0)

  useEffect(() => {
    if (!slug) return
    setLoading(true)
    api.temple(slug).then(setData).catch(() => setData(null)).finally(() => setLoading(false))
  }, [slug])

  const handleSyncWithAi = async () => {
    if (!slug || syncing) return
    setSyncing(true)
    try {
      const updated = await api.enrichTemple(slug)
      setData(updated)
    } catch (err) {
      console.error("Enrichment error:", err)
    } finally {
      setSyncing(false)
    }
  }

  if (loading) return <Spinner />
  if (!data) {
    return (
      <div className="container-page py-20 text-center">
        <p className="font-english-display tracking-wide text-3xl font-semibold text-charcoal">No verified temple record found in the Kalvettu archive.</p>
        <p className="mt-2 text-stone">Try an alternate spelling or browse temples by district.</p>
        <Link to="/temples" className="btn-gold mt-6 inline-block">Browse all verified temples</Link>
      </div>
    )
  }

  const { temple, images, inscriptions, dynasty, district, source } = data
  const hero = images[activeImg] || images[0]

  const tabs: { id: Tab; label: string }[] = [
    { id: 'overview', label: 'Overview' },
    { id: 'history', label: 'History' },
    { id: 'architecture', label: 'Architecture' },
    { id: 'inscriptions', label: `Inscriptions (${inscriptions.length})` },
    { id: 'gallery', label: `Gallery (${images.length})` },
    { id: 'map', label: 'Map & location' },
    { id: 'references', label: 'References' },
  ]

  return (
    <div>
      {/* HERO */}
      <section className="relative h-[44vh] min-h-[320px] w-full overflow-hidden bg-charcoal">
        {hero && (
          <img src={hero.imageUrl} alt={temple.nameEn} referrerPolicy="no-referrer" className="h-full w-full object-cover opacity-90" />
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-charcoal via-charcoal/40 to-transparent" />
        <div className="container-page absolute bottom-0 left-1/2 w-full -translate-x-1/2 pb-6 text-ivory">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex flex-wrap gap-2">
              {temple.unescoWorldHeritage && <span className="chip bg-gold text-ivory-card">UNESCO World Heritage</span>}
              {temple.asiMonument && <span className="chip">ASI Monument</span>}
              {temple.wikipediaUrl && <span className="chip bg-charcoal/80 border border-gold/40 text-gold-light">Wikipedia &amp; AI Verified</span>}
            </div>
            <button
              onClick={handleSyncWithAi}
              disabled={syncing}
              className="flex items-center gap-2 rounded-full border border-gold/60 bg-charcoal/85 px-4 py-1.5 text-xs font-medium text-gold-light hover:bg-gold hover:text-charcoal transition disabled:opacity-50"
              title="Fetch fresh data from Wikipedia and re-synthesize using AI"
            >
              <span className={`h-2 w-2 rounded-full bg-gold ${syncing ? 'animate-ping' : ''}`} />
              <span>{syncing ? 'Syncing Wikipedia via AI…' : 'Sync with Wikipedia (AI)'}</span>
            </button>
          </div>
          <h1 className="mt-3 font-english-display tracking-wide text-4xl font-semibold sm:text-5xl">{temple.nameEn}</h1>
          {temple.nameTa && <p className="mt-1 text-xl font-medium tracking-wide text-ivory/90 font-tamil-regular" lang="ta">{temple.nameTa}</p>}
          <p className="mt-2 text-sm uppercase tracking-wide text-gold-light">
            {[temple.town, district?.nameEn, dynasty?.nameEn].filter(Boolean).join(' · ')}
          </p>
        </div>
      </section>

      {/* TABS */}
      <div className="sticky top-16 z-40 border-b border-gold/20 bg-ivory/95 backdrop-blur">
        <div className="container-page flex gap-1 overflow-x-auto">
          {tabs.map((t) => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`whitespace-nowrap px-4 py-3 text-sm font-medium transition ${
                tab === t.id ? 'border-b-2 border-gold text-gold-dark' : 'text-ink/60 hover:text-ink'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      <div className="container-page py-10">
        {tab === 'overview' && (
          <div className="grid gap-10 lg:grid-cols-3">
            <div className="lg:col-span-2">
              <SectionHeading eyebrow="Overview" title={temple.nameEn} />
              <p className="text-lg leading-relaxed text-ink/85">{temple.summary}</p>
              {temple.alternateNames && (
                <p className="mt-4 text-sm text-stone"><span className="font-semibold text-ink">Also known as:</span> {temple.alternateNames}</p>
              )}
              <dl className="mt-8 grid gap-5 sm:grid-cols-2">
                <Fact label="Deity" value={temple.deity} />
                <Fact label="Patron" value={temple.patron} />
                <Fact label="Dynasty" value={dynasty?.nameEn} ta={dynasty?.nameTa} />
                <Fact label="Consecrated" value={temple.consecrationYear ? `≈ ${temple.consecrationYear} CE` : undefined} />
                <Fact label="District" value={district?.nameEn} />
                <Fact label="Managed by" value={temple.managedBy} />
              </dl>
            </div>
            <aside className="card-surface h-fit p-5">
              <h3 className="label-eyebrow mb-3">Quick facts</h3>
              <ul className="space-y-3 text-sm">
                <li className="flex justify-between"><span className="text-stone">Coordinates</span><span className="font-medium">{temple.lat?.toFixed(4)}, {temple.lng?.toFixed(4)}</span></li>
                <li className="flex justify-between"><span className="text-stone">UNESCO</span><span className="font-medium">{temple.unescoWorldHeritage ? 'Yes' : 'No'}</span></li>
                <li className="flex justify-between"><span className="text-stone">ASI monument</span><span className="font-medium">{temple.asiMonument ? 'Yes' : 'No'}</span></li>
                <li className="flex justify-between"><span className="text-stone">Inscriptions</span><span className="font-medium">{inscriptions.length} records</span></li>
              </ul>
              <Link to={`/map?temple=${temple.slug}`} className="btn-gold mt-5 w-full">View on map</Link>
            </aside>
          </div>
        )}

        {tab === 'history' && <Prose title="History" body={temple.history} templeName={temple.nameEn} wikiUrl={temple.wikipediaUrl} onSync={handleSyncWithAi} syncing={syncing} />}
        {tab === 'architecture' && <Prose title="Architecture" body={temple.architecture} templeName={temple.nameEn} wikiUrl={temple.wikipediaUrl} onSync={handleSyncWithAi} syncing={syncing} />}

        {tab === 'inscriptions' && (
          <div>
            <SectionHeading eyebrow="Inscriptions at this temple" title={`${inscriptions.length} documented record${inscriptions.length !== 1 ? 's' : ''}`} />
            {inscriptions.length === 0 ? (
              <p className="text-ink/60">No inscription records are seeded for this temple yet. The dataset is kept small and verified.</p>
            ) : (
              <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {inscriptions.map((i, idx) => <InscriptionCardItem key={i.slug} inscription={i} index={idx} />)}
              </div>
            )}
          </div>
        )}

        {tab === 'gallery' && (
          <div>
            <SectionHeading eyebrow="Gallery" title="Photographs" />
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
              {images.map((im, idx) => (
                <button key={im.id} onClick={() => setActiveImg(idx)} className={`overflow-hidden rounded-md border ${idx === activeImg ? 'border-gold' : 'border-transparent'}`}>
                  <ImageWithAttribution image={im} showAttribution={false} className="aspect-[4/3]" />
                </button>
              ))}
            </div>
            {hero && (
              <div className="mt-6 card-surface overflow-hidden">
                <ImageWithAttribution image={hero} className="aspect-[16/9]" />
              </div>
            )}
          </div>
        )}

        {tab === 'map' && (
          <div>
            <SectionHeading eyebrow="Map & location" title="Where the temple stands" />
            <p className="mb-4 text-ink/70">The interactive temple map (with documented inscription locations) is available on the Map page.</p>
            <Link to={`/map?temple=${temple.slug}`} className="btn-gold">Open interactive map</Link>
            {temple.lat && temple.lng && (
              <p className="mt-4 text-sm text-stone">Coordinates: {temple.lat.toFixed(5)}, {temple.lng.toFixed(5)}</p>
            )}
          </div>
        )}

        {tab === 'references' && (
          <div>
            <SectionHeading eyebrow="References" title="Data sources for this temple" />
            <div className="card-surface space-y-4 p-5 text-sm">
              {temple.wikipediaUrl && (
                <div className="border-b border-gold/20 pb-3">
                  <span className="label-eyebrow">Online Encyclopedia</span>
                  <h4 className="mt-1 font-semibold text-charcoal">Wikipedia - {temple.nameEn}</h4>
                  <p className="text-stone">Comprehensive historical, architectural, and epigraphical record from the Wikimedia Foundation.</p>
                  <a href={temple.wikipediaUrl} target="_blank" rel="noreferrer" className="mt-1 inline-block text-gold-dark underline">
                    Open Wikipedia Article ↗
                  </a>
                </div>
              )}
              {source && (
                <div className="border-b border-gold/20 pb-3">
                  <span className="label-eyebrow">Canonical Record Source</span>
                  <h4 className="mt-1 font-semibold text-charcoal">{source.institution}</h4>
                  <p className="text-stone">{source.reference}</p>
                  {source.url && (
                    <a href={source.url} target="_blank" rel="noreferrer" className="mt-1 inline-block text-gold-dark underline">
                      Source Repository / Publication ↗
                    </a>
                  )}
                </div>
              )}
              {temple.unescoWorldHeritage && temple.unescoUrl && (
                <a href={temple.unescoUrl} target="_blank" rel="noreferrer" className="block text-gold-dark hover:underline">UNESCO World Heritage Centre - {temple.nameEn} ↗</a>
              )}
              {temple.asiUrl && <a href={temple.asiUrl} target="_blank" rel="noreferrer" className="block text-gold-dark hover:underline">Archaeological Survey of India ↗</a>}
              {temple.sourceNote && <p className="text-ink/75 italic">{temple.sourceNote}</p>}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function Fact({ label, value, ta }: { label: string; value?: string; ta?: string }) {
  return (
    <div>
      <dt className="label-eyebrow">{label}</dt>
      <dd className="mt-1 text-sm text-ink/85">
        {value || <span className="italic text-stone">Not recorded</span>}
        {ta && <span className="ml-1 text-stone font-tamil-regular tracking-wide text-sm font-semibold" lang="ta">({ta})</span>}
      </dd>
    </div>
  )
}

function wikitextToMarkdown(text: string): string {
  if (!text) return ''
  let md = text
  
  md = md.replace(/\r\n/g, '\n')
  md = md.replace(/^=====\s*(.+?)\s*=====$/gm, '##### $1')
  md = md.replace(/^====\s*(.+?)\s*====$/gm, '#### $1')
  md = md.replace(/^===\s*(.+?)\s*===$/gm, '### $1')
  md = md.replace(/^==\s*(.+?)\s*==$/gm, '## $1')
  md = md.replace(/'''(.*?)'''/g, '**$1**')
  md = md.replace(/''(.*?)''/g, '*$1*')

  // Citations and common templates
  md = md.replace(/\{\{sfn\|([^}]+)\}\}/g, (match, inner) => {
    const parts = inner.split('|')
    return `(${parts.join(', ').replace('p=', 'p. ')})`
  })
  md = md.replace(/\{\{reign\|([^|]+)\|([^}]+)\}\}/gi, '$1–$2')
  md = md.replace(/\{\{cite[^}]+\}\}/gi, '')
  md = md.replace(/\{\{lang[^|]*\|([^}]+)\}\}/gi, '$1')
  md = md.replace(/\{\{IAST\|([^}]+)\}\}/g, '$1')
  md = md.replace(/\{\{transl[^|]*\|[^|]+\|([^}]+)\}\}/g, '$1')
  
  // Clean internal links
  md = md.replace(/\[\[(?:[^|\]]*\|)?([^\]]+)\]\]/g, '$1')
  
  // Remove remaining unhandled templates
  md = md.replace(/\{\{[^}]+\}\}/g, '')

  return md
}

function Prose({
  title,
  body,
  templeName,
  wikiUrl,
  onSync,
  syncing,
}: {
  title: string
  body?: string
  templeName: string
  wikiUrl?: string
  onSync?: () => void
  syncing?: boolean
}) {
  return (
    <div className="max-w-4xl space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <SectionHeading eyebrow={title} title={title} />
        <div className="flex flex-wrap items-center gap-2">
          <div className="flex items-center gap-2 rounded-full border border-gold/30 bg-gold/5 px-3 py-1 text-xs text-gold-dark">
            <span className="h-2 w-2 rounded-full bg-gold animate-pulse" />
            <span>AI Synthesis &middot; Wikipedia &amp; Epigraphy</span>
          </div>
          {onSync && (
            <button
              onClick={onSync}
              disabled={syncing}
              className="flex items-center gap-1.5 rounded-full border border-gold/40 bg-gold/10 px-3 py-1 text-xs font-medium text-gold-dark hover:bg-gold/20 transition disabled:opacity-50"
              title="Re-fetch Wikipedia & re-synthesize using AI"
            >
              <span className={`h-1.5 w-1.5 rounded-full bg-gold ${syncing ? 'animate-ping' : ''}`} />
              <span>{syncing ? 'Syncing…' : 'Sync with Wikipedia'}</span>
            </button>
          )}
        </div>
      </div>

      {body ? (
        <div className="space-y-4">
          <div className="prose prose-stone prose-lg max-w-none prose-headings:font-english-display prose-headings:text-charcoal prose-headings:font-semibold prose-a:text-gold-dark hover:prose-a:text-gold text-ink/85">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {wikitextToMarkdown(body)}
            </ReactMarkdown>
          </div>
          {wikiUrl && (
            <div className="mt-6 pt-4 border-t border-gold/20 flex flex-wrap items-center justify-between gap-2 text-xs text-stone">
              <span>Source: Synthesized from Wikipedia &amp; Archaeological records</span>
              <a href={wikiUrl} target="_blank" rel="noreferrer" className="text-gold-dark hover:underline font-medium">
                Read full Wikipedia article for {templeName} &rarr;
              </a>
            </div>
          )}
        </div>
      ) : (
        <div className="card-surface p-6 border-dashed border-stone/30">
          <p className="text-ink/60">No verified text is available for this section yet.</p>
          {onSync && (
            <button
              onClick={onSync}
              disabled={syncing}
              className="btn-gold mt-4 text-xs"
            >
              {syncing ? 'Fetching from Wikipedia…' : 'Fetch from Wikipedia with AI'}
            </button>
          )}
        </div>
      )}
    </div>
  )
}
