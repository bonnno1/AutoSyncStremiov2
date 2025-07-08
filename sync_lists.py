import requests
import os
import json

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE = "https://api.themoviedb.org/3"
HEADERS = {"accept": "application/json"}

def fetch_tmdb(url, params={}):
    params["api_key"] = TMDB_API_KEY
    params.setdefault("region", "AU")
    params.setdefault("language", "en-AU")

    print(f"🔍 Fetching: {url} | Params: {params}")
    res = requests.get(f"{TMDB_BASE}{url}", params=params, headers=HEADERS)

    try:
        data = res.json()
    except ValueError:
        print(f"❌ Invalid JSON from TMDb at {url}")
        return []

    if res.status_code != 200:
        print(f"❌ TMDb error {res.status_code} at {url}: {data.get('status_message')}")
        return []

    if "results" not in data:
        print(f"⚠️ No 'results' in TMDb response for {url}")
        return []

    return data["results"]

def fetch_imdb_id(tmdb_id, media_type="tv"):
    url = f"/{media_type}/{tmdb_id}/external_ids"
    print(f"🔍 Fetching IMDb ID for {media_type.upper()} ID {tmdb_id}")
    res = requests.get(f"{TMDB_BASE}{url}", params={"api_key": TMDB_API_KEY}, headers=HEADERS)

    try:
        data = res.json()
        return data.get("imdb_id")
    except ValueError:
        print(f"❌ Invalid JSON fetching IMDb ID for {tmdb_id}")
        return None

def to_json_format(results, media_type):
    formatted = []
    for item in results:
        imdb_id = fetch_imdb_id(item["id"], media_type)
        if not imdb_id:
            print(f"⚠️ No IMDb ID for TMDb ID {item['id']} — skipping.")
            continue

        formatted.append({
            "title": item.get("name") or item.get("title"),
            "imdb_id": imdb_id,
            "type": "movie" if media_type == "movie" else "series"
        })
    return formatted

def fetch_shows_for_list(list_def):
    media_type = list_def.get("media_type", "tv")

    if list_def.get("special") == "trending":
        return to_json_format(fetch_tmdb(f"/trending/{media_type}/week"), media_type)
    if list_def.get("special") == "popular":
        return to_json_format(fetch_tmdb(f"/{media_type}/popular"), media_type)
    if list_def.get("special") == "now_playing":
        return to_json_format(fetch_tmdb("/movie/now_playing"), "movie")
    if list_def.get("special") == "airing_today":
        return to_json_format(fetch_tmdb("/tv/airing_today"), "tv")

    return to_json_format(fetch_tmdb(f"/discover/{media_type}", list_def["tmdb_params"]), media_type)

def get_category_list():
    return [
        # Streaming Services
        {"slug": "netflix-series", "tmdb_params": {"with_networks": "213"}, "name": "Netflix TV", "media_type": "tv"},
        {"slug": "netflix-movies", "tmdb_params": {"with_networks": "213"}, "name": "Netflix Movies", "media_type": "movie"},
        {"slug": "disney-series", "tmdb_params": {"with_networks": "2739"}, "name": "Disney+ TV", "media_type": "tv"},
        {"slug": "disney-movies", "tmdb_params": {"with_networks": "2739"}, "name": "Disney+ Movies", "media_type": "movie"},
        {"slug": "prime-series", "tmdb_params": {"with_networks": "1024"}, "name": "Prime TV", "media_type": "tv"},
        {"slug": "prime-movies", "tmdb_params": {"with_networks": "1024"}, "name": "Prime Movies", "media_type": "movie"},
        {"slug": "apple-series", "tmdb_params": {"with_networks": "2552"}, "name": "Apple TV+ Series", "media_type": "tv"},
        {"slug": "apple-movies", "tmdb_params": {"with_networks": "2552"}, "name": "Apple TV+ Movies", "media_type": "movie"},
        {"slug": "stan-series", "tmdb_params": {"with_keywords": "186729"}, "name": "Stan TV", "media_type": "tv"},
        {"slug": "stan-movies", "tmdb_params": {"with_keywords": "186729"}, "name": "Stan Movies", "media_type": "movie"},

        # Genres
        {"slug": "action-series", "tmdb_params": {"with_genres": "10759"}, "name": "Action Series", "media_type": "tv"},
        {"slug": "action-movies", "tmdb_params": {"with_genres": "28"}, "name": "Action Movies", "media_type": "movie"},
        {"slug": "comedy-series", "tmdb_params": {"with_genres": "35"}, "name": "Comedy Series", "media_type": "tv"},
        {"slug": "comedy-movies", "tmdb_params": {"with_genres": "35"}, "name": "Comedy Movies", "media_type": "movie"},
        {"slug": "horror-series", "tmdb_params": {"with_genres": "27"}, "name": "Horror Series", "media_type": "tv"},
        {"slug": "horror-movies", "tmdb_params": {"with_genres": "27"}, "name": "Horror Movies", "media_type": "movie"},
        {"slug": "romance-series", "tmdb_params": {"with_genres": "10749"}, "name": "Romance Series", "media_type": "tv"},
        {"slug": "romance-movies", "tmdb_params": {"with_genres": "10749"}, "name": "Romance Movies", "media_type": "movie"},

        # Specials
        {"slug": "trending-series", "special": "trending", "name": "Trending Series", "media_type": "tv"},
        {"slug": "trending-movies", "special": "trending", "name": "Trending Movies", "media_type": "movie"},
        {"slug": "popular-series", "special": "popular", "name": "Popular Series", "media_type": "tv"},
        {"slug": "popular-movies", "special": "popular", "name": "Popular Movies", "media_type": "movie"},
        {"slug": "cinema", "special": "now_playing", "name": "In Cinemas", "media_type": "movie"},
        {"slug": "newreleases", "special": "airing_today", "name": "New Releases", "media_type": "tv"}
    ]
