#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Security and content-safety checks for the ਸਿੱਖੀ ਸੋਲ repository.

Run from the repository root:
    python tools/security_check.py

It runs on every push, on every pull request and once a week in GitHub Actions
(.github/workflows/security.yml). Each check prints ✓ or ✗, and the script exits
non-zero if any check fails. It needs only Python 3.9+ and Pillow.

What it checks, and why (see SECURITY.md):
  page      the security policy, referrer policy and self-hosted fonts are still in place,
            with no inline scripts, inline styles or event-handler attributes
  script    app.js still validates every URL from the data files and never builds HTML from strings
  svg       no asset can run code or load anything from elsewhere when opened or printed
  data      every gallery and library path points inside this repository, and every image licence is free
  images    files are what their extension says, and carry no hidden EXIF/XMP/GPS metadata
  secrets   no keys, tokens or private keys have been committed
  ci        every GitHub Action is pinned to an exact commit and runs with read-only permissions
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
failures = 0


def check(name, ok, detail=""):
    global failures
    print(("✓ " if ok else "✗ ") + name + ("" if ok or not detail else "  — " + str(detail)))
    if not ok:
        failures += 1


def tracked_files():
    """Files git knows about (so untracked local junk is ignored); falls back to a walk."""
    try:
        out = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True).stdout
        return [ROOT / p for p in out.decode().split("\0") if p]
    except (OSError, subprocess.CalledProcessError):
        return [p for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts and "node_modules" not in p.parts]


FILES = tracked_files()


# ---------------------------------------------------------------- page
def check_page():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    csp = re.search(r'<meta http-equiv="Content-Security-Policy" content="([^"]+)"', html)
    csp = csp.group(1) if csp else ""
    needed = ["default-src 'none'", "script-src 'self'", "style-src 'self'", "font-src 'self'",
              "base-uri 'none'", "form-action 'none'", "object-src 'none'"]
    check("page: Content-Security-Policy is present and strict",
          all(d in csp for d in needed) and "unsafe-" not in csp,
          [d for d in needed if d not in csp] or "contains unsafe-*")
    img_src = re.search(r"img-src ([^;]+)", csp)
    allowed = {"'self'", "https://commons.wikimedia.org", "https://upload.wikimedia.org"}
    check("page: images may come only from this site and Wikimedia Commons",
          bool(img_src) and set(img_src.group(1).split()) <= allowed, img_src and img_src.group(1))
    check("page: referrer policy is no-referrer", '<meta name="referrer" content="no-referrer">' in html)

    inline_scripts = [m for m in re.findall(r"<script\b([^>]*)>(.*?)</script>", html, re.S) if m[1].strip()]
    check("page: no inline scripts", not inline_scripts)
    check("page: no inline style attributes or <style> blocks", not re.search(r"\sstyle\s*=|<style\b", html))
    check("page: no event-handler attributes (onclick= …)", not re.search(r"\son[a-z]+\s*=", html, re.I))
    ext = re.findall(r'<(?:script|link)\b[^>]*(?:src|href)="(https?:)?//[^"]+"', html)
    check("page: no scripts, styles or fonts loaded from other sites", not ext, ext)
    check("page: fonts are self-hosted (no Google Fonts)", "fonts.googleapis" not in html and "fonts.gstatic" not in html)
    blank = re.findall(r'<a\b[^>]*target="_blank"[^>]*>', html)
    check("page: every new-tab link has rel=noopener noreferrer",
          all("noopener" in a and "noreferrer" in a for a in blank), blank)

    fonts = ROOT / "site" / "fonts"
    font_files = list(fonts.glob("*"))
    check("fonts: only .woff2 font files plus their OFL licences",
          font_files and all(f.suffix == ".woff2" or f.name.startswith("OFL") for f in font_files))
    bad = [f.name for f in fonts.glob("*.woff2") if f.read_bytes()[:4] != b"wOF2"]
    check("fonts: every .woff2 really is a WOFF2 file", not bad, bad)
    css = "".join(p.read_text(encoding="utf-8") for p in (ROOT / "site" / "css").glob("*.css"))
    check("css: no @import or url() pointing at another site", not re.search(r"@import|url\(\s*['\"]?(https?:)?//", css))


# ---------------------------------------------------------------- script
def check_script():
    js = (ROOT / "site" / "js" / "app.js").read_text(encoding="utf-8")
    sinks = re.findall(r"\.(?:innerHTML|outerHTML)\s*=|insertAdjacentHTML|document\.write|\beval\s*\(|new Function\s*\(|"
                       r"setTimeout\s*\(\s*['\"]|setInterval\s*\(\s*['\"]", js)
    check("app.js: never builds HTML from strings or runs strings as code", not sinks, sinks)
    for name in ("SAFE_LOCAL_IMAGE", "SAFE_ASSET_PATH", "SAFE_SOURCE_PAGE"):
        check(f"app.js: URL allowlist {name} is defined and used", js.count(name) >= 2)
    check("app.js: el() refuses event-handler attributes", "refusing attribute" in js)
    opens = re.findall(r"window\.open\([^)]*\)", js)
    check("app.js: window.open uses noopener,noreferrer", all("noopener,noreferrer" in o for o in opens), opens)
    rels = re.findall(r'rel:\s*"([^"]*)"', js)
    check("app.js: links it creates use rel=noopener noreferrer",
          all("noopener" in r and "noreferrer" in r for r in rels), rels)


