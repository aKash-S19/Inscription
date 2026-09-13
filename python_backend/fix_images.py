from database import engine
from sqlmodel import Session
from sqlalchemy import text

temples = [
    "sittanavasal-cave",
    "mandagapattu-cave",
    "kazhugumalai-vettuvan-koil",
    "kudumiyanmalai-sikhagiriswarar",
    "kampahareswarar-thirubuvanam",
    "vaikunta-perumal-kanchipuram",
    "chidambaram-nataraja",
    "ekambareswarar-kanchipuram"
]

with Session(engine) as db:
    for slug in temples:
        img_url = f"/temples/{slug}.jpg"
        # check if exists
        res = db.execute(text("SELECT id FROM images WHERE entity_type = 'temple' AND entity_slug = :slug"), {"slug": slug}).fetchone()
        if res:
            db.execute(text("UPDATE images SET image_url = :url WHERE id = :id"), {"url": img_url, "id": res[0]})
        else:
            db.execute(text("INSERT INTO images (entity_type, entity_slug, image_url, category) VALUES ('temple', :slug, :url, 'hero')"), {"slug": slug, "url": img_url})
    db.commit()
print("Done inserting images via sqlmodel")
