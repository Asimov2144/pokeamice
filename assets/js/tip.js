/* Tooltips and hover cards for the whole site.
 *
 * One tooltip element, filled on demand, for three kinds of anchor:
 *
 *   [data-tip="…"]            a line of text, shown at once (with
 *                             data-tip-if-clipped: only while the element's
 *                             own text is cut off; data-tip-pos="bottom"
 *                             puts it under the anchor)
 *   [title="…"]               the browser's own tooltip, upgraded: the title is
 *                             moved into data-tip on first hover so the native
 *                             one (a second late, unstyled, absent on touch)
 *                             never shows
 *   a[href="/people/<slug>/"] a hover card: portrait, name, role, how many
 *   [data-tip-person="slug"]  entries and credits, the profile's first line
 *   a[href="/credits/<slug>/"] a hover card for a game: icon, title, year,
 *   [data-tip-work="slug"]    developer, names on the credits, entries about it
 *
 * The cards read assets/js/tips.json, fetched once on the first card hover.
 * Hover shows after a short delay (longer for a card, so scanning a list does
 * not flash cards); keyboard focus shows at once and wires aria-describedby;
 * a touch on a non-link anchor toggles it. Esc, scrolling or leaving hides it.
 * Positioned above the anchor, below when there is no room, kept inside the
 * viewport; the arrow follows the anchor. No jQuery.
 */
