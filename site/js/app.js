/*
  ਸਿੱਖੀ ਸੋਲ — page behaviour
  SPDX-License-Identifier: GPL-3.0-or-later

  Two independent parts, each driven by a JSON file:
    Gallery  (#chitra-mala) <- site/data/gallery.json   endless carousels, one per category
    Library  (#bhandar)     <- site/data/assets.json    tabbed grid with search and downloads

  No framework and no build step. To change content, edit the JSON files
  (see docs/SITE.md); this script should rarely need touching.
*/
(function () {
  "use strict";

  // Seconds each card stays in view while a carousel rolls. Lower = faster.
  var SECONDS_PER_CARD = 5;
  // A category needs at least this many images (and must be wider than the screen) to roll endlessly.
  var MIN_LOOP = 3;
  // Width requested from Wikimedia when an image has not been downloaded locally yet.
  var REMOTE_WIDTH = 480;

  /* ---------- small helpers ---------- */

  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
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

  function imageSrc(item, width) {
    if (item.local) return item.local;
    return "https://commons.wikimedia.org/wiki/Special:FilePath/" +
      encodeURIComponent(item.commons) + "?width=" + (width || REMOTE_WIDTH);
  }

  function sourcePage(item) {
    return item.source_page ||
      "https://commons.wikimedia.org/wiki/File:" + encodeURIComponent(item.commons.replace(/ /g, "_"));
  }

  /* ================= Gallery ================= */

  var gallery = null;   // parsed gallery.json

  function fillSelect(select, map) {
    Object.keys(map).forEach(function (key) {
      select.appendChild(el("option", { value: key, text: map[key].pa + " — " + map[key].en }));
    });
  }

  // Shown when an image cannot be loaded (offline, or blocked): a quiet motif, never broken alt text.
  var PLACEHOLDER = "assets/01_borders_burhanpuri/motifs/bur_b01_motif.svg";
  function guardImage(img) {
    img.addEventListener("error", function onErr() {
      img.removeEventListener("error", onErr);
      img.src = PLACEHOLDER;
      img.classList.add("is-placeholder");
    });
    return img;
  }

  function makeCard(item, isCopy) {
    var era = gallery.eras[item.era] || gallery.eras.unknown;
    var card = el("button", { class: "card", type: "button" }, [
      guardImage(el("img", { src: imageSrc(item), alt: item.pa + " — " + item.en, loading: "lazy", decoding: "async" })),
      el("div", { class: "card__text" }, [
        el("div", { class: "card__title", text: item.pa }),
        el("div", { class: "card__era", text: era.pa })
      ])
    ]);
    if (isCopy) {
      // The second copy exists only to make the loop seamless; hide it from assistive tech.
      card.setAttribute("data-copy", "");
      card.setAttribute("aria-hidden", "true");
      card.tabIndex = -1;
    }
    card.addEventListener("click", function () { openViewer(item); });
    return card;
  }

  function renderGallery() {
    var era = document.getElementById("filter-era").value;
    var guru = document.getElementById("filter-guru").value;
    var host = document.getElementById("carousels");
    host.textContent = "";

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
      var track = el("div", { class: "carousel__track" });
      // Fewer than MIN_LOOP images: show them still; looping one or two pictures looks careless.
      var looping = items.length >= MIN_LOOP;
      if (looping) {
        // One "set" must be wider than the widest screen, so short lists repeat inside it.
        var set = items.slice();
        while (set.length < 7) set = set.concat(items);
        set.forEach(function (it, i) { track.appendChild(makeCard(it, i >= items.length)); });
        // A second identical set; the CSS animation slides by exactly one set (-50%) and repeats.
        set.forEach(function (it) { track.appendChild(makeCard(it, true)); });
        track.style.setProperty("--duration", (set.length * SECONDS_PER_CARD) + "s");
      } else {
        items.forEach(function (it) { track.appendChild(makeCard(it, false)); });
      }

      host.appendChild(el("section", { class: "carousel" + (looping ? "" : " carousel--still"), "aria-label": cat.pa }, [
        el("h3", {}, [el("span", { text: cat.pa }), el("span", { class: "en", text: cat.en + " · " + items.length })]),
        el("div", { class: "carousel__window" }, [track])
      ]));
    });

    if (!shown) host.appendChild(el("p", { class: "empty", text: "ਇਸ ਚੋਣ ਲਈ ਅਜੇ ਕੋਈ ਚਿੱਤਰ ਨਹੀਂ। No images for this selection yet." }));
  }

  function openViewer(item) {
    var dlg = document.getElementById("viewer");
    var era = gallery.eras[item.era] || gallery.eras.unknown;
    var img = document.getElementById("viewer-img");
    img.classList.remove("is-placeholder");
    if (!img.dataset.guarded) { guardImage(img); img.dataset.guarded = "1"; }
    img.src = imageSrc(item, 1200);
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
    meta.appendChild(el("dt", { text: "ਮੂਲ ਸਰੋਤ" }));
    meta.appendChild(el("dd", {}, [el("a", { href: sourcePage(item), target: "_blank", rel: "noopener", text: "Wikimedia Commons" })]));

    if (typeof dlg.showModal === "function") dlg.showModal();
    else window.open(sourcePage(item), "_blank", "noopener");
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
        document.getElementById("carousels").classList.toggle("is-still", e.target.checked);
      });
      renderGallery();
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
      var files = it.files.map(function (f) {
        return el("a", { class: "button", href: f.path, download: "", text: "⤓ " + f.label_pa + (f.label_pa !== f.label_en.toUpperCase() ? " · " + f.label_en : "") });
      });
      grid.appendChild(el("article", { class: "asset" }, [
        el("div", { class: "asset__preview" }, [el("img", { src: it.preview, alt: it.pa, loading: "lazy" })]),
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
    initGallery();
    initLibrary();
  });
})();
