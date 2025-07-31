from flask import Flask, render_template, redirect, url_for, abort
from utils import load_platforms_from_json, scrape_ia_games, slugify

import os
import json
import sys

app = Flask(__name__)

CACHE_DIR = 'store_internetarchive/cache'
PLATFORM_DIR = 'store_internetarchive/plataforms.json'

os.makedirs(CACHE_DIR, exist_ok=True)

@app.route('/')
def home():
    """Displays the homepage with a list of available platforms."""
    platforms = load_platforms_from_json(PLATFORM_DIR)
    # Add a slug to each platform for URL generation
    for p in platforms:
        p['slug'] = slugify(p['name'])
    return render_template('home.html', platforms=platforms)

@app.route('/platform/<platform_slug>')
def show_platform(platform_slug):
    """Displays a single platform's data from its specific cache file."""
    cache_path = os.path.join(CACHE_DIR, f'cache_{platform_slug}.json')
    try:
        with open(cache_path, 'r') as f:
            platform_data = json.load(f)
        return render_template('platform.html', platform=platform_data)
    except FileNotFoundError:
        # If no cache exists for this platform, trigger a refresh for it
        return redirect(url_for('refresh_platform', platform_slug=platform_slug))

@app.route('/refresh/<platform_slug>')
def refresh_platform(platform_slug):
    """Refreshes the data for ONLY ONE platform and caches it."""
    all_platforms = load_platforms_from_json(PLATFORM_DIR)
    
    # Find the specific platform to refresh by matching its slug
    target_platform = None
    for p in all_platforms:
        if slugify(p['name']) == platform_slug:
            target_platform = p
            break
            
    if not target_platform:
        return "Platform not found", 404

    print(f"==> Refreshing data for: {target_platform['name']}", file=sys.stderr)
    
    collections_for_platform = []
    for identifier in target_platform.get('identifiers', []):
        try:
            games = scrape_ia_games(identifier)
            collections_for_platform.append({
                'identifier': identifier,
                'games': games
            })
        except Exception as e:
            print(f"--> ERROR processing '{identifier}': {e}", file=sys.stderr)

    # This is the final data structure for this single platform
    final_platform_data = {
        'name': target_platform['name'],
        'slug': platform_slug,
        'collections': collections_for_platform
    }
    
    # Save to the platform-specific cache file
    cache_path = os.path.join(CACHE_DIR, f'cache_{platform_slug}.json')
    with open(cache_path, 'w') as f:
        json.dump(final_platform_data, f, indent=4)
        
    print(f"==> Refresh complete for {target_platform['name']}", file=sys.stderr)
    
    # Redirect back to the platform's main page
    return redirect(url_for('show_platform', platform_slug=platform_slug))

if __name__ == '__main__':
    app.run(debug=True)