from flask import Flask, jsonify, request, send_from_directory
from config import Config
from models import db, init_db, Recipe, Malt, Hop, Yeast, OtherIngredient
from scale_recipe import scale_single_recipe, build_ordering_list

app = Flask(__name__)
app.config.from_object(Config)
init_db(app)

@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')

@app.route('/api/recipes', methods=['GET'])
def list_recipes():
    target_vol = request.args.get('volume', type=float)
    search = request.args.get('q', '').strip().lower()
    recipes = Recipe.query.order_by(Recipe.id.asc()).all()
    result = []
    for r in recipes:
        if search and search not in r.name.lower() and search not in (r.style or '').lower():
            continue
        vol = target_vol if target_vol is not None else 5.0
        result.append(r.to_dict(target_volume_gal=vol))
    return jsonify(result)

@app.route('/api/recipes/<int:recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    target_vol = request.args.get('volume', default=5.0, type=float)
    recipe = Recipe.query.get_or_404(recipe_id)
    return jsonify(scale_single_recipe(recipe, target_volume_gal=target_vol))

@app.route('/api/recipes/<int:recipe_id>/ingredients', methods=['GET'])
def get_scaled_ingredients(recipe_id):
    target_gal = request.args.get('volume', default=5.0, type=float)
    recipe = Recipe.query.get_or_404(recipe_id)
    scaled = scale_single_recipe(recipe, target_volume_gal=target_gal)

    ingredients = []
    for m in scaled['malts']:
        ingredients.append({
            "type": "malt",
            "name": m["name"],
            "amount": m["amount_lb"],
            "unit": "lb",
            "amount_metric": m["amount_kg"],
            "unit_metric": "kg",
            "color_srm": m["color_srm"]
        })
    for h in scaled['hops']:
        ingredients.append({
            "type": "hop",
            "name": h["name"],
            "amount": h["amount_oz"],
            "unit": "oz",
            "amount_metric": h["amount_g"],
            "unit_metric": "g",
            "alpha_acid": h["alpha_acid"],
            "addition_time": h["time_display"] or f"{h['addition_time_min']} min",
            "use": h["use"]
        })
    for y in scaled['yeasts']:
        ingredients.append({
            "type": "yeast",
            "name": y["strain_name"],
            "amount": y["scaled_packs"],
            "unit": "pack(s)",
            "attenuation_pct": y["attenuation_pct"]
        })
    for o in scaled['others']:
        ingredients.append({
            "type": "other",
            "name": o["name"],
            "amount": o["amount"],
            "unit": o["unit"],
            "use": o["use"],
            "addition_time": o["time_display"]
        })

    return jsonify({
        "recipe_id": recipe.id,
        "recipe": recipe.name,
        "style": recipe.style,
        "original_volume_gal": recipe.original_volume_gal,
        "target_volume_gal": target_gal,
        "scale_factor": scaled["scale_factor"],
        "ingredients": ingredients
    })

@app.route('/api/ordering-list', methods=['POST'])
def create_ordering_list():
    """
    Accepts JSON payload:
    {
      "default_volume_gal": 5.0,
      "items": [
        {"recipe_id": 7, "volume_gal": 5.0},
        {"recipe_id": 8, "volume_gal": 10.0}
      ]
    }
    Or simpler:
    {
      "recipe_ids": [7, 8, 10],
      "volume_gal": 5.0
    }
    """
    payload = request.get_json(silent=True) or {}
    default_vol = float(payload.get("default_volume_gal") or payload.get("volume_gal") or 5.0)

    recipes_with_volumes = []
    if "items" in payload and isinstance(payload["items"], list):
        for item in payload["items"]:
            r_id = item.get("recipe_id")
            vol = float(item.get("volume_gal", default_vol))
            recipe = db.session.get(Recipe, r_id)
            if recipe and vol > 0:
                recipes_with_volumes.append((recipe, vol))
    elif "recipe_ids" in payload and isinstance(payload["recipe_ids"], list):
        for r_id in payload["recipe_ids"]:
            recipe = db.session.get(Recipe, r_id)
            if recipe:
                recipes_with_volumes.append((recipe, default_vol))

    return jsonify(build_ordering_list(recipes_with_volumes))

@app.route('/api/recipes/<int:recipe_id>', methods=['PUT'])
def update_recipe(recipe_id):
    """Allow updating a recipe's base volume, name, style, or saving a scaled version as the new baseline."""
    recipe = Recipe.query.get_or_404(recipe_id)
    data = request.get_json(silent=True) or {}

    if "name" in data:
        recipe.name = data["name"]
    if "style" in data:
        recipe.style = data["style"]
    if "notes" in data:
        recipe.notes = data["notes"]

    # If normalize_to_volume_gal is passed, permanently scale the stored ingredients to that batch size
    if "normalize_to_volume_gal" in data:
        new_vol = float(data["normalize_to_volume_gal"])
        if new_vol > 0 and recipe.original_volume_gal > 0:
            factor = new_vol / recipe.original_volume_gal
            for m in recipe.malts:
                m.amount_lb = round(m.amount_lb * factor, 3)
            for h in recipe.hops:
                h.amount_oz = round(h.amount_oz * factor, 3)
            for o in recipe.others:
                o.amount = round(o.amount * factor, 3)
            recipe.original_volume_gal = round(new_vol, 2)

    db.session.commit()
    return jsonify(recipe.to_dict(target_volume_gal=recipe.original_volume_gal))

@app.route('/api/recipes/normalize-all', methods=['POST'])
def normalize_all_recipes():
    """Normalize all recipes in the database to a target baseline volume (default 5.0 gal)."""
    data = request.get_json(silent=True) or {}
    target_vol = float(data.get("target_volume_gal", 5.0))
    recipes = Recipe.query.all()
    for recipe in recipes:
        if recipe.original_volume_gal > 0 and abs(recipe.original_volume_gal - target_vol) > 0.001:
            factor = target_vol / recipe.original_volume_gal
            for m in recipe.malts:
                m.amount_lb = round(m.amount_lb * factor, 3)
            for h in recipe.hops:
                h.amount_oz = round(h.amount_oz * factor, 3)
            for o in recipe.others:
                o.amount = round(o.amount * factor, 3)
            recipe.original_volume_gal = round(target_vol, 2)
    db.session.commit()
    return jsonify({"status": "ok", "normalized_count": len(recipes), "target_volume_gal": target_vol})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5050))
    app.run(host='127.0.0.1', port=port, debug=False)
