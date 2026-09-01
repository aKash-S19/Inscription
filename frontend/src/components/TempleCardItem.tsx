import { Link } from 'react-router-dom'
import type { TempleCard } from '../types'
import ImageWithAttribution from './ImageWithAttribution'

export default function TempleCardItem({ temple, image }: { temple: TempleCard; image?: string }) {
  const src = image || temple.heroImageUrl
  return (
    <Link to={`/temples/${temple.slug}`} className="card-surface group flex flex-col overflow-hidden transition hover:shadow-soft">
      <div className="relative h-52 overflow-hidden bg-ivory-deep">
        {src ? (
          <img
            src={src}
            alt={temple.nameEn}
            loading="lazy"
            referrerPolicy="no-referrer"
            className="h-full w-full object-cover transition duration-500 group-hover:scale-105"
          />
        ) : (
          <div className="grid h-full place-items-center text-charcoal/30 font-display text-4xl">கோயில்</div>
        )}
        <div className="absolute left-3 top-3 flex gap-2">
          {temple.unescoWorldHeritage && <span className="chip bg-gold text-ivory-card">UNESCO</span>}
          {temple.asiMonument && <span className="chip">ASI</span>}
        </div>
      </div>
      <div className="flex flex-1 flex-col p-4">
        <h3 className="font-display text-xl font-semibold text-charcoal group-hover:text-gold-dark">{temple.nameEn}</h3>
        {temple.nameTa && <p className="text-sm text-stone" lang="ta">{temple.nameTa}</p>}
        <p className="mt-1 text-xs uppercase tracking-wide text-stone">{temple.town}{temple.deity ? ` · ${temple.deity}` : ''}</p>
        <p className="mt-3 line-clamp-3 text-sm leading-relaxed text-ink/80">{temple.summary}</p>
        {temple.consecrationYear && (
          <p className="mt-auto pt-3 text-xs font-medium text-gold-dark">Consecrated ≈ {temple.consecrationYear} CE</p>
        )}
      </div>
    </Link>
  )
}
