# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Sikh Manuscript Revival contributors
"""
Download the images listed in site/data/gallery.json from Wikimedia Commons
into gallery/<category>/, and record their licence, author, date and source
page back into gallery.json.

    python tools/fetch_gallery.py            # fetch anything not yet downloaded
    python tools/fetch_gallery.py --refresh  # re-check licences for every item

Only images whose Commons licence is public domain or a Creative Commons
licence are downloaded. Anything else is left as a remote link and reported,
so a person can review it before it is added.

Wikimedia rate-limits busy clients, so this script asks for all metadata in
batches of 50, waits between downloads, retries politely on HTTP 429, and
saves gallery.json after every image (safe to stop and re-run).

Needs network access to commons.wikimedia.org and upload.wikimedia.org.
Standard library only.
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOGUE = os.path.join(ROOT, "site", "data", "gallery.json")
GALLERY = os.path.join(ROOT, "gallery")
API = "https://commons.wikimedia.org/w/api.php"
WIDTH = 1200          # pixel width of the copy we keep
PAUSE = 2.0           # seconds between downloads
UA = "SikhiSoul-gallery/1.1 (https://github.com/arvinderss/sikhisoul; heritage archive)"

ALLOWED = re.compile(r"^(public domain|pd|cc0|cc[- ]by(-sa)?[- ]\d)", re.I)


def strip_html(s):
    return re.sub(r"<[^>]+>", "", s or "").strip()


def get(url, tries=6):
    """GET with polite retries on 429/5xx, honouring Retry-After."""
    wait = 5
    for attempt in range(tries):
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504) or attempt == tries - 1:
                raise
            wait = int(e.headers.get("Retry-After") or wait)
            print(f"    busy ({e.code}); waiting {wait}s")
            time.sleep(wait)
            wait = min(wait * 2, 120)


def fetch_metadata(titles):
    """title -> imageinfo dict, asking Commons for up to 50 titles at a time."""
    out = {}
    for i in range(0, len(titles), 50):
        chunk = titles[i:i + 50]
        params = {
            "action": "query", "format": "json", "formatversion": "2",
            "titles": "|".join("File:" + t for t in chunk),
            "prop": "imageinfo", "iiprop": "url|extmetadata|mime", "iiurlwidth": str(WIDTH),
        }
        data = json.loads(get(API + "?" + urllib.parse.urlencode(params)))
        # Commons normalises titles (e.g. underscores); map back to what we asked for.
        norm = {n["to"]: n["from"] for n in data["query"].get("normalized", [])}
        for page in data["query"]["pages"]:
            asked = norm.get(page["title"], page["title"])[len("File:"):]
            if page.get("imageinfo"):
                out[asked] = page["imageinfo"][0]
        time.sleep(PAUSE)
    return out


def save(cat):
    with open(CATALOGUE, "w", encoding="utf-8") as fh:
        json.dump(cat, fh, ensure_ascii=False, indent=2)


def main():
    refresh = "--refresh" in sys.argv
    cat = json.load(open(CATALOGUE, encoding="utf-8"))
    todo = [it for it in cat["items"] if refresh or not it.get("local")]
    meta = fetch_metadata([it["commons"] for it in todo])
    review = []
    for item in todo:
        info = meta.get(item["commons"])
        if not info:
            print(f"  not found on Commons: {item['commons']}")
            review.append(item["id"]); continue
        em = info.get("extmetadata", {})
        licence = strip_html(em.get("LicenseShortName", {}).get("value", ""))
        item["licence"] = licence
        item["author"] = strip_html(em.get("Artist", {}).get("value", ""))[:200]
        item["date"] = strip_html(em.get("DateTimeOriginal", {}).get("value", ""))[:80]
        item["source_page"] = info.get("descriptionurl", "")
        if not ALLOWED.match(licence):
            print(f"  review needed ({licence or 'no licence'}): {item['id']}")
            review.append(item["id"]); save(cat); continue
        if item.get("local") and not refresh:
            continue
        thumb = info.get("thumburl") or info["url"]
        ext = os.path.splitext(urllib.parse.urlparse(thumb).path)[1].lower() or ".jpg"
        folder = os.path.join(GALLERY, item["category"])
        os.makedirs(folder, exist_ok=True)
        dest = os.path.join(folder, item["id"] + ext)
        with open(dest, "wb") as fh:
            fh.write(get(thumb))
        item["local"] = os.path.relpath(dest, ROOT).replace(os.sep, "/")
        save(cat)
        print(f"  ok  {item['local']}  [{licence}]")
        time.sleep(PAUSE)
    save(cat)
    print(f"done; {len(review)} item(s) need review: {', '.join(review) or '-'}")


if __name__ == "__main__":
    main()
