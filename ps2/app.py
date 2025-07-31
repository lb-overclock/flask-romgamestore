from flask import Flask, render_template, redirect, url_for
from utils import load_platforms_from_json, scrape_ia_games
import sys
import json

app = Flask(__name__)
CACHE_FILENAME = 'cache.json'

@app.route('/')
def show_cached_platforms():
    """
    Instantly loads platform data from the local cache file.
    If the cache doesn't exist, it redirects to the refresh route.
    """
    try:
        with open(CACHE_FILENAME, 'r') as f:
            platforms_data = json.load(f)
        return render_template('index.html', platforms=platforms_data)
    except FileNotFoundError:
        print("--> Cache not found. Redirecting to refresh...", file=sys.stderr)
        return redirect(url_for('refresh_data'))

@app.route('/refresh')
def refresh_data():
    """
    This runs the long scraping process and saves the results to the cache.
    """
    print("==> Starting data refresh...", file=sys.stderr)
    
    # 1. Load the list of platforms from the JSON file
    platforms_list = load_platforms_from_json('./plataforms.json')
    
    all_platform_data = []

    # 2. Loop through each platform and scrape its data
    for platform in platforms_list:
        platform_name = platform.get('name')
        identifiers = platform.get('identifiers', [])
        
        print(f"==> Processing Platform: {platform_name}", file=sys.stderr)
        
        collections_for_platform = []
        for identifier in identifiers:
            print(f"--> Scraping identifier: {identifier}", file=sys.stderr)
            try:
                games = scrape_ia_games(identifier)
                collections_for_platform.append({
                    'identifier': identifier,
                    'games': games
                })
            except Exception as e:
                print(f"--> ERROR processing '{identifier}': {e}", file=sys.stderr)
                collections_for_platform.append({'identifier': identifier, 'games': [], 'error': str(e)})
        
        all_platform_data.append({
            'name': platform_name,
            'collections': collections_for_platform
        })

    # 3. Save the final data structure to our cache file
    with open(CACHE_FILENAME, 'w') as f:
        json.dump(all_platform_data, f, indent=4)
    print("==> Data refresh complete. Cache file created.", file=sys.stderr)

    # 4. Redirect back to the main page, which will now load from the cache
    return redirect(url_for('show_cached_platforms'))

if __name__ == '__main__':
    app.run(debug=True)