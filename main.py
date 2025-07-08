from sync_lists import get_category_list, fetch_shows_for_list
import os
import json

def main():
    output_folder = "catalogs"
    os.makedirs(output_folder, exist_ok=True)

    for category in get_category_list():
        slug = category["slug"]
        name = category.get("name", slug)
        print(f"Fetching: {name}")

        try:
            items = fetch_shows_for_list(category)
            out_path = os.path.join(output_folder, f"{slug}.json")

            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(items, f, indent=2, ensure_ascii=False)

            print(f"✅ Saved {len(items)} items to {out_path}")
        except Exception as e:
            print(f"❌ Failed to process {slug}: {e}")

if __name__ == "__main__":
    main()
