#!/usr/bin/env python3
import json
import re
import sys
from urllib.request import urlopen

JSON_PATH = "../current_versions.json"
WORDPRESS_RELEASES_URL = "https://wordpress.org/download/releases/"


def get_latest_wordpress_version():
    try:
        with urlopen(WORDPRESS_RELEASES_URL) as response:
            html = response.read().decode("utf-8")
        # Look for the first .zip or .tar.gz release link (e.g., wordpress-6.8.2.zip)
        match = re.search(r"wordpress-(\d+\.\d+\.\d+)\.(zip|tar\.gz)", html)
        if match:
            print(f"Found WordPress version: {match.group(1)}")
            return match.group(1)
    except Exception as e:
        print(f"Error fetching WordPress version: {e}", file=sys.stderr)
    return None


def update_json_with_wordpress_version(new_version):
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        current = data["software"]["wordpress"]["latest"]
        if current == new_version:
            print(f"WordPress version is already up to date: {current}")
            return False
        data["software"]["wordpress"]["latest"] = new_version
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent="\t")
        print(f"Updated WordPress version to {new_version}")
        return True
    except Exception as e:
        print(f"Error updating JSON: {e}", file=sys.stderr)
        return False


def main():
    new_version = get_latest_wordpress_version()
    if not new_version:
        print("Could not determine latest WordPress version.", file=sys.stderr)
        sys.exit(1)
    update_json_with_wordpress_version(new_version)


if __name__ == "__main__":
    main()
