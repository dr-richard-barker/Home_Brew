import re
from collections import defaultdict

SYNONYM_MAP = {
    "us - pale 2-row": "American - Pale 2-Row",
    "american 2-row": "American - Pale 2-Row",
    "two-row pale malt": "American - Pale 2-Row",
    "crystal 80l": "American - Caramel / Crystal 80L",
    "crystal 60l": "American - Caramel / Crystal 60L",
    "caramel / crystal 60l": "American - Caramel / Crystal 60L",
    "crystal 45l": "American - Caramel / Crystal 45L",
    "chocolate malt": "American - Chocolate",
    "carapils": "American - Carapils (Dextrine Malt)",
    "carapils (dextrine)": "American - Carapils (Dextrine Malt)",
    "carafoam": "German - CaraFoam",
    "munich malt - 10l": "American - Munich - Light 10L",
    "melanoidin malt": "German - Melanoidin",
    "flaked corn (maize)": "Flaked Corn",
    "corn sugar (dextrose)": "Corn Sugar - Dextrose",
    "columbus (ctz)": "Columbus",
    "saaz": "Saaz",
    "wyeast 1084 irish ale": "Wyeast - Irish Ale 1084",
    "wyeast 1318 - london ale iii": "Wyeast - London Ale III 1318"
}

def normalize_name(name):
    """Normalize ingredient names so identical malts/hops aggregate cleanly."""
    if not name:
        return "Unknown"
    cleaned = " ".join(name.strip().split())
    # Strip trailing tooltip duplication if present
    cleaned = re.sub(r"\d+(?:\.\d+)?\s*(?:lb|oz|kg|g)\s+.*$", "", cleaned, flags=re.I).strip()
    lower = cleaned.lower()
    if lower in SYNONYM_MAP:
        return SYNONYM_MAP[lower]
    return cleaned

def scale_single_recipe(recipe, target_volume_gal=5.0):
    """Return a dictionary of scaled ingredients for a single Recipe ORM object."""
    return recipe.to_dict(target_volume_gal=target_volume_gal)

