# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Sikh Manuscript Revival contributors
"""
Build site/data/assets.json — the index the website (index.html) reads to list
and offer downloads of everything in assets/.

Run from the repository root after adding or changing files in assets/:

    python tools/build_site_data.py

Titles for individual files live in TITLES below (Gurmukhi first, English second).
Files without an entry still appear, titled by their file name.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
OUT = os.path.join(ROOT, "site", "data", "assets.json")

GURMUKHI_DIGITS = "੦੧੨੩੪੫੬੭੮੯"


def gnum(n):
    """Integer -> Gurmukhi numerals (੧, ੨, ...)."""
    return "".join(GURMUKHI_DIGITS[int(d)] for d in str(n))


# Collections, in the order they appear on the site.
COLLECTIONS = [
    ("01_borders_burhanpuri", "ਹਾਸ਼ੀਏ — ਸੁਨਹਿਰੀ ਬੀੜ, ਬੁਰਹਾਨਪੁਰ", "Border designs — Burhanpuri saroop"),
    ("02_opening_illumination", "ਆਰੰਭਕ ਪੱਤਰਿਆਂ ਦੀ ਚਿੱਤਰਕਾਰੀ", "Opening-folio illumination"),
    ("03_calligraphy_nishans", "ਨੀਸਾਣ ਤੇ ਪੁਰਾਤਨ ਲਿਖਤ", "Nishans & historic calligraphy"),
    ("04_binding_coins", "ਜਿਲਦਸਾਜ਼ੀ ਦੇ ਨਮੂਨੇ ਤੇ ਸਿੱਕੇ", "Binding tooling & coins"),
    ("05_source_studies", "ਸਰੋਤਾਂ ਤੋਂ ਅਧਿਐਨ", "Studies from sources"),
]

# Hand-written titles: file stem -> (Gurmukhi, English, source note)
TITLES = {
    # 02 opening illumination
    "bha_opening_frame_full": ("ਆਰੰਭਕ ਪੱਤਰੇ ਦਾ ਪੂਰਾ ਚੌਖਟਾ", "Full opening-page frame", "Bhanno MS p.70"),
    "bha_kangura_band": ("ਕੰਗੂਰੇਦਾਰ ਹਾਸ਼ੀਆ — ਇਕਾਈ", "Kangura scalloped band — tile", "Bhanno MS p.70–71"),
    "bha_kangura_band_strip": ("ਕੰਗੂਰੇਦਾਰ ਹਾਸ਼ੀਆ — ਪੱਟੀ", "Kangura scalloped band — strip", "Bhanno MS p.70–71"),
    "bha_cartouche_band": ("ਲਾਜਵਰਦੀ ਪੱਟੀ ਵਿੱਚ ਬੇਲ-ਬੂਟੇ — ਇਕਾਈ", "Oval cartouche band — tile", "Bhanno MS p.70–71"),
    "bha_cartouche_band_strip": ("ਲਾਜਵਰਦੀ ਪੱਟੀ ਵਿੱਚ ਬੇਲ-ਬੂਟੇ — ਪੱਟੀ", "Oval cartouche band — strip", "Bhanno MS p.70–71"),
    "bur_cartouche_panel_h": ("ਲਾਜਵਰਦੀ ਤਖ਼ਤੀ (ਲੇਟਵੀਂ)", "Lapis panel with stepped cartouche (horizontal)", "Burhanpuri p.7"),
    "bur_cartouche_panel_v": ("ਲਾਜਵਰਦੀ ਤਖ਼ਤੀ (ਖੜ੍ਹਵੀਂ)", "Lapis panel with stepped cartouche (vertical)", "Burhanpuri p.7"),
    "bur_mandorla_panel": ("ਮਿਹਰਾਬ ਵਿੱਚ ਸੁਨਹਿਰੀ ਸ਼ਮਸਾ", "Lobed mandorla in cusped niche", "Burhanpuri p.7"),
    "bur_ogee_arcade_headpiece": ("ਗੁੰਬਦਦਾਰ ਸਿਰਲੇਖ-ਪੱਟੀ", "Ogee arcade headpiece", "Burhanpuri p.8"),
    "bur_star_cartouche_band": ("ਅੱਠ-ਨੁਕਰੇ ਤਾਰਿਆਂ ਦੀ ਪੱਟੀ", "8-point star & cartouche band", "Burhanpuri p.8"),
    "bur_diamond_lattice_panel": ("ਕਿਰਮਚੀ ਜਾਲੀ", "Crimson diamond lattice", "Burhanpuri p.8"),
    "bur_scroll_border_tile": ("ਸੁਨਹਿਰੀ ਵੇਲ — ਇਕਾਈ", "Gold scroll-vine border — tile", "Burhanpuri pp.7–8"),
    "bur_scroll_border_strip": ("ਸੁਨਹਿਰੀ ਵੇਲ — ਪੱਟੀ", "Gold scroll-vine border — strip", "Burhanpuri pp.7–8"),
    "bur_cloud_heading": ("ਬੱਦਲਨੁਮਾ ਸਿਰਲੇਖ-ਖ਼ਾਨਾ", "Cloud-band heading (placeholder)", "Burhanpuri p.33"),
    "bur_baluster_columns": ("ਥੰਮ੍ਹਾਂ ਦਾ ਜੋੜਾ", "Paired baluster columns", "Burhanpuri p.8"),
    # 03 calligraphy
    "cal_nishan_g5_kartarpuri": ("ਨੀਸਾਣ — ਸ੍ਰੀ ਗੁਰੂ ਅਰਜਨ ਦੇਵ ਜੀ (ਕਰਤਾਰਪੁਰੀ ਬੀੜ)", "Nishan — Sri Guru Arjan Dev Ji (Kartarpuri Bir)", "via Kapoor p.2"),
    "cal_nishan_g5_sabot": ("ਨੀਸਾਣ — ਸ੍ਰੀ ਗੁਰੂ ਅਰਜਨ ਦੇਵ ਜੀ (ਸਬੋਤ ਬੀੜ)", "Nishan — Sri Guru Arjan Dev Ji (Sabot Bir)", "via Kapoor p.3"),
    "cal_moolmantar_g5_red": ("ਮੂਲ ਮੰਤ੍ਰ — ਸ਼ਿੰਗਰਫ਼ੀ ਸਿਆਹੀ", "Mool Mantar in red ink", "attributed to Sri Guru Arjan Dev Ji"),
    "cal_nishan_g6_kartarpuri": ("ਨੀਸਾਣ — ਸ੍ਰੀ ਗੁਰੂ ਹਰਿਗੋਬਿੰਦ ਸਾਹਿਬ ਜੀ (ਕਰਤਾਰਪੁਰੀ ਬੀੜ)", "Nishan — Sri Guru Hargobind Sahib Ji (Kartarpuri Bir)", "via Kapoor p.10"),
    "cal_nishan_g6_hargobind": ("ਨੀਸਾਣ — ਸ੍ਰੀ ਗੁਰੂ ਹਰਿਗੋਬਿੰਦ ਸਾਹਿਬ ਜੀ", "Nishan — Sri Guru Hargobind Sahib Ji", ""),
    "cal_nishan_g7_dehradun": ("ਨੀਸਾਣ — ਸ੍ਰੀ ਗੁਰੂ ਹਰਿ ਰਾਇ ਸਾਹਿਬ ਜੀ (ਦੇਹਰਾਦੂਨ ਬੀੜ, ੧੬੫੯)", "Nishan — Sri Guru Har Rai Sahib Ji (Dehra Dun Bir, 1659)", "via Kapoor p.15"),
    "cal_nishan_g7_harrai": ("ਨੀਸਾਣ — ਸ੍ਰੀ ਗੁਰੂ ਹਰਿ ਰਾਇ ਸਾਹਿਬ ਜੀ", "Nishan — Sri Guru Har Rai Sahib Ji", ""),
    "cal_nishan_g9_teghbahadur": ("ਨੀਸਾਣ — ਸ੍ਰੀ ਗੁਰੂ ਤੇਗ ਬਹਾਦਰ ਸਾਹਿਬ ਜੀ", "Nishan — Sri Guru Tegh Bahadur Sahib Ji", ""),
    "cal_nishan_g10_gobindsingh": ("ਨੀਸਾਣ — ਸ੍ਰੀ ਗੁਰੂ ਗੋਬਿੰਦ ਸਿੰਘ ਜੀ", "Nishan — Sri Guru Gobind Singh Ji", ""),
    "cal_writing_g10": ("ਲਿਖਤ — ਸਰੋਤ ਅਨੁਸਾਰ ਦਸਮ ਪਾਤਸ਼ਾਹ ਜੀ ਦੀ", "Writing attributed to Sri Guru Gobind Singh Ji", ""),
    "cal_mool_rupa_panel": ("ਖ਼ਾਨੇ ਵਿੱਚ ਮੂਲ ਮੰਤ੍ਰ — ਭਾਈ ਰੂਪਾ ਪੋਥੀ", "Framed Mool Mantar — Bhai Rupa pothi", "p.488"),
    # 04 binding & coins
    "bind_bhanno_arabesque_symmetric": ("ਜਿਲਦ ਦੀ ਬੇਲ — ਚਹੁੰ-ਪਾਸੀ ਸਮਰੂਪ", "Cover arabesque — four-fold symmetric", "for brass block / stamp"),
    "bind_bhanno_front_arabesque": ("ਜਿਲਦ ਦੀ ਬੇਲ — ਜਿਵੇਂ ਮਿਲੀ", "Cover arabesque — as found", "Bhanno MS front cover"),
    "coin_ranjit_singh_obverse": ("ਨਾਨਕਸ਼ਾਹੀ ਰੁਪਈਆ — ਇੱਕ ਪਾਸਾ", "Nanakshahi rupee — face 1", "Maharaja Ranjit Singh era"),
    "coin_ranjit_singh_reverse": ("ਨਾਨਕਸ਼ਾਹੀ ਰੁਪਈਆ — ਦੂਜਾ ਪਾਸਾ", "Nanakshahi rupee — face 2", "Maharaja Ranjit Singh era"),
    # 05 studies
    "study_kangura_sawtooth": ("ਕੰਗੂਰਾ ਕਿਨਾਰਾ", "Kangura sawtooth edge", "Bhanno cover · Damdami Bir"),
    "study_kurukshetra_cusped_arch": ("ਸੁਨਹਿਰੀ ਮਿਹਰਾਬ", "Cusped arch on gold ground", "Kurukshetra MN-000403"),
    "study_burhanpuri_nishan_niche": ("ਨੀਸਾਣ ਲਈ ਥੰਮ੍ਹਾਂ ਵਾਲੀ ਮਿਹਰਾਬ", "Nishan niche on pillars", "Burhanpuri"),
    "study_lapis_arabesque_frame": ("ਲਾਜਵਰਦੀ ਬੇਲਦਾਰ ਚੌਖਟਾ", "Lapis arabesque frame", "pothi folio"),
    "study_cloud_collar_cartouche": ("ਬੱਦਲਨੁਮਾ ਖ਼ਾਨਾ", "Cloud-collar cartouche", ""),
    "study_damdami_millefleur_frame": ("ਫੁੱਲਕਾਰੀ ਚੌਖਟਾ", "Millefleur frame with rose cartouches", "Utara Damdami Bir"),
    "study_janamsakhi_triangle_field": ("ਤਿਕੋਣਾ ਲਿਖਤ-ਖੇਤਰ", "Triangular text field, folk border", "Janamsakhi Bhai Bala"),
    "study_hukamnama_layouts": ("ਹੁਕਮਨਾਮਿਆਂ ਦੀ ਬਣਤਰ", "Hukamnama layouts", ""),
}


def rel(path):
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


def border_items(folder):
    """Borders come with an index.json; each style has tile + strip (+ motif)."""
    index = json.load(open(os.path.join(folder, "index.json"), encoding="utf-8"))
    items = []
    for n, style in enumerate(index, start=1):
        key = style["key"]
        files = [
            {"label_pa": "ਪੱਟੀ", "label_en": "strip", "path": rel(os.path.join(folder, style["strip"]))},
            {"label_pa": "ਇਕਾਈ", "label_en": "tile", "path": rel(os.path.join(folder, style["tile"]))},
        ]
        if style.get("motif"):
            files.append({"label_pa": "ਫੁੱਲ", "label_en": "motif", "path": rel(os.path.join(folder, style["motif"]))})
        items.append({
            "id": key,
            "pa": f"ਹਾਸ਼ੀਆ {gnum(n)}",
            "en": style["title"],
            "note": style["source"],
            "preview": files[0]["path"],
            "files": files,
        })
    return items


def plain_items(folder):
    items = []
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".svg"):
            continue
        stem = name[:-4]
        pa, en, note = TITLES.get(stem, (stem, stem.replace("_", " "), ""))
        path = rel(os.path.join(folder, name))
        items.append({
            "id": stem, "pa": pa, "en": en, "note": note, "preview": path,
            "files": [{"label_pa": "SVG", "label_en": "svg", "path": path}],
        })
    return items


def main():
    data = {"generated_by": "tools/build_site_data.py", "collections": []}
    for key, pa, en in COLLECTIONS:
        folder = os.path.join(ASSETS, key)
        if not os.path.isdir(folder):
            print(f"skip (missing): {key}", file=sys.stderr)
            continue
        items = border_items(folder) if os.path.exists(os.path.join(folder, "index.json")) else plain_items(folder)
        data["collections"].append({"id": key, "pa": pa, "en": en, "items": items})
        print(f"{key}: {len(items)} items")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1)
    print(f"wrote {rel(OUT)}")


if __name__ == "__main__":
    main()
