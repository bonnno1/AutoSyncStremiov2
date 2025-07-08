import requests
import os
import json

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE = "https://api.themoviedb.org/3"

HEADERS = {"accept": "application/json"}


def fetch_tmdb(url, params={}):
    params["api_key"] = TMDB_API_KEY
    params.setdefault("region", "AU")       # 🇦🇺 Australian availability
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


def fetch_imdb_id(tmdb_id, media_type):
    url = f"/{media_type}/{tmdb_id}/external_ids"
    params = {"api_key": TMDB_API_KEY}
    print(f"🔍 Fetching IMDb ID for TMDb ID {tmdb_id} ({media_type})")

    res = requests.get(f"{TMDB_BASE}{url}", params=params, headers=HEADERS)
    try:
        data = res.json()
        print(f"📨 IMDb Response: {json.dumps(data, indent=2)}")
        return data.get("imdb_id")
    except ValueError:
        print(f"❌ Invalid JSON when fetching IMDb ID for {tmdb_id}")
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
            "type": media_type
        })
    return formatted


def save_json(slug, data):
    os.makedirs("catalogs", exist_ok=True)
    with open(f"catalogs/{slug}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        print(f"✅ Saved {len(data)} items to catalogs/{slug}.json")


# Example usage for a single list (repeat for each category in your full script)
if __name__ == "__main__":
    # Netflix series
    netflix_series = fetch_tmdb("/discover/tv", {
        "with_networks": "213",
        "sort_by": "vote_average.desc",
        "vote_count.gte": 50
    })
    formatted_series = to_json_format(netflix_series, media_type="series")
    save_json("netflix-series", formatted_series)

    # Netflix movies
    netflix_movies = fetch_tmdb("/discover/movie", {
        "with_watch_providers": "8",  # Netflix
        "watch_region": "AU",
        "sort_by": "vote_average.desc",
        "vote_count.gte": 50
    })
    formatted_movies = to_json_format(netflix_movies, media_type="movie")
    save_json("netflix-movie", formatted_movies)

    # Repeat above for each streaming service, genre, etc.