def build_ordering_list(recipes_with_volumes):
    """
    Aggregate scaled ingredients across multiple selected recipes into a consolidated
    Master Ordering List (Shopping List) grouped by category:
      1. Fermentables / Malts (aggregated by name, total lb & kg, plus recommended bag/lb rounding)
      2. Hops (aggregated by variety, total oz & grams, plus recommended pack sizes)
      3. Yeast Strains (aggregated by strain name, total packs)
      4. Other / Finings / Adjuncts (aggregated by name & unit)

    :param recipes_with_volumes: list of tuples (Recipe, target_volume_gal)
    :return: dict with aggregated ordering list and individual scaled recipe summaries
    """
    malts_agg = defaultdict(lambda: {
        "name": "",
        "total_lb": 0.0,
        "total_kg": 0.0,
        "color_srm": None,
        "used_in": []
    })
    hops_agg = defaultdict(lambda: {
        "name": "",
        "total_oz": 0.0,
        "total_g": 0.0,
        "alpha_acid": None,
        "used_in": []
    })
    yeasts_agg = defaultdict(lambda: {
        "strain_name": "",
        "total_packs": 0,
        "attenuation_pct": None,
        "used_in": []
    })
    others_agg = defaultdict(lambda: {
        "name": "",
        "total_amount": 0.0,
        "unit": "",
        "type": "",
        "used_in": []
    })

    scaled_recipes = []

    for recipe, target_vol in recipes_with_volumes:
        r_dict = scale_single_recipe(recipe, target_volume_gal=target_vol)
        scaled_recipes.append(r_dict)

        # 1. Aggregate Malts
        for m in r_dict["malts"]:
            key = normalize_name(m["name"]).lower()
            entry = malts_agg[key]
            entry["name"] = entry["name"] or normalize_name(m["name"])
            entry["total_lb"] += m["amount_lb"]
            entry["total_kg"] += m["amount_kg"]
            if entry["color_srm"] is None and m.get("color_srm") is not None:
                entry["color_srm"] = m["color_srm"]
            entry["used_in"].append({
                "recipe_id": recipe.id,
                "recipe_name": recipe.name,
                "amount_lb": round(m["amount_lb"], 2),
                "target_volume_gal": target_vol
            })

        # 2. Aggregate Hops (combine same hop variety within and across recipes)
        recipe_hop_totals = defaultdict(float)
        recipe_hop_aa = {}
        recipe_hop_name = {}
        for h in r_dict["hops"]:
            h_key = normalize_name(h["name"]).lower()
            recipe_hop_name[h_key] = normalize_name(h["name"])
            recipe_hop_totals[h_key] += h["amount_oz"]
            if h.get("alpha_acid") is not None:
                recipe_hop_aa[h_key] = h["alpha_acid"]

        for h_key, oz_sum in recipe_hop_totals.items():
            entry = hops_agg[h_key]
            entry["name"] = entry["name"] or recipe_hop_name[h_key]
            entry["total_oz"] += oz_sum
            entry["total_g"] += oz_sum * 28.3495
            if entry["alpha_acid"] is None and h_key in recipe_hop_aa:
                entry["alpha_acid"] = recipe_hop_aa[h_key]
            entry["used_in"].append({
                "recipe_id": recipe.id,
                "recipe_name": recipe.name,
                "amount_oz": round(oz_sum, 2),
                "target_volume_gal": target_vol
            })

        # 3. Aggregate Yeasts
        for y in r_dict["yeasts"]:
            y_key = normalize_name(y["strain_name"]).lower()
            entry = yeasts_agg[y_key]
            entry["strain_name"] = entry["strain_name"] or normalize_name(y["strain_name"])
            packs = y.get("scaled_packs", 1)
            entry["total_packs"] += packs
            if entry["attenuation_pct"] is None and y.get("attenuation_pct") is not None:
                entry["attenuation_pct"] = y["attenuation_pct"]
            entry["used_in"].append({
                "recipe_id": recipe.id,
                "recipe_name": recipe.name,
                "packs": packs,
                "target_volume_gal": target_vol
            })

        # 4. Aggregate Other Ingredients
        for o in r_dict["others"]:
            o_key = (normalize_name(o["name"]).lower(), (o.get("unit") or "").lower())
            entry = others_agg[o_key]
            entry["name"] = entry["name"] or normalize_name(o["name"])
            entry["total_amount"] += o["amount"]
            entry["unit"] = o.get("unit") or "unit"
            entry["type"] = o.get("type") or "Additive"
            entry["used_in"].append({
                "recipe_id": recipe.id,
                "recipe_name": recipe.name,
                "amount": round(o["amount"], 2),
                "unit": entry["unit"],
                "target_volume_gal": target_vol
            })

    # Format and sort aggregated lists (heaviest/most used first)
    malts_list = sorted(
        [
            {
                **v,
                "total_lb": round(v["total_lb"], 2),
                "total_kg": round(v["total_kg"], 2),
                "total_oz": round(v["total_lb"] * 16.0, 1)
            }
            for v in malts_agg.values()
        ],
        key=lambda x: x["total_lb"],
        reverse=True
    )

    hops_list = sorted(
        [
            {
                **v,
                "total_oz": round(v["total_oz"], 2),
                "total_g": round(v["total_g"], 1)
            }
            for v in hops_agg.values()
        ],
        key=lambda x: x["total_oz"],
        reverse=True
    )

    yeasts_list = sorted(
        list(yeasts_agg.values()),
        key=lambda x: x["total_packs"],
        reverse=True
    )

    others_list = sorted(
        [
            {
                **v,
                "total_amount": round(v["total_amount"], 2)
            }
            for v in others_agg.values()
        ],
        key=lambda x: x["name"]
    )

    total_grain_lb = round(sum(m["total_lb"] for m in malts_list), 2)
    total_hops_oz = round(sum(h["total_oz"] for h in hops_list), 2)
    total_yeast_packs = sum(y["total_packs"] for y in yeasts_list)
    total_batch_volume_gal = round(sum(vol for _, vol in recipes_with_volumes), 2)

    return {
        "summary": {
            "selected_recipe_count": len(recipes_with_volumes),
            "total_batch_volume_gal": total_batch_volume_gal,
            "total_grain_lb": total_grain_lb,
            "total_grain_kg": round(total_grain_lb * 0.453592, 2),
            "total_hops_oz": total_hops_oz,
            "total_hops_g": round(total_hops_oz * 28.3495, 1),
            "total_yeast_packs": total_yeast_packs,
            "unique_malts": len(malts_list),
            "unique_hops": len(hops_list),
            "unique_yeasts": len(yeasts_list)
        },
        "ordering_list": {
            "malts": malts_list,
            "hops": hops_list,
            "yeasts": yeasts_list,
            "others": others_list
        },
        "recipes": scaled_recipes
    }
