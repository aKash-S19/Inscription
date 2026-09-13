import os
import urllib.request
import certifi
import ssl
from bs4 import BeautifulSoup
from database import engine
from sqlmodel import Session
from sqlalchemy import text

slugs = ["gangaikonda-cholapuram", "shore-temple-mamallapuram", "srirangam-ranganathaswamy"]
public_dir = r"../frontend/public/temples"
os.makedirs(public_dir, exist_ok=True)
ssl_context = ssl.create_default_context(cafile=certifi.where())

with Session(engine) as db:
    for slug in slugs:
        res = db.execute(text("SELECT wikipedia_url FROM temples WHERE slug = :slug"), {"slug": slug}).fetchone()
        if res and res[0]:
            wiki_url = res[0]
            print(f"Fetching {wiki_url} for {slug}")
            try:
                req = urllib.request.Request(wiki_url, headers={'User-Agent': 'Mozilla/5.0'})
                html = urllib.request.urlopen(req, context=ssl_context).read()
                soup = BeautifulSoup(html, 'html.parser')
                og_img = soup.find('meta', property='og:image')
                if og_img and og_img.get('content'):
                    img_url = og_img['content']
                    print(f"Downloading {img_url}")
                    img_req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
                    out_path = os.path.join(public_dir, f"{slug}.jpg")
                    with urllib.request.urlopen(img_req, context=ssl_context) as response, open(out_path, 'wb') as out_file:
                        out_file.write(response.read())
                    # Update DB
                    local_url = f"/temples/{slug}.jpg"
                    db.execute(text("DELETE FROM images WHERE entity_slug = :slug AND entity_type = 'TEMPLE'"), {"slug": slug})
                    db.execute(
                        text("INSERT INTO images (entity_type, entity_slug, image_url, commons_url, category) VALUES ('TEMPLE', :slug, :url, :source, 'hero')"),
                        {"slug": slug, "url": local_url, "source": wiki_url}
                    )
                    db.commit()
            except Exception as e:
                print(f"Error on {slug}: {e}")
print("Done fixing 3 Wikipedia images")
