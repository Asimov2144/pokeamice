/* The scan reader (interview-body-scan.html): the page on the stage, the text
   beside it, and the ties between them.

   - the stage shows one page; ‹ › the strip, ← → and the 下一页 links turn it,
     and turning it scrolls the text to that page
   - the text pane scrolls; the page whose section is under the middle of the
     window is the one on the stage (follow reading)
   - a region with a box: the paragraph under the pointer (or focused, or
     clicked) lights its box on the page; the box clicked on the page scrolls
     to its paragraph and flashes it
   - a caption's crop (.sc-crop) is cut from the page image itself, around
     the caption's box, once that image is loaded
   - zoom, drag to pan, 整页 opens the image; on a phone the stage is a strip
     and tapping it opens the page full screen
   - the ⚙ switch 竖排原文 sets the original of a vertical region vertically
   Only the current page and its neighbours have their image loaded. */
(function () {
  "use strict";
  var root = document.querySelector("[data-parallel-translation]");
  var reader = document.querySelector("[data-scan-reader]");
  if (!root || !reader) return;
  var stage = reader.querySelector("[data-scan-stage]");
  var view = reader.querySelector("[data-scan-viewport]");
  var canvas = reader.querySelector("[data-scan-canvas]");
  var text = reader.querySelector("[data-scan-text]");
  if (!stage || !view || !canvas || !text) return;
  var plates = Array.prototype.slice.call(canvas.querySelectorAll("[data-scan-page]"));
  var sections = Array.prototype.slice.call(text.querySelectorAll("[data-scan-page-section]"));
  var blocks = Array.prototype.slice.call(text.querySelectorAll("[data-scan-page-index]"));
  var strip = Array.prototype.slice.call(reader.querySelectorAll("[data-scan-strip] a"));
  var current = -1, zoom = 1, active = null, lastTurn = 0;
  var phone = window.matchMedia("(max-width: 900px)");

  function plateOf(i) { return plates[i] || null; }
  function imgOf(i) { var p = plateOf(i); return p ? p.querySelector(".sc-plate__img") : null; }
  function svgOf(i) { var p = plateOf(i); return p ? p.querySelector("[data-scan-hotspots]") : null; }

  // ---- images: the current page and its neighbours only ------------------
  function load(i) {
    var img = imgOf(i);
    if (!img) return null;
    if (!img.getAttribute("src") && img.dataset.src) img.src = img.dataset.src;
    return img;
  }
  function ready(img, fn) {
    if (!img) return;
    if (img.complete && img.naturalWidth) fn(img);
    else img.addEventListener("load", function () { fn(img); }, { once: true });
  }
  // the overlay maps the image's pixel space onto its box
  function fitSvg(i) {
    var img = imgOf(i), svg = svgOf(i);
    if (!img || !svg || svg.getAttribute("viewBox")) return;
    ready(img, function () { svg.setAttribute("viewBox", "0 0 " + img.naturalWidth + " " + img.naturalHeight); });
  }

  // ---- the page on the stage -----------------------------------------------
  function show(i, why) {
    if (!plates.length) return;
    i = Math.max(0, Math.min(plates.length - 1, i));
    if (i === current) return;
    current = i;
    plates.forEach(function (p, k) { p.hidden = k !== i; });
    strip.forEach(function (a) { a.classList.toggle("is-active", Number(a.dataset.scanGoto) === i); });
    var num = reader.querySelector("[data-scan-current]");
    if (num) num.textContent = String(i + 1);
    var open = reader.querySelector("[data-scan-open]"), img = load(i);
    if (open) { open.href = img ? (img.getAttribute("src") || img.dataset.src) : "#"; open.hidden = !img; }
    fitSvg(i);
    load(i + 1); load(i - 1);
    if (why !== "scroll") view.scrollTop = 0;
    clearHighlight();
    cropsOf(i);
  }
  function goTo(i, andScroll) {
    show(i, "nav");
    lastTurn = Date.now();
    if (andScroll && sections[i]) {
      var top = sections[i].getBoundingClientRect().top + window.pageYOffset - 72;
      window.scrollTo({ top: top, behavior: "smooth" });
    }
  }
  reader.querySelectorAll("[data-scan-prev]").forEach(function (b) { b.addEventListener("click", function () { goTo(current - 1, true); }); });
  reader.querySelectorAll("[data-scan-next]").forEach(function (b) { b.addEventListener("click", function () { goTo(current + 1, true); }); });
  reader.querySelectorAll("[data-scan-goto]").forEach(function (a) {
    a.addEventListener("click", function (e) { e.preventDefault(); goTo(Number(a.dataset.scanGoto), true); });
  });
  window.addEventListener("keydown", function (e) {
    if (e.defaultPrevented || e.altKey || e.ctrlKey || e.metaKey) return;
    var t = e.target;
    if (t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.isContentEditable)) return;
    if (e.key === "ArrowLeft") { goTo(current - 1, true); e.preventDefault(); }
    if (e.key === "ArrowRight") { goTo(current + 1, true); e.preventDefault(); }
  });

  // follow reading: the section under the middle of the window is the page
  if ("IntersectionObserver" in window && sections.length) {
    var io = new IntersectionObserver(function (entries) {
      if (Date.now() - lastTurn < 900) return;   // a turn the reader asked for is settling
      entries.forEach(function (en) {
        if (en.isIntersecting) show(Number(en.target.dataset.scanPageSection), "scroll");
      });
    }, { rootMargin: "-45% 0px -45% 0px", threshold: 0 });
    sections.forEach(function (s) { io.observe(s); });
  }

  // ---- zoom and pan ----------------------------------------------------------
  function setZoom(z) {
    zoom = Math.min(3, Math.max(1, z));
    canvas.style.width = (zoom * 100) + "%";
    stage.classList.toggle("is-zoomed", zoom > 1);
  }
  reader.querySelectorAll("[data-scan-zoom-in]").forEach(function (b) { b.addEventListener("click", function () { setZoom(zoom + 0.25); }); });
  reader.querySelectorAll("[data-scan-zoom-out]").forEach(function (b) { b.addEventListener("click", function () { setZoom(zoom - 0.25); }); });
  reader.querySelectorAll("[data-scan-zoom-reset]").forEach(function (b) { b.addEventListener("click", function () { setZoom(1); view.scrollTo({ top: 0, left: 0 }); }); });
  var drag = null;
  view.addEventListener("mousedown", function (e) {
    if (e.button !== 0 || e.target.closest("rect, a, button")) return;
    drag = { x: e.clientX, y: e.clientY, l: view.scrollLeft, t: view.scrollTop };
    view.classList.add("is-dragging");
    e.preventDefault();
  });
  window.addEventListener("mousemove", function (e) {
    if (!drag) return;
    view.scrollLeft = drag.l - (e.clientX - drag.x);
    view.scrollTop = drag.t - (e.clientY - drag.y);
  });
  window.addEventListener("mouseup", function () { if (drag) { drag = null; view.classList.remove("is-dragging"); } });

  // ---- ties: paragraph <-> box -----------------------------------------------
  function boxesOf(el) {
    var all = el.dataset.scanBoxes || el.dataset.scanBox || "";
    return all.split(";").map(function (s) { return s.split(",").map(Number); }).filter(function (b) { return b.length === 4 && !b.some(isNaN); });
  }
  function clearHighlight() {
    plates.forEach(function (p) {
      var h = p.querySelector("[data-scan-highlight]");
      if (h) { h.setAttribute("width", "0"); h.setAttribute("height", "0"); h.classList.remove("is-on"); }
      p.querySelectorAll(".sc-hotspot.is-on").forEach(function (r) { r.classList.remove("is-on"); });
    });
  }
  function highlight(el, scroll) {
    var i = Number(el.dataset.scanPageIndex);
    var boxes = boxesOf(el);
    var svg = svgOf(i);
    clearHighlight();
    if (!svg || !boxes.length) return;
    var b = boxes[0], h = svg.querySelector("[data-scan-highlight]");
    if (h) {
      h.setAttribute("x", b[0]); h.setAttribute("y", b[1]);
      h.setAttribute("width", b[2] - b[0]); h.setAttribute("height", b[3] - b[1]);
      h.classList.add("is-on");
    }
    svg.querySelectorAll('[data-scan-seg="' + el.id + '"]').forEach(function (r) { r.classList.add("is-on"); });
    if (scroll && !phone.matches) {
      var img = imgOf(i);
      ready(img, function () {
        var k = img.clientHeight / img.naturalHeight;
        var y = b[1] * k, hgt = (b[3] - b[1]) * k;
        if (y < view.scrollTop + 8 || y + hgt > view.scrollTop + view.clientHeight - 8) {
          view.scrollTo({ top: Math.max(0, y - Math.max(24, (view.clientHeight - hgt) / 3)), behavior: "smooth" });
        }
      });
    }
  }
  function activate(el, scroll) {
    if (!el) return;
    if (active && active !== el) active.classList.remove("is-active");
    active = el;
    el.classList.add("is-active");
    var i = Number(el.dataset.scanPageIndex);
    if (i !== current) { show(i, "tie"); lastTurn = Date.now(); }
    highlight(el, scroll);
  }
  blocks.forEach(function (el) {
    el.addEventListener("mouseenter", function () {
      // a hover only points; it does not turn the page under the reader
      if (Number(el.dataset.scanPageIndex) === current) { if (active !== el) { if (active) active.classList.remove("is-active"); active = el; el.classList.add("is-active"); } highlight(el, true); }
    });
    el.addEventListener("click", function (e) {
      if (e.target.closest("a, button, summary")) return;
      activate(el, true);
    });
    el.addEventListener("focusin", function () { activate(el, true); });
  });
  canvas.addEventListener("click", function (e) {
    var r = e.target.closest("[data-scan-seg]");
    if (!r) return;
    var el = document.getElementById(r.dataset.scanSeg);
    if (!el) return;
    lastTurn = Date.now();
    el.scrollIntoView({ block: "center", behavior: "smooth" });
    activate(el, false);
    el.classList.remove("is-flash"); void el.offsetWidth; el.classList.add("is-flash");
    if (el.querySelector("summary") && root.getAttribute("data-view") === "translation") {
      // the page shows the original; open it here too so the reader sees the same words
      var d = el.querySelector("details.parallel-text__cell--original");
      if (d) d.open = true;
    }
  });
  canvas.addEventListener("mouseover", function (e) {
    var r = e.target.closest("[data-scan-seg]");
    if (!r) return;
    var el = document.getElementById(r.dataset.scanSeg);
    if (el && el !== active) { blocks.forEach(function (b) { b.classList.remove("is-peek"); }); el.classList.add("is-peek"); }
  });
  canvas.addEventListener("mouseout", function (e) {
    if (e.target.closest("[data-scan-seg]")) blocks.forEach(function (b) { b.classList.remove("is-peek"); });
  });

  // ---- crops: a caption's neighbourhood, from the page image ----------------
  var cropIo = ("IntersectionObserver" in window) ? new IntersectionObserver(function (entries) {
    entries.forEach(function (en) { if (en.isIntersecting) { cut(en.target); cropIo.unobserve(en.target); } });
  }, { rootMargin: "200px 0px" }) : null;
  function cut(el) {
    var i = Number(el.dataset.scanPageIndex), img = load(i), b = boxesOf(el)[0];
    if (!img || !b) return;
    ready(img, function () {
      var W = img.naturalWidth, H = img.naturalHeight;
      var cw = el.clientWidth || 72, ch = el.clientHeight || 72;
      // a square around the caption, a little wider than it, so the picture it names is in the cut
      var side = Math.max(b[2] - b[0], b[3] - b[1]) * 1.5, cx = (b[0] + b[2]) / 2, cy = (b[1] + b[3]) / 2;
      side = Math.max(side, 160);
      var k = cw / side;
      el.style.backgroundImage = "url(\"" + (img.currentSrc || img.src) + "\")";
      el.style.backgroundSize = (W * k) + "px " + (H * k) + "px";
      el.style.backgroundPosition = (-(cx - side / 2) * k) + "px " + (-(cy - side / 2) * k + (ch - cw) / 2) + "px";
      el.classList.add("is-cut");
    });
  }
  function cropsOf(i) {
    text.querySelectorAll('[data-scan-crop][data-scan-page-index="' + i + '"]').forEach(function (el) { if (!el.classList.contains("is-cut")) cut(el); });
  }
  text.querySelectorAll("[data-scan-crop]").forEach(function (el) { if (cropIo) cropIo.observe(el); });

  // ---- the page on a phone: full screen --------------------------------------
  var box = reader.querySelector("[data-scan-lightbox]");
  function openLightbox() {
    if (!box) return;
    var img = load(current);
    if (!img) return;
    var holder = box.querySelector("[data-scan-lightbox-view]");
    holder.innerHTML = "";
    var big = document.createElement("img");
    big.src = img.getAttribute("src") || img.dataset.src;
    big.alt = img.alt;
    holder.appendChild(big);
    var title = box.querySelector("[data-scan-lightbox-title]");
    if (title) title.textContent = "第 " + (current + 1) + " / " + plates.length + " 页";
    box.hidden = false;
    document.body.classList.add("sc-lightbox-open");
    var b = active && Number(active.dataset.scanPageIndex) === current ? boxesOf(active)[0] : null;
    ready(big, function () {
      if (!b) return;
      var k = big.clientHeight / big.naturalHeight;
      holder.scrollTo({ top: Math.max(0, b[1] * k - 60), left: Math.max(0, b[0] * k - 20) });
    });
  }
  function closeLightbox() { if (box) { box.hidden = true; document.body.classList.remove("sc-lightbox-open"); } }
  if (box) {
    box.querySelectorAll("[data-scan-lightbox-close]").forEach(function (b) { b.addEventListener("click", closeLightbox); });
    window.addEventListener("keydown", function (e) { if (e.key === "Escape" && !box.hidden) closeLightbox(); });
    view.addEventListener("click", function (e) {
      if (!phone.matches || e.target.closest("rect, a, button")) return;
      openLightbox();
    });
  }

  // ---- vertical originals: the ⚙ switch ---------------------------------------
  var vKey = "scanVerticalOriginal";
  var vBtn = root.querySelector("[data-vertical-toggle]");
  function setVertical(on) {
    root.classList.toggle("is-vertical-orig", on);
    if (vBtn) { vBtn.classList.toggle("is-active", on); vBtn.setAttribute("aria-pressed", on ? "true" : "false"); }
    try { localStorage.setItem(vKey, on ? "1" : "0"); } catch (e) {}
  }
  var vStored = null;
  try { vStored = localStorage.getItem(vKey); } catch (e) {}
  setVertical(vStored !== "0");
  if (vBtn) vBtn.addEventListener("click", function () { setVertical(!root.classList.contains("is-vertical-orig")); });

  // ---- arriving by anchor: the page first, then the paragraph -----------------
  function byHash() {
    var h = location.hash || "";
    var m = h.match(/^#scan-page-(\d+)$/);
    if (m) { goTo(Number(m[1]) - 1, false); return; }
    if (/^#segment-\d+$/.test(h)) {
      var el = document.getElementById(h.slice(1));
      if (el && el.dataset.scanPageIndex !== undefined) { activate(el, true); lastTurn = Date.now(); }
    }
  }
  window.addEventListener("hashchange", byHash);
  setZoom(1);
  show(0, "init");
  byHash();
})();
