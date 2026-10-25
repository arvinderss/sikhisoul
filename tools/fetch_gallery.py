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

Needs network access to commons.wikimedia.org and upload.wikimedia.org.
Standard library only.
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOGUE = os.path.join(ROOT, "site", "data", "gallery.json")
GALLERY = os.path.join(ROOT, "gallery")
API = "https://commons.wikimedia.org/w/api.php"
WIDTH = 1200  # pixel width of the copy we keep; large enough for the site and for study
UA = "SikhiSoul-gallery/1.0 (https://github.com/arvinderss/sikhisoul)"

ALLOWED = re.compile(r"^(public domain|pd|cc0|cc[- ]by(-sa)?[- ]\d)", re.I)


def strip_html(s):
    return re.sub(r"<[^>]+>", "", s or "").strip()


def api_info(title):
    params = {
        "action": "query", "format": "json", "titles": "File:" + title,
        "prop": "imageinfo", "iiprop": "url|extmetadata|mime", "iiurlwidth": str(WIDTH),
    }
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(params), headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        pages = json.load(r)["query"]["pages"]
    page = next(iter(pages.values()))
    if "imageinfo" not in page:
        return None
    return page["imageinfo"][0]


def download(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as fh:
        fh.write(r.read())


def main():
    refresh = "--refresh" in sys.argv
    cat = json.load(open(CATALOGUE, encoding="utf-8"))
    skipped = []
    for item in cat["items"]:
        if item.get("local") and not refresh:
            continue
        info = api_info(item["commons"])
        if not info:
            print(f"  not found on Commons: {item['commons']}")
            skipped.append(item["id"]); continue
        meta = info.get("extmetadata", {})
        licence = strip_html(meta.get("LicenseShortName", {}).get("value", ""))
        item["licence"] = licence
        item["author"] = strip_html(meta.get("Artist", {}).get("value", ""))[:200]
        item["date"] = strip_html(meta.get("DateTimeOriginal", {}).get("value", ""))[:80]
        item["source_page"] = info.get("descriptionurl", "")
        if not ALLOWED.match(licence):
            print(f"  review needed ({licence or 'no licence'}): {item['id']}")
            skipped.append(item["id"]); continue
        thumb = info.get("thumburl") or info["url"]
        ext = os.path.splitext(urllib.parse.urlparse(thumb).path)[1].lower() or ".jpg"
        folder = os.path.join(GALLERY, item["category"])
        os.makedirs(folder, exist_ok=True)
        dest = os.path.join(folder, item["id"] + ext)
        download(thumb, dest)
        item["local"] = os.path.relpath(dest, ROOT).replace(os.sep, "/")
        print(f"  ok  {item['local']}  [{licence}]")
        time.sleep(0.5)  # be gentle with Commons
    with open(CATALOGUE, "w", encoding="utf-8") as fh:
        json.dump(cat, fh, ensure_ascii=False, indent=2)
    print(f"done; {len(skipped)} item(s) need review: {', '.join(skipped) or '-'}")


if __name__ == "__main__":
    main()
