# CoSE BrewLab — All-Grain Recipe Database & Multi-Batch Ingredient Ordering System

A local-first Python Flask + SQLite + React/Ant Design (**CoSE** theme) application that scrapes all‑grain homebrew recipes from [BrewersFriend](https://www.brewersfriend.com/homebrew-recipes/all-grain/), normalizes and scales recipes dynamically to any target batch size (default **5.0 gallons**), and generates a consolidated **Master Ingredient Ordering List** across any number of selected recipes.

## Features
- **BrewersFriend All-Grain Scraper** ([`scrape_recipes.py`](file:///Users/drb_laptop/Documents/Home_Brew/scrape_recipes.py)): Extracts recipe metadata, original fermentor batch volume, grain bills (malts/fermentables with PPG and °L/SRM), hop schedules (boil, whirlpool, dry-hop with AA%), yeast strains (attenuation & temp ranges), and finings/adjuncts.
- **Dynamic Volume Scaling & Multi-Recipe Ordering** ([`scale_recipe.py`](file:///Users/drb_laptop/Documents/Home_Brew/scale_recipe.py)):
  - Scale all recipes globally to **5.0 gallons** (or `2.5g`, `6g`, `10g`, `15.5g`, or any custom volume).
  - Override target batch volume per individual recipe.
  - Consolidate ingredients across multiple selected recipes into a single ordered shopping list grouped by **Malts/Fermentables**, **Hops**, **Yeasts**, and **Other/Finings**, with synonym normalization and both **US Imperial (`lb`/`oz`/`gal`)** and **Metric (`kg`/`g`/`L`)** units.
- **CoSE Theme Interface** ([`templates/index.html`](file:///Users/drb_laptop/Documents/Home_Brew/templates/index.html)): Built with Ant Design v5 `ConfigProvider` using the CoSE deep slate/navy (`#1a365d`) and lab teal (`#0f766e`) palette, SRM color swatches, in-stock checklist filtering, CSV export, clipboard copy, and print sheet.

## Quick Start

```bash
cd /Users/drb_laptop/Documents/Home_Brew

# 1. Scrape additional recipes from BrewersFriend (optional — 16 recipes are already loaded!)
./venv/bin/python scrape_recipes.py --limit 20 --pages 2

# 2. Start the server (runs on http://127.0.0.1:5050)
./venv/bin/python app.py

# 3. Run unit tests
./venv/bin/python -m unittest discover -s tests
```
