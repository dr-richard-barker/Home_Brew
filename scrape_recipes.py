import os
import re
import sys
import time
import argparse
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from flask import Flask

from config import Config
from models import db, init_db, Recipe, Malt, Hop, Yeast, OtherIngredient

app = Flask(__name__)
app.config.from_object(Config)
init_db(app)

BASE_URL = "https://www.brewersfriend.com"
LIST_URL = "https://www.brewersfriend.com/homebrew-recipes/all-grain/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

def parse_weight_lb(val_str):
    if not val_str:
        return 0.0
    val_str = val_str.lower().strip()
    match = re.search(r"([\d.]+)\s*(lb|oz|kg|g)?", val_str)
    if not match:
        return 0.0
    num = float(match.group(1))
    unit = match.group(2) or "lb"
    if unit == "lb":
        return num
    elif unit == "oz":
        return num / 16.0
    elif unit == "kg":
        return num * 2.20462
    elif unit == "g":
        return num / 453.592
    return num

def parse_weight_oz(val_str):
    if not val_str:
        return 0.0
    val_str = val_str.lower().strip()
    match = re.search(r"([\d.]+)\s*(oz|lb|g|kg)?", val_str)
    if not match:
        return 0.0
    num = float(match.group(1))
    unit = match.group(2) or "oz"
    if unit == "oz":
        return num
    elif unit == "lb":
        return num * 16.0
    elif unit == "g":
        return num / 28.3495
    elif unit == "kg":
        return num * 35.274
    return num