# ---------------------------------------------------------------- svg
SVG_DANGER = [
    (r"<script\b", "<script>"),
    (r"\son[a-z]+\s*=", "event handler"),
    (r"javascript:", "javascript: URL"),
    (r"<foreignObject\b", "<foreignObject>"),
    (r"<!ENTITY|<!DOCTYPE", "DOCTYPE/ENTITY (XXE)"),
    (r"<(?:iframe|embed|object|use)\b[^>]*(?:xlink:)?href\s*=\s*['\"](?!#)", "external <use>/<iframe>/<embed>"),
    (r"(?:xlink:)?href\s*=\s*['\"](?:https?:)?//", "remote href"),
    (r"url\(\s*['\"]?(?:https?:)?//", "remote url()"),
    (r"@import", "@import"),
]


def check_svg():
    svgs = [p for p in FILES if p.suffix.lower() == ".svg"]
    problems = []
    no_spdx = []
    for p in svgs:
        text = p.read_text(encoding="utf-8", errors="replace")
        for pattern, label in SVG_DANGER:
            if re.search(pattern, text, re.I):
                problems.append(f"{p.relative_to(ROOT)}: {label}")
        if p.is_relative_to(ROOT / "assets") and "SPDX-License-Identifier" not in text[:600]:
            no_spdx.append(str(p.relative_to(ROOT)))
    check(f"svg: none of the {len(svgs)} SVGs contain active or remote content", not problems, problems[:5])
    check("svg: every library asset carries its SPDX licence header", not no_spdx, no_spdx[:5])


# ---------------------------------------------------------------- data
# Public domain (PD-*), CC0, CC BY and CC BY-SA, written either as "CC BY-SA 4.0" or as Commons' "cc-by-sa-4.0".
FREE_LICENCE = re.compile(r"^(public domain|pd-[a-z0-9-]+|cc0(-1\.0)?|cc[- ]by(-sa)?[- ][1-4]\.\d)"
                          r"(\s*,\s*(pd-[a-z0-9-]+|cc0(-1\.0)?|cc[- ]by(-sa)?[- ][1-4]\.\d))*$", re.I)


def check_data():
    g = json.loads((ROOT / "site/data/gallery.json").read_text(encoding="utf-8"))
    a = json.loads((ROOT / "site/data/assets.json").read_text(encoding="utf-8"))
    local_re = re.compile(r"gallery/[a-z]+/[a-z0-9-]+\.(jpe?g|png)")
    page_re = re.compile(r"https://commons\.wikimedia\.org/wiki/File:[^\s\"'<>\\]+")
    id_re = re.compile(r"[a-z0-9-]+")

    bad = []
    for it in g["items"]:
        if not id_re.fullmatch(it.get("id", "")):
            bad.append(f"id {it.get('id')!r}")
        if "local" in it and (not local_re.fullmatch(it["local"]) or ".." in it["local"] or not (ROOT / it["local"]).is_file()):
            bad.append(f"{it['id']}: local {it['local']!r}")
        if "source_page" in it and not page_re.fullmatch(it["source_page"]):
            bad.append(f"{it['id']}: source_page")
        if it.get("category") not in g["categories"] or it.get("era") not in g["eras"]:
            bad.append(f"{it['id']}: category/era")
    check("data: gallery paths and links stay inside this site or Wikimedia Commons", not bad, bad[:5])

    unfree = [it["id"] for it in g["items"] if "local" in it and not FREE_LICENCE.match(it.get("licence", ""))]
    check("data: every downloaded gallery image has a free licence recorded", not unfree, unfree)

    asset_re = re.compile(r"assets/[0-9A-Za-z_/-]+(\.[0-9A-Za-z_-]+)*\.svg")
    paths = [it["preview"] for c in a["collections"] for it in c["items"]] + \
            [f["path"] for c in a["collections"] for it in c["items"] for f in it["files"]]
    bad = [p for p in paths if not asset_re.fullmatch(p) or ".." in p or not (ROOT / p).is_file()]
    check(f"data: all {len(paths)} library paths are real files inside assets/", not bad, bad[:5])

    gallery_files = {str(p.relative_to(ROOT)) for p in FILES if p.parts[len(ROOT.parts)] == "gallery"
                     and p.suffix.lower() in (".jpg", ".jpeg", ".png")}
    listed = {it["local"] for it in g["items"] if "local" in it}
    check("data: every image in gallery/ is catalogued (no unreviewed images)",
          gallery_files <= listed, sorted(gallery_files - listed)[:5])


