import os
import json
from sync_lists import get_category_list, fetch_items_for_list

OUTPUT_DIR = "catalogs"

def save_to_file(filename, items):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)
    print(f"✅ Saved {len(items)} items to {path}")

def main():
    categories = get_category_list()
    for category in categories:
        print(f"\n📦 Fetching: {category['name']}")
        try:
            items = fetch_items_for_list(category)
            if not items:
                print(f"⚠️ No data returned for {category['slug']}")
                continue
            filename = f"{category['slug']}.json"
            save_to_file(filename, items)
        except Exception as e:
            print(f"❌ Error processing {category['slug']}: {e}")

if __name__ == "__main__":
    main()
