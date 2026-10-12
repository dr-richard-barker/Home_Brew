from flask import Flask
from config import Config
from models import db, init_db, Recipe, Malt, Hop, Yeast, OtherIngredient

app = Flask(__name__)
app.config.from_object(Config)
init_db(app)

SEED_DATA = [
    {
        "name": "Avg. Perfect Northeast IPA (NEIPA)",
        "style": "Specialty IPA: New England IPA",
        "original_volume_gal": 5.75,
        "target_og": 1.062,
        "target_fg": 1.014,
        "target_ibu": 45.0,
        "target_abv": 6.3,
        "color_srm": 4.5,
        "source_url": "https://www.brewersfriend.com/homebrew/recipe/view/363082/avg-perfect-northeast-ipa-neipa-",
        "notes": "Hazy, juicy, double dry-hopped New England IPA. Massive whirlpool and dry hop aroma.",
        "malts": [
            {"name": "US - Pale 2-Row", "amount_lb": 10.75, "ppg": 37.0, "color": 1.8},
            {"name": "American - Wheat", "amount_lb": 1.40, "ppg": 38.0, "color": 1.8},
            {"name": "Flaked Oats", "amount_lb": 1.40, "ppg": 33.0, "color": 2.2},
            {"name": "Honey Malt", "amount_lb": 0.42, "ppg": 37.0, "color": 25.0}
        ],
        "hops": [
            {"name": "Citra", "amount_oz": 1.0, "aa": 12.6, "use": "Boil", "addition_time_min": 10, "time_display": "10 min"},
            {"name": "Galaxy", "amount_oz": 1.0, "aa": 15.6, "use": "Boil", "addition_time_min": 10, "time_display": "10 min"},
            {"name": "Citra", "amount_oz": 1.5, "aa": 12.6, "use": "Whirlpool", "addition_time_min": 20, "time_display": "Whirlpool at 170°F"},
            {"name": "Galaxy", "amount_oz": 1.5, "aa": 15.6, "use": "Whirlpool", "addition_time_min": 20, "time_display": "Whirlpool at 170°F"},
            {"name": "Mosaic", "amount_oz": 1.5, "aa": 11.3, "use": "Whirlpool", "addition_time_min": 20, "time_display": "Whirlpool at 170°F"},
            {"name": "Citra", "amount_oz": 2.25, "aa": 12.6, "use": "Dry Hop", "addition_time_min": 10080, "time_display": "7 days"},
            {"name": "Galaxy", "amount_oz": 3.0, "aa": 15.6, "use": "Dry Hop", "addition_time_min": 10080, "time_display": "7 days"},
            {"name": "Mosaic", "amount_oz": 2.0, "aa": 11.3, "use": "Dry Hop", "addition_time_min": 10080, "time_display": "7 days"}
        ],
        "yeasts": [
            {"strain_name": "Wyeast 1318 - London Ale III", "attenuation_pct": 78.0, "temp_range_low": 64.0, "temp_range_high": 74.0, "amount_units": "1 pack"}
        ],
        "others": [
            {"name": "Irish Moss", "amount": 0.5, "unit": "tsp", "item_type": "Fining", "use": "Boil", "time_display": "15 min"},
            {"name": "Yeast Nutrient", "amount": 0.5, "unit": "tsp", "item_type": "Other", "use": "Boil", "time_display": "15 min"}
        ]
    },
    {
        "name": "Russian River Pliny The Elder Clone",
        "style": "Imperial IPA",
        "original_volume_gal": 6.0,
        "target_og": 1.072,
        "target_fg": 1.011,
        "target_ibu": 190.0,
        "target_abv": 8.0,
        "color_srm": 7.0,
        "source_url": "https://www.brewersfriend.com/homebrew/recipe/view/37534/russian-river-pliny-the-elder-original-",
        "notes": "Classic Double IPA with pungent pine, resin, and citrus notes. Clean bitterness.",
        "malts": [
            {"name": "Two-row Pale Malt", "amount_lb": 13.25, "ppg": 37.0, "color": 1.8},
            {"name": "Crystal 45L", "amount_lb": 0.75, "ppg": 35.0, "color": 45.0},
            {"name": "Carapils (Dextrine)", "amount_lb": 0.75, "ppg": 33.0, "color": 1.5},
            {"name": "Corn Sugar (Dextrose)", "amount_lb": 0.75, "ppg": 46.0, "color": 0.0}
        ],
        "hops": [
            {"name": "Columbus (CTZ)", "amount_oz": 3.5, "aa": 15.0, "use": "Boil", "addition_time_min": 90, "time_display": "90 min"},
            {"name": "Columbus (CTZ)", "amount_oz": 0.75, "aa": 15.0, "use": "Boil", "addition_time_min": 45, "time_display": "45 min"},
            {"name": "Simcoe", "amount_oz": 1.0, "aa": 13.0, "use": "Boil", "addition_time_min": 30, "time_display": "30 min"},
            {"name": "Centennial", "amount_oz": 1.0, "aa": 10.0, "use": "Flameout", "addition_time_min": 0, "time_display": "0 min"},
            {"name": "Simcoe", "amount_oz": 2.5, "aa": 13.0, "use": "Flameout", "addition_time_min": 0, "time_display": "0 min"},
            {"name": "Columbus (CTZ)", "amount_oz": 1.0, "aa": 15.0, "use": "Dry Hop", "addition_time_min": 14400, "time_display": "10 days"},
            {"name": "Centennial", "amount_oz": 1.0, "aa": 10.0, "use": "Dry Hop", "addition_time_min": 14400, "time_display": "10 days"},
            {"name": "Simcoe", "amount_oz": 1.0, "aa": 13.0, "use": "Dry Hop", "addition_time_min": 14400, "time_display": "10 days"}
        ],
        "yeasts": [
            {"strain_name": "White Labs WLP001 California Ale", "attenuation_pct": 80.0, "temp_range_low": 68.0, "temp_range_high": 72.0, "amount_units": "2 packs"}
        ],
        "others": [
            {"name": "Whirlfloc Tablet", "amount": 1.0, "unit": "tablet", "item_type": "Fining", "use": "Boil", "time_display": "15 min"}
        ]
    },
    {
        "name": "Sierra Nevada Pale Ale Clone",
        "style": "American Pale Ale",
        "original_volume_gal": 5.5,
        "target_og": 1.053,
        "target_fg": 1.012,
        "target_ibu": 38.0,
        "target_abv": 5.4,
        "color_srm": 9.5,
        "source_url": "https://www.brewersfriend.com/homebrew/recipe/view/28546/sierra-nevada-pale-ale-clone",
        "notes": "The benchmark American Pale Ale. Balanced caramel malt with unmistakable Cascade citrus and floral character.",
        "malts": [
            {"name": "American 2-Row", "amount_lb": 10.5, "ppg": 37.0, "color": 1.8},
            {"name": "Caramel / Crystal 60L", "amount_lb": 1.0, "ppg": 34.0, "color": 60.0}
        ],
        "hops": [
            {"name": "Magnum", "amount_oz": 0.5, "aa": 14.0, "use": "Boil", "addition_time_min": 60, "time_display": "60 min"},
            {"name": "Perle", "amount_oz": 0.5, "aa": 8.0, "use": "Boil", "addition_time_min": 30, "time_display": "30 min"},
            {"name": "Cascade", "amount_oz": 1.0, "aa": 5.5, "use": "Boil", "addition_time_min": 10, "time_display": "10 min"},
            {"name": "Cascade", "amount_oz": 2.0, "aa": 5.5, "use": "Flameout", "addition_time_min": 0, "time_display": "0 min"},
            {"name": "Cascade", "amount_oz": 1.5, "aa": 5.5, "use": "Dry Hop", "addition_time_min": 5760, "time_display": "4 days"}
        ],
        "yeasts": [
            {"strain_name": "SafAle US-05 / WLP001", "attenuation_pct": 77.0, "temp_range_low": 65.0, "temp_range_high": 70.0, "amount_units": "1 pack"}
        ],
        "others": [
            {"name": "Irish Moss", "amount": 1.0, "unit": "tsp", "item_type": "Fining", "use": "Boil", "time_display": "15 min"}
        ]
    },
    {
        "name": "Zombie Dust Clone - ALL GRAIN",
        "style": "American Pale Ale",
        "original_volume_gal": 5.5,
        "target_og": 1.065,
        "target_fg": 1.015,
        "target_ibu": 60.0,
        "target_abv": 6.5,
        "color_srm": 7.8,
        "source_url": "https://www.brewersfriend.com/homebrew/recipe/view/5916/zombie-dust-clone-all-grain",
        "notes": "100% Citra single hop showcase pale ale with intense mango, guava, and citrus punch.",
        "malts": [
            {"name": "Two-row Pale Malt", "amount_lb": 11.75, "ppg": 37.0, "color": 1.8},
            {"name": "Munich Malt - 10L", "amount_lb": 1.25, "ppg": 35.0, "color": 10.0},
            {"name": "CaraFoam", "amount_lb": 0.5, "ppg": 33.0, "color": 2.0},
            {"name": "Crystal 60L", "amount_lb": 0.5, "ppg": 34.0, "color": 60.0},
            {"name": "Melanoidin Malt", "amount_lb": 0.5, "ppg": 37.0, "color": 20.0}
        ],
        "hops": [
            {"name": "Citra", "amount_oz": 0.75, "aa": 12.5, "use": "Boil", "addition_time_min": 60, "time_display": "60 min"},
            {"name": "Citra", "amount_oz": 1.0, "aa": 12.5, "use": "Boil", "addition_time_min": 15, "time_display": "15 min"},
            {"name": "Citra", "amount_oz": 1.5, "aa": 12.5, "use": "Boil", "addition_time_min": 10, "time_display": "10 min"},
            {"name": "Citra", "amount_oz": 1.5, "aa": 12.5, "use": "Boil", "addition_time_min": 5, "time_display": "5 min"},
            {"name": "Citra", "amount_oz": 1.5, "aa": 12.5, "use": "Flameout", "addition_time_min": 0, "time_display": "0 min"},
            {"name": "Citra", "amount_oz": 3.0, "aa": 12.5, "use": "Dry Hop", "addition_time_min": 7200, "time_display": "5 days"}
        ],
        "yeasts": [
            {"strain_name": "Fermentis - Safale - American Ale Yeast US-05", "attenuation_pct": 77.0, "temp_range_low": 64.0, "temp_range_high": 72.0, "amount_units": "1 pack"}
        ],
        "others": [
            {"name": "Irish Moss", "amount": 1.0, "unit": "tsp", "item_type": "Fining", "use": "Boil", "time_display": "10 min"}
        ]
    },
    {
        "name": "Vanilla Cream Ale",
        "style": "Cream Ale",
        "original_volume_gal": 5.0,
        "target_og": 1.050,
        "target_fg": 1.010,
        "target_ibu": 16.0,
        "target_abv": 5.2,
        "color_srm": 3.5,
        "source_url": "https://www.brewersfriend.com/homebrew/recipe/view/1633/vanilla-cream-ale",
        "notes": "Crisp, refreshing, slightly sweet cream ale with subtle Madagascar bourbon vanilla aroma.",
        "malts": [
            {"name": "American 2-Row", "amount_lb": 7.5, "ppg": 37.0, "color": 1.8},
            {"name": "Flaked Corn (Maize)", "amount_lb": 2.0, "ppg": 37.0, "color": 1.0},
            {"name": "Carapils", "amount_lb": 0.5, "ppg": 33.0, "color": 1.5}
        ],
        "hops": [
            {"name": "Willamette", "amount_oz": 1.0, "aa": 5.0, "use": "Boil", "addition_time_min": 60, "time_display": "60 min"},
            {"name": "Cascade", "amount_oz": 0.5, "aa": 5.5, "use": "Boil", "addition_time_min": 10, "time_display": "10 min"}
        ],
        "yeasts": [
            {"strain_name": "White Labs WLP080 Cream Ale Blend", "attenuation_pct": 78.0, "temp_range_low": 65.0, "temp_range_high": 70.0, "amount_units": "1 pack"}
        ],
        "others": [
            {"name": "Madagascar Vanilla Beans", "amount": 2.0, "unit": "beans", "item_type": "Spice", "use": "Secondary", "time_display": "7 days"}
        ]
    },
    {
        "name": "Velvet Oatmeal Stout",
        "style": "Oatmeal Stout",
        "original_volume_gal": 5.5,
        "target_og": 1.058,
        "target_fg": 1.016,
        "target_ibu": 32.0,
        "target_abv": 5.5,
        "color_srm": 35.0,
        "source_url": "https://www.brewersfriend.com/homebrew/recipe/view/99001/velvet-oatmeal-stout",
        "notes": "Rich, creamy mouthfeel with dark roast coffee, cocoa, and silky oats.",
        "malts": [
            {"name": "Maris Otter Pale Malt", "amount_lb": 8.5, "ppg": 38.0, "color": 3.0},
            {"name": "Flaked Oats", "amount_lb": 1.5, "ppg": 33.0, "color": 2.0},
            {"name": "Roasted Barley", "amount_lb": 0.75, "ppg": 25.0, "color": 300.0},
            {"name": "Chocolate Malt", "amount_lb": 0.75, "ppg": 28.0, "color": 350.0},
            {"name": "Crystal 80L", "amount_lb": 0.5, "ppg": 34.0, "color": 80.0}
        ],
        "hops": [
            {"name": "East Kent Goldings", "amount_oz": 1.5, "aa": 5.0, "use": "Boil", "addition_time_min": 60, "time_display": "60 min"},
            {"name": "Fuggles", "amount_oz": 0.75, "aa": 4.5, "use": "Boil", "addition_time_min": 15, "time_display": "15 min"}
        ],
        "yeasts": [
            {"strain_name": "Wyeast 1084 Irish Ale", "attenuation_pct": 74.0, "temp_range_low": 62.0, "temp_range_high": 72.0, "amount_units": "1 pack"}
        ],
        "others": [
            {"name": "Whirlfloc", "amount": 1.0, "unit": "tablet", "item_type": "Fining", "use": "Boil", "time_display": "15 min"}
        ]
    }
]

