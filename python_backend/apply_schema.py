import os
import sys
from dotenv import load_dotenv
import psycopg
from supabase import create_client, Client

load_dotenv()

db_url = os.getenv("SUPABASE_DB_URL")
supabase_url = os.getenv("SUPABASE_URL")
service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

print("1. Configuring Supabase Storage Buckets...")
supabase: Client = create_client(supabase_url, service_role_key)

try:
    existing_buckets = [b.name for b in supabase.storage.list_buckets()]
    print("Existing buckets:", existing_buckets)
    
    if "temples" not in existing_buckets:
        supabase.storage.create_bucket("temples", options={"public": True})
        print("Created public bucket 'temples'")
    else:
        print("Bucket 'temples' already exists")
        
    if "inscriptions" not in existing_buckets:
        supabase.storage.create_bucket("inscriptions", options={"public": True})
        print("Created public bucket 'inscriptions'")
    else:
        print("Bucket 'inscriptions' already exists")
except Exception as e:
    print("Notice regarding storage bucket creation:", e)

print("\n2. Executing PostgreSQL Schema & Extensions...")

SQL_SCHEMA = """
-- Extensions
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- 1. Sources table (provenance & authority tracking)
CREATE TABLE IF NOT EXISTS sources (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(100) UNIQUE,
    institution VARCHAR(255) NOT NULL,
    publication VARCHAR(255),
    volume VARCHAR(100),
    year VARCHAR(50),
    page VARCHAR(100),
    reference VARCHAR(255) NOT NULL,
    url TEXT,
    source_type VARCHAR(100) DEFAULT 'PRIMARY_EPIGRAPHIC',
    source_priority INT DEFAULT 1, -- 1: ASI/Epigraphy, 2: TN Arch, 3: Scholarly, 4: Wikidata, 5: Secondary
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 2. Dynasties table
CREATE TABLE IF NOT EXISTS dynasties (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(100) UNIQUE NOT NULL,
    name_en VARCHAR(255) NOT NULL,
    name_ta VARCHAR(255),
    start_year INT,
    end_year INT,
    capital VARCHAR(255),
    description TEXT,
    source_id INT REFERENCES sources(id) ON DELETE SET NULL,
    source_note TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 3. Rulers table
CREATE TABLE IF NOT EXISTS rulers (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(100) UNIQUE NOT NULL,
    name_en VARCHAR(255) NOT NULL,
    name_ta VARCHAR(255),
    dynasty_id INT REFERENCES dynasties(id) ON DELETE SET NULL,
    dynasty_slug VARCHAR(100),
    reign_start INT,
    reign_end INT,
    capital VARCHAR(255),
    note TEXT,
    source_id INT REFERENCES sources(id) ON DELETE SET NULL,
    source_note TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 4. Districts table
CREATE TABLE IF NOT EXISTS districts (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(100) UNIQUE NOT NULL,
    name_en VARCHAR(255) NOT NULL,
    headquarters VARCHAR(255),
    lat DOUBLE PRECISION,
    lng DOUBLE PRECISION,
    note TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 5. Temples table
CREATE TABLE IF NOT EXISTS temples (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(100) UNIQUE NOT NULL,
    name_en VARCHAR(255) NOT NULL,
    name_ta VARCHAR(255),
    alternate_names TEXT,
    district_id INT REFERENCES districts(id) ON DELETE SET NULL,
    district_slug VARCHAR(100),
    state VARCHAR(100) DEFAULT 'Tamil Nadu',
    town VARCHAR(255),
    lat DOUBLE PRECISION,
    lng DOUBLE PRECISION,
    period_note TEXT,
    consecration_year INT,
    dynasty_id INT REFERENCES dynasties(id) ON DELETE SET NULL,
    dynasty_slug VARCHAR(100),
    ruler_id INT REFERENCES rulers(id) ON DELETE SET NULL,
    patron VARCHAR(255),
    deity VARCHAR(255),
    history TEXT,
    architecture TEXT,
    summary TEXT,
    unesco_world_heritage BOOLEAN DEFAULT FALSE,
    unesco_url TEXT,
    asi_monument BOOLEAN DEFAULT FALSE,
    asi_url TEXT,
    managed_by VARCHAR(255),
    source_id INT REFERENCES sources(id) ON DELETE SET NULL,
    source_priority INT DEFAULT 1,
    verification_status VARCHAR(50) DEFAULT 'VERIFIED', -- VERIFIED, DRAFT, UNDER_REVIEW, REJECTED
    verified BOOLEAN DEFAULT TRUE,
    source_note TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 6. Inscriptions table
CREATE TABLE IF NOT EXISTS inscriptions (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(100) UNIQUE NOT NULL,
    temple_id INT REFERENCES temples(id) ON DELETE CASCADE,
    temple_slug VARCHAR(100) NOT NULL,
    reference_id VARCHAR(255),
    title VARCHAR(500) NOT NULL,
    title_ta VARCHAR(500),
    are_number VARCHAR(100),
    sii_reference VARCHAR(255),
    epigraphia_indica VARCHAR(255),
    dynasty_id INT REFERENCES dynasties(id) ON DELETE SET NULL,
    dynasty_slug VARCHAR(100),
    ruler_id INT REFERENCES rulers(id) ON DELETE SET NULL,
    ruler_slug VARCHAR(100),
    regnal_year VARCHAR(255),
    approximate_date VARCHAR(255),
    date_note VARCHAR(255),
    language VARCHAR(100),
    script VARCHAR(100),
    physical_location TEXT,
    original_text TEXT,
    original_text_source TEXT,
    transliteration TEXT,
    translation TEXT,
    translation_source TEXT,
    simple_explanation TEXT,
    historical_significance TEXT,
    source_id INT REFERENCES sources(id) ON DELETE SET NULL,
    source_citation TEXT NOT NULL,
    source_url TEXT,
    verification_status VARCHAR(50) DEFAULT 'VERIFIED',
    verified BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 7. Inscription locations table (schematic / coordinates)
CREATE TABLE IF NOT EXISTS inscription_locations (
    id SERIAL PRIMARY KEY,
    inscription_slug VARCHAR(100) NOT NULL,
    temple_slug VARCHAR(100) NOT NULL,
    label VARCHAR(255) NOT NULL,
    description TEXT,
    area VARCHAR(255),
    map_x DOUBLE PRECISION,
    map_y DOUBLE PRECISION,
    coordinate_system VARCHAR(255),
    lat DOUBLE PRECISION,
    lng DOUBLE PRECISION,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 8. Images table (unified with attribution metadata)
CREATE TABLE IF NOT EXISTS images (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL, -- TEMPLE or INSCRIPTION
    entity_slug VARCHAR(100) NOT NULL,
    category VARCHAR(100),
    commons_file VARCHAR(500),
    image_url TEXT NOT NULL,
    thumb_url TEXT,
    width INT,
    height INT,
    author VARCHAR(255),
    license VARCHAR(100),
    license_url TEXT,
    commons_url TEXT,
    caption TEXT,
    storage_path TEXT,
    source_id INT REFERENCES sources(id) ON DELETE SET NULL,
    verification_status VARCHAR(50) DEFAULT 'VERIFIED',
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 9. Historical events table (for chronological timeline)
CREATE TABLE IF NOT EXISTS historical_events (
    id SERIAL PRIMARY KEY,
    year VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    entity_type VARCHAR(50) NOT NULL,
    entity_slug VARCHAR(100) NOT NULL,
    source_id INT REFERENCES sources(id) ON DELETE SET NULL,
    source_note TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 10. Audit logs table (for data provenance & moderation tracking)
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    actor VARCHAR(100) NOT NULL,
    action VARCHAR(100) NOT NULL,
    record_type VARCHAR(100) NOT NULL,
    record_id VARCHAR(100) NOT NULL,
    old_state JSONB,
    new_state JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- INDEXES for search & performance
CREATE INDEX IF NOT EXISTS idx_temples_slug ON temples(slug);
CREATE INDEX IF NOT EXISTS idx_temples_district ON temples(district_slug);
CREATE INDEX IF NOT EXISTS idx_temples_dynasty ON temples(dynasty_slug);
CREATE INDEX IF NOT EXISTS idx_temples_verified ON temples(verification_status);

CREATE INDEX IF NOT EXISTS idx_inscriptions_slug ON inscriptions(slug);
CREATE INDEX IF NOT EXISTS idx_inscriptions_temple ON inscriptions(temple_slug);
CREATE INDEX IF NOT EXISTS idx_inscriptions_ruler ON inscriptions(ruler_slug);
CREATE INDEX IF NOT EXISTS idx_inscriptions_dynasty ON inscriptions(dynasty_slug);
CREATE INDEX IF NOT EXISTS idx_inscriptions_title ON inscriptions(title);
CREATE INDEX IF NOT EXISTS idx_inscriptions_verified ON inscriptions(verification_status);

CREATE INDEX IF NOT EXISTS idx_images_entity ON images(entity_type, entity_slug);
CREATE INDEX IF NOT EXISTS idx_locations_temple ON inscription_locations(temple_slug);

-- Trigram indexes for typo-tolerant & Tamil search
CREATE INDEX IF NOT EXISTS idx_temples_name_en_trgm ON temples USING gin (name_en gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_temples_alt_trgm ON temples USING gin (alternate_names gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_inscriptions_title_trgm ON inscriptions USING gin (title gin_trgm_ops);

-- Full-text search index on inscriptions
CREATE INDEX IF NOT EXISTS idx_inscriptions_fts ON inscriptions USING gin(
    to_tsvector('english', coalesce(title, '') || ' ' || coalesce(translation, '') || ' ' || coalesce(simple_explanation, ''))
);

-- ROW LEVEL SECURITY (RLS) POLICIES
ALTER TABLE temples ENABLE ROW LEVEL SECURITY;
ALTER TABLE inscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE images ENABLE ROW LEVEL SECURITY;
ALTER TABLE sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE dynasties ENABLE ROW LEVEL SECURITY;
ALTER TABLE rulers ENABLE ROW LEVEL SECURITY;
ALTER TABLE districts ENABLE ROW LEVEL SECURITY;
ALTER TABLE inscription_locations ENABLE ROW LEVEL SECURITY;
ALTER TABLE historical_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Public can read only VERIFIED records:
DO $$
BEGIN
    DROP POLICY IF EXISTS "Public can view verified temples" ON temples;
    CREATE POLICY "Public can view verified temples" ON temples
        FOR SELECT USING (verification_status = 'VERIFIED');

    DROP POLICY IF EXISTS "Public can view verified inscriptions" ON inscriptions;
    CREATE POLICY "Public can view verified inscriptions" ON inscriptions
        FOR SELECT USING (verification_status = 'VERIFIED');

    DROP POLICY IF EXISTS "Public can view verified images" ON images;
    CREATE POLICY "Public can view verified images" ON images
        FOR SELECT USING (verification_status = 'VERIFIED');

    DROP POLICY IF EXISTS "Public can view public reference tables" ON dynasties;
    CREATE POLICY "Public can view public reference tables" ON dynasties FOR SELECT USING (true);

    DROP POLICY IF EXISTS "Public can view rulers" ON rulers;
    CREATE POLICY "Public can view rulers" ON rulers FOR SELECT USING (true);

    DROP POLICY IF EXISTS "Public can view districts" ON districts;
    CREATE POLICY "Public can view districts" ON districts FOR SELECT USING (true);

    DROP POLICY IF EXISTS "Public can view sources" ON sources;
    CREATE POLICY "Public can view sources" ON sources FOR SELECT USING (true);

    DROP POLICY IF EXISTS "Public can view locations" ON inscription_locations;
    CREATE POLICY "Public can view locations" ON inscription_locations FOR SELECT USING (true);

    DROP POLICY IF EXISTS "Public can view timeline" ON historical_events;
    CREATE POLICY "Public can view timeline" ON historical_events FOR SELECT USING (true);

    -- Service role / postgres user has full bypass privileges (as defined by PostgreSQL superuser & service_role)
END $$;
"""

with psycopg.connect(db_url) as conn:
    with conn.cursor() as cur:
        cur.execute(SQL_SCHEMA)
    conn.commit()

print("Schema, indexes, and RLS policies created successfully on Supabase PostgreSQL!")
