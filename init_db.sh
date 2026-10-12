#!/usr/bin/env bash

set -e

# Ensure virtual environment exists
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize SQLite DB (tables will be created on first request) and run scraper
python scrape_recipes.py

echo "Database initialized and recipes scraped."
