export interface TempleCard {
  id: number
  slug: string
  nameEn: string
  nameTa?: string
  town?: string
  districtSlug?: string
  dynastySlug?: string
  deity?: string
  periodNote?: string
  patron?: string
  consecrationYear?: number
  lat?: number
  lng?: number
  summary?: string
  history?: string
  architecture?: string
  unescoWorldHeritage?: boolean
  unescoUrl?: string
  asiMonument?: boolean
  asiUrl?: string
  managedBy?: string
  alternateNames?: string
  sourceNote?: string
  heroImageUrl?: string
}

export interface InscriptionCard {
  id: number
  slug: string
  templeSlug: string
  title: string
  titleTa?: string
  referenceId?: string
  areNumber?: string
  siiReference?: string
  rulerSlug?: string
  dynastySlug?: string
  regnalYear?: string
  language?: string
  script?: string
  physicalLocation?: string
  thumbImageUrl?: string
  verified?: boolean
}

export interface ImageDto {
  id: number
  entityType: string
  entitySlug: string
  category?: string
  imageUrl: string
  thumbUrl?: string
  width?: number
  height?: number
  author?: string
  license?: string
  licenseUrl?: string
  commonsUrl?: string
  caption?: string
}

export interface InscriptionLocationDto {
  id: number
  inscriptionSlug: string
  templeSlug: string
  label: string
  description?: string
  area?: string
  mapX?: number
  mapY?: number
  coordinateSystem?: string
  lat?: number
  lng?: number
}

export interface DynastyDto {
  id: number
  slug: string
  nameEn: string
  nameTa?: string
  startYear?: number
  endYear?: number
  capital?: string
  description?: string
  sourceNote?: string
}

export interface RulerDto {
  id: number
  slug: string
  nameEn: string
  nameTa?: string
  dynastySlug?: string
  reignStart?: number
  reignEnd?: number
  capital?: string
  note?: string
  sourceNote?: string
}

export interface DistrictDto {
  id: number
  slug: string
  nameEn: string
  headquarters?: string
  lat?: number
  lng?: number
  note?: string
}

export interface TimelineEvent {
  year: string
  title: string
  description: string
  type: string
  relatedSlug: string
  sourceNote?: string
}

export interface TempleDetail {
  temple: TempleCard
  images: ImageDto[]
  inscriptions: InscriptionCard[]
  locations: InscriptionLocationDto[]
  dynasty?: DynastyDto
  district?: DistrictDto
}

export interface InscriptionDetail {
  id: number
  slug: string
  templeSlug: string
  title: string
  titleTa?: string
  referenceId?: string
  areNumber?: string
  siiReference?: string
  epigraphiaIndica?: string
  rulerSlug?: string
  dynastySlug?: string
  regnalYear?: string
  dateNote?: string
  language?: string
  script?: string
  physicalLocation?: string
  originalText?: string
  originalTextSource?: string
  transliteration?: string
  translation?: string
  translationSource?: string
  simpleExplanation?: string
  historicalSignificance?: string
  sourceCitation: string
  sourceUrl?: string
  verified?: boolean
  images: ImageDto[]
  temple?: TempleCard
}

export interface SearchResult {
  temples: TempleCard[]
  inscriptions: InscriptionCard[]
}
