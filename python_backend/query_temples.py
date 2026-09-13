from database import engine
from sqlmodel import Session
from sqlalchemy import text

with Session(engine) as db:
    res = db.execute(text("SELECT entity_slug, image_url FROM images WHERE entity_type = 'TEMPLE' AND (entity_slug LIKE '%gangaikonda%' OR entity_slug LIKE '%shore%' OR entity_slug LIKE '%srirangam%')")).fetchall()
    for row in res:
        print(row)
