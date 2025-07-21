#!/usr/bin/env python3
import json
import re
import sys
from urllib.request import urlopen

JSON_PATH = "../current_versions.json"
NGINX_DOWNLOAD_URL = "https://nginx.org/en/download.html"


def get_latest_nginx_version():
    try:
        with urlopen(NGINX_DOWNLOAD_URL) as response:
            html = response.read().decode("utf-8")

        # Look for the first stable release tarball (e.g., nginx-1.29.0.tar.gz)
        match = re.search(r"nginx-(\d+\.\d+\.\d+)\.tar\.gz", html)

        if match:
            print(f"Found nginx version: {match.group(1)}")

            return match.group(1)
    except Exception as e:
        print(f"Error fetching nginx version: {e}", file=sys.stderr)

    return None


def update_json_with_nginx_version(new_version):
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        current = data["software"]["nginx"]["latest"]

        if current == new_version:
            print(f"nginx version is already up to date: {current}")
            return False

        data["software"]["nginx"]["latest"] = new_version

        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        print(f"Updated nginx version to {new_version}")

        return True
    except Exception as e:
        print(f"Error updating JSON: {e}", file=sys.stderr)

        return False


def main():
    new_version = get_latest_nginx_version()

    if not new_version:
        print("Could not determine latest nginx version.", file=sys.stderr)
        sys.exit(1)

    update_json_with_nginx_version(new_version)


if __name__ == "__main__":
    main()