def parse_recipe_page(url):
    resp = requests.get(url, headers=HEADERS, timeout=20)
    if resp.status_code != 200:
        print(f"Failed to fetch {url} (HTTP {resp.status_code})")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    # Name
    h1 = soup.find("h1")
    name = h1.get_text(strip=True) if h1 else "Unknown Recipe"

    # Style
    style = "All Grain"
    for el in soup.find_all(["span", "div"]):
        txt = el.get_text(" ", strip=True)
        if "Style:" in txt and len(txt) < 80:
            parts = txt.split("Style:")
            if len(parts) > 1 and parts[1].strip():
                style = parts[1].strip()
                break

    # Stats
    batch_size = 5.0
    og = None
    fg = None
    ibu = None
    abv = None
    srm = None

    for el in soup.find_all(["span", "div", "td", "li"]):
        txt = el.get_text(" ", strip=True)
        if "Batch Size:" in txt and len(txt) < 80:
            m = re.search(r"([\d.]+)\s*(gallons?|gal|liters?|l\b)", txt, re.I)
            if m:
                val = float(m.group(1))
                u = m.group(2).lower()
                batch_size = val if u.startswith("gal") else round(val / 3.78541, 2)
        if "Original Gravity:" in txt and len(txt) < 50:
            m = re.search(r"1\.\d{3}", txt)
            if m:
                og = float(m.group(0))
        if "Final Gravity:" in txt and len(txt) < 50:
            m = re.search(r"1\.\d{3}", txt)
            if m:
                fg = float(m.group(0))
        if "IBU" in txt and ":" in txt and len(txt) < 50:
            m = re.search(r":\s*([\d.]+)", txt)
            if m:
                ibu = float(m.group(1))
        if "ABV:" in txt and len(txt) < 50:
            m = re.search(r":\s*([\d.]+)%?", txt)
            if m:
                abv = float(m.group(1))
        if "Color:" in txt or "SRM:" in txt:
            if len(txt) < 50:
                m = re.search(r":\s*([\d.]+)", txt)
                if m:
                    srm = float(m.group(1))

    malts = []
    hops = []
    yeasts = []
    others = []

    # Tables parsing
    for tbl in soup.find_all("table"):
        headers = [th.get_text(strip=True) for th in tbl.find_all("th")]

        # 1. Fermentables
        if any("Fermentable" in h for h in headers):
            for tr in tbl.find_all("tr")[1:]:
                tds = tr.find_all("td")
                if len(tds) >= 2:
                    amt_str = tds[0].get_text(strip=True)
                    name_a = tds[1].find("a")
                    m_name = name_a.get_text(strip=True) if name_a else next(tds[1].stripped_strings, "")
                    if not m_name or "total" in m_name.lower():
                        continue
                    ppg = None
                    color = None
                    if len(tds) > 3:
                        try:
                            ppg = float(re.findall(r"[\d.]+", tds[3].get_text(strip=True))[0])
                        except Exception:
                            pass
                    if len(tds) > 4:
                        try:
                            color = float(re.findall(r"[\d.]+", tds[4].get_text(strip=True))[0])
                        except Exception:
                            pass
                    amt_lb = parse_weight_lb(amt_str)
                    if amt_lb > 0:
                        malts.append({
                            "name": m_name,
                            "amount_lb": amt_lb,
                            "ppg": ppg,
                            "color": color
                        })

        # 2. Hops
        elif any("Variety" in h for h in headers) and any("AA" in h for h in headers):
            for tr in tbl.find_all("tr")[1:]:
                tds = tr.find_all("td")
                if len(tds) >= 2:
                    amt_str = tds[0].get_text(strip=True)
                    name_a = tds[1].find("a")
                    h_name = name_a.get_text(strip=True) if name_a else next(tds[1].stripped_strings, "")
                    if not h_name or "total" in h_name.lower():
                        continue
                    aa = None
                    use = "Boil"
                    time_disp = ""
                    time_min = 60
                    if len(tds) > 4:
                        try:
                            aa = float(re.findall(r"[\d.]+", tds[4].get_text(strip=True))[0])
                        except Exception:
                            pass
                    if len(tds) > 5:
                        use = " ".join(tds[5].get_text().split())
                    if len(tds) > 6:
                        time_disp = tds[6].get_text(strip=True)
                        m_time = re.findall(r"\d+", time_disp)
                        if m_time:
                            time_val = int(m_time[0])
                            time_min = time_val * 1440 if "day" in time_disp.lower() else time_val

                    amt_oz = parse_weight_oz(amt_str)
                    if amt_oz > 0:
                        hops.append({
                            "name": h_name,
                            "amount_oz": amt_oz,
                            "aa": aa,
                            "use": use,
                            "time_display": time_disp,
                            "addition_time_min": time_min
                        })

        # 3. Yeasts
        elif any("Attenuation" in tbl.get_text() for _ in [0]) and len(tbl.find_all("th")) == 1:
            th_name = tbl.find("th").get_text(strip=True)
            if th_name and len(th_name) < 100:
                y_text = tbl.get_text(" ", strip=True)
                att = None
                m_att = re.search(r"Attenuation[^:]*:\s*([\d.]+)%", y_text)
                if m_att:
                    att = float(m_att.group(1))
                t_low, t_high = None, None
                m_temp = re.search(r"Optimum Temp:\s*([\d.]+)\s*-\s*([\d.]+)", y_text)
                if m_temp:
                    t_low = float(m_temp.group(1))
                    t_high = float(m_temp.group(2))
                yeasts.append({
                    "strain_name": th_name,
                    "attenuation_pct": att,
                    "temp_range_low": t_low,
                    "temp_range_high": t_high,
                    "amount_units": "1 pack"
                })

        # 4. Other Ingredients
        elif any("Name" in h for h in headers) and any("Type" in h for h in headers) and any("Use" in h for h in headers):
            for tr in tbl.find_all("tr")[1:]:
                tds = tr.find_all("td")
                if len(tds) >= 2:
                    amt_str = tds[0].get_text(strip=True)
                    name_a = tds[1].find("a")
                    o_name = name_a.get_text(strip=True) if name_a else tds[1].get_text(strip=True)
                    if not o_name:
                        continue
                    o_type = tds[3].get_text(strip=True) if len(tds) > 3 else "Other"
                    o_use = tds[4].get_text(strip=True) if len(tds) > 4 else "Boil"
                    o_time = tds[5].get_text(strip=True) if len(tds) > 5 else ""

                    m_amt = re.search(r"([\d.]+)\s*(.*)", amt_str)
                    amt_val = float(m_amt.group(1)) if m_amt else 1.0
                    unit_val = m_amt.group(2).strip() if (m_amt and m_amt.group(2).strip()) else "items"

                    others.append({
                        "name": o_name,
                        "amount": amt_val,
                        "unit": unit_val,
                        "item_type": o_type,
                        "use": o_use,
                        "time_display": o_time
                    })

    # Fallback yeast if no yeast table
    if not yeasts:
        yeast_node = soup.find(string=re.compile(r"Yeast", re.I))
        if yeast_node and yeast_node.parent:
            nxt = yeast_node.parent.find_next(["b", "strong"])
            if nxt and len(nxt.get_text(strip=True)) < 60:
                yeasts.append({
                    "strain_name": nxt.get_text(strip=True),
                    "amount_units": "1 pack"
                })

    return {
        "name": name,
        "style": style,
        "original_volume_gal": batch_size if batch_size > 0 else 5.0,
        "target_og": og,
        "target_fg": fg,
        "target_ibu": ibu,
        "target_abv": abv,
        "color_srm": srm,
        "source_url": url,
        "malts": malts,
        "hops": hops,
        "yeasts": yeasts,
        "others": others
    }