# ---------------------------------------------------------------- images
MAGIC = {".jpg": [b"\xff\xd8\xff"], ".jpeg": [b"\xff\xd8\xff"], ".png": [b"\x89PNG\r\n\x1a\n"],
         ".gif": [b"GIF87a", b"GIF89a"], ".webp": [b"RIFF"], ".pdf": [b"%PDF-"], ".woff2": [b"wOF2"]}
MAX_BYTES = 15 * 1024 * 1024


def check_images():
    try:
        from PIL import Image
    except ImportError:
        check("images: Pillow is installed", False, "pip install pillow")
        return
    rasters = [p for p in FILES if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".gif", ".webp")]
    wrong, meta, broken = [], [], []
    for p in rasters:
        head = p.read_bytes()[:16]
        if not any(head.startswith(m) for m in MAGIC[p.suffix.lower()]):
            wrong.append(str(p.relative_to(ROOT)))
            continue
        try:
            with Image.open(p) as im:
                im.verify()
            with Image.open(p) as im:
                has = []
                if len(im.getexif()):
                    has.append("EXIF")
                if any(k in im.info for k in ("exif", "xmp", "XML:com.adobe.xmp")):
                    has.append("XMP/EXIF block")
                if im.format == "JPEG" and b"http://ns.adobe.com/xap/1.0/" in p.read_bytes()[:65536]:
                    has.append("XMP")
                if im.format == "PNG" and any(k.lower() in ("comment", "description", "author") for k in im.info):
                    has.append("text chunk")
                if has:
                    meta.append(f"{p.relative_to(ROOT)} ({', '.join(sorted(set(has)))})")
        except Exception as e:  # a file Pillow cannot parse is suspicious
            broken.append(f"{p.relative_to(ROOT)}: {e}")
    check(f"images: all {len(rasters)} images are what their extension says", not wrong, wrong[:5])
    check("images: all images decode cleanly", not broken, broken[:5])
    check("images: no hidden EXIF/XMP/GPS metadata (run tools/strip_metadata.py)", not meta, meta[:5])
    big = [str(p.relative_to(ROOT)) for p in FILES if p.is_file() and p.stat().st_size > MAX_BYTES]
    check("repo: no file larger than 15 MB", not big, big)


# ---------------------------------------------------------------- secrets
SECRET_PATTERNS = {
    "private key": r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY",
    "GitHub token": r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36}\b|\bgithub_pat_[A-Za-z0-9_]{60,}\b",
    "AWS key": r"\bAKIA[0-9A-Z]{16}\b",
    "Google API key": r"\bAIza[0-9A-Za-z_\-]{35}\b",
    "Slack token": r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b",
    "Anthropic/OpenAI key": r"\bsk-(?:ant-)?[A-Za-z0-9_\-]{32,}\b",
    "password assignment": r"(?i)\b(?:password|passwd|secret|api[_-]?key|token)\s*[:=]\s*['\"][^'\"\s]{8,}['\"]",
}
TEXT_SUFFIXES = {".py", ".js", ".json", ".html", ".css", ".md", ".txt", ".yml", ".yaml", ".svg", ".sh", ".toml", ".cfg", ""}


def check_secrets():
    hits = []
    for p in FILES:
        if p.suffix.lower() not in TEXT_SUFFIXES or not p.is_file() or p.stat().st_size > 2_000_000:
            continue
        if p.name in ("security_check.py",):  # contains the patterns themselves
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        for label, pattern in SECRET_PATTERNS.items():
            if re.search(pattern, text):
                hits.append(f"{p.relative_to(ROOT)}: {label}")
    check("secrets: no keys, tokens or passwords committed", not hits, hits[:5])
    env = [str(p.relative_to(ROOT)) for p in FILES if p.name in (".env", ".npmrc", "id_rsa", "credentials.json")
           or p.suffix in (".pem", ".key", ".p12", ".pfx")]
    check("secrets: no credential files committed", not env, env)


# ---------------------------------------------------------------- ci
def check_ci():
    wf = sorted((ROOT / ".github" / "workflows").glob("*.y*ml"))
    check("ci: GitHub workflows exist", bool(wf))
    for p in wf:
        text = p.read_text(encoding="utf-8")
        uses = re.findall(r"uses:\s*([^\s#]+)", text)
        unpinned = [u for u in uses if not u.startswith("./") and not re.search(r"@[0-9a-f]{40}$", u)]
        check(f"ci: {p.name}: every action pinned to a full commit SHA", not unpinned, unpinned)
        check(f"ci: {p.name}: declares least-privilege permissions", re.search(r"^permissions:", text, re.M) is not None)
        check(f"ci: {p.name}: never runs untrusted pull_request_target code", "pull_request_target" not in text)
        check(f"ci: {p.name}: no ${{{{ github.event… }}}} expressions inside run: scripts",
              not re.search(r"run:[^\n]*\$\{\{\s*github\.event\.", text))


if __name__ == "__main__":
    for section in (check_page, check_script, check_svg, check_data, check_images, check_secrets, check_ci):
        print(f"\n— {section.__name__[6:]}")
        section()
    print(f"\n{failures} check(s) failed" if failures else "\nall security checks passed")
    sys.exit(1 if failures else 0)
