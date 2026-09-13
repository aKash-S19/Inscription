import os
import urllib.request
import certifi
import ssl
from bs4 import BeautifulSoup
from database import engine
from sqlmodel import Session
from sqlalchemy import text

temples_data = [
    ("sittanavasal-cave", "https://reluctantbookworm.com/2025/07/22/climbing-the-steps-of-time-sithannavasals-jain-heritage/"),
    ("mandagapattu-cave", "https://thumb.wikimedia.org/wikipedia/commons/thumb/2/28/N-TN-C235_Mandagapattu_Villupuram.jpg/960px-N-TN-C235_Mandagapattu_Villupuram.jpg"),
    ("kazhugumalai-vettuvan-koil", "https://thumb.wikimedia.org/wikipedia/commons/thumb/5/5d/Vettuvan_Kovil_%283%29.jpg/960px-Vettuvan_Kovil_%283%29.jpg"),
    ("kudumiyanmalai-sikhagiriswarar", "https://thumb.wikimedia.org/wikipedia/commons/thumb/d/d7/N-TN-C127_Rock_cut_shrine_Melakkoil_mandaba_Kudumiyanmalai.jpg/960px-N-TN-C127_Rock_cut_shrine_Melakkoil_mandaba_Kudumiyanmalai.jpg"),
    ("kampahareswarar-thirubuvanam", "https://thumb.wikimedia.org/wikipedia/commons/thumb/9/97/Thirubuvanam_%2812%29.jpg/960px-Thirubuvanam_%2812%29.jpg"),
    ("vaikunta-perumal-kanchipuram", "https://www.trawell.in/admin/images/upload/705432257Vaikunta_Perumal_Temple_Main.jpg"),
    ("chidambaram-nataraja", "https://www.templefolks.com/templefolks_admin/public/uploads/products/Thillai-Nataraja-4421.jpg"),
    ("ekambareswarar-kanchipuram", "https://upload.wikimedia.org/wikipedia/commons/d/dc/Ekambareswarar_Temple%2C_Kanchipuram%2C_Tamil_Nadu.jpg")
]

public_dir = r"../frontend/public/temples"
os.makedirs(public_dir, exist_ok=True)

ssl_context = ssl.create_default_context(cafile=certifi.where())

def download_image(slug, url):
    out_path = os.path.join(public_dir, f"{slug}.jpg")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    if url.endswith('/') or 'reluctantbookworm.com' in url:
        # Scrape for image
        try:
            html = urllib.request.urlopen(req, context=ssl_context).read()
            soup = BeautifulSoup(html, 'html.parser')
            # Look for og:image
            og_img = soup.find('meta', property='og:image')
            if og_img and og_img.get('content'):
                img_url = og_img['content']
                print(f"Found image for {slug}: {img_url}")
                img_req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(img_req, context=ssl_context) as response, open(out_path, 'wb') as out_file:
                    out_file.write(response.read())
                return
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            pass
            
    # Direct download
    try:
        with urllib.request.urlopen(req, context=ssl_context) as response, open(out_path, 'wb') as out_file:
            out_file.write(response.read())
        print(f"Downloaded {slug}")
    except Exception as e:
        print(f"Failed direct download for {slug}: {e}")

with Session(engine) as db:
    for slug, source_url in temples_data:
        download_image(slug, source_url)
        img_url = f"/temples/{slug}.jpg"
        db.execute(
            text("UPDATE images SET image_url = :url, commons_url = :source WHERE entity_type = 'temple' AND entity_slug = :slug"),
            {"url": img_url, "source": source_url, "slug": slug}
        )
    db.commit()
print("Done updating real images")
