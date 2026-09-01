import { useEffect, useState, useMemo } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import L from 'leaflet'
import { api } from '../services/api'
import type { TempleCard, InscriptionLocationDto } from '../types'

// Inline (CSS) pin so markers never depend on external image URLs.
const templeIcon = L.divIcon({
  className: 'kalvettu-marker',
  html: '<div class="kalvettu-pin-wrap"><div class="kalvettu-pin"></div></div>',
  iconSize: [26, 42],
  iconAnchor: [13, 27],
  popupAnchor: [0, -26],
})

export default function InteractiveMap() {
  const [params, setParams] = useSearchParams()
  const [temples, setTemples] = useState<TempleCard[]>([])
  const [selected, setSelected] = useState<string>(params.get('temple') ?? '')
  const [locations, setLocations] = useState<InscriptionLocationDto[]>([])

  useEffect(() => {
    api.temples().then(setTemples).catch(() => {})
  }, [])

  useEffect(() => {
    if (selected) api.locations(selected).then(setLocations).catch(() => setLocations([]))
    else setLocations([])
  }, [selected])

  const temple = temples.find((t) => t.slug === selected)
  const center = useMemo<[number, number]>(() => {
    if (temple?.lat && temple?.lng) return [temple.lat, temple.lng]
    return [11.0, 79.0]
  }, [temple])

  return (
    <div className="heritage-bg">
      <div className="bg-charcoal py-10 text-ivory">
        <div className="container-page">
          <p className="label-eyebrow text-gold-light">Interactive Temple Map</p>
          <h1 className="mt-2 font-display text-4xl font-semibold sm:text-5xl">Where the inscriptions live</h1>
          <p className="mt-3 max-w-2xl text-ivory/70">
            Pick a temple to see its documented inscription locations. Locations are shown only where a source verifies them —
            we never invent where an inscription sits.
          </p>
        </div>
      </div>

      <div className="container-page grid gap-6 py-10 lg:grid-cols-[1fr_360px]">
        <div className="card-surface overflow-hidden">
          <MapContainer center={center} zoom={selected ? 16 : 7} scrollWheelZoom className="h-[60vh] min-h-[420px] w-full">
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <MapController center={center} zoom={selected ? 16 : 7} />
            {temples.map((t) => (
              t.lat && t.lng ? (
                <Marker
                  key={t.slug}
                  position={[t.lat, t.lng]}
                  icon={templeIcon}
                  eventHandlers={{ click: () => setSelected(t.slug) }}
                >
                  <Popup>
                    <strong>{t.nameEn}</strong>
                    <br />{t.town}
                    <br />
                    <Link to={`/temples/${t.slug}`} className="text-gold-dark underline">Temple page</Link>
                  </Popup>
                </Marker>
              ) : null
            ))}
          </MapContainer>
        </div>

        <aside className="space-y-4">
          <label className="block">
            <span className="label-eyebrow">Select a temple</span>
            <select
              value={selected}
              onChange={(e) => { setSelected(e.target.value); setParams(e.target.value ? { temple: e.target.value } : {}) }}
              className="mt-1 w-full rounded-sm border border-charcoal/15 px-3 py-2.5 text-sm focus:border-gold focus:outline-none"
            >
              <option value="">— Choose —</option>
              {temples.map((t) => <option key={t.slug} value={t.slug}>{t.nameEn}</option>)}
            </select>
          </label>

          {selected && (
            <div className="card-surface p-4">
              <h3 className="font-display text-lg font-semibold text-charcoal">{temple?.nameEn}</h3>
              <p className="text-xs text-stone">{locations.length} documented inscription location(s)</p>

              {locations.length > 0 ? (
                <ul className="mt-3 space-y-2">
                  {locations.map((l) => (
                    <li key={l.id} className="rounded-sm border border-charcoal/10 p-3 transition hover:border-gold">
                      <Link to={`/inscriptions/${l.inscriptionSlug}`} className="font-medium text-gold-dark hover:underline">{l.label}</Link>
                      {l.area && <p className="text-xs text-stone">{l.area}</p>}
                      {l.description && <p className="mt-1 text-sm text-ink/75">{l.description}</p>}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="mt-3 text-sm italic text-stone">
                  No inscription locations are seeded for this temple yet (we only plot verified positions).
                </p>
              )}

              <InTemplePlan locations={locations} />
            </div>
          )}

          <div className="card-surface border-gold/30 p-4 text-xs leading-relaxed text-stone">
            <strong className="text-ink">Note on methodology.</strong> Geographic pins use the temple's real coordinates.
            In-temple markers are an approximate schematic; the authoritative temple plans are not redistributed here, so
            positions are indicative and every marker links back to its verified source.
          </div>
        </aside>
      </div>
    </div>
  )
}

function MapController({ center, zoom }: { center: [number, number]; zoom: number }) {
  const map = useMap()
  useEffect(() => {
    map.setView(center, zoom)
  }, [center, zoom, map])
  return null
}

function InTemplePlan({ locations }: { locations: InscriptionLocationDto[] }) {
  // Approximate in-temple schematic using mapX/mapY (0..1) as percentages.
  // This is an indicative layout, NOT an authoritative temple plan.
  if (locations.length === 0) return null
  return (
    <div className="mt-4">
      <p className="label-eyebrow mb-2">In-temple schematic</p>
      <div className="relative h-56 w-full overflow-hidden rounded-sm border border-charcoal/15 bg-ivory-deep">
        <div className="absolute inset-x-6 top-1/2 h-24 -translate-y-1/2 rounded-sm border border-charcoal/20 bg-charcoal/5" />
        <div className="absolute inset-0 grid place-items-center text-charcoal/15 font-display text-sm">temple plan (schematic)</div>
        {locations.map((l) => (
          <Link
            key={l.id}
            to={`/inscriptions/${l.inscriptionSlug}`}
            className="group absolute -translate-x-1/2 -translate-y-1/2"
            style={{ left: `${(l.mapX ?? 0.5) * 100}%`, top: `${(l.mapY ?? 0.5) * 100}%` }}
            title={l.label}
          >
            <span className="block h-3.5 w-3.5 rounded-full border-2 border-ivory-card bg-gold transition group-hover:scale-125" />
          </Link>
        ))}
      </div>
      <p className="mt-1 text-[11px] text-stone">Indicative positions only · click a marker for the inscription.</p>
    </div>
  )
}
