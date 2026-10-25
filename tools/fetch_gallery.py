# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Sikh Manuscript Revival contributors
"""
Download the images listed in site/data/gallery.json from Wikimedia Commons
into gallery/<category>/, and record their licence, author, date and source
page back into gallery.json.

    python tools/fetch_gallery.py            # fetch anything not yet downloaded
    python tools/fetch_gallery.py --refresh  # re-check licences for every item

How it works (deliberately light on Wikimedia's servers):
  * licence, author and date come from the file page's raw wikitext
    (index.php?action=raw). It is cheap and is not subject to the API's rate limit for busy IPs.
  * the image itself is a standard-width thumbnail from upload.wikimedia.org
    (Wikimedia only serves certain widths; 960 px is one of them).
  * requests are spaced out, HTTP 429/5xx are retried honouring Retry-After,
    and gallery.json is saved after every image, so it is safe to stop and re-run.

Only public-domain and Creative Commons (CC0, BY, BY-SA) files are downloaded.
Anything else is left as a remote link and listed for a person to review.

Standard library only.
"""
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import strip_metadata  # noqa: E402  (sibling script)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOGUE = os.path.join(ROOT, "site", "data", "gallery.json")
GALLERY = os.path.join(ROOT, "gallery")
WIDTH = 960           # a standard Wikimedia thumbnail width
PAUSE = 3.0           # seconds between requests
MAX_BYTES = 15 * 1024 * 1024   # refuse anything larger than this
ALLOWED_HOSTS = {"commons.wikimedia.org", "upload.wikimedia.org"}
SAFE_ID = re.compile(r"^[a-z0-9-]{1,64}$")
MAGIC = {".jpg": b"\xff\xd8\xff", ".jpeg": b"\xff\xd8\xff", ".png": b"\x89PNG\r\n\x1a\n"}
UA = "SikhiSoul-gallery/1.2 (https://github.com/arvinderss/sikhisoul; heritage archive)"

# Licence templates we accept, matched against the wikitext.
FREE = [
    (re.compile(r"\{\{\s*(PD-[\w-]+)", re.I), None),
    (re.compile(r"\{\{\s*(CC-zero|CC0)", re.I), "CC0"),
    (re.compile(r"(cc-by-sa-[\d.]+(?:-[\w,-]+)?)", re.I), None),
    (re.compile(r"(cc-by-[\d.]+(?:-[\w,-]+)?)", re.I), None),
]
NON_FREE = re.compile(r"\{\{\s*(non-free|fair use|copyvio|delete|nld)", re.I)


def get(url, tries=6):
    """GET with polite retries on 429/5xx, honouring Retry-After."""
    if urllib.parse.urlsplit(url).scheme != "https" or urllib.parse.urlsplit(url).hostname not in ALLOWED_HOSTS:
        raise ValueError(f"refusing to fetch from outside Wikimedia: {url}")
    wait = 10
    for attempt in range(tries):
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                # Redirects must also stay on Wikimedia, and the size is capped.
                if urllib.parse.urlsplit(r.geturl()).hostname not in ALLOWED_HOSTS:
                    raise ValueError(f"redirected outside Wikimedia: {r.geturl()}")
                data = r.read(MAX_BYTES + 1)
                if len(data) > MAX_BYTES:
                    raise ValueError(f"file larger than {MAX_BYTES // 2**20} MB: {url}")
                return data
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504) or attempt == tries - 1:
                raise
            wait = max(int(e.headers.get("Retry-After") or 0), wait)
            print(f"    busy ({e.code}); waiting {wait}s", flush=True)
            time.sleep(wait)
            wait = min(wait * 2, 180)


def canonical(name):
    """Commons file name as used in URLs: spaces -> underscores, first letter upper-case."""
    name = name.strip().replace(" ", "_")
    return name[:1].upper() + name[1:]


def thumb_url(name, width=WIDTH):
    n = canonical(name)
    h = hashlib.md5(n.encode("utf-8")).hexdigest()
    q = urllib.parse.quote(n)
    url = f"https://upload.wikimedia.org/wikipedia/commons/thumb/{h[0]}/{h[:2]}/{q}/{width}px-{q}"
    if n.lower().endswith((".tif", ".tiff", ".pdf")):
        url += ".jpg"
    return url


