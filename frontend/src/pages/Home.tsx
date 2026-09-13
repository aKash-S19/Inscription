import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../services/api'
import type { TempleCard, InscriptionCard, DynastyDto, DistrictDto } from '../types'
import SectionHeading from '../components/SectionHeading'
import FadeIn from '../components/FadeIn'
import InscriptionCardItem from '../components/InscriptionCardItem'

export default function Home() {
  const navigate = useNavigate()
  const [q, setQ] = useState('')
  const [temples, setTemples] = useState<TempleCard[]>([])
  const [inscriptions, setInscriptions] = useState<InscriptionCard[]>([])
  const [dynasties, setDynasties] = useState<DynastyDto[]>([])
  const [districts, setDistricts] = useState<DistrictDto[]>([])

  useEffect(() => {
    api.temples().then(setTemples).catch(() => { })
    api.inscriptions().then((r) => setInscriptions(r.slice(0, 6))).catch(() => { })
    api.dynasties().then(setDynasties).catch(() => { })
    api.districts().then(setDistricts).catch(() => { })
  }, [])

  const featured = temples.slice(0, 6)
  const featuredInscriptions = inscriptions.slice(0, 3)

  return (
    <div className="bg-obsidian text-ivory min-h-screen selection:bg-gold/30">
      {/* HERO SECTION */}
      <section className="relative min-h-[90vh] flex flex-col justify-center overflow-hidden">
        {/* Background Image on Right */}
        <div className="absolute inset-0 z-0 flex justify-end">
          <div className="w-full lg:w-[65%] h-full relative">
            <img
              src="/temples/gangaikonda-cholapuram.jpg"
              alt="Brihadisvara Temple"
              className="w-full h-full object-cover object-center"
            />
            {/* Gradients to blend image into the obsidian background */}
            <div className="absolute inset-0 bg-gradient-to-r from-obsidian via-obsidian/80 to-transparent" />
            <div className="absolute inset-0 bg-gradient-to-t from-obsidian via-transparent to-obsidian/40" />
            <div className="absolute inset-0 bg-obsidian/30 mix-blend-multiply" />
          </div>
        </div>

        <div className="container-page relative z-10 py-20">

          <FadeIn delay={100} direction="up" className="max-w-3xl">

            <h1 className="font-display text-4xl sm:text-7xl lg:text-[5.5rem] leading-[1.1] font-normal tracking-tight text-ivory">
              Reading the <br />
              <span className="text-gold"><span className="text-[0.85em]" style={{ fontFamily: 'Arima, sans-serif' }}>கல்வெட்டு - </span>Stone Memory</span><br />
              of the Tamil Temples
            </h1>

            <p className="mt-8 max-w-xl text-lg leading-relaxed text-ivory/60 font-english-regular">
              Kalvettu connects each temple to the inscriptions carved in its walls&nbsp;-
              the original image, the transcription, an honest translation, and the authoritative source behind every word.
            </p>

            {/* Search Box */}
            <div className="mt-10 max-w-2xl">
              <form
                className="flex w-full overflow-hidden rounded-[4px] border border-gold/30 bg-[#161616]/80 backdrop-blur-md"
                onSubmit={(e) => { e.preventDefault(); if (q.trim()) navigate(`/inscriptions?q=${encodeURIComponent(q)}`) }}
              >
                <div className="flex items-center justify-center pl-4 pr-2 text-ivory/40">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
                </div>
                <input
                  value={q}
                  onChange={(e) => setQ(e.target.value)}
                  placeholder="Search..."
                  className="w-full bg-transparent px-2 py-3 sm:py-4 text-sm text-ivory placeholder:text-stone focus:outline-none"
                />
                <button type="submit" className="bg-[#bda165] px-4 sm:px-8 py-3 sm:py-4 text-sm font-english-regular font-semibold text-charcoal-dark hover:bg-gold-light transition flex items-center gap-2">
                  Search <span className="hidden sm:inline text-lg leading-none">→</span>
                </button>
              </form>
            </div>
          </FadeIn>
        </div>
      </section>

      {/* EXPLORE TEMPLES CARDS ROW */}
      <section className="bg-obsidian border-t border-gold/10 py-16 relative z-10">
        <div className="container-page mb-8 flex items-end justify-between">
          <SectionHeading
            eyebrow="Explore Temples"
            title=""
            className="!mb-0"
            dark
          />
          <Link to="/temples" className="text-gold text-sm font-english-regular hover:text-gold-light flex items-center gap-2 transition">
            View All Temples <span className="text-lg leading-none">→</span>
          </Link>
        </div>

        {/* Horizontal scroll container */}
        <div className="container-page">
          <div className="flex gap-6 overflow-x-auto pb-8 snap-x snap-mandatory hide-scrollbar">
            {featured.map((t) => (
              <Link
                key={t.slug}
                to={`/temples/${t.slug}`}
                className="relative flex-none w-[280px] h-[180px] sm:w-[400px] sm:h-[240px] rounded-md overflow-hidden group snap-start border border-gold/10 hover:border-gold/40 transition-colors"
              >
                {t.heroImageUrl ? (
                  <img src={t.heroImageUrl} alt={t.nameEn} className="absolute inset-0 w-full h-full object-cover transition-transform duration-700 group-hover:scale-105" loading="lazy" />
                ) : (
                  <div className="absolute inset-0 bg-[#161616]" />
                )}
                <div className="absolute inset-0 bg-gradient-to-t from-obsidian via-obsidian/40 to-transparent opacity-90" />

                <div className="absolute bottom-0 left-0 right-0 p-5 flex items-end justify-between">
                  <div>
                    <h3 className="font-english-display font-semibold text-lg sm:text-xl text-ivory tracking-wide">{t.nameEn}</h3>
                    <p className="text-[10px] uppercase tracking-[0.2em] text-gold/80 mt-1 font-english-regular">{t.districtSlug || 'TAMIL NADU'}</p>
                  </div>
                  <div className="w-8 h-8 rounded-full border border-gold/30 flex items-center justify-center text-ivory/50 group-hover:text-gold group-hover:border-gold transition shrink-0 ml-4">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* EXPLORE BY DYNASTY / DISTRICT */}
      <section className="border-t border-gold/10 bg-[#0d0e0c] py-16">
        <div className="container-page grid gap-10 lg:grid-cols-2">
          <FadeIn direction="up">
            <SectionHeading eyebrow="By dynasty" title="Walk the ages of patronage" dark />
            <div className="flex flex-wrap gap-3">
              {dynasties.map((d) => (
                <Link
                  key={d.slug}
                  to={`/explore?dynasty=${d.slug}`}
                  className="rounded-lg border border-gold/10 bg-obsidian px-4 py-3 transition hover:border-gold/40 flex items-center gap-3"
                >
                  <img src={`/emblems/${d.slug}_emblem.jpg`} alt={`${d.nameEn} emblem`} className="h-16 w-16 rounded-md object-cover border border-gold/20 shrink-0" />
                  <div>
                    <div className="font-tamil-display text-xl text-gold tracking-wide">{d.nameTa}</div>
                    <div className="text-sm text-ivory/80 font-english-regular mt-0.5">{d.nameEn}</div>
                  </div>
                  {d.startYear && <span className="ml-auto text-xs text-stone font-english-regular self-center">{d.startYear}-{d.endYear}</span>}
                </Link>
              ))}
            </div>
          </FadeIn>
          <FadeIn direction="up" delay={150}>
            <SectionHeading eyebrow="By district" title="Explore" dark />
            <div className="grid gap-3 sm:grid-cols-2">
              {districts.map((d) => (
                <Link key={d.slug} to={`/explore?district=${d.slug}`} className="rounded-lg border border-gold/10 bg-obsidian px-4 py-3 transition hover:border-gold/40">
                  <span className="font-english-display text-lg text-ivory/90 font-semibold tracking-wide">{d.nameEn}</span>
                  {d.headquarters && <span className="block text-xs text-stone font-english-regular mt-1">HQ: {d.headquarters}</span>}
                </Link>
              ))}
            </div>
          </FadeIn>
        </div>
      </section>

      {/* FEATURED INSCRIPTIONS */}
      <section className="container-page py-16 border-t border-gold/10 bg-obsidian">
        <FadeIn direction="up">
          <SectionHeading
            eyebrow="From the walls"
            title="Recent & featured inscriptions"
            subtitle="Each record carries its publication reference - SII, ARE, or Epigraphia Indica."
            right={<Link to="/inscriptions" className="btn-ghost !text-ivory !border-gold/30 hover:!border-gold hover:!text-gold">Explore all</Link>}
            dark
          />
        </FadeIn>
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {featuredInscriptions.map((i, idx) => <InscriptionCardItem key={i.slug} inscription={i} index={idx} dark={true} />)}
        </div>
      </section>

      {/* CTA STRIP */}
      <section className="bg-gradient-to-r from-obsidian via-[#141512] to-obsidian border-t border-gold/20 text-ivory">
        <FadeIn direction="up" className="container-page flex flex-col items-start justify-between gap-6 py-16 sm:flex-row sm:items-center">
          <div>
            <h2 className="font-english-display text-3xl font-semibold tracking-wide text-gold">Follow the full journey</h2>
            <p className="mt-2 text-ivory/60 font-english-regular text-sm tracking-wide">Temple → location → image → transcription → translation → meaning → source.</p>
          </div>
          <div className="flex gap-4">
            <Link to="/map" className="btn-gold !bg-[#bda165] !text-charcoal-dark hover:!bg-gold-light">Open the map</Link>
            <Link to="/timeline" className="btn-ghost !text-ivory/80 !border-ivory/20 hover:!border-gold hover:!text-gold">View timeline</Link>
          </div>
        </FadeIn>
      </section>
    </div>
  )
}
