import os
import urllib.request
import certifi
import ssl
from database import engine
from sqlmodel import Session
from sqlalchemy import text

temples_data = [
    ("gangaikonda-cholapuram", "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Gangaikondacholapuram_temple_view.jpg/1280px-Gangaikondacholapuram_temple_view.jpg"),
    ("shore-temple-mamallapuram", "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Shore_Temple%2C_Mahabalipuram%2C_Tamil_Nadu%2C_India.jpg/1280px-Shore_Temple%2C_Mahabalipuram%2C_Tamil_Nadu%2C_India.jpg"),
    ("srirangam-ranganathaswamy", "https://upload.wikimedia.org/wikipedia/commons/thumb/2/29/Srirangam_Temple_Tower_View.jpg/1280px-Srirangam_Temple_Tower_View.jpg")
]

public_dir = r"../frontend/public/temples"
os.makedirs(public_dir, exist_ok=True)
ssl_context = ssl.create_default_context(cafile=certifi.where())

def download_image(slug, url):
    out_path = os.path.join(public_dir, f"{slug}.jpg")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, context=ssl_context) as response, open(out_path, 'wb') as out_file:
            out_file.write(response.read())
        print(f"Downloaded {slug}")
    except Exception as e:
        print(f"Failed download for {slug}: {e}")

with Session(engine) as db:
    for slug, url in temples_data:
        download_image(slug, url)
        img_url = f"/temples/{slug}.jpg"
        
        # We can just delete all images for this slug and re-insert the local one to be safe, 
        # or just update the first one and delete the rest.
        db.execute(text("DELETE FROM images WHERE entity_type = 'TEMPLE' AND entity_slug = :slug"), {"slug": slug})
        db.execute(
            text("INSERT INTO images (entity_type, entity_slug, image_url, commons_url, category) VALUES ('TEMPLE', :slug, :url, :source, 'hero')"),
            {"slug": slug, "url": img_url, "source": url}
        )
    db.commit()
print("Done fixing 3 broken temples")
