import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../services/api'
import type { InscriptionDetail } from '../types'
import ImageWithAttribution from '../components/ImageWithAttribution'
import Spinner from '../components/Spinner'
import { SourceBadge, Field } from '../components/SourceBadge'

export default function InscriptionDetails() {
  const { slug } = useParams()
  const [data, setData] = useState<InscriptionDetail | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!slug) return
    setLoading(true)
    api.inscription(slug).then(setData).catch(() => setData(null)).finally(() => setLoading(false))
  }, [slug])

  if (loading) return <Spinner />
  if (!data) return <div className="container-page py-20 text-center text-ink/70">Inscription not found.</div>

  const img = data.images[0]

  return (
    <div>
      {/* HERO */}
      <section className="bg-charcoal py-12 text-ivory">
        <div className="container-page">
          <nav className="mb-3 text-xs text-ivory/50">
            <Link to="/inscriptions" className="hover:text-gold-light">Inscriptions</Link>
            {data.temple && <span> · <Link to={`/temples/${data.temple.slug}`} className="hover:text-gold-light">{data.temple.nameEn}</Link></span>}
          </nav>
          {data.referenceId && <p className="label-eyebrow text-gold-light">{data.referenceId}</p>}
          <h1 className="mt-2 font-display text-4xl font-semibold sm:text-5xl">{data.title}</h1>
          {data.titleTa && <p className="mt-1 text-lg text-ivory/80" lang="ta">{data.titleTa}</p>}
          <div className="mt-3 flex flex-wrap items-center gap-3">
            <SourceBadge verified={data.verified} />
            {data.temple && <span className="text-sm text-ivory/60">at {data.temple.nameEn}</span>}
          </div>
        </div>
      </section>

      <div className="container-page grid gap-10 py-10 lg:grid-cols-3">
        {/* LEFT: image + identification */}
        <div className="lg:col-span-1">
          <div className="card-surface overflow-hidden">
            {img ? (
              <ImageWithAttribution image={img} className="aspect-[4/5]" />
            ) : (
              <div className="grid aspect-[4/5] place-items-center bg-ivory-deep text-charcoal/30 font-display text-4xl">கல்வெட்டு</div>
            )}
          </div>
          <div className="card-surface mt-5 p-5">
            <h2 className="label-eyebrow mb-3">Identification</h2>
            <dl className="space-y-3">
              <Field label="Reference">{data.referenceId}</Field>
              <Field label="ARE no.">{data.areNumber}</Field>
              <Field label="SII">{data.siiReference}</Field>
              <Field label="Epigraphia Indica">{data.epigraphiaIndica}</Field>
              <Field label="Ruler / dynasty">{[data.rulerSlug, data.dynastySlug].filter(Boolean).join(' · ')}</Field>
              <Field label="Regnal year">{data.regnalYear}</Field>
              <Field label="Date note">{data.dateNote}</Field>
              <Field label="Language / script">{[data.language, data.script].filter(Boolean).join(' · ')}</Field>
              <Field label="Physical location">{data.physicalLocation}</Field>
            </dl>
          </div>
        </div>

        {/* RIGHT: transcription, translation, meaning */}
        <div className="lg:col-span-2 space-y-8">
          <Block title="Original inscription" eyebrow="Authentic record">
            {data.originalText ? (
              <div className="rounded-md bg-ivory-deep p-5 font-display text-2xl leading-loose text-charcoal" lang="ta">{data.originalText}</div>
            ) : (
              <p className="rounded-md border border-dashed border-stone/40 bg-ivory-deep p-5 text-sm italic text-stone">
                The original Tamil/Grantha text is published in the source cited below and is not transcribed here to avoid errors.
                {data.originalTextSource && <span className="block mt-2 not-italic text-ink/70">{data.originalTextSource}</span>}
              </p>
            )}
          </Block>

          {data.transliteration && (
            <Block title="Transliteration" eyebrow="Romanised">
              <p className="rounded-md bg-ivory-deep p-4 font-mono text-sm leading-relaxed text-ink/85">{data.transliteration}</p>
            </Block>
          )}

          <Block title="Translation" eyebrow="From the published source">
            <p className="text-lg leading-relaxed text-ink/90">{data.translation}</p>
            {data.translationSource && <p className="mt-3 text-xs italic text-stone">{data.translationSource}</p>}
          </Block>

          <Block title="Simple explanation" eyebrow="In plain language">
            <p className="text-lg leading-relaxed text-ink/90">{data.simpleExplanation}</p>
          </Block>

          <Block title="Historical significance" eyebrow="Why it matters">
            <p className="text-lg leading-relaxed text-ink/90">{data.historicalSignificance}</p>
          </Block>

          <div className="card-surface border-gold/30 p-5">
            <h2 className="label-eyebrow mb-2">Source / reference</h2>
            <p className="text-sm leading-relaxed text-ink/85">{data.sourceCitation}</p>
            {data.sourceUrl && (
              <a href={data.sourceUrl} target="_blank" rel="noreferrer noopener" className="mt-3 inline-block text-sm font-medium text-gold-dark hover:underline">
                Open source ↗
              </a>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

function Block({ title, eyebrow, children }: { title: string; eyebrow: string; children: React.ReactNode }) {
  return (
    <section>
      <p className="label-eyebrow mb-2">{eyebrow}</p>
      <h2 className="font-display text-2xl font-semibold text-charcoal">{title}</h2>
      <div className="mt-3">{children}</div>
      <div className="tamil-rule mt-6" />
    </section>
  )
}
