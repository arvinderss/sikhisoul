# The website — how it works

The site is one static page, with no framework and no build step. Any web server, including GitHub Pages, can serve it.

```
index.html              markup and all page text (Gurmukhi first, English secondary)
site/css/main.css       styling; tokens at the top (colours, fonts, spacing)
site/js/app.js          renders the gallery and library from the two JSON files
site/data/gallery.json  image catalogue: hand-edited
site/data/assets.json   asset index: generated, do not edit by hand
gallery/<category>/     downloaded heritage images
assets/                 the SVG library itself
```

## Publishing with GitHub Pages
Settings → Pages → *Deploy from a branch* → `main` / `/ (root)`. The `.nojekyll` file makes GitHub serve the files as they are.

## Preview locally
```bash
python -m http.server 8000
# open http://localhost:8000
```
Opening `index.html` directly as a `file://` URL will not work, because browsers block `fetch()` of the JSON files that way.

## Adding an SVG to the library
1. Put the file in the right `assets/NN_*/` folder. Add the SPDX header comment
   `<!-- SPDX-License-Identifier: CC-BY-SA-4.0 ... -->` (copy it from any existing SVG).
2. Add a Gurmukhi and English title to `TITLES` in `tools/build_site_data.py`.
3. Run `python tools/build_site_data.py`, then commit the asset and the updated `site/data/assets.json`.

## Adding an image to the gallery
1. Find it on Wikimedia Commons, and check that its licence is public domain or Creative Commons.
2. Add an entry to `items` in `site/data/gallery.json`:
   ```json
   { "id": "short-unique-id", "category": "pothi", "era": "c18", "gurus": ["10"],
     "commons": "Exact Commons file name.jpg",
     "pa": "ਗੁਰਮੁਖੀ ਸਿਰਲੇਖ", "en": "English title" }
   ```
   - `category`: one of the keys in `categories` (`pothi`, `nishan`, `janamsakhi`, `chitra`, `sikke`, `itihas`)
   - `era`: one of the keys in `eras`. Use `unknown` when the source does not give a date.
   - `gurus`: the Guru Sahiban the item relates to (`"1"`–`"10"`), or `[]`
3. Run `python tools/fetch_gallery.py`. It downloads the image to `gallery/<category>/<id>.<ext>` and fills in
   `licence`, `author`, `date`, `source_page` and `local`. If an image is not public domain or Creative Commons,
   the script leaves it as a remote link and reports it for review.

Until an image is downloaded, the page shows it straight from Wikimedia Commons (`Special:FilePath`).

## Writing guidance
- Gurmukhi comes first; English is the secondary line (`class="en"`).
- Always refer to the Gurus in full and with respect: *ਸ੍ਰੀ ਗੁਰੂ … ਜੀ / Sri Guru … Ji*.
  Use respectful phrasing for events, e.g. *ਜੋਤੀ ਜੋਤਿ ਸਮਾਉਣਾ* (Joti Jot), never "death".
- Give dates and attributions **as the source states them**, marked *ਸਰੋਤ ਅਨੁਸਾਰ / per source* when they are claims.
- Do not add Gurbani text to the page beyond the opening *ੴ ਸਤਿਗੁਰ ਪ੍ਰਸਾਦਿ ॥* and the closing Fateh.

## Accessibility
- All controls are real buttons, links and form fields, at least 44 px tall.
- The carousel pauses on hover or focus and with the "ਠਹਿਰਾਓ" (pause) checkbox. With *reduced motion* switched on, it stops
  moving and becomes a scrollable row. The duplicate cards used for the loop are hidden from screen readers.
