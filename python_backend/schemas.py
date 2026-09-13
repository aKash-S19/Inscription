from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from typing import List, Optional, Any

class BaseSchema(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)

class SourceDto(BaseSchema):
    id: int
    slug: Optional[str] = None
    institution: str
    publication: Optional[str] = None
    volume: Optional[str] = None
    year: Optional[str] = None
    page: Optional[str] = None
    reference: str
    url: Optional[str] = None
    source_type: Optional[str] = None
    source_priority: Optional[int] = 1
    notes: Optional[str] = None

class ImageDto(BaseSchema):
    id: int
    entity_type: str
    entity_slug: str
    category: Optional[str] = None
    image_url: str
    thumb_url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    author: Optional[str] = None
    license: Optional[str] = None
    license_url: Optional[str] = None
    commons_url: Optional[str] = None
    caption: Optional[str] = None
    storage_path: Optional[str] = None
    verification_status: Optional[str] = "VERIFIED"

class InscriptionCard(BaseSchema):
    id: int
    slug: str
    temple_slug: str
    title: str
    title_ta: Optional[str] = None
    reference_id: Optional[str] = None
    are_number: Optional[str] = None
    sii_reference: Optional[str] = None
    ruler_slug: Optional[str] = None
    dynasty_slug: Optional[str] = None
    regnal_year: Optional[str] = None
    language: Optional[str] = None
    script: Optional[str] = None
    physical_location: Optional[str] = None
    image_url: Optional[str] = None
    thumb_image_url: Optional[str] = None
    verified: bool = True
    verification_status: Optional[str] = "VERIFIED"

class InscriptionLocationDto(BaseSchema):
    id: int
    inscription_slug: str
    temple_slug: str
    label: str
    description: Optional[str] = None
    area: Optional[str] = None
    map_x: Optional[float] = None
    map_y: Optional[float] = None
    coordinate_system: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None

class DynastyDto(BaseSchema):
    id: int
    slug: str
    name_en: str
    name_ta: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    capital: Optional[str] = None
    description: Optional[str] = None
    source_note: Optional[str] = None

class DistrictDto(BaseSchema):
    id: int
    slug: str
    name_en: str
    headquarters: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    note: Optional[str] = None

class RulerDto(BaseSchema):
    id: int
    slug: str
    name_en: str
    name_ta: Optional[str] = None
    dynasty_slug: Optional[str] = None
    reign_start: Optional[int] = None
    reign_end: Optional[int] = None
    capital: Optional[str] = None
    note: Optional[str] = None
    source_note: Optional[str] = None

class TempleCard(BaseSchema):
    id: int
    slug: str
    name_en: str
    name_ta: Optional[str] = None
    town: Optional[str] = None
    district_slug: Optional[str] = None
    dynasty_slug: Optional[str] = None
    deity: Optional[str] = None
    period_note: Optional[str] = None
    consecration_year: Optional[int] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    summary: Optional[str] = None
    history: Optional[str] = None
    architecture: Optional[str] = None
    managed_by: Optional[str] = None
    source_note: Optional[str] = None
    unesco_world_heritage: bool = False
    unesco_url: Optional[str] = None
    asi_monument: bool = False
    asi_url: Optional[str] = None
    wikipedia_url: Optional[str] = None
    image_url: Optional[str] = None
    hero_image_url: Optional[str] = None
    alternate_names: Optional[str] = None
    patron: Optional[str] = None
    verification_status: Optional[str] = "VERIFIED"

class TempleDetail(BaseSchema):
    temple: TempleCard
    images: List[ImageDto]
    inscriptions: List[InscriptionCard]
    locations: List[InscriptionLocationDto]
    dynasty: Optional[DynastyDto] = None
    district: Optional[DistrictDto] = None
    source: Optional[SourceDto] = None

class InscriptionDetail(BaseSchema):
    id: int
    slug: str
    temple_slug: str
    title: str
    title_ta: Optional[str] = None
    reference_id: Optional[str] = None
    are_number: Optional[str] = None
    sii_reference: Optional[str] = None
    epigraphia_indica: Optional[str] = None
    ruler_slug: Optional[str] = None
    dynasty_slug: Optional[str] = None
    regnal_year: Optional[str] = None
    date_note: Optional[str] = None
    language: Optional[str] = None
    script: Optional[str] = None
    physical_location: Optional[str] = None
    original_text: Optional[str] = None
    original_text_source: Optional[str] = None
    transliteration: Optional[str] = None
    translation: Optional[str] = None
    translation_source: Optional[str] = None
    simple_explanation: Optional[str] = None
    historical_significance: Optional[str] = None
    source_citation: str
    source_url: Optional[str] = None
    verified: bool = True
    verification_status: Optional[str] = "VERIFIED"
    images: List[ImageDto] = []
    temple: Optional[TempleCard] = None
    source: Optional[SourceDto] = None

class TimelineEvent(BaseSchema):
    year: str
    title: str
    description: Optional[str] = None
    entity_type: str
    entity_slug: str
    type: Optional[str] = None
    related_slug: Optional[str] = None
    source_note: Optional[str] = None

class SearchResult(BaseSchema):
    temples: List[TempleCard]
    inscriptions: List[InscriptionCard]
    dynasties: Optional[List[DynastyDto]] = []
    rulers: Optional[List[RulerDto]] = []
    districts: Optional[List[DistrictDto]] = []
    total_matches: Optional[int] = 0

# AI Models
class ChatMessage(BaseSchema):
    role: str
    content: str

class ChatRequest(BaseSchema):
    messages: List[ChatMessage]
    language: Optional[str] = "English"

class SourceCitation(BaseSchema):
    institution: str
    publication: Optional[str] = None
    reference: str
    url: Optional[str] = None

class ChatResponse(BaseSchema):
    answer: str
    language: str
    sources: Optional[List[SourceCitation]] = []
    related_temples: Optional[List[str]] = []
    related_inscriptions: Optional[List[str]] = []
    provider_used: Optional[str] = None

class TranslateRequest(BaseSchema):
    text: str
    target_language: Optional[str] = "English"
    image_base64: Optional[str] = None
    mime_type: Optional[str] = None

class TranslateResponse(BaseSchema):
    detected_language: Optional[str] = "Tamil"
    detected_script: Optional[str] = "Tamil"
    original_text: Optional[str] = None
    translation: str
    explanation: str
    target_language: str
    important_terms: Optional[List[str]] = []
    historical_context: Optional[str] = None
    is_draft: bool = False
    verification_status: str = "VERIFIED"
    provider_used: Optional[str] = None

class IngestRequest(BaseSchema):
    image_base64: Optional[str] = None
    mime_type: Optional[str] = None
    text: Optional[str] = None
    temple_name: Optional[str] = None
    location_in_temple: Optional[str] = None
    notes: Optional[str] = None

class IngestResponse(BaseSchema):
    title: str
    language: str
    script: str
    translation: str
    simple_explanation: str
    historical_significance: str
    ruler: str
    dynasty: Optional[str] = None
    notes: str
    verification_status: str = "DRAFT"
    status_message: str = "AI-generated draft - requires human verification before publication."
    provider_used: Optional[str] = None

class WikiFetchRequest(BaseSchema):
    query_or_url: str

