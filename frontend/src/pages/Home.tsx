import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../services/api'
import type { TempleCard, InscriptionCard, DynastyDto, DistrictDto } from '../types'
import TempleCardItem from '../components/TempleCardItem'
import InscriptionCardItem from '../components/InscriptionCardItem'
import SectionHeading from '../components/SectionHeading'

export default function Home() {
  const navigate = useNavigate()
  const [q, setQ] = useState('')
  const [temples, setTemples] = useState<TempleCard[]>([])
  const [inscriptions, setInscriptions] = useState<InscriptionCard[]>([])
  const [dynasties, setDynasties] = useState<DynastyDto[]>([])
  const [districts, setDistricts] = useState<DistrictDto[]>([])

  useEffect(() => {
    api.temples().then(setTemples).catch(() => {})
    api.inscriptions().then((r) => setInscriptions(r.slice(0, 6))).catch(() => {})
    api.dynasties().then(setDynasties).catch(() => {})
    api.districts().then(setDistricts).catch(() => {})
  }, [])

  const featured = temples.slice(0, 6)
  const featuredInscriptions = inscriptions.slice(0, 3)

  return (
    <div>
      {/* HERO */}
      <section className="relative overflow-hidden bg-charcoal text-ivory">
        <div className="absolute inset-0 opacity-30 heritage-bg" />
        <div
          className="absolute inset-0 opacity-25"
          style={{ backgroundImage: 'radial-gradient(circle at 80% 20%, rgba(176,141,54,0.4), transparent 45%)' }}
        />
        <div className="container-page relative grid gap-10 py-20 lg:grid-cols-2 lg:py-28">
          <div className="animate-fadeup">
            <p className="label-eyebrow text-gold-light">கல்வெட்டு · The Inscription Archive</p>
            <h1 className="mt-4 font-display text-5xl font-semibold leading-tight sm:text-6xl">
              Reading the stone<br />memory of the Tamil temples
            </h1>
            <p className="mt-5 max-w-xl text-lg leading-relaxed text-ivory/75">
              Kalvettu connects each temple to the inscriptions carved in its walls —
              the original image, the transcription, an honest translation, and the
              authoritative source behind every word.
            </p>
            <form
              className="mt-8 flex max-w-md overflow-hidden rounded-sm border border-gold/40 bg-ivory/95"
              onSubmit={(e) => { e.preventDefault(); if (q.trim()) navigate(`/inscriptions?q=${encodeURIComponent(q)}`) }}
            >
              <input
                value={q}
                onChange={(e) => setQ(e.target.value)}
                placeholder="Search a temple, ruler, or inscription…"
                className="w-full bg-transparent px-4 py-3 text-sm text-charcoal placeholder:text-stone focus:outline-none"
              />
              <button type="submit" className="bg-gold px-5 py-3 text-sm font-semibold text-ivory-card hover:bg-gold-dark">Search</button>
            </form>
            <div className="mt-5 flex flex-wrap gap-2 text-xs">
              {['Rajaraja I', 'Brihadisvara', 'Chola', 'Chidambaram', 'SII'].map((t) => (
                <button key={t} onClick={() => navigate(`/inscriptions?q=${encodeURIComponent(t)}`)} className="rounded-full border border-ivory/20 px-3 py-1 text-ivory/70 hover:border-gold-light hover:text-gold-light">
                  {t}
                </button>
              ))}
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3 self-center">
            {featured.slice(0, 4).map((t) => (
              <Link
                key={t.slug}
                to={`/temples/${t.slug}`}
                className="group relative h-40 overflow-hidden rounded-md border border-gold/20"
              >
                {t.heroImageUrl ? (
                  <img src={t.heroImageUrl} alt={t.nameEn} referrerPolicy="no-referrer" loading="lazy" className="h-full w-full object-cover transition duration-500 group-hover:scale-110" />
                ) : (
                  <div className="h-full bg-charcoal-light" />
                )}
                <div className="absolute inset-0 bg-gradient-to-t from-charcoal/90 to-transparent" />
                <span className="absolute bottom-2 left-2 right-2 font-display text-sm font-semibold text-ivory">{t.nameEn}</span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* FEATURED TEMPLES */}
      <section className="container-page py-16 heritage-bg">
        <SectionHeading
          eyebrow="Featured temples"
          title="Great temples of the Tamil country"
          subtitle="Six well-documented monuments, each with verified history, architecture, and epigraphic records."
          right={<Link to="/temples" className="btn-ghost">All temples</Link>}
        />
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {featured.map((t) => <TempleCardItem key={t.slug} temple={t} />)}
        </div>
      </section>

      {/* EXPLORE BY DYNASTY / DISTRICT */}
      <section className="border-y border-gold/20 bg-ivory-deep py-16">
        <div className="container-page grid gap-10 lg:grid-cols-2">
          <div>
            <SectionHeading eyebrow="By dynasty" title="Walk the ages of patronage" />
            <div className="flex flex-wrap gap-3">
              {dynasties.map((d) => (
                <Link
                  key={d.slug}
                  to={`/explore?dynasty=${d.slug}`}
                  className="card-surface flex items-center gap-3 px-4 py-3 transition hover:border-gold"
                >
                  <span className="font-display text-lg text-gold-dark">{d.nameTa}</span>
                  <span className="text-sm text-ink/80">{d.nameEn}</span>
                  {d.startYear && <span className="ml-auto text-xs text-stone">{d.startYear}–{d.endYear}</span>}
                </Link>
              ))}
            </div>
          </div>
          <div>
            <SectionHeading eyebrow="By district" title="From Thanjavur to the coast" />
            <div className="grid gap-3 sm:grid-cols-2">
              {districts.map((d) => (
                <Link key={d.slug} to={`/explore?district=${d.slug}`} className="card-surface px-4 py-3 transition hover:border-gold">
                  <span className="font-display text-lg text-charcoal">{d.nameEn}</span>
                  {d.headquarters && <span className="block text-xs text-stone">HQ: {d.headquarters}</span>}
                </Link>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* FEATURED INSCRIPTIONS */}
      <section className="container-page py-16">
        <SectionHeading
          eyebrow="From the walls"
          title="Recent & featured inscriptions"
          subtitle="Each record carries its publication reference — SII, ARE, or Epigraphia Indica."
          right={<Link to="/inscriptions" className="btn-ghost">Explore all</Link>}
        />
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {featuredInscriptions.map((i) => <InscriptionCardItem key={i.slug} inscription={i} />)}
        </div>
      </section>

      {/* CTA STRIP */}
      <section className="bg-charcoal text-ivory">
        <div className="container-page flex flex-col items-start justify-between gap-6 py-12 sm:flex-row sm:items-center">
          <div>
            <h2 className="font-display text-3xl font-semibold">Follow the full journey</h2>
            <p className="mt-2 text-ivory/70">Temple → location → image → transcription → translation → meaning → source.</p>
          </div>
          <div className="flex gap-3">
            <Link to="/map" className="btn-gold">Open the map</Link>
            <Link to="/timeline" className="btn-ghost text-ivory/80">View timeline</Link>
          </div>
        </div>
      </section>
    </div>
  )
}
