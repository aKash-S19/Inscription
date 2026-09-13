import json
import os
from sqlmodel import Session, select
from database import engine, create_db_and_tables
from models import Dynasty, Ruler, District, Temple, Inscription, InscriptionLocation, Image

DATASET_PATH = os.path.join(os.path.dirname(__file__), "data", "dataset.json")
IMAGES_PATH = os.path.join(os.path.dirname(__file__), "data", "commons_images.json")

def as_int(val):
    return int(val) if val is not None else None

def as_float(val):
    return float(val) if val is not None else None

def seed_db():
    create_db_and_tables()
    with Session(engine) as session:
        # Check if already seeded
        if session.exec(select(Temple)).first() is not None:
            print("Dataset already present; skipping seed.")
            return

        with open(DATASET_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for d in data.get("dynasties", []):
            session.add(Dynasty(
                slug=d.get("slug"), name_en=d.get("nameEn"), name_ta=d.get("nameTa"),
                start_year=as_int(d.get("startYear")), end_year=as_int(d.get("endYear")),
                capital=d.get("capital"), description=d.get("description"), source_note=d.get("sourceNote")
            ))

        for r in data.get("rulers", []):
            session.add(Ruler(
                slug=r.get("slug"), name_en=r.get("nameEn"), name_ta=r.get("nameTa"),
                dynasty_slug=r.get("dynastySlug"), reign_start=as_int(r.get("reignStart")),
                reign_end=as_int(r.get("reignEnd")), capital=r.get("capital"),
                note=r.get("note"), source_note=r.get("sourceNote")
            ))

        for d in data.get("districts", []):
            session.add(District(
                slug=d.get("slug"), name_en=d.get("nameEn"), headquarters=d.get("headquarters"),
                lat=as_float(d.get("lat")), lng=as_float(d.get("lng")), note=d.get("note")
            ))

        for t in data.get("temples", []):
            session.add(Temple(
                slug=t.get("slug"), name_en=t.get("nameEn"), name_ta=t.get("nameTa"),
                alternate_names=t.get("alternateNames"), district_slug=t.get("districtSlug"),
                town=t.get("town"), deity=t.get("deity"), dynasty_slug=t.get("dynastySlug"),
                patron=t.get("patron"), period_note=t.get("periodNote"),
                consecration_year=as_int(t.get("consecrationYear")), lat=as_float(t.get("lat")),
                lng=as_float(t.get("lng")), unesco_world_heritage=t.get("unescoWorldHeritage", False),
                unesco_url=t.get("unescoUrl"), asi_monument=t.get("asiMonument", False),
                asi_url=t.get("asiUrl"), managed_by=t.get("managedBy"), history=t.get("history"),
                architecture=t.get("architecture"), summary=t.get("summary"),
                verified=t.get("verified", True), source_note=t.get("sourceNote")
            ))

        for i in data.get("inscriptions", []):
            session.add(Inscription(
                slug=i.get("slug"), temple_slug=i.get("templeSlug"), title=i.get("title"),
                title_ta=i.get("titleTa"), reference_id=i.get("referenceId"), are_number=i.get("areNumber"),
                sii_reference=i.get("siiReference"), epigraphia_indica=i.get("epigraphiaIndica"),
                ruler_slug=i.get("rulerSlug"), dynasty_slug=i.get("dynastySlug"),
                regnal_year=i.get("regnalYear"), date_note=i.get("dateNote"), language=i.get("language"),
                script=i.get("script"), physical_location=i.get("physicalLocation"),
                original_text=i.get("originalText"), original_text_source=i.get("originalTextSource"),
                transliteration=i.get("transliteration"), translation=i.get("translation"),
                translation_source=i.get("translationSource"), simple_explanation=i.get("simpleExplanation"),
                historical_significance=i.get("historicalSignificance"), source_citation=i.get("sourceCitation"),
                source_url=i.get("sourceUrl"), verified=i.get("verified", True)
            ))

        for l in data.get("inscriptionLocations", []):
            session.add(InscriptionLocation(
                inscription_slug=l.get("inscriptionSlug"), temple_slug=l.get("templeSlug"),
                label=l.get("label"), description=l.get("description"), area=l.get("area"),
                map_x=as_float(l.get("mapX")), map_y=as_float(l.get("mapY")),
                coordinate_system=l.get("coordinateSystem"), lat=as_float(l.get("lat")),
                lng=as_float(l.get("lng"))
            ))

        if os.path.exists(IMAGES_PATH):
            with open(IMAGES_PATH, 'r', encoding='utf-8') as f:
                images_data = json.load(f)
            
            for temple_slug, imgs in images_data.items():
                for idx, im in enumerate(imgs):
                    session.add(Image(
                        entity_type="TEMPLE", entity_slug=temple_slug,
                        category="exterior" if idx == 0 else "detail",
                        commons_file=im.get("title"), image_url=im.get("url"),
                        thumb_url=im.get("thumb"), width=as_int(im.get("width")),
                        height=as_int(im.get("height")), author=im.get("author"),
                        license=im.get("license"), license_url=im.get("license_url"),
                        commons_url=im.get("commons_url"), caption=f"Photograph from Wikimedia Commons: {im.get('title')}"
                    ))
        
        session.commit()
        print("Database seeded successfully.")

if __name__ == "__main__":
    seed_db()
