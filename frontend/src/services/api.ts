import type {
  TempleCard, TempleDetail, InscriptionCard, InscriptionDetail,
  DynastyDto, RulerDto, DistrictDto, InscriptionLocationDto, TimelineEvent, SearchResult,
} from '../types'

const BASE = '/api'

async function get<T>(path: string): Promise<T> {
  const res = await fetch(BASE + path)
  if (!res.ok) {
    throw new Error(`Request failed: ${path} (${res.status})`)
  }
  return res.json() as Promise<T>
}

export const api = {
  temples: (q?: string, district?: string, dynasty?: string) =>
    get<TempleCard[]>(`/temples?` + new URLSearchParams(
      Object.entries({ q: q ?? '', district: district ?? '', dynasty: dynasty ?? '' })
        .filter(([, v]) => v).map(([k, v]) => [k, v]) as [string, string][],
    ).toString()),

  temple: (slug: string) => get<TempleDetail>(`/temples/${slug}`),

  inscriptions: (params: Record<string, string | undefined> = {}) =>
    get<InscriptionCard[]>(`/inscriptions?` + new URLSearchParams(
      Object.entries(params).filter(([, v]) => v) as [string, string][],
    ).toString()),

  inscription: (slug: string) => get<InscriptionDetail>(`/inscriptions/${slug}`),

  dynasties: () => get<DynastyDto[]>('/dynasties'),
  rulers: (dynasty?: string) =>
    get<RulerDto[]>(`/rulers?` + (dynasty ? `dynasty=${encodeURIComponent(dynasty)}` : '')),
  districts: () => get<DistrictDto[]>('/districts'),

  locations: (templeSlug: string) => get<InscriptionLocationDto[]>(`/temples/${templeSlug}/locations`),

  timeline: () => get<TimelineEvent[]>('/timeline'),

  search: (q: string) => get<SearchResult>(`/search?q=${encodeURIComponent(q)}`),
}

export type { TempleCard, TempleDetail, InscriptionCard, InscriptionDetail, DynastyDto, RulerDto, DistrictDto, InscriptionLocationDto, TimelineEvent, SearchResult }
