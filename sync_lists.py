import requests
import os
import json

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE = "https://api.themoviedb.org/3"

HEADERS = {"accept": "application/json"}

def fetch_tmdb(url, params={}):
    params["api_key"] = TMDB_API_KEY
   # params.setdefault("region", "AU")       # 🇦🇺 Target Australian content
    params.setdefault("language", "en-AU")

    print(f"🔍 Fetching: {url} | Params: {params}")
    res = requests.get(f"{TMDB_BASE}{url}", params=params, headers=HEADERS)

    try:
        data = res.json()
    except ValueError:
        print(f"❌ Invalid JSON from TMDb at {url}")
        return []

    print(f"📨 Response: {json.dumps(data, indent=2)}")

    if res.status_code != 200:
        print(f"❌ TMDb error {res.status_code} at {url}: {data.get('status_message')}")
        return []

    if "results" not in data:
        print(f"⚠️ No 'results' in TMDb response for {url}")
        return []

    return data["results"]

def fetch_imdb_id(tmdb_id, content_type="tv"):
    url = f"/{content_type}/{tmdb_id}/external_ids"
    params = {"api_key": TMDB_API_KEY}
    print(f"🔍 Fetching IMDb ID for TMDb ID {tmdb_id} ({content_type})")

    res = requests.get(f"{TMDB_BASE}{url}", params=params, headers=HEADERS)
    try:
        data = res.json()
        print(f"📨 IMDb Response: {json.dumps(data, indent=2)}")
        return data.get("imdb_id")
    except ValueError:
        print(f"❌ Invalid JSON when fetching IMDb ID for {tmdb_id}")
        return None

def to_json_format(results, content_type):
    formatted = []
    for item in results:
        imdb_id = fetch_imdb_id(item["id"], "tv" if content_type == "series" else "movie")
        if not imdb_id:
            print(f"⚠️ No IMDb ID for TMDb ID {item['id']} — skipping.")
            continue
        formatted.append({
            "title": item.get("name") or item.get("title"),
            "imdb_id": imdb_id,
            "type": content_type
        })
    return formatted

def fetch_shows_for_list(list_def):
    params = list_def.get("tmdb_params", {})
    special = list_def.get("special")
    content_type = list_def.get("type", "series")  # Default to series

    if special == "trending":
        return to_json_format(fetch_tmdb(f"/trending/{content_type}/week"), content_type)
    elif special == "popular":
        return to_json_format(fetch_tmdb(f"/{content_type}/popular"), content_type)
    elif special == "now_playing":
        return to_json_format(fetch_tmdb("/movie/now_playing"), "movie")
    elif special == "airing_today":
        return to_json_format(fetch_tmdb("/tv/airing_today"), "series")

    path = "/discover/" + ("tv" if content_type == "series" else "movie")
    return to_json_format(fetch_tmdb(path, params), content_type)

def get_category_list():
    return [
        # Streaming Services
        {"slug": "netflix-series", "tmdb_params": {"with_networks": "213"}, "name": "Netflix Series", "type": "series"},
        {"slug": "netflix-movies", "tmdb_params": {"with_networks": "213"}, "name": "Netflix Movies", "type": "movie"},
        {"slug": "disney-series", "tmdb_params": {"with_networks": "2739"}, "name": "Disney+ Series", "type": "series"},
        {"slug": "disney-movies", "tmdb_params": {"with_networks": "2739"}, "name": "Disney+ Movies", "type": "movie"},
        {"slug": "prime-series", "tmdb_params": {"with_networks": "1024"}, "name": "Prime Series", "type": "series"},
        {"slug": "prime-movies", "tmdb_params": {"with_networks": "1024"}, "name": "Prime Movies", "type": "movie"},
        {"slug": "apple-series", "tmdb_params": {"with_networks": "2552"}, "name": "Apple TV+ Series", "type": "series"},
        {"slug": "apple-movies", "tmdb_params": {"with_networks": "2552"}, "name": "Apple TV+ Movies", "type": "movie"},
        {"slug": "stan-series", "tmdb_params": {"with_keywords": "186729"}, "name": "Stan Series", "type": "series"},
        {"slug": "stan-movies", "tmdb_params": {"with_keywords": "186729"}, "name": "Stan Movies", "type": "movie"},

        # General Categories
        {"slug": "trending-series", "special": "trending", "name": "Trending Series", "type": "series"},
        {"slug": "trending-movies", "special": "trending", "name": "Trending Movies", "type": "movie"},
        {"slug": "popular-series", "special": "popular", "name": "Popular Series", "type": "series"},
        {"slug": "popular-movies", "special": "popular", "name": "Popular Movies", "type": "movie"},
        {"slug": "cinema", "special": "now_playing", "name": "In Cinemas", "type": "movie"},
        {"slug": "newreleases", "special": "airing_today", "name": "New Releases", "type": "series"},

        # Genres
        {"slug": "action-series", "tmdb_params": {"with_genres": "10759"}, "name": "Action Series", "type": "series"},
        {"slug": "action-movies", "tmdb_params": {"with_genres": "28"}, "name": "Action Movies", "type": "movie"},
        {"slug": "comedy-series", "tmdb_params": {"with_genres": "35"}, "name": "Comedy Series", "type": "series"},
        {"slug": "comedy-movies", "tmdb_params": {"with_genres": "35"}, "name": "Comedy Movies", "type": "movie"},
        {"slug": "family-series", "tmdb_params": {"with_genres": "10751"}, "name": "Family Series", "type": "series"},
        {"slug": "family-movies", "tmdb_params": {"with_genres": "10751"}, "name": "Family Movies", "type": "movie"},
        {"slug": "horror-series", "tmdb_params": {"with_genres": "27"}, "name": "Horror Series", "type": "series"},
        {"slug": "horror-movies", "tmdb_params": {"with_genres": "27"}, "name": "Horror Movies", "type": "movie"},
        {"slug": "kids-series", "tmdb_params": {"with_genres": "10762"}, "name": "Kids Series", "type": "series"},
        {"slug": "kids-movies", "tmdb_params": {"with_genres": "16"}, "name": "Kids Movies", "type": "movie"},
        {"slug": "thriller-series", "tmdb_params": {"with_genres": "53"}, "name": "Thriller Series", "type": "series"},
        {"slug": "thriller-movies", "tmdb_params": {"with_genres": "53"}, "name": "Thriller Movies", "type": "movie"},
        {"slug": "romance-series", "tmdb_params": {"with_genres": "10749"}, "name": "Romance Series", "type": "series"},
        {"slug": "romance-movies", "tmdb_params": {"with_genres": "10749"}, "name": "Romance Movies", "type": "movie"},
        {"slug": "adventure-series", "tmdb_params": {"with_genres": "12"}, "name": "Adventure Series", "type": "series"},
        {"slug": "adventure-movies", "tmdb_params": {"with_genres": "12"}, "name": "Adventure Movies", "type": "movie"}
    ]
