import os
import re
import json
from app import app
from models import Recipe

def export_recipes():
    with app.app_context():
        recipes = Recipe.query.order_by(Recipe.id.asc()).all()
        data = [r.to_dict(target_volume_gal=r.original_volume_gal) for r in recipes]

    os.makedirs("docs", exist_ok=True)

    # 1. Write standalone JSON files
    with open("recipes.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    with open(os.path.join("docs", "recipes.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    # 2. Inject embedded recipes into templates/index.html and write to index.html and docs/index.html
    with open(os.path.join("templates", "index.html"), "r", encoding="utf-8") as f:
        html_content = f.read()

    embedded_script = (
        '<script id="embedded-recipes-script">\n'
        f'    window.EMBEDDED_RECIPES = {json.dumps(data)};\n'
        '  </script>'
    )
    updated_html = re.sub(
        r'<script id="embedded-recipes-script">.*?</script>',
        lambda _: embedded_script,
        html_content,
        flags=re.DOTALL
    )

    for target_path in [
        os.path.join("templates", "index.html"),
        "index.html",
        os.path.join("docs", "index.html")
    ]:
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(updated_html)

    # 3. Create .nojekyll files so GitHub Pages serves static assets directly
    for nojekyll_path in [".nojekyll", os.path.join("docs", ".nojekyll")]:
        with open(nojekyll_path, "w", encoding="utf-8") as f:
            f.write("")

    print(f"Exported {len(data)} recipes and generated GitHub Pages bundle in ./index.html and ./docs/index.html!")
    return data

if __name__ == "__main__":
    export_recipes()
