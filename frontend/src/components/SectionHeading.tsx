interface Props {
  eyebrow?: string
  title: string
  subtitle?: string
  right?: React.ReactNode
}

export default function SectionHeading({ eyebrow, title, subtitle, right }: Props) {
  return (
    <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div>
        {eyebrow && <p className="label-eyebrow mb-2">{eyebrow}</p>}
        <h2 className="section-title">{title}</h2>
        {subtitle && <p className="mt-2 max-w-2xl text-ink/70">{subtitle}</p>}
      </div>
      {right && <div className="shrink-0">{right}</div>}
    </div>
  )
}