def original_url(name):
    n = canonical(name)
    h = hashlib.md5(n.encode("utf-8")).hexdigest()
    return f"https://upload.wikimedia.org/wikipedia/commons/{h[0]}/{h[:2]}/{urllib.parse.quote(n)}"


def field(wikitext, key):
    m = re.search(r"\|\s*" + key + r"\s*=\s*(.*?)(?=\n\s*\||\n\}\})", wikitext, re.S | re.I)
    if not m:
        return ""
    text = re.sub(r"\{\{\s*(?:en|pa)\s*\|\s*(?:1=)?", "", m.group(1))
    text = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", text)      # [[link|label]] -> label
    text = re.sub(r"\[https?://\S+\s*([^\]]*)\]", r"\1", text)           # [url label] -> label
    text = re.sub(r"\{\{|\}\}|'''|''|<[^>]+>", "", text)
    return " ".join(text.split())[:200]


def licence_of(wikitext):
    if NON_FREE.search(wikitext):
        return ""
    found = []
    for rx, label in FREE:
        for m in rx.finditer(wikitext):
            lic = label or m.group(1)
            if lic.upper() not in (f.upper() for f in found):
                found.append(lic)
    return ", ".join(found)


def save(cat):
    with open(CATALOGUE, "w", encoding="utf-8") as fh:
        json.dump(cat, fh, ensure_ascii=False, indent=2)


def main():
    refresh = "--refresh" in sys.argv
    cat = json.load(open(CATALOGUE, encoding="utf-8"))
    review = []
    for item in cat["items"]:
        if item.get("local") and not refresh:
            continue
        if not SAFE_ID.match(item.get("id", "")) or item.get("category") not in cat["categories"]:
            print(f"  skipped (id must be a-z, 0-9 and '-', category must be known): {item.get('id')!r}", flush=True)
            review.append(str(item.get("id"))); continue
        name = canonical(item["commons"])
        raw_url = "https://commons.wikimedia.org/w/index.php?" + urllib.parse.urlencode({"title": "File:" + name, "action": "raw"})
        try:
            wikitext = get(raw_url).decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            print(f"  not found ({e.code}): {item['commons']}", flush=True)
            review.append(item["id"]); continue
        time.sleep(PAUSE)

        licence = licence_of(wikitext)
        item["licence"] = licence
        item["author"] = field(wikitext, "author")
        item["date"] = field(wikitext, "date")
        item["source_page"] = "https://commons.wikimedia.org/wiki/File:" + urllib.parse.quote(name)
        if not licence:
            print(f"  review needed (no free licence found): {item['id']}", flush=True)
            review.append(item["id"]); save(cat); continue

        if not (item.get("local") and not refresh):
            try:
                data = get(thumb_url(name))
                ext = ".jpg" if name.lower().endswith((".tif", ".tiff", ".pdf")) else os.path.splitext(name)[1].lower()
            except urllib.error.HTTPError:
                # Image narrower than the thumbnail width: take the original instead.
                data = get(original_url(name))
                ext = os.path.splitext(name)[1].lower()
            if ext not in MAGIC or not data.startswith(MAGIC[ext]):
                print(f"  review needed (not a real JPEG/PNG): {item['id']}", flush=True)
                review.append(item["id"]); save(cat); continue
            folder = os.path.join(GALLERY, item["category"])
            os.makedirs(folder, exist_ok=True)
            dest = os.path.join(folder, item["id"] + ext)
            with open(dest, "wb") as fh:
                fh.write(data)
            strip_metadata.strip(Path(dest))   # drop EXIF/XMP/GPS; the picture itself is unchanged
            item["local"] = os.path.relpath(dest, ROOT).replace(os.sep, "/")
        save(cat)
        print(f"  ok  {item['local']}  [{licence}]", flush=True)
        time.sleep(PAUSE)
    save(cat)
    print(f"done; {len(review)} item(s) need review: {', '.join(review) or '-'}", flush=True)


if __name__ == "__main__":
    main()
