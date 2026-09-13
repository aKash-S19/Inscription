import { Link } from 'react-router-dom'
import type { InscriptionCard } from '../types'
import FadeIn from './FadeIn'

export default function InscriptionCardItem({ inscription, index = 0, dark = false }: { inscription: InscriptionCard; index?: number; dark?: boolean }) {
  const staggerDelay = Math.min((index % 12) * 100, 800)

  return (
    <FadeIn delay={staggerDelay}>
      <Link to={`/inscriptions/${inscription.slug}`} className={`group flex flex-col overflow-hidden transition-all duration-300 hover:-translate-y-1 hover:shadow-xl h-full rounded-md border ${dark ? 'bg-obsidian border-gold/10 hover:border-gold/40' : 'card-surface hover:shadow-soft'}`}>
        <div className={`relative h-36 shrink-0 overflow-hidden ${dark ? 'bg-[#161616]' : 'bg-ivory-deep'}`}>
          {inscription.thumbImageUrl ? (
            <img
              src={inscription.thumbImageUrl}
              alt={inscription.title}
              loading="lazy"
              referrerPolicy="no-referrer"
              className="h-full w-full object-cover transition duration-500 group-hover:scale-105"
            />
          ) : (
            <div className={`grid h-full place-items-center font-tamil-display text-3xl tracking-wide ${dark ? 'bg-obsidian text-ivory/10' : 'bg-charcoal/5 text-charcoal/30'}`}>கல்வெட்டு</div>
          )}
          {inscription.referenceId && (
            <span className={`absolute left-3 top-3 chip font-english-regular ${dark ? 'bg-charcoal-dark/80 text-gold border-gold/30' : 'bg-charcoal/70 text-gold-light'}`}>{inscription.referenceId}</span>
          )}
        </div>
        <div className="flex flex-1 flex-col p-4">
          <h3 className={`font-english-display text-lg font-semibold leading-snug group-hover:text-gold-light ${dark ? 'text-ivory' : 'text-charcoal'}`}>{inscription.title}</h3>
          <p className={`mt-1 text-xs uppercase tracking-wide font-english-regular ${dark ? 'text-gold/80' : 'text-stone'}`}>
            {[inscription.language, inscription.script].filter(Boolean).join(' · ')}
          </p>
          {inscription.physicalLocation && (
            <p className={`mt-2 line-clamp-2 text-sm font-english-regular ${dark ? 'text-ivory/60' : 'text-ink/75'}`}>{inscription.physicalLocation}</p>
          )}
          {inscription.regnalYear && (
            <p className="mt-auto pt-3 text-xs font-medium text-gold font-english-regular">{inscription.regnalYear}</p>
          )}
        </div>
      </Link>
    </FadeIn>
  )
}
