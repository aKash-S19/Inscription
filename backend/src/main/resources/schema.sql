-- ============================================================================
--  Kalvettu — Tamil Temple Inscription Archive
--  PostgreSQL DDL (also compatible with H2 running in MODE=PostgreSQL).
--  Nothing here is fabricated; the data is loaded by DataLoader from a
--  verified JSON dataset (src/main/resources/data/dataset.json).
-- ============================================================================

CREATE TABLE IF NOT EXISTS dynasties (
    id           BIGSERIAL PRIMARY KEY,
    slug         VARCHAR(120) NOT NULL UNIQUE,
    name_en      VARCHAR(200) NOT NULL,
    name_ta      VARCHAR(200),
    start_year   INTEGER,
    end_year     INTEGER,
    capital      VARCHAR(200),
    description  TEXT,
    source_note  TEXT
);

CREATE TABLE IF NOT EXISTS rulers (
    id           BIGSERIAL PRIMARY KEY,
    slug         VARCHAR(120) NOT NULL UNIQUE,
    name_en      VARCHAR(200) NOT NULL,
    name_ta      VARCHAR(200),
    dynasty_slug VARCHAR(120),
    reign_start  INTEGER,
    reign_end    INTEGER,
    capital      VARCHAR(200),
    note         TEXT,
    source_note  TEXT
);

CREATE TABLE IF NOT EXISTS districts (
    id            BIGSERIAL PRIMARY KEY,
    slug          VARCHAR(120) NOT NULL UNIQUE,
    name_en       VARCHAR(200) NOT NULL,
    headquarters  VARCHAR(200),
    lat           DOUBLE PRECISION,
    lng           DOUBLE PRECISION,
    note          TEXT
);

CREATE TABLE IF NOT EXISTS temples (
    id                  BIGSERIAL PRIMARY KEY,
    slug                VARCHAR(120) NOT NULL UNIQUE,
    name_en             VARCHAR(255) NOT NULL,
    name_ta             VARCHAR(255),
    alternate_names     TEXT,
    district_slug       VARCHAR(120),
    town                VARCHAR(200),
    deity               VARCHAR(200),
    dynasty_slug        VARCHAR(120),
    patron              VARCHAR(200),
    period_note         TEXT,
    consecration_year   INTEGER,
    lat                 DOUBLE PRECISION,
    lng                 DOUBLE PRECISION,
    unesco_world_heritage BOOLEAN NOT NULL DEFAULT FALSE,
    unesco_url          TEXT,
    asi_monument        BOOLEAN NOT NULL DEFAULT FALSE,
    asi_url             TEXT,
    managed_by          VARCHAR(255),
    history             TEXT,
    architecture        TEXT,
    summary             TEXT,
    verified            BOOLEAN NOT NULL DEFAULT TRUE,
    source_note         TEXT
);

CREATE TABLE IF NOT EXISTS inscriptions (
    id                   BIGSERIAL PRIMARY KEY,
    slug                 VARCHAR(120) NOT NULL UNIQUE,
    temple_slug          VARCHAR(120) NOT NULL,
    title                VARCHAR(255) NOT NULL,
    title_ta             VARCHAR(255),
    reference_id         VARCHAR(120),
    are_number           VARCHAR(120),
    sii_reference        VARCHAR(200),
    epigraphia_indica    VARCHAR(200),
    ruler_slug           VARCHAR(120),
    dynasty_slug         VARCHAR(120),
    regnal_year          VARCHAR(120),
    date_note            TEXT,
    language             VARCHAR(120),
    script               VARCHAR(120),
    physical_location    TEXT,
    original_text        TEXT,
    original_text_source TEXT,
    transliteration      TEXT,
    translation          TEXT,
    translation_source   TEXT,
    simple_explanation   TEXT,
    historical_significance TEXT,
    source_citation      TEXT NOT NULL,
    source_url           TEXT,
    verified             BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS inscription_locations (
    id                BIGSERIAL PRIMARY KEY,
    inscription_slug  VARCHAR(120) NOT NULL,
    temple_slug       VARCHAR(120) NOT NULL,
    label             VARCHAR(255) NOT NULL,
    description        TEXT,
    area              TEXT,
    map_x             DOUBLE PRECISION,
    map_y             DOUBLE PRECISION,
    coordinate_system VARCHAR(120),
    lat               DOUBLE PRECISION,
    lng               DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS images (
    id            BIGSERIAL PRIMARY KEY,
    entity_type   VARCHAR(20) NOT NULL,
    entity_slug   VARCHAR(120) NOT NULL,
    category      VARCHAR(40),
    commons_file  TEXT,
    image_url     TEXT NOT NULL,
    thumb_url     TEXT,
    width         INTEGER,
    height        INTEGER,
    author        TEXT,
    license       TEXT,
    license_url   TEXT,
    commons_url   TEXT,
    caption       TEXT
);

CREATE INDEX IF NOT EXISTS idx_temples_district ON temples (district_slug);
CREATE INDEX IF NOT EXISTS idx_temples_dynasty  ON temples (dynasty_slug);
CREATE INDEX IF NOT EXISTS idx_inscriptions_temple ON inscriptions (temple_slug);
CREATE INDEX IF NOT EXISTS idx_inscriptions_dynasty ON inscriptions (dynasty_slug);
CREATE INDEX IF NOT EXISTS idx_inscriptions_ruler  ON inscriptions (ruler_slug);
CREATE INDEX IF NOT EXISTS idx_images_entity ON images (entity_type, entity_slug);
CREATE INDEX IF NOT EXISTS idx_locations_temple ON inscription_locations (temple_slug);
