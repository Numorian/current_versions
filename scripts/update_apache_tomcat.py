#!/usr/bin/env python3
import json
import re
import sys
from collections import OrderedDict
from urllib.request import urlopen

JSON_PATH = "../current_versions.json"
TOMCAT_NEWS_URL = "https://tomcat.apache.org/"

# Regex to match Tomcat release news headers, e.g. <h3 id="Tomcat_9.0.107_Released"> ... Tomcat 9.0.107 Released</h3>
TOMCAT_RELEASE_RE = re.compile(
    r'<h3 id="Tomcat_(\d+\.\d+\.\d+)_Released">.*?Tomcat (\d+\.\d+\.\d+) Released',
    re.DOTALL,
)

# Map series to their upgrade path (10.0 -> 10.1)
SERIES_UPGRADE = {"10.0": "10.1"}


def get_tomcat_versions():
    try:
        with urlopen(TOMCAT_NEWS_URL) as response:
            html = response.read().decode("utf-8")
        # Find all Tomcat release headers
        matches = TOMCAT_RELEASE_RE.findall(html)
        # OrderedDict to preserve order (first occurrence per series)
        versions = OrderedDict()
        all_versions = []
        for full, _ in matches:
            major_minor = ".".join(full.split(".")[:2])
            if major_minor not in versions:
                versions[major_minor] = full
            all_versions.append(tuple(map(int, full.split("."))))
        # Find the highest version for 'latest'
        if all_versions:
            highest = max(all_versions)
            latest = ".".join(str(x) for x in highest)
        else:
            latest = None
        return latest, versions
    except Exception as e:
        print(f"Error fetching Tomcat versions: {e}", file=sys.stderr)
        return None, {}


def update_json_with_tomcat_versions(latest, series_versions):
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        tomcat_data = data["software"].get("apache_tomcat", {})
        updated = False
        # Update latest
        if tomcat_data.get("latest") != latest:
            tomcat_data["latest"] = latest
            updated = True
        # Update or add series
        for series, version in series_versions.items():
            if tomcat_data.get(series) != version:
                tomcat_data[series] = version
                updated = True
        # Special handling: always set 10.0 to latest 10.1 version if 10.1 exists
        if "10.1" in series_versions:
            if tomcat_data.get("10.0") != series_versions["10.1"]:
                tomcat_data["10.0"] = series_versions["10.1"]
                updated = True
        # Remove series that are no longer present, except for 10.0 (which is synthetic)
        for key in list(tomcat_data.keys()):
            if key not in ["latest"] + list(series_versions.keys()) + ["10.0"]:
                del tomcat_data[key]
                updated = True
        data["software"]["apache_tomcat"] = tomcat_data
        if updated:
            with open(JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            print(f"Updated Tomcat versions: latest={latest}, series={series_versions}")
        else:
            print("Tomcat versions are already up to date.")
        return updated
    except Exception as e:
        print(f"Error updating JSON: {e}", file=sys.stderr)
        return False


def main():
    latest, series_versions = get_tomcat_versions()
    if not latest or not series_versions:
        print("Could not determine Tomcat versions.", file=sys.stderr)
        sys.exit(1)
    update_json_with_tomcat_versions(latest, series_versions)


if __name__ == "__main__":
    main()