def save_recipe_data(data):
    if not data or not data.get("name"):
        return False

    existing = Recipe.query.filter_by(source_url=data["source_url"]).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()

    recipe = Recipe(
        name=data["name"],
        style=data.get("style", "All Grain"),
        original_volume_gal=data.get("original_volume_gal", 5.0),
        target_og=data.get("target_og"),
        target_fg=data.get("target_fg"),
        target_ibu=data.get("target_ibu"),
        target_abv=data.get("target_abv"),
        color_srm=data.get("color_srm"),
        source_url=data["source_url"]
    )
    db.session.add(recipe)
    db.session.flush()

    for m in data.get("malts", []):
        db.session.add(Malt(
            recipe_id=recipe.id,
            name=m["name"],
            amount_lb=m["amount_lb"],
            potential_gravity=m.get("ppg"),
            color_srm=m.get("color")
        ))

    for h in data.get("hops", []):
        db.session.add(Hop(
            recipe_id=recipe.id,
            name=h["name"],
            amount_oz=h["amount_oz"],
            alpha_acid=h.get("aa"),
            addition_time_min=h.get("addition_time_min"),
            time_display=h.get("time_display"),
            use=h.get("use", "Boil")
        ))

    for y in data.get("yeasts", []):
        db.session.add(Yeast(
            recipe_id=recipe.id,
            strain_name=y["strain_name"],
            attenuation_pct=y.get("attenuation_pct"),
            temp_range_low=y.get("temp_range_low"),
            temp_range_high=y.get("temp_range_high"),
            amount_units=y.get("amount_units", "1 pack")
        ))

    for o in data.get("others", []):
        db.session.add(OtherIngredient(
            recipe_id=recipe.id,
            name=o["name"],
            amount=o["amount"],
            unit=o["unit"],
            item_type=o.get("item_type"),
            use=o.get("use"),
            time_display=o.get("time_display")
        ))

    db.session.commit()
    return True

def scrape(max_recipes=20, max_pages=2):
    count = 0
    with app.app_context():
        for page in range(1, max_pages + 1):
            if count >= max_recipes:
                break
            page_url = f"{LIST_URL}?page={page}" if page > 1 else LIST_URL
            print(f"Fetching recipe list from {page_url}...")
            try:
                resp = requests.get(page_url, headers=HEADERS, timeout=20)
                if resp.status_code != 200:
                    print(f"Failed to fetch list page: {resp.status_code}")
                    break
                soup = BeautifulSoup(resp.text, "html.parser")
                links = soup.select('a[href*="/homebrew/recipe/view/"]')
                unique_urls = []
                for a in links:
                    full_url = urljoin(BASE_URL, a["href"])
                    if full_url not in unique_urls:
                        unique_urls.append(full_url)

                print(f"Found {len(unique_urls)} recipes on page {page}.")
                for url in unique_urls:
                    if count >= max_recipes:
                        break
                    print(f"[{count+1}/{max_recipes}] Scraping {url}...")
                    try:
                        data = parse_recipe_page(url)
                        if data and (data.get("malts") or data.get("hops")):
                            save_recipe_data(data)
                            count += 1
                            print(f"  ✓ Saved '{data['name']}' (Vol: {data['original_volume_gal']} gal, {len(data['malts'])} malts, {len(data['hops'])} hops)")
                    except Exception as err:
                        print(f"  ✗ Error parsing {url}: {err}")
                    time.sleep(0.5)
            except Exception as e:
                print(f"Error on page {page}: {e}")
                break

        print(f"\nSuccessfully scraped and saved {count} recipes to database!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape BrewersFriend all-grain recipes.")
    parser.add_argument("--limit", type=int, default=15, help="Maximum number of recipes to scrape")
    parser.add_argument("--pages", type=int, default=2, help="Maximum pages to inspect")
    args = parser.parse_args()
    scrape(max_recipes=args.limit, max_pages=args.pages)