(function () {
  "use strict";
  if (!document.body || !("closest" in Element.prototype)) return;

  var ID = "site-tip";
  var DATA_URL = document.body.getAttribute("data-tips-url") || "/assets/js/tips.json";
  var SEL = "[data-tip],[data-tip-person],[data-tip-work],[title],a[href*='/people/'],a[href*='/credits/']";
  var PEOPLE_RE = /\/people\/([a-z0-9][a-z0-9-]*)\/?(?:[#?].*)?$/i;
  var WORK_RE = /\/credits\/([a-z0-9][a-z0-9-]*)\/?(?:[#?].*)?$/i;
  var DELAY_TEXT = 90, DELAY_CARD = 240;
  var reduce = false;
  try { reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches; } catch (_) {}

  var tip, arrow, inner;
  var current = null;      // the anchor the tip is for
  var showTimer = 0, byFocus = false, byTouch = false;
  var data = null, loading = null;

  function ensure() {
    if (tip) return;
    tip = document.createElement("div");
    tip.id = ID;
    tip.className = "tip";
    tip.setAttribute("role", "tooltip");
    tip.hidden = true;
    inner = document.createElement("div");
    inner.className = "tip__inner";
    arrow = document.createElement("i");
    arrow.className = "tip__arrow";
    tip.appendChild(inner);
    tip.appendChild(arrow);
    document.body.appendChild(tip);
  }

  /* ---- what an element wants ------------------------------------------- */
  function want(el) {
    if (!el || el.closest("#" + ID) || el.closest(".masthead .site-title")) return null;
    var s = el.getAttribute("data-tip-person");
    if (s) return { kind: "person", key: s };
    s = el.getAttribute("data-tip-work");
    if (s) return { kind: "work", key: s };
    var text = el.getAttribute("data-tip");
    if (text) {
      /* a clipped line (the trail's last crumb) tells its whole self only when it is clipped */
      if (el.hasAttribute("data-tip-if-clipped") && el.scrollWidth <= el.clientWidth + 1) return null;
      return { kind: "text", text: text, pos: el.getAttribute("data-tip-pos") || "" };
    }
    var title = el.getAttribute("title");
    if (title && el.tagName !== "IFRAME" && !el.hasAttribute("data-tip-native")) {
      el.setAttribute("data-tip", title);
      el.removeAttribute("title");
      return { kind: "text", text: title, pos: el.getAttribute("data-tip-pos") || "" };
    }
    if (el.tagName === "A") {
      var href = el.getAttribute("href") || "";
      var m = PEOPLE_RE.exec(href);
      if (m) return { kind: "person", key: m[1] };
      m = WORK_RE.exec(href);
      if (m) return { kind: "work", key: m[1] };
    }
    return null;
  }

  function anchorOf(target) {
    var el = target && target.closest ? target.closest(SEL) : null;
    while (el) {
      var w = want(el);
      if (w) return { el: el, w: w };
      var up = el.parentElement;
      el = up && up.closest ? up.closest(SEL) : null;
    }
    return null;
  }

  /* ---- the cards -------------------------------------------------------- */
  function load() {
    if (data) return Promise.resolve(data);
    if (loading) return loading;
    loading = fetch(DATA_URL, { credentials: "same-origin" })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (j) { data = j || { people: {}, works: {} }; return data; })
      .catch(function () { data = { people: {}, works: {} }; return data; });
    return loading;
  }

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  function personCard(p) {
    var card = el("div", "tip__card tip__card--person");
    if (p.a) {
      var img = el("img", "tip__avatar");
      img.src = p.a; img.alt = ""; img.width = 48; img.height = 48; img.loading = "eager";
      card.appendChild(img);
    } else {
      card.appendChild(el("span", "tip__avatar tip__avatar--blank", (p.n || "").slice(0, 1)));
    }
    var body = el("div", "tip__body");
    body.appendChild(el("b", "tip__name", p.n));
    if (p.r) body.appendChild(el("span", "tip__role", p.r));
    var facts = [];
    if (p.i) facts.push(p.k && p.k !== p.i ? "访谈 " + p.i + " 篇 · 发言 " + p.k + " 篇" : "访谈 " + p.i + " 篇");
    if (p.g) facts.push("署名 " + p.g + " 作");
    if (facts.length) body.appendChild(el("span", "tip__facts", facts.join(" · ")));
    if (p.x && p.x.length) {
      var chips = el("span", "tip__chips");
      p.x.forEach(function (x) { chips.appendChild(el("i", "", x)); });
      body.appendChild(chips);
    }
    if (p.s) body.appendChild(el("span", "tip__summary", p.s));
    card.appendChild(body);
    return card;
  }

  function workCard(w) {
    var card = el("div", "tip__card tip__card--work");
    if (w.i) {
      var img = el("img", "tip__icon");
      img.src = w.i; img.alt = ""; img.width = 40; img.height = 40;
      card.appendChild(img);
    }
    var body = el("div", "tip__body");
    body.appendChild(el("b", "tip__name", w.n + (w.y ? "（" + w.y + "）" : "")));
    if (w.e && w.e !== w.n) body.appendChild(el("span", "tip__role", w.e));
    var facts = [];
    if (w.d) facts.push(w.d);
    if (w.c) facts.push("名单 " + w.c + " 人");
    if (w.m) facts.push("站内 " + w.m + " 篇提到");
    if (facts.length) body.appendChild(el("span", "tip__facts", facts.join(" · ")));
    card.appendChild(body);
    return card;
  }

  /* ---- show / hide ------------------------------------------------------ */
  function fill(w) {
    inner.textContent = "";
    tip.classList.remove("tip--card");
    if (w.kind === "text") {
      inner.textContent = w.text;
      return true;
    }
    if (!data) return false;
    var rec = w.kind === "person" ? data.people[w.key] : data.works[w.key];
    if (!rec) return false;
    tip.classList.add("tip--card");
    inner.appendChild(w.kind === "person" ? personCard(rec) : workCard(rec));
    return true;
  }

  function place(anchor, pos) {
    var r = anchor.getBoundingClientRect();
    if (!r.width && !r.height) return false;
    tip.style.left = "0px"; tip.style.top = "0px";
    tip.hidden = false;
    var tw = tip.offsetWidth, th = tip.offsetHeight;
    var vw = document.documentElement.clientWidth, vh = document.documentElement.clientHeight;
    var gap = 9, pad = 8;
    var cx = r.left + r.width / 2;
    var above = pos === "bottom" ? false : (r.top - gap - th >= pad || (pos !== "top" && r.bottom + gap + th > vh - pad && r.top > vh - r.bottom));
    var top = above ? r.top - gap - th : r.bottom + gap;
    var left = Math.round(cx - tw / 2);
    if (left < pad) left = pad;
    if (left + tw > vw - pad) left = Math.max(pad, vw - pad - tw);
    tip.style.left = left + "px";
    tip.style.top = Math.round(top) + "px";
    tip.classList.toggle("tip--above", above);
    tip.classList.toggle("tip--below", !above);
    var ax = Math.max(12, Math.min(tw - 12, cx - left));
    arrow.style.left = ax + "px";
    return true;
  }

  function show(anchor, w) {
    ensure();
    if (!fill(w)) { hide(); return; }
    current = anchor;
    if (!place(anchor, w.pos || "")) { hide(); return; }
    if (byFocus) anchor.setAttribute("aria-describedby", ID);
    tip.classList.remove("is-in");
    if (reduce) { tip.classList.add("is-in"); }
    else { requestAnimationFrame(function () { if (current === anchor) tip.classList.add("is-in"); }); }
  }

  function hide() {
    if (showTimer) { clearTimeout(showTimer); showTimer = 0; }
    if (current) current.removeAttribute("aria-describedby");
    current = null;
    byTouch = false;
    if (tip) { tip.hidden = true; tip.classList.remove("is-in"); }
  }

  function open(hit, delay) {
    if (showTimer) { clearTimeout(showTimer); showTimer = 0; }
    var run = function () {
      showTimer = 0;
      if (hit.w.kind === "text") { show(hit.el, hit.w); return; }
      load().then(function () { if (hit.el.matches(":hover") || byFocus || byTouch) show(hit.el, hit.w); });
    };
    if (delay <= 0) run(); else showTimer = setTimeout(run, delay);
  }

  /* ---- events ----------------------------------------------------------- */
  document.addEventListener("mouseover", function (e) {
    if (byTouch) return;
    var hit = anchorOf(e.target);
    if (!hit) return;
    if (current === hit.el) return;
    byFocus = false;
    if (current) hide();
    open(hit, hit.w.kind === "text" ? DELAY_TEXT : DELAY_CARD);
  }, true);

  document.addEventListener("mouseout", function (e) {
    if (byTouch || byFocus) return;
    var hit = anchorOf(e.target);
    if (!hit) return;
    var to = e.relatedTarget;
    if (to && hit.el.contains(to)) return;
    hide();
  }, true);

  document.addEventListener("focusin", function (e) {
    var hit = anchorOf(e.target);
    if (!hit || hit.el !== e.target) return;
    byFocus = true;
    open(hit, 0);
  });
  document.addEventListener("focusout", function () {
    if (byFocus) { byFocus = false; hide(); }
  });

  document.addEventListener("pointerdown", function (e) {
    if (e.pointerType !== "touch") { if (current && !e.target.closest("#" + ID)) hide(); return; }
    var hit = anchorOf(e.target);
    if (hit && current === hit.el) { hide(); return; }
    hide();
    /* a link navigates on tap; only a non-link anchor holds its tip for a tap */
    if (hit && !hit.el.closest("a[href]") && !hit.el.closest("button")) {
      byTouch = true;
      open(hit, 0);
    }
  }, true);

  /* ---- names in the dialogue ------------------------------------------- */
  /* The byline links each speaker to their page; the name over every turn is
     plain text. Give the turns the card the byline's link carries, matched by
     name, so hovering 石原恒和 anywhere in the piece says who that is. */
  function enrich() {
    var map = {};
    var links = document.querySelectorAll(".ed-people a[href], .parallel-translation__people a[href]");
    for (var i = 0; i < links.length; i++) {
      var m = PEOPLE_RE.exec(links[i].getAttribute("href") || "");
      if (m) map[links[i].textContent.replace(/\s+/g, " ").trim()] = m[1];
    }
    var names = Object.keys(map);
    if (!names.length) return;
    var turns = document.querySelectorAll(".ed-turn__who, .ed-pull footer, .parallel-text__speaker");
    for (var j = 0; j < turns.length; j++) {
      var name = turns[j].textContent.replace(/^[\s—–\-]+/, "").replace(/\s+/g, " ").trim();
      if (map[name]) turns[j].setAttribute("data-tip-person", map[name]);
    }
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", enrich); else enrich();

  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && current) hide(); });
  window.addEventListener("scroll", function () { if (current && !byFocus) hide(); }, { passive: true });
  window.addEventListener("resize", function () { if (current) hide(); });
  window.addEventListener("pagehide", hide);
})();
