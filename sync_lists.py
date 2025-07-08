import requests
import os
import json

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE = "https://api.themoviedb.org/3"
HEADERS = {"accept": "application/json"}

def fetch_tmdb(endpoint, params={}):
    params["api_key"] = TMDB_API_KEY
    params.setdefault("region", "AU")
    params.setdefault("language", "en-AU")
    params.setdefault("sort_by", "vote_average.desc")
    params.setdefault("vote_count.gte", 50)
    params.setdefault("page", 1)

    print(f"🔍 Fetching: {endpoint} | Params: {params}")
    res = requests.get(f"{TMDB_BASE}{endpoint}", params=params, headers=HEADERS)

    try:
        data = res.json()
    except ValueError:
        print(f"❌ Invalid JSON from TMDb at {endpoint}")
        return []

    if res.status_code != 200 or "results" not in data:
        print(f"⚠️ TMDb error {res.status_code} or no 'results' in response")
        return []

    return data["results"][:100]  # Limit to top 100 results

def fetch_imdb_id(item_id, is_movie):
    endpoint = f"/movie/{item_id}/external_ids" if is_movie else f"/tv/{item_id}/external_ids"
    res = requests.get(f"{TMDB_BASE}{endpoint}", params={"api_key": TMDB_API_KEY}, headers=HEADERS)
    try:
        data = res.json()
        return data.get("imdb_id")
    except ValueError:
        return None

def to_json_format(items, is_movie):
    result = []
    for item in items:
        imdb_id = fetch_imdb_id(item["id"], is_movie)
        if not imdb_id:
            print(f"⚠️ No IMDb ID for TMDb ID {item['id']} — skipping.")
            continue
        result.append({
            "title": item.get("title") if is_movie else item.get("name"),
            "imdb_id": imdb_id
        })
    return result

def save_catalog(slug, items, type_label):
    if not items:
        print(f"⚠️ No data to save for {slug}-{type_label}")
        return
    filename = f"catalogs/{slug}-{type_label}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)
    print(f"✅ Saved {len(items)} items to {filename}")

def get_categories():
    # Each entry: slug, TMDB params (genre/network/keyword), display name
    return [
        {"slug": "netflix", "params": {"with_networks": "213"}, "name": "Netflix"},
        {"slug": "disney", "params": {"with_networks": "2739"}, "name": "Disney+"},
        {"slug": "prime", "params": {"with_networks": "1024"}, "name": "Prime Video"},
        {"slug": "apple", "params": {"with_networks": "2552"}, "name": "Apple TV+"},
        {"slug": "stan", "params": {"with_keywords": "186729"}, "name": "Stan"},
        {"slug": "trending", "special": "trending", "name": "Trending"},
        {"slug": "popular", "special": "popular", "name": "Popular"},
        {"slug": "cinema", "special": "now_playing", "name": "In Cinemas"},
        {"slug": "newreleases", "special": "airing_today", "name": "New Releases"},
        {"slug": "action", "params": {"with_genres": "28"}, "name": "Action"},
        {"slug": "comedy", "params": {"with_genres": "35"}, "name": "Comedy"},
        {"slug": "family", "params": {"with_genres": "10751"}, "name": "Family"},
        {"slug": "horror", "params": {"with_genres": "27"}, "name": "Horror"},
        {"slug": "kids", "params": {"with_genres": "16"}, "name": "Kids"},
        {"slug": "thriller", "params": {"with_genres": "53"}, "name": "Thriller"},
        {"slug": "romance", "params": {"with_genres": "10749"}, "name": "Romance"},
        {"slug": "adventure", "params": {"with_genres": "12"}, "name": "Adventure"},
    ]

def fetch_shows_and_movies():
    categories = get_categories()
    for cat in categories:
        slug = cat["slug"]

        # Special categories (no movies equivalent)
        if cat.get("special") == "trending":
            tv_items = fetch_tmdb("/trending/tv/week")
            save_catalog(slug, to_json_format(tv_items, is_movie=False), "series")
            continue
        elif cat.get("special") == "popular":
            tv_items = fetch_tmdb("/tv/popular")
            save_catalog(slug, to_json_format(tv_items, is_movie=False), "series")
            continue
        elif cat.get("special") == "now_playing":
            movie_items = fetch_tmdb("/movie/now_playing")
            save_catalog(slug, to_json_format(movie_items, is_movie=True), "movies")
            continue
        elif cat.get("special") == "airing_today":
            tv_items = fetch_tmdb("/tv/airing_today")
            save_catalog(slug, to_json_format(tv_items, is_movie=False), "series")
            continue

        # Regular genre/network/keyword-based categories
        tv_params = dict(cat["params"])
        movie_params = dict(cat["params"])

        tv_items = fetch_tmdb("/discover/tv", tv_params)
        movie_items = fetch_tmdb("/discover/movie", movie_params)

        save_catalog(slug, to_json_format(tv_items, is_movie=False), "series")
        save_catalog(slug, to_json_format(movie_items, is_movie=True), "movies")

# Only runs if executed directly
if __name__ == "__main__":
    fetch_shows_and_movies()
