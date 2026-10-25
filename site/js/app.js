/*
  ਸਿੱਖੀ ਸੋਲ — page behaviour
  SPDX-License-Identifier: GPL-3.0-or-later

  Three independent parts:
    Gallery  (#chitra-mala) <- site/data/gallery.json   endless carousels, one per category
    Viewer   (#viewer)                                   image details in a modal dialog
    Library  (#bhandar)     <- site/data/assets.json    tabbed grid with search and downloads

  No framework and no build step. To change content, edit the JSON files
  (see docs/SITE.md); this script should rarely need touching.
  Behaviour is covered by tests/site.test.js (see docs/SITE.md › Testing).
*/
(function () {
  "use strict";

  /* ---------- settings ---------- */

  var SPEED_PX_PER_SEC = 40;   // how fast a carousel rolls
  var RESUME_AFTER_MS = 2500;  // a carousel waits this long after the visitor stops touching it
  var MIN_LOOP = 3;            // fewer images than this: shown still, not looped
  // Wikimedia only serves certain thumbnail widths; 500 and 1280 are two of them.
  var REMOTE_WIDTH = 500;
  var REMOTE_WIDTH_LARGE = 1280;
  // Shown when an image cannot be loaded (offline, or blocked): a quiet motif, never broken alt text.
  var PLACEHOLDER = "assets/01_borders_burhanpuri/motifs/bur_b01_motif.svg";

  var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- small helpers ---------- */

  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      // Never set event-handler attributes from here; text always goes in as text, never as HTML.
      if (/^on/i.test(k)) throw new Error("el(): refusing attribute " + k);
      if (k === "text") node.textContent = attrs[k];
      else if (k === "class") node.className = attrs[k];
      else node.setAttribute(k, attrs[k]);
    });
    (children || []).forEach(function (c) { if (c) node.appendChild(c); });
    return node;
  }

  function loadJSON(url) {
    return fetch(url).then(function (r) {
      if (!r.ok) throw new Error(url + " " + r.status);
      return r.json();
    });
  }

  /* ---- Safe URLs ----
     Every link and image address that comes from the JSON data is checked against these patterns
     before it reaches the page. If a data file were ever edited carelessly or maliciously, the worst
     outcome is a placeholder image or a missing link, never a "javascript:" URL or a foreign site. */
  var SAFE_LOCAL_IMAGE = /^gallery\/[a-z]+\/[a-z0-9-]+\.(jpe?g|png)$/;
  var SAFE_ASSET_PATH = /^assets\/[0-9A-Za-z_\/-]+(\.[0-9A-Za-z_-]+)*\.svg$/;
  var SAFE_SOURCE_PAGE = /^https:\/\/commons\.wikimedia\.org\/wiki\/File:[^\s"'<>\\]+$/;

  function safeLocal(path, pattern) {
    return typeof path === "string" && pattern.test(path) && path.indexOf("..") === -1 ? path : null;
  }

  function commonsName(item) {
    return typeof item.commons === "string" && item.commons.length ? item.commons : null;
  }

  function imageSrc(item, width) {
    var local = safeLocal(item.local, SAFE_LOCAL_IMAGE);
    if (local) return local;
    var name = commonsName(item);
    if (!name) return PLACEHOLDER;
    return "https://commons.wikimedia.org/wiki/Special:FilePath/" +
      encodeURIComponent(name) + "?width=" + (width || REMOTE_WIDTH);
  }

  function sourcePage(item) {
    if (typeof item.source_page === "string" && SAFE_SOURCE_PAGE.test(item.source_page)) return item.source_page;
    var name = commonsName(item);
    return name ? "https://commons.wikimedia.org/wiki/File:" + encodeURIComponent(name.replace(/ /g, "_")) : null;
  }

  function assetPath(path) {
    return safeLocal(path, SAFE_ASSET_PATH);
  }

  function guardImage(img) {
    img.addEventListener("error", function () {
      if (img.src.indexOf(PLACEHOLDER) !== -1) return;
      img.src = PLACEHOLDER;
      img.classList.add("is-placeholder");
    });
    return img;
  }

  /* ================= Carousel ("Roller") =================
     Each carousel is a horizontally scrollable window holding two identical
     sets of cards. A requestAnimationFrame loop advances scrollLeft; when it
     passes the end of the first set it jumps back by one set width, which
     looks seamless because both sets are identical.
     Because it is a real scroll area, visitors can swipe, drag the trackpad,
     use the ‹ › buttons or the keyboard; rolling pauses while they do and
     resumes RESUME_AFTER_MS later. */

  var rollers = [];
  var globalStill = false;   // the "ਠਹਿਰਾਓ" checkbox
  var viewerOpen = false;

  function Roller(win, looping) {
    this.win = win;
    this.looping = looping && !reduceMotion;
    this.pos = 0;              // exact (fractional) scroll position we drive
    this.hover = false;
    this.lastTouch = -Infinity; // time of last visitor interaction (none yet)
    var self = this;
    ["pointerdown", "wheel", "touchstart", "keydown"].forEach(function (ev) {
      win.addEventListener(ev, function () { self.touched(); }, { passive: true });
    });
    win.addEventListener("mouseenter", function () { self.hover = true; });
    win.addEventListener("mouseleave", function () { self.hover = false; self.touched(); });
    win.addEventListener("scroll", function () { self.wrap(); }, { passive: true });
  }
  Roller.prototype.setWidth = function () {
    return this.looping ? this.win.firstElementChild.scrollWidth / 2 : 0;
  };
  Roller.prototype.touched = function () { this.lastTouch = performance.now(); };
  Roller.prototype.paused = function (now) {
    var a = document.activeElement;
    return !this.looping || globalStill || viewerOpen || this.hover || document.hidden ||
      now - this.lastTouch < RESUME_AFTER_MS ||
      // pause only while a keyboard user is focused inside (not after a mouse/tap click)
      (this.win.contains(a) && a.matches && a.matches(":focus-visible"));
  };
  Roller.prototype.wrap = function () {
    // Keep the scroll position inside [1, setWidth + 1]. Both sets are identical, so a jump
    // of exactly one set width is invisible. The 1px margins stop the two rules undoing each other.
    var w = this.setWidth();
    if (!w) return;
    if (this.win.scrollLeft > w + 1) this.win.scrollLeft -= w;
    else if (this.win.scrollLeft < 1) this.win.scrollLeft += w;
  };
  Roller.prototype.step = function (now, dt) {
    if (!this.win.isConnected) return false;
    // If the visitor moved it, adopt their position.
    if (Math.abs(this.win.scrollLeft - Math.round(this.pos)) > 2) this.pos = this.win.scrollLeft;
    if (this.paused(now)) return true;
    this.pos += SPEED_PX_PER_SEC * dt;
    var w = this.setWidth();
    if (w && this.pos > w + 1) this.pos -= w;
    this.win.scrollLeft = Math.round(this.pos);
    return true;
  };
  Roller.prototype.nudge = function (dir) {
    this.touched();
    var card = this.win.querySelector(".card");
    var by = card ? (card.getBoundingClientRect().width + 16) * 2 : 300;
    this.win.scrollBy({ left: dir * by, behavior: reduceMotion ? "auto" : "smooth" });
  };

  var lastFrame = 0;
  function tick(now) {
    var dt = lastFrame ? Math.min((now - lastFrame) / 1000, 0.1) : 0;
    lastFrame = now;
    rollers = rollers.filter(function (r) { return r.step(now, dt); });
    window.requestAnimationFrame(tick);
  }

  /* ================= Gallery ================= */

  var gallery = null;   // parsed gallery.json

  function fillSelect(select, map) {
    Object.keys(map).forEach(function (key) {
      select.appendChild(el("option", { value: key, text: map[key].pa + " — " + map[key].en }));
    });
  }

  function makeCard(item, isCopy) {
    var era = gallery.eras[item.era] || gallery.eras.unknown;
    var card = el("button", { class: "card", type: "button" }, [
      guardImage(el("img", { src: imageSrc(item), referrerpolicy: "no-referrer", alt: item.pa + " — " + item.en, loading: "lazy", decoding: "async", draggable: "false" })),
      el("div", { class: "card__text" }, [
        el("div", { class: "card__title", text: item.pa }),
        el("div", { class: "card__era", text: era.pa })
      ])
    ]);
    if (isCopy) {
      // Copies exist only to make the loop seamless; hide them from assistive tech and Tab.
      card.setAttribute("data-copy", "");
      card.setAttribute("aria-hidden", "true");
      card.tabIndex = -1;
    }
    card.addEventListener("click", function () { openViewer(item, card); });
    return card;
  }

  function renderGallery() {
    var era = document.getElementById("filter-era").value;
    var guru = document.getElementById("filter-guru").value;
    var host = document.getElementById("carousels");
    host.textContent = "";
    rollers = [];

    var shown = 0;
    Object.keys(gallery.categories).forEach(function (catKey) {
      var items = gallery.items.filter(function (it) {
        return it.category === catKey &&
          (!era || it.era === era) &&
          (!guru || (it.gurus || []).indexOf(guru) !== -1);
      });
      if (!items.length) return;
      shown += items.length;

      var cat = gallery.categories[catKey];
      var looping = items.length >= MIN_LOOP;
      var track = el("div", { class: "carousel__track" });
      if (looping) {
        // One "set" must be wider than the widest screen, so short lists repeat inside it.
        var set = items.slice();
        while (set.length < 7) set = set.concat(items);
        set.forEach(function (it, i) { track.appendChild(makeCard(it, i >= items.length)); });
        set.forEach(function (it) { track.appendChild(makeCard(it, true)); });   // second, identical set
      } else {
        items.forEach(function (it) { track.appendChild(makeCard(it, false)); });
      }

      var win = el("div", { class: "carousel__window", tabindex: "-1" }, [track]);
      var roller = new Roller(win, looping);
      rollers.push(roller);

      var prev = el("button", { class: "carousel__nav", type: "button", "aria-label": "ਪਿੱਛੇ — previous", text: "‹" });
      var next = el("button", { class: "carousel__nav", type: "button", "aria-label": "ਅੱਗੇ — next", text: "›" });
      prev.addEventListener("click", function () { roller.nudge(-1); });
      next.addEventListener("click", function () { roller.nudge(1); });

      host.appendChild(el("section", { class: "carousel" + (looping ? "" : " carousel--still"), "aria-label": cat.pa }, [
        el("div", { class: "carousel__head" }, [
          el("h3", {}, [el("span", { text: cat.pa }), el("span", { class: "en", text: cat.en + " · " + items.length })]),
          el("div", { class: "carousel__navs" }, [prev, next])
        ]),
        win
      ]));
      // start a little in, so the visitor can also scroll left from the start
      if (roller.looping) window.requestAnimationFrame(function () { roller.pos = win.scrollLeft = 1; });
    });

    if (!shown) host.appendChild(el("p", { class: "empty", text: "ਇਸ ਚੋਣ ਲਈ ਅਜੇ ਕੋਈ ਚਿੱਤਰ ਨਹੀਂ। No images for this selection yet." }));
  }

  /* ================= Viewer =================
     Closes with: the ✕ bar button, the "ਵਾਪਸ" button, Esc, a tap outside the
     picture, or the browser/phone Back gesture (we push a history entry when
     it opens). After closing, focus returns to the card without pausing the carousel. */

  var returnFocus = null;

  function openViewer(item, fromCard) {
    var dlg = document.getElementById("viewer");
    var era = gallery.eras[item.era] || gallery.eras.unknown;
    var img = document.getElementById("viewer-img");
    img.classList.remove("is-placeholder");
    img.src = imageSrc(item, REMOTE_WIDTH_LARGE);
    img.alt = item.pa + " — " + item.en;
    document.getElementById("viewer-title").textContent = item.pa;
    document.getElementById("viewer-en").textContent = item.en;

    var gurus = (item.gurus || []).map(function (g) { return gallery.gurus[g] ? gallery.gurus[g].pa : g; }).join(", ");
    var rows = [
      ["ਵੰਨਗੀ", gallery.categories[item.category].pa],
      ["ਸਮਾਂ", era.pa + (item.date ? " (" + item.date + ")" : "")],
      ["ਸਬੰਧ", gurus || "—"],
      ["ਲਾਇਸੈਂਸ", item.licence || "ਵਿਕੀਮੀਡੀਆ ਕਾਮਨਜ਼ ਉੱਤੇ ਵੇਖੋ"],
      ["ਕਰਤਾ", item.author || "—"]
    ];
    var meta = document.getElementById("viewer-meta");
    meta.textContent = "";
    rows.forEach(function (r) {
      meta.appendChild(el("dt", { text: r[0] }));
      meta.appendChild(el("dd", { text: r[1] }));
    });
    var source = sourcePage(item);
    meta.appendChild(el("dt", { text: "ਮੂਲ ਸਰੋਤ" }));
    meta.appendChild(el("dd", source ? {} : { text: "—" }, source ? [el("a", {
      href: source, target: "_blank", rel: "noopener noreferrer external", referrerpolicy: "no-referrer",
      text: "Wikimedia Commons"
    })] : []));

    if (typeof dlg.showModal !== "function") {
      if (source) window.open(source, "_blank", "noopener,noreferrer");
      return;
    }
    returnFocus = fromCard || null;
    viewerOpen = true;
    dlg.showModal();
    dlg.scrollTop = 0;
    document.getElementById("viewer-close").focus({ preventScroll: true });
    // A history entry so Back (browser button, phone swipe) closes the viewer instead of leaving the page.
    if (!(history.state && history.state.viewer)) history.pushState({ viewer: true }, "");
  }

  function closeViewer(fromHistory) {
    var dlg = document.getElementById("viewer");
    if (!dlg.open) return;
    dlg.close();                       // fires "close" -> afterClose()
    if (!fromHistory && history.state && history.state.viewer) history.back();
  }

  function afterClose() {
    viewerOpen = false;
    // Give focus back to the card that opened the viewer (keyboard users keep their place).
    // The carousel only stays paused for *keyboard* focus (:focus-visible), so after a
    // mouse click or tap it simply rolls on.
    if (returnFocus && returnFocus.isConnected) returnFocus.focus({ preventScroll: true });
    returnFocus = null;
    rollers.forEach(function (r) { r.touched(); });  // a short, gentle pause before rolling on
  }

  function initViewer() {
    var dlg = document.getElementById("viewer");
    document.getElementById("viewer-close").addEventListener("click", function () { closeViewer(false); });
    document.getElementById("viewer-back").addEventListener("click", function () { closeViewer(false); });
    dlg.addEventListener("cancel", function (e) { e.preventDefault(); closeViewer(false); });   // Esc
    dlg.addEventListener("close", afterClose);
    // tap/click on the dimmed backdrop (the dialog element itself, outside its content box)
    dlg.addEventListener("click", function (e) {
      if (e.target !== dlg) return;
      var r = dlg.getBoundingClientRect();
      var inside = e.clientX >= r.left && e.clientX <= r.right && e.clientY >= r.top && e.clientY <= r.bottom;
      if (!inside) closeViewer(false);
    });
    window.addEventListener("popstate", function () { closeViewer(true); });
  }

  function initGallery() {
    return loadJSON("site/data/gallery.json").then(function (data) {
      gallery = data;
      // Only offer eras that actually occur, in the catalogue's order.
      var usedEras = {};
      data.items.forEach(function (it) { usedEras[it.era] = true; });
      var eras = {};
      Object.keys(data.eras).forEach(function (k) { if (usedEras[k]) eras[k] = data.eras[k]; });
      fillSelect(document.getElementById("filter-era"), eras);
      fillSelect(document.getElementById("filter-guru"), data.gurus);

      document.getElementById("filter-era").addEventListener("change", renderGallery);
      document.getElementById("filter-guru").addEventListener("change", renderGallery);
      document.getElementById("filter-still").addEventListener("change", function (e) {
        globalStill = e.target.checked;
        if (!globalStill) rollers.forEach(function (r) { r.lastTouch = -Infinity; });
      });
      renderGallery();
      window.requestAnimationFrame(tick);
    }).catch(function (err) {
      document.getElementById("carousels").textContent = "ਚਿੱਤਰ-ਮਾਲਾ ਲੋਡ ਨਹੀਂ ਹੋ ਸਕੀ। (" + err.message + ")";
    });
  }

  /* ================= Library ================= */

  var library = null;     // parsed assets.json
  var activeTab = 0;

  function renderTabs() {
    var tabs = document.getElementById("library-tabs");
    tabs.textContent = "";
    library.collections.forEach(function (col, i) {
      var b = el("button", { type: "button", role: "tab", "aria-selected": String(i === activeTab) }, [
        document.createTextNode(col.pa + " (" + col.items.length + ")")
      ]);
      b.title = col.en;
      b.addEventListener("click", function () { activeTab = i; renderTabs(); renderGrid(); });
      tabs.appendChild(b);
    });
  }

  function renderGrid() {
    var q = document.getElementById("library-search").value.trim().toLowerCase();
    var grid = document.getElementById("library-grid");
    grid.textContent = "";

    // A search looks across every collection; otherwise show the active tab.
    var pool = q
      ? library.collections.reduce(function (all, c) { return all.concat(c.items); }, [])
      : library.collections[activeTab].items;
    var items = pool.filter(function (it) {
      return !q || (it.pa + " " + it.en + " " + it.note + " " + it.id).toLowerCase().indexOf(q) !== -1;
    });

    items.forEach(function (it) {
      var files = it.files.filter(function (f) { return assetPath(f.path); }).map(function (f) {
        return el("a", { class: "button", href: assetPath(f.path), download: "", text: "⤓ " + f.label_pa + (f.label_pa !== f.label_en.toUpperCase() ? " · " + f.label_en : "") });
      });
      grid.appendChild(el("article", { class: "asset" }, [
        el("div", { class: "asset__preview" }, [guardImage(el("img", { src: assetPath(it.preview) || PLACEHOLDER, alt: it.pa, loading: "lazy" }))]),
        el("div", { class: "asset__title", text: it.pa }),
        el("div", { class: "en", text: it.en }),
        it.note ? el("div", { class: "asset__note", text: it.note }) : null,
        el("div", { class: "asset__files" }, files)
      ]));
    });
    if (!items.length) grid.appendChild(el("p", { class: "empty", text: "ਕੁਝ ਨਹੀਂ ਮਿਲਿਆ। Nothing found." }));
  }

  function initLibrary() {
    return loadJSON("site/data/assets.json").then(function (data) {
      library = data;
      renderTabs();
      renderGrid();
      document.getElementById("library-search").addEventListener("input", renderGrid);
    }).catch(function (err) {
      document.getElementById("library-grid").textContent = "ਭੰਡਾਰ ਲੋਡ ਨਹੀਂ ਹੋ ਸਕਿਆ। (" + err.message + ")";
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initViewer();
    initGallery();
    initLibrary();
  });
})();
