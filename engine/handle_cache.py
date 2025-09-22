import os
import json
from typing import Dict

CACHE_PATH = 'audio_cache/cache.json'
RESPONSE_PATH = './test/response.json'


def ensure_parent_dir(path: str) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)

def load_cache() -> Dict[str, str]:
    ensure_parent_dir(CACHE_PATH)
    if not os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump({}, f)
        return {}
    try:
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except Exception:
        pass
    return {}

def save_cache(cache: Dict[str, str]) -> None:
    ensure_parent_dir(CACHE_PATH)
    # Load existing cache if it exists
    if os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                existing_cache = json.load(f)
                if not isinstance(existing_cache, dict):
                    existing_cache = {}
        except Exception:
            existing_cache = {}
    else:
        existing_cache = {}

    # Only add new entries that don't already exist in the cache
    new_entries = {}
    for key, value in cache.items():
        if key not in existing_cache:
            new_entries[key] = value
    
    # If there are new entries, merge them with existing cache
    if new_entries:
        existing_cache.update(new_entries)
        with open(CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(existing_cache, f, indent=2, ensure_ascii=False)



def load_response(file_path = RESPONSE_PATH):
    ensure_parent_dir(file_path)
    with open(file_path, "r") as f:
        data = json.load(f)
        return data
