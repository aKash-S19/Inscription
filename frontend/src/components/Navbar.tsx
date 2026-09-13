import { Link, useLocation } from 'react-router-dom'
import { useEffect, useState } from 'react'

const links = [
  { to: '/', label: 'Home' },
  { to: '/temples', label: 'Temples' },
  { to: '/inscriptions', label: 'Inscriptions' },
  { to: '/map', label: 'Map' },
  { to: '/explore', label: 'Dynasty & District' },
  { to: '/timeline', label: 'Timeline' },
  { to: '/ai', label: 'AI' },
  { to: '/about', label: 'Sources' },
]

export default function Navbar() {
  const location = useLocation()
  const [open, setOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12)
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <header className={`sticky top-0 z-50 transition-all duration-500 ${scrolled ? 'border-b border-gold/20 bg-[#0a0a0a]/85 backdrop-blur-md shadow-md' : 'border-b border-transparent bg-[#0a0a0a]'}`}>
      <nav className="container-page flex h-16 items-center justify-between">
        <Link to="/" className="flex items-center gap-3 -ml-2" onClick={() => setOpen(false)}>
          <img src="/logo-Photoroom.png" alt="Silaimozhi Logo" className="h-14 w-14 object-contain" />
          <span className="leading-tight">
            <span className="block font-english-display tracking-wide text-xl font-semibold tracking-wide text-ivory">Silaimozhi</span>
            <span className="hidden sm:block text-[10px] uppercase tracking-[0.28em] text-gold-light/80">Tamil Temple Inscriptions</span>
          </span>
        </Link>

        <ul className="hidden items-center gap-1 lg:flex">
          {links.map((l) => {
            const active = l.to === '/' ? location.pathname === '/' : location.pathname.startsWith(l.to)
            return (
              <li key={l.to}>
                <Link
                  to={l.to}
                  className={`rounded-sm px-3 py-2 text-sm font-medium transition ${
                    active ? 'text-gold-light' : 'text-ivory/75 hover:text-ivory'
                  }`}
                >
                  {l.label}
                </Link>
              </li>
            )
          })}
        </ul>

        <button className="text-ivory lg:hidden" onClick={() => setOpen((o) => !o)} aria-label="Menu">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
            {open ? <path d="M6 6l12 12M18 6L6 18" /> : <><path d="M3 6h18M3 12h18M3 18h18" /></>}
          </svg>
        </button>
      </nav>

      {open && (
        <ul className="border-t border-gold/20 bg-charcoal px-4 py-2 lg:hidden">
          {links.map((l) => (
            <li key={l.to}>
              <Link
                to={l.to}
                onClick={() => setOpen(false)}
                className="block rounded-sm px-3 py-2 text-sm font-medium text-ivory/80 hover:bg-charcoal-light"
              >
                {l.label}
              </Link>
            </li>
          ))}
        </ul>
      )}
    </header>
  )
}
