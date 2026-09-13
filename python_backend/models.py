from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, DateTime, func

class Source(SQLModel, table=True):
    __tablename__ = "sources"
    id: Optional[int] = Field(default=None, primary_key=True)
    slug: Optional[str] = Field(default=None, unique=True, index=True)
    institution: str
    publication: Optional[str] = None
    volume: Optional[str] = None
    year: Optional[str] = None
    page: Optional[str] = None
    reference: str
    url: Optional[str] = None
    source_type: Optional[str] = "PRIMARY_EPIGRAPHIC"
    source_priority: int = Field(default=1)
    notes: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

class Dynasty(SQLModel, table=True):
    __tablename__ = "dynasties"
    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str = Field(unique=True, index=True)
    name_en: str
    name_ta: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    capital: Optional[str] = None
    description: Optional[str] = None
    source_id: Optional[int] = Field(default=None, foreign_key="sources.id")
    source_note: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

class Ruler(SQLModel, table=True):
    __tablename__ = "rulers"
    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str = Field(unique=True, index=True)
    name_en: str
    name_ta: Optional[str] = None
    dynasty_id: Optional[int] = Field(default=None, foreign_key="dynasties.id")
    dynasty_slug: Optional[str] = Field(default=None, index=True)
    reign_start: Optional[int] = None
    reign_end: Optional[int] = None
    capital: Optional[str] = None
    note: Optional[str] = None
    source_id: Optional[int] = Field(default=None, foreign_key="sources.id")
    source_note: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

class District(SQLModel, table=True):
    __tablename__ = "districts"
    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str = Field(unique=True, index=True)
    name_en: str
    headquarters: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    note: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

class Temple(SQLModel, table=True):
    __tablename__ = "temples"
    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str = Field(unique=True, index=True)
    name_en: str
    name_ta: Optional[str] = None
    alternate_names: Optional[str] = None
    district_id: Optional[int] = Field(default=None, foreign_key="districts.id")
    district_slug: Optional[str] = Field(default=None, index=True)
    state: Optional[str] = "Tamil Nadu"
    town: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    period_note: Optional[str] = None
    consecration_year: Optional[int] = None
    dynasty_id: Optional[int] = Field(default=None, foreign_key="dynasties.id")
    dynasty_slug: Optional[str] = Field(default=None, index=True)
    ruler_id: Optional[int] = Field(default=None, foreign_key="rulers.id")
    patron: Optional[str] = None
    deity: Optional[str] = None
    history: Optional[str] = None
    architecture: Optional[str] = None
    summary: Optional[str] = None
    unesco_world_heritage: bool = Field(default=False)
    unesco_url: Optional[str] = None
    asi_monument: bool = Field(default=False)
    asi_url: Optional[str] = None
    wikipedia_url: Optional[str] = None
    managed_by: Optional[str] = None
    source_id: Optional[int] = Field(default=None, foreign_key="sources.id")
    source_priority: int = Field(default=1)
    verification_status: str = Field(default="VERIFIED") # VERIFIED, DRAFT, UNDER_REVIEW, REJECTED
    verified: bool = Field(default=True)
    source_note: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

class Inscription(SQLModel, table=True):
    __tablename__ = "inscriptions"
    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str = Field(unique=True, index=True)
    temple_id: Optional[int] = Field(default=None, foreign_key="temples.id")
    temple_slug: str = Field(index=True)
    reference_id: Optional[str] = None
    title: str = Field(index=True)
    title_ta: Optional[str] = None
    are_number: Optional[str] = None
    sii_reference: Optional[str] = None
    epigraphia_indica: Optional[str] = None
    dynasty_id: Optional[int] = Field(default=None, foreign_key="dynasties.id")
    dynasty_slug: Optional[str] = Field(default=None, index=True)
    ruler_id: Optional[int] = Field(default=None, foreign_key="rulers.id")
    ruler_slug: Optional[str] = Field(default=None, index=True)
    regnal_year: Optional[str] = None
    approximate_date: Optional[str] = None
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
    source_id: Optional[int] = Field(default=None, foreign_key="sources.id")
    source_citation: str
    source_url: Optional[str] = None
    verification_status: str = Field(default="VERIFIED") # VERIFIED, DRAFT, UNDER_REVIEW, REJECTED
    verified: bool = Field(default=True)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

class InscriptionLocation(SQLModel, table=True):
    __tablename__ = "inscription_locations"
    id: Optional[int] = Field(default=None, primary_key=True)
    inscription_slug: str
    temple_slug: str = Field(index=True)
    label: str
    description: Optional[str] = None
    area: Optional[str] = None
    map_x: Optional[float] = None
    map_y: Optional[float] = None
    coordinate_system: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

class Image(SQLModel, table=True):
    __tablename__ = "images"
    id: Optional[int] = Field(default=None, primary_key=True)
    entity_type: str = Field(index=True) # TEMPLE or INSCRIPTION
    entity_slug: str = Field(index=True)
    category: Optional[str] = None
    commons_file: Optional[str] = None
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
    source_id: Optional[int] = Field(default=None, foreign_key="sources.id")
    verification_status: str = Field(default="VERIFIED")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

class HistoricalEvent(SQLModel, table=True):
    __tablename__ = "historical_events"
    id: Optional[int] = Field(default=None, primary_key=True)
    year: str
    title: str
    description: Optional[str] = None
    entity_type: str # TEMPLE or RULER
    entity_slug: str
    source_id: Optional[int] = Field(default=None, foreign_key="sources.id")
    source_note: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs"
    id: Optional[int] = Field(default=None, primary_key=True)
    actor: str
    action: str
    record_type: str
    record_id: str
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
