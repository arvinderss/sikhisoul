# ਸਿੱਖੀ ਸੋਲ · Sikhi Soul

**ਪਾਵਨ ਹੱਥ-ਲਿਖਤ ਬੀੜਾਂ, ਪੋਥੀਆਂ ਅਤੇ ਹੁਕਮਨਾਮਿਆਂ ਦੀ ਕਲਾ ਦਾ ਖੁੱਲ੍ਹਾ ਭੰਡਾਰ**
An open treasury of the ornament, calligraphy and binding art of historic Sikh manuscripts (16th–19th century),
redrawn as scalable vectors. It is free for everyone, forever.

🌐 **Website:** `index.html` (served with GitHub Pages; see [docs/SITE.md](docs/SITE.md))

[![Assets: CC BY-SA 4.0](https://img.shields.io/badge/assets-CC%20BY--SA%204.0-lightgrey.svg)](LICENSES/CC-BY-SA-4.0.txt)
[![Code: GPL-3.0](https://img.shields.io/badge/code-GPL--3.0--or--later-blue.svg)](LICENSE)

## ਅਦਬ · Respect

These designs come from sacred manuscripts. Please use them with full respect for Gurbani and the Guru Sahiban:
- Check any Gurbani text against an authentic source before you print it.
- Do not put Gurbani on anything that is walked on, thrown away or treated without respect.
- Follow Sri Akal Takht Sahib guidance before printing complete saroops.
- Paintings of the Guru Sahiban are artists' imaginings; they are kept here as historic art.

## What is here

| Folder | Contents |
|---|---|
| [`assets/`](assets/) | **134 SVG files**: 42 border designs, opening-folio illumination, Nishan tracings, binding tooling, coins, studies ([catalogue](assets/ASSETS.md)) |
| [`gallery/`](gallery/) | Heritage images (manuscripts, Nishans, Janamsakhi paintings, frescoes, coins), each with its licence ([README](gallery/README.md)) |
| [`index.html`](index.html) + [`site/`](site/) | The website: endless image carousels and a downloadable asset library |
| [`tools/`](tools/) | Python scripts that generate the borders, trace scans, build the site index and fetch gallery images |
| [`docs/`](docs/) | How the site works and how to add images or assets |

## Licences

- **Artwork and text:** [CC BY-SA 4.0](LICENSES/CC-BY-SA-4.0.txt). Credit the project, and share any changed versions under the same terms.
- **Code:** [GPL-3.0-or-later](LICENSE).
- **Gallery images** keep their own licences (public domain or Creative Commons), as recorded in `site/data/gallery.json`.
- Nobody may claim exclusive rights to these designs. See [LICENSING.md](LICENSING.md) and the dated
  [prior-art statement](PRIOR_ART.md).

Suggested credit:
> Ornament from ਸਿੱਖੀ ਸੋਲ / Sikhi Soul, CC BY-SA 4.0, https://github.com/arvinderss/sikhisoul

## ਬੇਨਤੀ ਤੇ ਸਪਸ਼ਟੀਕਰਨ · A humble note

ਇਹ ਭੰਡਾਰ ਅਤੇ ਵੈੱਬਸਾਈਟ ਮੁੱਖ ਤੌਰ 'ਤੇ ਬਣਾਉਟੀ ਬੁੱਧੀ (AI) ਦੀ ਸਹਾਇਤਾ ਨਾਲ ਤਿਆਰ ਕੀਤੇ ਗਏ ਹਨ, ਅਤੇ ਹੱਥੀਂ ਪੜਤਾਲ ਸੀਮਤ ਹੀ ਹੋ ਸਕੀ ਹੈ।
ਫਿਰ ਵੀ ਜਿਨ੍ਹਾਂ ਸਰੋਤਾਂ ਤੋਂ ਜਾਣਕਾਰੀ ਤੇ ਨਮੂਨੇ ਲਏ ਗਏ ਹਨ, ਉਹ ਪੂਰੀ ਲਗਨ, ਸਾਵਧਾਨੀ ਅਤੇ ਸਤਿਕਾਰ ਨਾਲ ਚੁਣੇ ਤੇ ਪਰਖੇ ਗਏ ਹਨ।
ਜੇ ਕਿਤੇ ਕੋਈ ਭੁੱਲ-ਚੁੱਕ ਨਜ਼ਰ ਆਵੇ ਤਾਂ ਖ਼ਿਮਾ ਕਰਨਾ ਜੀ ਅਤੇ ਸਾਨੂੰ ਜ਼ਰੂਰ ਦੱਸਣਾ।

This library and website were created mainly with the help of AI, with only limited manual review. The sources
the information and designs come from were nevertheless chosen and checked diligently, carefully and with respect.
If you find any mistake, please forgive it, and let us know.

**ਸੰਗਤ ਨੂੰ ਸੱਦਾ · An invitation to the Sangat.** If this work speaks to you, please join in. Corrections, better scans,
new tracings, translations, historical knowledge and ideas are all welcome; open an
[issue](https://github.com/arvinderss/sikhisoul/issues) or a pull request (see [CONTRIBUTING.md](CONTRIBUTING.md)).
We would love to keep this treasury growing and up to date, guided by the ideas of the whole Sangat.

ਵਾਹਿਗੁਰੂ ਜੀ ਕਾ ਖ਼ਾਲਸਾ ॥ ਵਾਹਿਗੁਰੂ ਜੀ ਕੀ ਫ਼ਤਹਿ ॥

## Working on it

```bash
python tools/build_site_data.py      # after adding/changing anything in assets/
python tools/fetch_gallery.py        # download gallery images + licences from Wikimedia Commons
python tools/strip_metadata.py       # remove hidden EXIF/XMP/GPS from gallery images
python tools/security_check.py       # the security & content-safety checks
npm test                             # browser tests (needs: npm ci && npx playwright install chromium)
python -m http.server                # preview at http://localhost:8000
```
Details: [docs/SITE.md](docs/SITE.md) · Contributing: [CONTRIBUTING.md](CONTRIBUTING.md) · Sources: [SOURCES.md](SOURCES.md) · Security: [SECURITY.md](SECURITY.md)

**ਸੁਰੱਖਿਆ · Safety:** the site uses no trackers, cookies or outside fonts. A security scan runs automatically
every week and on every change ([SECURITY.md](SECURITY.md)). Please report security problems privately via
*Security → Report a vulnerability*.

---
ਵਾਹਿਗੁਰੂ ਜੀ ਕਾ ਖ਼ਾਲਸਾ ॥ ਵਾਹਿਗੁਰੂ ਜੀ ਕੀ ਫ਼ਤਹਿ ॥
