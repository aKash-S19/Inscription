import { Link } from 'react-router-dom'
import type { TempleCard } from '../types'
import ImageWithAttribution from './ImageWithAttribution'
import FadeIn from './FadeIn'

export default function TempleCardItem({ temple, image, index = 0 }: { temple: TempleCard; image?: string; index?: number }) {
  const src = image || temple.heroImageUrl
  // Cap the delay so items far down the page don't take forever if they load all at once.
  const staggerDelay = Math.min((index % 12) * 100, 800)
  
  return (
    <FadeIn delay={staggerDelay}>
      <Link to={`/temples/${temple.slug}`} className="card-surface group flex h-full flex-col overflow-hidden transition hover:shadow-soft">
        <div className="relative h-52 shrink-0 overflow-hidden bg-ivory-deep">
          {src ? (
            <img
              src={src}
              alt={temple.nameEn}
              loading="lazy"
              referrerPolicy="no-referrer"
              className="h-full w-full object-cover transition duration-500 group-hover:scale-105"
            />
          ) : (
            <div className="grid h-full place-items-center text-charcoal/30 font-tamil-display text-4xl tracking-wide">கோயில்</div>
          )}
          <div className="absolute left-3 top-3 flex gap-2">
            {temple.unescoWorldHeritage && <span className="chip bg-gold text-ivory-card">UNESCO</span>}
            {temple.asiMonument && <span className="chip">ASI</span>}
          </div>
        </div>
        <div className="flex flex-1 flex-col p-4">
          <h3 className="font-english-display text-xl font-semibold text-charcoal group-hover:text-gold-dark">{temple.nameEn}</h3>
          {temple.nameTa && <p className="text-lg font-semibold text-stone font-tamil-regular mt-1" lang="ta">{temple.nameTa}</p>}
          <p className="mt-1 text-xs uppercase tracking-wide text-stone font-english-regular">{temple.town}{temple.deity ? ` · ${temple.deity}` : ''}</p>
          <p className="mt-3 line-clamp-3 text-sm leading-relaxed text-ink/80 font-english-regular">{temple.summary}</p>
          {temple.consecrationYear && (
            <p className="mt-auto pt-3 text-xs font-medium text-gold-dark font-english-regular">Consecrated ≈ {temple.consecrationYear} CE</p>
          )}
        </div>
      </Link>
    </FadeIn>
  )
}
