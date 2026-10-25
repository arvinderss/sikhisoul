# Contributing · ਸੇਵਾ

Corrections, better scans, new tracings and translations are all welcome. Thank you for your seva.

- **Corrections first.** Errors in Gurmukhi, an attribution or a date matter most. Open an issue with the source.
- **New assets:** SVG only, with a `viewBox` and the SPDX header. Record the source manuscript and page in your pull request,
  and add titles in `tools/build_site_data.py`. See [docs/SITE.md](docs/SITE.md).
- **Gallery images:** public domain or Creative Commons only, added through `site/data/gallery.json`. Never upload
  scans whose holder has not released them.
- **Language:** Gurmukhi first, English second; refer to the Guru Sahiban with full honorifics.
- **Safety checks:** before a pull request, run `python tools/security_check.py` and `npm test`. The same checks run
  automatically on your pull request. SVGs must not contain scripts, event handlers or links to other sites. Report
  security problems privately (see [SECURITY.md](SECURITY.md)).

By contributing you agree that your contribution is licensed under the same terms as the rest of the repository:
artwork and text under CC BY-SA 4.0, code under GPL-3.0-or-later.
