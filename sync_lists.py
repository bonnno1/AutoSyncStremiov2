import requests
import os
import json

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE = "https://api.themoviedb.org/3"
HEADERS = {"accept": "application/json"}

def fetch_tmdb(url, params={}, pages=5):
    all_results = []
    for page in range(1, pages + 1):
        params["page"] = page
        params["api_key"] = TMDB_API_KEY
        params.setdefault("region", "AU")
        params.setdefault("language", "en-AU")

        print(f"🔍 Fetching: {url} | Page: {page} | Params: {params}")
        res = requests.get(f"{TMDB_BASE}{url}", params=params, headers=HEADERS)

        try:
            data = res.json()
        except ValueError:
            print(f"❌ Invalid JSON from TMDb at {url}")
            continue

        if res.status_code != 200 or "results" not in data:
            print(f"⚠️ Error or no 'results' in TMDb response for {url}")
            continue

        all_results.extend(data["results"])
    return all_results

def fetch_imdb_id(tmdb_id, content_type="tv"):
    url = f"/{content_type}/{tmdb_id}/external_ids"
    print(f"🔍 Fetching IMDb ID for TMDb ID {tmdb_id}")
    res = requests.get(f"{TMDB_BASE}{url}", params={"api_key": TMDB_API_KEY}, headers=HEADERS)

    try:
        data = res.json()
        return data.get("imdb_id")
    except ValueError:
        print(f"❌ Invalid JSON when fetching IMDb ID for {tmdb_id}")
        return None

def to_json_format(results, content_type):
    formatted = []
    for item in results:
        imdb_id = fetch_imdb_id(item["id"], content_type)
        if not imdb_id:
            print(f"⚠️ No IMDb ID for TMDb ID {item['id']} — skipping.")
            continue
        formatted.append({
            "title": item.get("name") or item.get("title"),
            "imdb_id": imdb_id
        })
    return formatted

def fetch_items_for_list(list_def):
    if list_def.get("special") == "trending":
        return to_json_format(fetch_tmdb("/trending/tv/week"), "tv")
    if list_def.get("special") == "popular":
        return to_json_format(fetch_tmdb("/tv/popular"), "tv")
    if list_def.get("special") == "now_playing":
        return to_json_format(fetch_tmdb("/movie/now_playing"), "movie")
    if list_def.get("special") == "airing_today":
        return to_json_format(fetch_tmdb("/tv/airing_today"), "tv")

    content_type = list_def.get("type", "tv")
    return to_json_format(fetch_tmdb(f"/discover/{content_type}", list_def["tmdb_params"]), content_type)

def get_category_list():
    return [
        # Streaming services
        {"slug": "netflix-series", "tmdb_params": {"with_networks": "213", "sort_by": "vote_average.desc"}, "name": "Netflix Series", "type": "tv"},
        {"slug": "netflix-movies", "tmdb_params": {"with_networks": "213", "sort_by": "vote_average.desc"}, "name": "Netflix Movies", "type": "movie"},
        {"slug": "disney-series", "tmdb_params": {"with_networks": "2739", "sort_by": "vote_average.desc"}, "name": "Disney+ Series", "type": "tv"},
        {"slug": "disney-movies", "tmdb_params": {"with_networks": "2739", "sort_by": "vote_average.desc"}, "name": "Disney+ Movies", "type": "movie"},
        {"slug": "prime-series", "tmdb_params": {"with_networks": "1024", "sort_by": "vote_average.desc"}, "name": "Prime Video Series", "type": "tv"},
        {"slug": "prime-movies", "tmdb_params": {"with_networks": "1024", "sort_by": "vote_average.desc"}, "name": "Prime Video Movies", "type": "movie"},
        {"slug": "apple-series", "tmdb_params": {"with_networks": "2552", "sort_by": "vote_average.desc"}, "name": "Apple TV+ Series", "type": "tv"},
        {"slug": "apple-movies", "tmdb_params": {"with_networks": "2552", "sort_by": "vote_average.desc"}, "name": "Apple TV+ Movies", "type": "movie"},
        {"slug": "stan-series", "tmdb_params": {"with_keywords": "186729", "sort_by": "vote_average.desc"}, "name": "Stan Series", "type": "tv"},
        {"slug": "stan-movies", "tmdb_params": {"with_keywords": "186729", "sort_by": "vote_average.desc"}, "name": "Stan Movies", "type": "movie"},

        # Specials
        {"slug": "trending", "tmdb_params": {}, "special": "trending", "name": "Trending Shows"},
        {"slug": "popular", "tmdb_params": {}, "special": "popular", "name": "Popular Shows"},
        {"slug": "cinema", "tmdb_params": {}, "special": "now_playing", "name": "In Cinemas"},
        {"slug": "newreleases", "tmdb_params": {}, "special": "airing_today", "name": "New Releases"},

        # Genres (TV + Movies)
        {"slug": "action-series", "tmdb_params": {"with_genres": "10759", "sort_by": "vote_average.desc"}, "name": "Action Series", "type": "tv"},
        {"slug": "action-movies", "tmdb_params": {"with_genres": "28", "sort_by": "vote_average.desc"}, "name": "Action Movies", "type": "movie"},
        {"slug": "comedy-series", "tmdb_params": {"with_genres": "35", "sort_by": "vote_average.desc"}, "name": "Comedy Series", "type": "tv"},
        {"slug": "comedy-movies", "tmdb_params": {"with_genres": "35", "sort_by": "vote_average.desc"}, "name": "Comedy Movies", "type": "movie"},
        {"slug": "family-series", "tmdb_params": {"with_genres": "10751", "sort_by": "vote_average.desc"}, "name": "Family Series", "type": "tv"},
        {"slug": "family-movies", "tmdb_params": {"with_genres": "10751", "sort_by": "vote_average.desc"}, "name": "Family Movies", "type": "movie"},
        {"slug": "horror-series", "tmdb_params": {"with_genres": "27", "sort_by": "vote_average.desc"}, "name": "Horror Series", "type": "tv"},
        {"slug": "horror-movies", "tmdb_params": {"with_genres": "27", "sort_by": "vote_average.desc"}, "name": "Horror Movies", "type": "movie"},
        {"slug": "romance-series", "tmdb_params": {"with_genres": "10749", "sort_by": "vote_average.desc"}, "name": "Romance Series", "type": "tv"},
        {"slug": "romance-movies", "tmdb_params": {"with_genres": "10749", "sort_by": "vote_average.desc"}, "name": "Romance Movies", "type": "movie"},
        {"slug": "thriller-series", "tmdb_params": {"with_genres": "53", "sort_by": "vote_average.desc"}, "name": "Thriller Series", "type": "tv"},
        {"slug": "thriller-movies", "tmdb_params": {"with_genres": "53", "sort_by": "vote_average.desc"}, "name": "Thriller Movies", "type": "movie"},
        {"slug": "adventure-series", "tmdb_params": {"with_genres": "12", "sort_by": "vote_average.desc"}, "name": "Adventure Series", "type": "tv"},
        {"slug": "adventure-movies", "tmdb_params": {"with_genres": "12", "sort_by": "vote_average.desc"}, "name": "Adventure Movies", "type": "movie"},
    ]