def seed():
    with app.app_context():
        count = 0
        for item in SEED_DATA:
            existing = Recipe.query.filter_by(source_url=item["source_url"]).first()
            if existing:
                continue
            r = Recipe(
                name=item["name"],
                style=item["style"],
                original_volume_gal=item["original_volume_gal"],
                target_og=item["target_og"],
                target_fg=item["target_fg"],
                target_ibu=item["target_ibu"],
                target_abv=item["target_abv"],
                color_srm=item["color_srm"],
                notes=item["notes"],
                source_url=item["source_url"]
            )
            db.session.add(r)
            db.session.flush()

            for m in item["malts"]:
                db.session.add(Malt(
                    recipe_id=r.id,
                    name=m["name"],
                    amount_lb=m["amount_lb"],
                    potential_gravity=m["ppg"],
                    color_srm=m["color"]
                ))
            for h in item["hops"]:
                db.session.add(Hop(
                    recipe_id=r.id,
                    name=h["name"],
                    amount_oz=h["amount_oz"],
                    alpha_acid=h["aa"],
                    use=h["use"],
                    addition_time_min=h["addition_time_min"],
                    time_display=h["time_display"]
                ))
            for y in item["yeasts"]:
                db.session.add(Yeast(
                    recipe_id=r.id,
                    strain_name=y["strain_name"],
                    attenuation_pct=y["attenuation_pct"],
                    temp_range_low=y["temp_range_low"],
                    temp_range_high=y["temp_range_high"],
                    amount_units=y["amount_units"]
                ))
            for o in item.get("others", []):
                db.session.add(OtherIngredient(
                    recipe_id=r.id,
                    name=o["name"],
                    amount=o["amount"],
                    unit=o["unit"],
                    item_type=o["item_type"],
                    use=o["use"],
                    time_display=o["time_display"]
                ))
            count += 1
        db.session.commit()
        print(f"Seeded {count} classic all-grain recipes into SQLite!")

if __name__ == "__main__":
    seed()
