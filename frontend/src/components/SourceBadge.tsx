export function SourceBadge({ verified = true }: { verified?: boolean }) {
  return verified ? (
    <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-800 ring-1 ring-emerald-200">
      <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" /> Verified source
    </span>
  ) : (
    <span className="inline-flex items-center gap-1 rounded-full bg-amber-50 px-2.5 py-1 text-xs font-medium text-amber-800 ring-1 ring-amber-200">
      <span className="h-1.5 w-1.5 rounded-full bg-amber-500" /> Unverified
    </span>
  )
}

export function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <dt className="label-eyebrow">{label}</dt>
      <dd className="mt-1 text-sm leading-relaxed text-ink/85">{children || <span className="italic text-stone">Not recorded in a citable source</span>}</dd>
    </div>
  )
}
