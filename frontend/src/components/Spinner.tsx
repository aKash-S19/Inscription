export default function Spinner() {
  return (
    <div className="grid min-h-[40vh] place-items-center">
      <div className="flex items-center gap-3 text-stone">
        <span className="h-5 w-5 animate-spin rounded-full border-2 border-gold/40 border-t-gold" />
        <span className="text-sm">Loading…</span>
      </div>
    </div>
  )
}

export function NotFound({ what = 'record' }: { what?: string }) {
  return (
    <div className="container-page grid min-h-[50vh] place-items-center text-center">
      <div>
        <p className="font-display text-6xl text-gold/50">404</p>
        <p className="mt-2 text-ink/70">The {what} you are looking for is not in the archive.</p>
        <a href="/" className="btn-gold mt-5">Return home</a>
      </div>
    </div>
  )
}
