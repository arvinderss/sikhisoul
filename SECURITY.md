# ਸੁਰੱਖਿਆ · Security

This site is meant to be a safe place for the Sangat. Visiting it should never expose anyone to tracking,
harmful code or misleading content, and the heritage material it holds should not be quietly altered.

## Reporting a problem
If you find a security or safety problem, please **do not open a public issue**. Report it privately
through GitHub: on the repository page, open **Security → Report a vulnerability**. You will get a reply
as soon as we can manage, and you will be credited when it is fixed, unless you prefer not to be.

Content concerns (a wrong attribution, a disrespectful caption, an image that should not be here) can be
raised openly as an [issue](https://github.com/arvinderss/sikhisoul/issues).

## How the site protects visitors
| Protection | Where |
|---|---|
| **Content-Security-Policy:** only this site's own scripts, styles and fonts can run. Images may come only from this site or Wikimedia Commons. No inline code, plug-ins, forms or `<base>` changes are allowed. | `index.html` `<meta>` |
| **No tracking:** fonts are self-hosted (`site/fonts/`, SIL OFL 1.1). There are no analytics, cookies or third-party requests, and `referrer: no-referrer` is set. | `index.html`, `site/css/fonts.css` |
| **Data never becomes code:** every text is inserted as text, never as HTML. Every URL from the JSON files is checked against an allowlist (`SAFE_LOCAL_IMAGE`, `SAFE_ASSET_PATH`, `SAFE_SOURCE_PAGE`) before use. `el()` refuses `on…` attributes. | `site/js/app.js` |
| **Safe external links:** links that open a new tab use `rel="noopener noreferrer"`. | `site/js/app.js` |
| **Safe SVGs:** no `<script>`, event handlers, `javascript:` links, `<foreignObject>`, DOCTYPE/ENTITY or remote references. | checked by `tools/security_check.py` |
| **Clean images:** EXIF, XMP, IPTC and GPS metadata are removed losslessly, and file types are verified by their bytes. | `tools/strip_metadata.py`, `tools/fetch_gallery.py` |
| **Safe downloads by the tools:** `fetch_gallery.py` talks only to Wikimedia over HTTPS (redirects included), caps file size at 15 MB, checks image bytes and strips metadata. | `tools/fetch_gallery.py` |
| **Only free-licensed images are stored**, each with its licence recorded. | `site/data/gallery.json` |

### A known limit of GitHub Pages
GitHub Pages cannot send custom HTTP headers. The policy is therefore given as a `<meta>` tag, which covers
everything above **except** `frame-ancestors`, so another site could embed this page in a frame. The page
has no sign-in, forms or actions, so there is nothing for such a frame to trick a visitor into doing. If the
site ever moves behind a proxy such as Cloudflare, also send `Content-Security-Policy: frame-ancestors 'none'`,
`X-Content-Type-Options: nosniff` and `Strict-Transport-Security`.

## The weekly scan
`.github/workflows/security.yml` runs **every Monday at 06:17 India time**, on every push to `main`, on
every pull request, and on demand (*Actions → security → Run workflow*). It runs:

1. **`tools/security_check.py`:** all of the protections above, plus committed-secret detection and
   checks that every GitHub Action is pinned to a full commit SHA with least-privilege permissions.
2. **The browser tests (`npm test`):** the site's behaviour, and these security checks:
   - no CSP violations;
   - no third-party requests;
   - fonts served locally;
   - safe links;
   - hostile JSON (with `javascript:` URLs, foreign hosts, `../` paths and HTML in titles) is fed in and must be neutralised.
3. **`npm audit`** and **`npm audit signatures`** on the exact lockfile.
4. **CodeQL** (`security-extended`) for the JavaScript, the Python tools and the workflows themselves.
   Findings appear under *Security → Code scanning*.

**Dependabot** (`.github/dependabot.yml`) proposes updates to Playwright and to the pinned actions every
Monday. If a scheduled run fails, GitHub emails the repository owner.

Run the same checks locally:
```bash
python tools/security_check.py
npm ci && npx playwright install chromium && npm test
npm audit
```

## Settings the repository owner should switch on
These live in GitHub's settings and cannot be set from a file:
- **Settings → Code security:** enable *Private vulnerability reporting*, *Dependabot alerts*,
  *Dependabot security updates*, *Secret scanning* and *Push protection*.
- **Settings → Branches → Add rule for `main`:** require a pull request, and require the `security`
  checks to pass. Block force pushes and deletion.
- **Settings → Actions → General:** set *Workflow permissions* to **Read repository contents**, and do not
  allow Actions to approve pull requests.
- **Settings → Pages:** tick **Enforce HTTPS**.
