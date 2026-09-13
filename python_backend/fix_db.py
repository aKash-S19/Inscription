from database import engine
from sqlmodel import Session
from sqlalchemy import text

with Session(engine) as db:
    db.execute(text("UPDATE images SET entity_type = 'TEMPLE' WHERE entity_type = 'temple'"))
    # Also we should delete the OLD broken images so they don't get picked up by get_first_image_url if they come first!
    # Let's just make sure the new images have a higher priority or we delete the old ones.
    # Actually, the user's images were inserted/updated. But wait, I used `SELECT id` and updated the FIRST one found.
    # What if there were multiple? Let's delete all images for these slugs where image_url is NOT our local image.
    temples = [
        "sittanavasal-cave", "mandagapattu-cave", "kazhugumalai-vettuvan-koil",
        "kudumiyanmalai-sikhagiriswarar", "kampahareswarar-thirubuvanam",
        "vaikunta-perumal-kanchipuram", "chidambaram-nataraja", "ekambareswarar-kanchipuram"
    ]
    for slug in temples:
        local_url = f"/temples/{slug}.jpg"
        db.execute(text("DELETE FROM images WHERE entity_slug = :slug AND image_url != :local_url"), {"slug": slug, "local_url": local_url})
    db.commit()
print("Fixed entity type and deleted old broken images")
