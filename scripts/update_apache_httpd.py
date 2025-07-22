#!/usr/bin/env python3
import json
import re
import sys
from urllib.request import urlopen

JSON_PATH = "../current_versions.json"
APACHE_HTTPD_DOWNLOAD_URL = "https://httpd.apache.org/download.cgi"


def get_latest_apache_httpd_version():
    try:
        with urlopen(APACHE_HTTPD_DOWNLOAD_URL) as response:
            html = response.read().decode("utf-8")
        # Look for the first httpd-X.Y.Z.tar.gz link
        match = re.search(r"httpd-(\d+\.\d+\.\d+)\.tar\.gz", html)
        if match:
            print(f"Found Apache HTTPD version: {match.group(1)}")
            return match.group(1)
    except Exception as e:
        print(f"Error fetching Apache HTTPD version: {e}", file=sys.stderr)
    return None


def update_json_with_apache_httpd_version(new_version):
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        current = data["software"]["apache_httpd"]["latest"]
        if current == new_version:
            print(f"Apache HTTPD version is already up to date: {current}")
            return False
        data["software"]["apache_httpd"]["latest"] = new_version
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent="\t")
        print(f"Updated Apache HTTPD version to {new_version}")
        return True
    except Exception as e:
        print(f"Error updating JSON: {e}", file=sys.stderr)
        return False


def main():
    new_version = get_latest_apache_httpd_version()
    if not new_version:
        print("Could not determine latest Apache HTTPD version.", file=sys.stderr)
        sys.exit(1)
    update_json_with_apache_httpd_version(new_version)


if __name__ == "__main__":
    main()
