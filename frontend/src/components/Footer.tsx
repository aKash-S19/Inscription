import { Link } from 'react-router-dom'

export default function Footer() {
  return (
    <footer className="border-t border-gold/30 bg-charcoal text-ivory/80">
      <div className="container-page grid gap-8 py-12 md:grid-cols-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="grid h-8 w-8 place-items-center rounded-sm border border-gold/50 text-gold-light font-display">க</span>
            <span className="font-display text-lg text-ivory">Kalvettu</span>
          </div>
          <p className="mt-3 max-w-xs text-sm leading-relaxed text-ivory/60">
            A digital archive of Tamil temple inscriptions — connecting the temple,
            its inscription locations, the original records, and their authoritative sources.
          </p>
        </div>
        <div>
          <h4 className="label-eyebrow mb-3">Explore</h4>
          <ul className="space-y-2 text-sm">
            <li><Link className="hover:text-gold-light" to="/temples">Temples</Link></li>
            <li><Link className="hover:text-gold-light" to="/inscriptions">Inscriptions</Link></li>
            <li><Link className="hover:text-gold-light" to="/map">Interactive Map</Link></li>
            <li><Link className="hover:text-gold-light" to="/timeline">Timeline</Link></li>
          </ul>
        </div>
        <div>
          <h4 className="label-eyebrow mb-3">Sources</h4>
          <ul className="space-y-2 text-sm text-ivory/60">
            <li>Archaeological Survey of India</li>
            <li>South Indian Inscriptions (SII)</li>
            <li>Annual Report on Indian Epigraphy</li>
            <li>Epigraphia Indica · UNESCO · TN Archaeology</li>
          </ul>
        </div>
        <div>
          <h4 className="label-eyebrow mb-3">About</h4>
          <p className="text-sm leading-relaxed text-ivory/60">
            Built as a heritage/epigraphy platform. Every record retains its source
            reference; facts that cannot be verified are marked as unavailable rather
            than invented.
          </p>
          <Link to="/about" className="mt-3 inline-block text-sm text-gold-light hover:underline">Read the data policy →</Link>
        </div>
      </div>
      <div className="border-t border-gold/15 py-4 text-center text-xs text-ivory/40">
        © {new Date().getFullYear()} Kalvettu Heritage Project · Photographs via Wikimedia Commons under their respective licences.
      </div>
    </footer>
  )
}
