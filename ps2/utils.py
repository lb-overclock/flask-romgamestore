from urllib.parse import quote

import internetarchive
import json
import sys

def load_platforms_from_json(filepath='platforms.json'):
    """Reads platform and identifier data from a JSON file."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            return data.get('platforms', []) # Return the list of platforms
    except FileNotFoundError:
        print(f"--> ERROR: Platform file not found at '{filepath}'", file=sys.stderr)
        return []
    except json.JSONDecodeError:
        print(f"--> ERROR: Could not decode JSON from '{filepath}'", file=sys.stderr)
        return []

def scrape_ia_games(ia_identifier):
    """Scrapes all .zip files from a single Internet Archive identifier."""
    item = internetarchive.get_item(ia_identifier)
    base_url = f"https://archive.org/download/{ia_identifier}"
    games_list = []
    for file_meta in item.files:
        filename = file_meta['name']
        if filename.lower().endswith('.zip'):
            games_list.append({
                'name': filename,
                'size': format_size(file_meta.get('size')),
                'url': f"{base_url}/{quote(filename)}"
            })
    return games_list

def format_size(size_in_bytes):
    """Converts bytes into a human-readable format (KB, MB, GB)."""
    if size_in_bytes is None: return "N/A"
    try:
        size = float(size_in_bytes)
        if size < 1024**2: return f"{size/1024:.2f} KB"
        if size < 1024**3: return f"{size/1024**2:.2f} MB"
        return f"{size/1024**3:.2f} GB"
    except (ValueError, TypeError):
        return "N/A"