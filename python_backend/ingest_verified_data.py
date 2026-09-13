import os
import json
import psycopg
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("SUPABASE_DB_URL")
DATASET_PATH = os.path.join(os.path.dirname(__file__), "data", "dataset.json")
IMAGES_PATH = os.path.join(os.path.dirname(__file__), "data", "commons_images.json")

def run_ingestion():
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            print("1. Ingesting canonical Epigraphic & Archaeological Sources...")
            sources_data = [
                {
                    "slug": "asi",
                    "institution": "Archaeological Survey of India",
                    "publication": "ASI National Monument Registry & Reports",
                    "volume": "All",
                    "year": "1900-present",
                    "page": "N/A",
                    "reference": "ASI Monument Protection Registry",
                    "url": "https://asi.nic.in/",
                    "source_type": "OFFICIAL_ARCHAEOLOGY",
                    "source_priority": 1,
                    "notes": "Primary federal authority for monument conservation and monument protection in India."
                },
                {
                    "slug": "sii-vol-1",
                    "institution": "Archaeological Survey of India",
                    "publication": "South Indian Inscriptions",
                    "volume": "Vol. I",
                    "year": "1890",
                    "page": "Various",
                    "reference": "SII Vol. I - Pallava Inscriptions of Kanchipuram and Mamallapuram, ed. E. Hultzsch",
                    "url": "https://archive.org/details/south-indian-inscriptions",
                    "source_type": "PRIMARY_EPIGRAPHIC",
                    "source_priority": 1,
                    "notes": "Foundational primary edition of Pallava inscriptions in Sanskrit (Grantha) and early Tamil."
                },
                {
                    "slug": "sii-vol-2",
                    "institution": "Archaeological Survey of India",
                    "publication": "South Indian Inscriptions",
                    "volume": "Vol. II",
                    "year": "1913",
                    "page": "416-449",
                    "reference": "SII Vol. II - Tamil Inscriptions of Rajaraja, Rajendra-Chola in the Rajarajesvara Temple at Tanjavur, ed. V. Venkayya",
                    "url": "https://archive.org/details/india.history.resource.93099",
                    "source_type": "PRIMARY_EPIGRAPHIC",
                    "source_priority": 1,
                    "notes": "Authoritative edition of the Brihadisvara (Rajarajesvaram) inscriptions recording gifts, war spoils, and administration."
                },
                {
                    "slug": "sii-vol-12",
                    "institution": "Archaeological Survey of India",
                    "publication": "South Indian Inscriptions",
                    "volume": "Vol. XII",
                    "year": "1943",
                    "page": "Various",
                    "reference": "SII Vol. XII - Inscriptions of the Chidambaram Nataraja Temple",
                    "url": "https://archive.org/details/south-indian-inscriptions",
                    "source_type": "PRIMARY_EPIGRAPHIC",
                    "source_priority": 1,
                    "notes": "Records of temple committees, flower-gardens, and administration at Chidambaram."
                },
                {
                    "slug": "are-1908",
                    "institution": "Archaeological Survey of India",
                    "publication": "Annual Report on (South) Indian Epigraphy",
                    "volume": "1908",
                    "year": "1908",
                    "page": "Nos. 16-27",
                    "reference": "A.R.E. 1908, Nos. 16–27 (Airavatesvara Temple, Darasuram)",
                    "url": "https://epigraphia.blogspot.com/",
                    "source_type": "PRIMARY_EPIGRAPHIC",
                    "source_priority": 1,
                    "notes": "First systematic epigraphic listing of Darasuram inscriptions."
                },
                {
                    "slug": "are-1913",
                    "institution": "Archaeological Survey of India",
                    "publication": "Annual Report on (South) Indian Epigraphy",
                    "volume": "1913",
                    "year": "1913",
                    "page": "Nos. 296, 304",
                    "reference": "A.R.E. 1913, Nos. 296 & 304 (Chidambaram)",
                    "url": "https://epigraphia.blogspot.com/",
                    "source_type": "PRIMARY_EPIGRAPHIC",
                    "source_priority": 1,
                    "notes": "Notices of Chidambaram 3rd prakara north wall records."
                },
                {
                    "slug": "unesco-250",
                    "institution": "UNESCO World Heritage Centre",
                    "publication": "World Heritage List",
                    "volume": "Ref. 250",
                    "year": "1987, 2004",
                    "page": "N/A",
                    "reference": "Great Living Chola Temples (Brihadisvara, Gangaikondacholapuram, Airavatesvara)",
                    "url": "https://whc.unesco.org/en/list/250",
                    "source_type": "OFFICIAL_ARCHAEOLOGY",
                    "source_priority": 1,
                    "notes": "UNESCO World Heritage documentation of architectural integrity and authenticity."
                },
                {
                    "slug": "unesco-249",
                    "institution": "UNESCO World Heritage Centre",
                    "publication": "World Heritage List",
                    "volume": "Ref. 249",
                    "year": "1984",
                    "page": "N/A",
                    "reference": "Group of Monuments at Mahabalipuram",
                    "url": "https://whc.unesco.org/en/list/249",
                    "source_type": "OFFICIAL_ARCHAEOLOGY",
                    "source_priority": 1,
                    "notes": "UNESCO inscription of the Pallava monuments including the Shore Temple."
                },
                {
                    "slug": "wikidata",
                    "institution": "Wikidata / Wikimedia Foundation",
                    "publication": "Wikidata Open Knowledge Base",
                    "volume": "Structured Data",
                    "year": "2024",
                    "page": "N/A",
                    "reference": "Wikidata QID entity entries",
                    "url": "https://www.wikidata.org/",
                    "source_type": "OPEN_KNOWLEDGE",
                    "source_priority": 4,
                    "notes": "Structured metadata for coordinates, alternate names, and cross-references."
                },
                {
                    "slug": "wikimedia-commons",
                    "institution": "Wikimedia Commons",
                    "publication": "Wikimedia Commons Repository",
                    "volume": "Media",
                    "year": "Various",
                    "page": "N/A",
                    "reference": "Freely-licensed historical and architectural photographs",
                    "url": "https://commons.wikimedia.org/",
                    "source_type": "OPEN_KNOWLEDGE",
                    "source_priority": 4,
                    "notes": "Curated photographs with full attribution (author, license, URL)."
                }
            ]

            source_map = {}
            for s in sources_data:
                cur.execute("""
                    INSERT INTO sources (slug, institution, publication, volume, year, page, reference, url, source_type, source_priority, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (slug) DO UPDATE SET
                        institution = EXCLUDED.institution,
                        publication = EXCLUDED.publication,
                        reference = EXCLUDED.reference,
                        url = EXCLUDED.url,
                        source_priority = EXCLUDED.source_priority
                    RETURNING id, slug;
                """, (s["slug"], s["institution"], s["publication"], s["volume"], s["year"], s["page"], s["reference"], s["url"], s["source_type"], s["source_priority"], s["notes"]))
                row = cur.fetchone()
                source_map[s["slug"]] = row[0]

            print(f"Sources synchronized: {len(source_map)} sources.")

            with open(DATASET_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)

            print("2. Ingesting Dynasties...")
            dynasty_map = {}
            for d in data.get("dynasties", []):
                cur.execute("""
                    INSERT INTO dynasties (slug, name_en, name_ta, start_year, end_year, capital, description, source_note)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (slug) DO UPDATE SET
                        name_en = EXCLUDED.name_en,
                        name_ta = EXCLUDED.name_ta,
                        start_year = EXCLUDED.start_year,
                        end_year = EXCLUDED.end_year,
                        capital = EXCLUDED.capital,
                        description = EXCLUDED.description
                    RETURNING id, slug;
                """, (d.get("slug"), d.get("nameEn"), d.get("nameTa"), d.get("startYear"), d.get("endYear"), d.get("capital"), d.get("description"), d.get("sourceNote")))
                row = cur.fetchone()
                dynasty_map[d["slug"]] = row[0]

            print("3. Ingesting Rulers...")
            ruler_map = {}
            for r in data.get("rulers", []):
                dyn_id = dynasty_map.get(r.get("dynastySlug"))
                cur.execute("""
                    INSERT INTO rulers (slug, name_en, name_ta, dynasty_id, dynasty_slug, reign_start, reign_end, capital, note, source_note)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (slug) DO UPDATE SET
                        name_en = EXCLUDED.name_en,
                        name_ta = EXCLUDED.name_ta,
                        dynasty_id = EXCLUDED.dynasty_id,
                        dynasty_slug = EXCLUDED.dynasty_slug,
                        reign_start = EXCLUDED.reign_start,
                        reign_end = EXCLUDED.reign_end,
                        note = EXCLUDED.note
                    RETURNING id, slug;
                """, (r.get("slug"), r.get("nameEn"), r.get("nameTa"), dyn_id, r.get("dynastySlug"), r.get("reignStart"), r.get("reignEnd"), r.get("capital"), r.get("note"), r.get("sourceNote")))
                row = cur.fetchone()
                ruler_map[r["slug"]] = row[0]

            print("4. Ingesting Districts...")
            district_map = {}
            for dist in data.get("districts", []):
                cur.execute("""
                    INSERT INTO districts (slug, name_en, headquarters, lat, lng, note)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (slug) DO UPDATE SET
                        name_en = EXCLUDED.name_en,
                        headquarters = EXCLUDED.headquarters,
                        lat = EXCLUDED.lat,
                        lng = EXCLUDED.lng
                    RETURNING id, slug;
                """, (dist.get("slug"), dist.get("nameEn"), dist.get("headquarters"), dist.get("lat"), dist.get("lng"), dist.get("note")))
                row = cur.fetchone()
                district_map[dist["slug"]] = row[0]

            print("5. Ingesting Temples...")
            temple_map = {}
            for t in data.get("temples", []):
                dyn_id = dynasty_map.get(t.get("dynastySlug"))
                dist_id = district_map.get(t.get("districtSlug"))
                
                # Determine primary source
                src_id = source_map.get("unesco-250") if t.get("unescoWorldHeritage") else source_map.get("asi")
                
                cur.execute("""
                    INSERT INTO temples (
                        slug, name_en, name_ta, alternate_names, district_id, district_slug,
                        town, lat, lng, period_note, consecration_year, dynasty_id, dynasty_slug,
                        patron, deity, history, architecture, summary, unesco_world_heritage,
                        unesco_url, asi_monument, asi_url, managed_by, source_id, verification_status,
                        verified, source_note
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, 'VERIFIED',
                        TRUE, %s
                    )
                    ON CONFLICT (slug) DO UPDATE SET
                        name_en = EXCLUDED.name_en,
                        name_ta = EXCLUDED.name_ta,
                        alternate_names = EXCLUDED.alternate_names,
                        district_id = EXCLUDED.district_id,
                        district_slug = EXCLUDED.district_slug,
                        town = EXCLUDED.town,
                        lat = EXCLUDED.lat,
                        lng = EXCLUDED.lng,
                        history = EXCLUDED.history,
                        architecture = EXCLUDED.architecture,
                        summary = EXCLUDED.summary,
                        unesco_world_heritage = EXCLUDED.unesco_world_heritage,
                        asi_monument = EXCLUDED.asi_monument,
                        source_id = EXCLUDED.source_id,
                        source_note = EXCLUDED.source_note
                    RETURNING id, slug;
                """, (
                    t.get("slug"), t.get("nameEn"), t.get("nameTa"), t.get("alternateNames"),
                    dist_id, t.get("districtSlug"), t.get("town"), t.get("lat"), t.get("lng"),
                    t.get("periodNote"), t.get("consecrationYear"), dyn_id, t.get("dynastySlug"),
                    t.get("patron"), t.get("deity"), t.get("history"), t.get("architecture"),
                    t.get("summary"), t.get("unescoWorldHeritage", False), t.get("unescoUrl"),
                    t.get("asiMonument", False), t.get("asiUrl"), t.get("managedBy"), src_id,
                    t.get("sourceNote")
                ))
                row = cur.fetchone()
                temple_map[t["slug"]] = row[0]

            print(f"Temples ingested: {len(temple_map)} temples.")

            print("6. Ingesting Inscriptions (with Title & Source Provenance)...")
            ins_count = 0
            for i in data.get("inscriptions", []):
                t_id = temple_map.get(i.get("templeSlug"))
                dyn_id = dynasty_map.get(i.get("dynastySlug"))
                ruler_id = ruler_map.get(i.get("rulerSlug"))

                # Match source ID based on citation
                ref = (i.get("referenceId") or "") + " " + (i.get("siiReference") or "")
                if "Vol. II" in ref:
                    src_id = source_map.get("sii-vol-2")
                elif "Vol. I" in ref:
                    src_id = source_map.get("sii-vol-1")
                elif "Vol. XII" in ref:
                    src_id = source_map.get("sii-vol-12")
                elif "1908" in ref or "ARE 17" in ref or "ARE 20" in ref or "ARE 24" in ref:
                    src_id = source_map.get("are-1908")
                else:
                    src_id = source_map.get("asi")

                cur.execute("""
                    INSERT INTO inscriptions (
                        slug, temple_id, temple_slug, reference_id, title, title_ta,
                        are_number, sii_reference, epigraphia_indica, dynasty_id, dynasty_slug,
                        ruler_id, ruler_slug, regnal_year, approximate_date, date_note, language,
                        script, physical_location, original_text, original_text_source,
                        transliteration, translation, translation_source, simple_explanation,
                        historical_significance, source_id, source_citation, source_url,
                        verification_status, verified
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        'VERIFIED', TRUE
                    )
                    ON CONFLICT (slug) DO UPDATE SET
                        temple_id = EXCLUDED.temple_id,
                        reference_id = EXCLUDED.reference_id,
                        title = EXCLUDED.title,
                        title_ta = EXCLUDED.title_ta,
                        are_number = EXCLUDED.are_number,
                        sii_reference = EXCLUDED.sii_reference,
                        ruler_id = EXCLUDED.ruler_id,
                        dynasty_id = EXCLUDED.dynasty_id,
                        translation = EXCLUDED.translation,
                        simple_explanation = EXCLUDED.simple_explanation,
                        historical_significance = EXCLUDED.historical_significance,
                        source_id = EXCLUDED.source_id,
                        source_citation = EXCLUDED.source_citation,
                        source_url = EXCLUDED.source_url
                    RETURNING id;
                """, (
                    i.get("slug"), t_id, i.get("templeSlug"), i.get("referenceId"), i.get("title"),
                    i.get("titleTa"), i.get("areNumber"), i.get("siiReference"), i.get("epigraphiaIndica"),
                    dyn_id, i.get("dynastySlug"), ruler_id, i.get("rulerSlug"), i.get("regnalYear"),
                    i.get("dateNote"), i.get("dateNote"), i.get("language"), i.get("script"),
                    i.get("physicalLocation"), i.get("originalText"), i.get("originalTextSource"),
                    i.get("transliteration"), i.get("translation"), i.get("translationSource"),
                    i.get("simpleExplanation"), i.get("historicalSignificance"), src_id,
                    i.get("sourceCitation"), i.get("sourceUrl")
                ))
                ins_count += 1

            print(f"Inscriptions ingested: {ins_count} records.")

            print("7. Ingesting Inscription Locations...")
            for l in data.get("inscriptionLocations", []):
                cur.execute("""
                    INSERT INTO inscription_locations (
                        inscription_slug, temple_slug, label, description, area,
                        map_x, map_y, coordinate_system, lat, lng
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """, (
                    l.get("inscriptionSlug"), l.get("templeSlug"), l.get("label"), l.get("description"),
                    l.get("area"), l.get("mapX"), l.get("mapY"), l.get("coordinateSystem"),
                    l.get("lat"), l.get("lng")
                ))

            print("8. Ingesting Wikimedia Commons Images...")
            img_count = 0
            if os.path.exists(IMAGES_PATH):
                with open(IMAGES_PATH, 'r', encoding='utf-8') as f:
                    images_data = json.load(f)

                wiki_src = source_map.get("wikimedia-commons")
                for temple_slug, imgs in images_data.items():
                    for idx, im in enumerate(imgs):
                        cur.execute("""
                            INSERT INTO images (
                                entity_type, entity_slug, category, commons_file,
                                image_url, thumb_url, width, height, author, license,
                                license_url, commons_url, caption, source_id, verification_status
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'VERIFIED');
                        """, (
                            "TEMPLE", temple_slug, "exterior" if idx == 0 else "detail",
                            im.get("title"), im.get("url"), im.get("thumb"),
                            im.get("width"), im.get("height"), im.get("author"),
                            im.get("license"), im.get("license_url"), im.get("commons_url"),
                            f"Photograph from Wikimedia Commons: {im.get('title')}", wiki_src
                        ))
                        img_count += 1

            print(f"Images ingested: {img_count} images.")

            print("9. Generating Timeline Events...")
            # Automatically populate historical_events from verified consecration years and ruler reign starts
            cur.execute("""
                INSERT INTO historical_events (year, title, description, entity_type, entity_slug, source_note)
                SELECT 
                    consecration_year::text,
                    name_en || ' - consecrated/built',
                    coalesce('Patron: ' || patron || '. ', '') || coalesce(period_note, ''),
                    'TEMPLE',
                    slug,
                    source_note
                FROM temples
                WHERE consecration_year IS NOT NULL;
            """)

            cur.execute("""
                INSERT INTO historical_events (year, title, description, entity_type, entity_slug, source_note)
                SELECT 
                    reign_start::text,
                    name_en || ' - reign begins',
                    coalesce('Dynasty: ' || dynasty_slug || '. ', '') || coalesce(note, ''),
                    'RULER',
                    slug,
                    source_note
                FROM rulers
                WHERE reign_start IS NOT NULL;
            """)

            conn.commit()
            print("Historical events generated.")

    print("\nVerified Data Ingestion completed successfully!")

if __name__ == "__main__":
    run_ingestion()
