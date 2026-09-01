import { Link } from 'react-router-dom'
import type { InscriptionCard } from '../types'

export default function InscriptionCardItem({ inscription }: { inscription: InscriptionCard }) {
  return (
    <Link to={`/inscriptions/${inscription.slug}`} className="card-surface group flex flex-col overflow-hidden transition hover:shadow-soft">
      <div className="relative h-36 overflow-hidden bg-ivory-deep">
        {inscription.thumbImageUrl ? (
          <img
            src={inscription.thumbImageUrl}
            alt={inscription.title}
            loading="lazy"
            referrerPolicy="no-referrer"
            className="h-full w-full object-cover transition duration-500 group-hover:scale-105"
          />
        ) : (
          <div className="grid h-full place-items-center bg-charcoal/5 text-charcoal/30 font-display text-3xl">கல்வெட்டு</div>
        )}
        {inscription.referenceId && (
          <span className="absolute left-3 top-3 chip bg-charcoal/70 text-gold-light">{inscription.referenceId}</span>
        )}
      </div>
      <div className="flex flex-1 flex-col p-4">
        <h3 className="font-display text-lg font-semibold leading-snug text-charcoal group-hover:text-gold-dark">{inscription.title}</h3>
        <p className="mt-1 text-xs uppercase tracking-wide text-stone">
          {[inscription.language, inscription.script].filter(Boolean).join(' · ')}
        </p>
        {inscription.physicalLocation && (
          <p className="mt-2 line-clamp-2 text-sm text-ink/75">{inscription.physicalLocation}</p>
        )}
        {inscription.regnalYear && (
          <p className="mt-auto pt-3 text-xs font-medium text-gold-dark">{inscription.regnalYear}</p>
        )}
      </div>
    </Link>
  )
}
