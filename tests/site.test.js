/*
  End-to-end tests for the ਸਿੱਖੀ ਸੋਲ website.
  SPDX-License-Identifier: GPL-3.0-or-later

  Run from the repository root:
      npm install playwright          (once; then: npx playwright install chromium)
      node tests/site.test.js         (starts its own local server on port 8765)

  Plain Node + Playwright (no test framework), so it is easy to read and change.
  Each check prints ✓ or ✗; the process exits non-zero if anything fails.
*/
const { chromium, devices } = require("playwright");
const http = require("http");
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const PORT = 8765;
const URL = `http://localhost:${PORT}/index.html`;
let failures = 0;

function check(name, ok, detail) {
  console.log(`${ok ? "✓" : "✗"} ${name}${!ok && detail ? "  — " + detail : ""}`);
  if (!ok) failures++;
}

/* ---- tiny static server (so the test has no other dependencies) ---- */
const TYPES = { ".html": "text/html", ".css": "text/css", ".js": "text/javascript", ".json": "application/json",
  ".svg": "image/svg+xml", ".jpg": "image/jpeg", ".png": "image/png", ".md": "text/plain", ".txt": "text/plain",
  ".woff2": "font/woff2" };
function serve() {
  return http.createServer((req, res) => {
    const p = path.join(ROOT, decodeURIComponent(req.url.split("?")[0]));
    if (!p.startsWith(ROOT) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); return res.end(); }
    res.writeHead(200, { "Content-Type": TYPES[path.extname(p)] || "application/octet-stream" });
    fs.createReadStream(p).pipe(res);
  }).listen(PORT);
}

async function open(browser, opts = {}) {
  const ctx = await browser.newContext(opts);
  const page = await ctx.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  // Block third-party images/fonts so tests are fast and deterministic offline.
  await page.route(/^https?:\/\/(?!localhost)/, (r) => r.abort());
  await page.goto(URL);
  await page.waitForSelector(".carousel .card");
  await page.waitForSelector(".asset");
  return { ctx, page, errors };
}

const scrollPos = (page, i = 0) => page.evaluate((i) => document.querySelectorAll(".carousel__window")[i].scrollLeft, i);
const dialogOpen = (page) => page.evaluate(() => document.getElementById("viewer").open);

async function rolls(page, i = 0, ms = 1200) {
  const a = await scrollPos(page, i);
  await page.waitForTimeout(ms);
  return (await scrollPos(page, i)) !== a;
}

// Like a real finger/mouse: touching the carousel pauses it first, then the tap lands on a still card.
async function openCard(page, card, tap) {
  await card.evaluate((c) => c.closest(".carousel__window").dispatchEvent(new Event("pointerdown")));
  await page.waitForTimeout(150);
  if (tap) await card.tap(); else await card.click();
  await page.waitForTimeout(350);
}

async function firstLoopingIndex(page) {
  return page.evaluate(() => [...document.querySelectorAll(".carousel")].findIndex((c) => !c.classList.contains("carousel--still")));
}

