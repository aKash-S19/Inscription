import type { ReactNode } from 'react'

interface Props {
  eyebrow?: string
  title: string
  subtitle?: string
  right?: ReactNode
  className?: string
  dark?: boolean
}

export default function SectionHeading({ eyebrow, title, subtitle, right, className = '', dark = false }: Props) {
  return (
    <div className={`mb-10 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between ${className}`}>
      <div className="max-w-2xl">
        {eyebrow && (
          <div className="mb-2 flex items-center gap-3">
            <span className={`h-px w-8 ${dark ? 'bg-gold/30' : 'bg-gold-light'}`} />
            <span className="label-eyebrow">{eyebrow}</span>
          </div>
        )}
        <h2 className={`section-title ${dark ? 'text-ivory' : ''}`}>{title}</h2>
        {subtitle && <p className={`mt-3 text-lg ${dark ? 'text-ivory/70' : 'text-charcoal/70'}`}>{subtitle}</p>}
      </div>
      {right && <div className="shrink-0">{right}</div>}
    </div>
  )
}