(async () => {
  const server = serve();
  const browser = await chromium.launch();

  /* ===== data integrity ===== */
  const gallery = JSON.parse(fs.readFileSync(path.join(ROOT, "site/data/gallery.json"), "utf8"));
  const assets = JSON.parse(fs.readFileSync(path.join(ROOT, "site/data/assets.json"), "utf8"));
  const ids = gallery.items.map((i) => i.id);
  check("gallery ids are unique", new Set(ids).size === ids.length);
  check("every gallery item has a known category and era",
    gallery.items.every((i) => gallery.categories[i.category] && gallery.eras[i.era]));
  const missingLocal = gallery.items.filter((i) => i.local && !fs.existsSync(path.join(ROOT, i.local)));
  check("every downloaded gallery image exists on disk", !missingLocal.length, missingLocal.map((i) => i.id).join(", "));
  const allFiles = assets.collections.flatMap((c) => c.items.flatMap((it) => it.files.map((f) => f.path)));
  const missingAssets = allFiles.filter((p) => !fs.existsSync(path.join(ROOT, p)));
  check(`all ${allFiles.length} download links point at real files`, !missingAssets.length, missingAssets.slice(0, 5).join(", "));

  /* ===== desktop ===== */
  {
    const { ctx, page, errors } = await open(browser, { viewport: { width: 1280, height: 900 } });
    const L = await firstLoopingIndex(page);
    await page.locator(".carousel").nth(L).scrollIntoViewIfNeeded();

    check("carousel rolls on its own", await rolls(page, L));
    check("6 categories shown", (await page.locator(".carousel").count()) === 6);

    // ‹ › buttons
    await page.mouse.move(5, 5);
    const before = await scrollPos(page, L);
    await page.locator(".carousel").nth(L).locator(".carousel__nav").nth(1).click();
    await page.waitForTimeout(700);
    const afterNext = await scrollPos(page, L);
    check("› button moves the carousel", afterNext !== before);
    await page.locator(".carousel").nth(L).locator(".carousel__nav").nth(0).click();
    await page.waitForTimeout(700);
    check("‹ button moves it back", (await scrollPos(page, L)) !== afterNext);

    // wheel / trackpad scrolling by hand
    const win = page.locator(".carousel__window").nth(L);
    const box = await win.boundingBox();
    await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
    const w0 = await scrollPos(page, L);
    await page.mouse.wheel(400, 0);
    await page.waitForTimeout(300);
    check("trackpad/wheel scrolls the carousel by hand", (await scrollPos(page, L)) !== w0);
    await page.mouse.move(5, 5);
    await page.waitForTimeout(3200);
    check("carousel resumes after the visitor lets go", await rolls(page, L));

    // viewer open / close by every route, and carousel keeps working afterwards
    const card = page.locator(".carousel").nth(L).locator(".card:not([data-copy])").first();
    const routes = {
      "✕ button": async () => page.click("#viewer-close"),
      "ਵਾਪਸ button": async () => { await page.locator("#viewer").evaluate((d) => d.scrollTo(0, d.scrollHeight)); await page.click("#viewer-back"); },
      "Esc key": async () => page.keyboard.press("Escape"),
      "click outside": async () => page.mouse.click(8, 8),
      "browser Back": async () => page.goBack(),
    };
    for (const [how, close] of Object.entries(routes)) {
      await openCard(page, card, false);
      const opened = await dialogOpen(page);
      const closeBox = await page.locator("#viewer-close").boundingBox();
      await close();
      await page.waitForTimeout(400);
      check(`viewer opens and closes with ${how}`, opened && !(await dialogOpen(page)));
      check(`  ✕ was visible while open (${how})`, !!closeBox && closeBox.y >= 0 && closeBox.y < 900);
      check(`  still on the page after ${how}`, page.url().startsWith(URL));
    }
    await page.mouse.move(5, 5);
    await page.waitForTimeout(3200);
    check("carousel rolls again after the viewer is closed", await rolls(page, L));
    {
      const b2 = await page.locator(".carousel__window").nth(L).boundingBox();
      await page.mouse.move(b2.x + 50, b2.y + 50);
      const h0 = await scrollPos(page, L);
      await page.mouse.wheel(300, 0);
      await page.waitForTimeout(300);
      check("carousel still scrolls by hand after the viewer is closed", (await scrollPos(page, L)) !== h0);
      await page.mouse.move(5, 5);
    }

    // pause checkbox
    await page.check("#filter-still");
    check("ਠਹਿਰਾਓ (pause) stops rolling", !(await rolls(page, L)));
    await page.uncheck("#filter-still");
    await page.mouse.move(5, 5);
    check("unticking resumes rolling", await rolls(page, L, 1500));

    // filters
    await page.selectOption("#filter-guru", "10");
    const titles10 = await page.locator(".card:not([data-copy]) .card__title").allTextContents();
    const expected10 = gallery.items.filter((i) => i.gurus.includes("10")).length;
    check("Guru filter shows only related images", new Set(titles10).size === expected10, `${new Set(titles10).size} vs ${expected10}`);
    await page.selectOption("#filter-guru", "");
    await page.selectOption("#filter-era", "c19");
    const n19 = await page.locator(".card:not([data-copy])").count();
    check("century filter works", n19 > 0 && n19 <= gallery.items.length);
    await page.selectOption("#filter-era", "");

    // keyboard: Tab to a card, Enter opens, focus lands on ✕, Esc returns
    await page.locator(".carousel .card:not([data-copy])").first().focus();
    await page.keyboard.press("Enter");
    await page.waitForTimeout(300);
    check("keyboard: Enter opens the viewer", await dialogOpen(page));
    check("keyboard: focus moves to the ✕ button", await page.evaluate(() => document.activeElement.id === "viewer-close"));
    await page.keyboard.press("Escape");
    await page.waitForTimeout(300);
    check("keyboard: Esc closes and focus returns to the card",
      !(await dialogOpen(page)) && (await page.evaluate(() => document.activeElement.classList.contains("card"))));

    // library
    check("library shows 5 collections", (await page.locator("#library-tabs button").count()) === 5);
    await page.locator("#library-tabs button").nth(2).click();
    check("library tab switches", (await page.locator(".asset").count()) === assets.collections[2].items.length);
    await page.fill("#library-search", "lotus");
    const found = await page.locator(".asset").count();
    check("library search finds 'lotus'", found > 0, String(found));
    await page.fill("#library-search", "zzzz-nothing");
    check("library search shows 'nothing found'", (await page.locator("#library-grid .empty").count()) === 1);
    await page.fill("#library-search", "");
    const dl = await page.locator(".asset__files a").first().getAttribute("download");
    check("download buttons use the download attribute", dl !== null);

    check("no JavaScript errors (desktop)", !errors.length, errors.join(" | "));
    await ctx.close();
  }

  /* ===== phone (touch) ===== */
  {
    const { ctx, page, errors } = await open(browser, { ...devices["iPhone 13"] });
    const L = await firstLoopingIndex(page);
    const card = page.locator(".carousel").nth(L).locator(".card:not([data-copy])").first();
    await page.locator(".carousel").nth(L).evaluate((n) => n.scrollIntoView());
    await page.waitForTimeout(200);
    await openCard(page, card, true);
    let b = await page.locator("#viewer-close").boundingBox();
    const vh = page.viewportSize().height;
    check("phone: ✕ visible at the top of the viewer", !!b && b.y >= 0 && b.y + b.height <= vh);
    await page.locator("#viewer").evaluate((d) => d.scrollTo(0, d.scrollHeight));
    await page.waitForTimeout(200);
    b = await page.locator("#viewer-close").boundingBox();
    check("phone: ✕ stays visible after scrolling the details", !!b && b.y >= 0 && b.y + b.height <= vh);
    await page.locator("#viewer-close").tap();
    await page.waitForTimeout(400);
    check("phone: tapping ✕ closes the viewer", !(await dialogOpen(page)));

    // swipe = native scroll of the window; simulate by scrolling it as a finger would
    await page.waitForTimeout(3000);
    check("phone: carousel rolls after closing", await rolls(page, L, 1500));
    await page.locator(".carousel__window").nth(L).dispatchEvent("touchstart");
    const s0 = await scrollPos(page, L);
    await page.locator(".carousel__window").nth(L).evaluate((w) => w.scrollBy(-250, 0));
    await page.waitForTimeout(200);
    check("phone: swiping left/right moves the carousel", (await scrollPos(page, L)) !== s0);
    check("phone: carousel holds still while being touched", !(await rolls(page, L, 800)));

    // phone Back gesture closes the viewer, not the page
    await openCard(page, card, true);
    await page.goBack();
    await page.waitForTimeout(300);
    check("phone: Back gesture closes the viewer and stays on the page", !(await dialogOpen(page)) && page.url().startsWith(URL));

    check("no JavaScript errors (phone)", !errors.length, errors.join(" | "));
    await ctx.close();
  }

  /* ===== layout at several widths ===== */
  for (const w of [320, 390, 768, 1024, 1440]) {
    const { ctx, page } = await open(browser, { viewport: { width: w, height: 800 } });
    const sw = await page.evaluate(() => document.documentElement.scrollWidth);
    check(`no sideways page scroll at ${w}px`, sw <= w, `${sw}px`);
    const small = await page.evaluate(() => [...document.querySelectorAll("button, a.button, select, .nav a")]
      .filter((e) => e.offsetParent && e.getBoundingClientRect().height < 36).length);
    check(`touch targets ≥ 36px tall at ${w}px`, small === 0, `${small} small`);
    await ctx.close();
  }

  /* ===== security and privacy ===== */
  {
    // Watch for Content-Security-Policy violations and for every request that leaves this site.
    const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 } });
    await ctx.addInitScript(() => {
      window.__csp = [];
      document.addEventListener("securitypolicyviolation", (e) => window.__csp.push(e.violatedDirective + " " + e.blockedURI));
    });
    const page = await ctx.newPage();
    const foreign = new Set();
    page.on("request", (r) => { const u = new globalThis.URL(r.url()); if (u.hostname !== "localhost") foreign.add(u.hostname); });
    await page.route(/^https?:\/\/(?!localhost)/, (r) => r.abort());
    await page.goto(URL);
    await page.waitForSelector(".carousel .card");
    await page.waitForSelector(".asset");
    await openCard(page, page.locator(".card:not([data-copy])").first());
    const rel = await page.evaluate(() => [...document.querySelectorAll('a[target="_blank"]')].map((a) => a.rel));
    check("links opening a new tab use rel=noopener noreferrer",
      rel.length > 0 && rel.every((r) => /noopener/.test(r) && /noreferrer/.test(r)), rel.join(", "));
    await page.click("#viewer-close");
    const csp = await page.evaluate(() => document.querySelector('meta[http-equiv="Content-Security-Policy"]')?.content || "");
    check("page declares a Content-Security-Policy", /default-src 'none'/.test(csp) && /script-src 'self'/.test(csp));
    check("page declares referrer: no-referrer",
      await page.evaluate(() => document.querySelector('meta[name="referrer"]')?.content === "no-referrer"));
    const violations = await page.evaluate(() => window.__csp);
    check("no Content-Security-Policy violations", !violations.length, violations.join(" | "));
    const extra = [...foreign].filter((h) => !["commons.wikimedia.org", "upload.wikimedia.org"].includes(h));
    check("no requests to trackers, font services or other third parties", !extra.length, extra.join(", "));
    const fonts = await page.evaluate(async () => { await document.fonts.ready;
      return document.fonts.check('20px "Noto Serif Gurmukhi"', "ੴ") && document.fonts.check('italic 20px "EB Garamond"', "Sikhi"); });
    check("Gurmukhi and English fonts load from this site", fonts);
    await ctx.close();
  }
  {
    // Feed the page hostile data and make sure none of it can run or send visitors elsewhere.
    const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 } });
    const page = await ctx.newPage();
    const evilText = '<img src=x onerror="window.__pwned=1">';
    const g = JSON.parse(JSON.stringify(gallery));
    g.items.forEach((it, i) => {
      if (i % 3 === 0) { it.local = "javascript:window.__pwned=1"; it.source_page = "javascript:window.__pwned=1"; }
      if (i % 3 === 1) { it.local = "https://evil.example/x.jpg"; it.source_page = "https://evil.example/"; }
      if (i % 3 === 2) { it.local = "gallery/pothi/../../x.jpg"; it.commons = '"><svg onload=window.__pwned=1>'; delete it.source_page; }
      it.pa = evilText; it.en = evilText;
    });
    const a = JSON.parse(JSON.stringify(assets));
    a.collections.forEach((c) => c.items.forEach((it, i) => {
      it.preview = i % 2 ? "javascript:window.__pwned=1" : "https://evil.example/x.svg";
      it.files.forEach((f) => { f.path = i % 2 ? "javascript:window.__pwned=1" : "//evil.example/x.svg"; });
      it.pa = evilText;
    }));
    await page.route("**/site/data/gallery.json", (r) => r.fulfill({ contentType: "application/json", body: JSON.stringify(g) }));
    await page.route("**/site/data/assets.json", (r) => r.fulfill({ contentType: "application/json", body: JSON.stringify(a) }));
    await page.route(/^https?:\/\/(?!localhost)/, (r) => r.abort());
    await page.goto(URL);
    await page.waitForSelector(".carousel .card");
    await page.waitForSelector(".asset");
    for (let i = 0; i < 3; i++) {
      await openCard(page, page.locator(".card:not([data-copy])").nth(i));
      await page.keyboard.press("Escape");
      await page.waitForTimeout(200);
    }
    const bad = await page.evaluate(() => [...document.querySelectorAll("[src], [href]")]
      .map((e) => e.getAttribute("src") || e.getAttribute("href"))
      .filter((u) => /^\s*javascript:/i.test(u) || /evil\.example/.test(u) || /\.\./.test(u)));
    check("hostile data: no javascript:, foreign or ../ URLs reach the page", !bad.length, bad.slice(0, 3).join(" | "));
    const injected = await page.evaluate(() => !!window.__pwned || document.querySelectorAll("[onerror], [onload], svg script").length);
    check("hostile data: titles are shown as text and never run as code", !injected);
    await ctx.close();
  }

  /* ===== reduced motion ===== */
  {
    const { ctx, page } = await open(browser, { viewport: { width: 1280, height: 900 }, reducedMotion: "reduce" });
    const L = await firstLoopingIndex(page);
    check("reduced motion: carousels do not move", L === -1 || !(await rolls(page, Math.max(L, 0), 1200)));
    const copiesShown = await page.evaluate(() => [...document.querySelectorAll(".card[data-copy]")].some((c) => c.offsetParent));
    check("reduced motion: duplicate cards are hidden", !copiesShown);
    await ctx.close();
  }

  await browser.close();
  server.close();
  console.log(failures ? `\n${failures} check(s) failed` : "\nall checks passed");
  process.exit(failures ? 1 : 0);
})();
