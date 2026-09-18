/* 今日一句 on the home page (home-quote.html): an aside, shown only when the reader
   has idled on the page for a while (no scroll, click or key for 75 s) or comes back
   after seven days or more; × puts it away for the session.
   The page carries a pool of ninety quotes; today's is pool[dayIndex % pool.length],
   the same for every reader on the same day, whatever day the site was built. 换一句
   draws another, avoiding the twenty most recently seen (localStorage); after five
   draws the whole pool (assets/js/quotes.json) is fetched once and drawn from. */
(function () {
  "use strict";
  var card = document.getElementById("frontQuote");
  var poolEl = document.getElementById("quotePool");
  if (!card || !poolEl) return;
  var pool;
  try { pool = JSON.parse(poolEl.textContent || "[]"); } catch (e) { return; }
  if (!pool.length) return;
  var SEEN_KEY = "pokeamice.quotes.seen", VISIT_KEY = "pokeamice.lastVisit", AWAY_KEY = "pokeamice.quotes.away";
  var IDLE_MS = 75000, LONG_GAP_MS = 7 * 86400000;
  var draws = 0, full = null, loading = false, shown = false;

  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]; }); }
  function store(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* private mode */ } }
  function load(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function seen() { try { return JSON.parse(load(SEEN_KEY) || "[]"); } catch (e) { return []; } }
  function remember(id) {
    var s = seen().filter(function (x) { return x !== id; });
    s.unshift(id);
    store(SEEN_KEY, JSON.stringify(s.slice(0, 20)));
  }
  function withLinks(text, links) {
    var html = esc(text || "");
    (links || []).forEach(function (l) {
      if (!l || !l.name) return;
      var href = l.type === "person" && l.slug ? card.dataset.peopleBase + l.slug + "/" : card.dataset.searchBase + encodeURIComponent(l.name);
      html = html.replace(esc(l.name), '<a href="' + href + '">' + esc(l.name) + '</a>');
    });
    return html;
  }
  function today() { var d = new Date(); return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0"); }

  function render(q, daily) {
    card.className = "front__quote is-kind-" + (q.k || "quote") + (q.c ? " has-cover cover-" + (q.ck || "own") : "");
    var cover = card.querySelector(".front__quote-cover");
    cover.href = q.u;
    cover.innerHTML = q.c ? '<img src="' + esc(q.c) + '" alt="" decoding="async" loading="lazy">' : "";
    card.querySelector(".front__quote-hook").innerHTML = '<a href="' + esc(q.u) + '">' + esc(q.h) + '</a>';
    card.querySelector(".front__quote-zh").textContent = q.z || "";
    card.querySelector(".front__quote-src").innerHTML =
      (q.a ? '<img src="' + esc(q.a) + '" alt="" width="18" height="18" loading="lazy">' : "") +
      (q.w ? "<b>" + esc(q.w) + "</b> · " : "") +
      '<a href="' + esc(q.u) + '">' + esc(q.t) + "</a>" + (q.p ? " · " + esc(q.p) : "") + " · " + esc(q.y) +
      (q.r ? " <small>（报道文字）</small>" : "");
    card.querySelector(".front__quote-ja").textContent = q.j || "";
    card.querySelector(".front__quote-why").innerHTML = q.e ? "<b>解析</b>" + esc(q.e) : "";
    card.querySelector(".front__quote-more").innerHTML = q.m ? "<b>扩展</b>" + withLinks(q.m, q.l) : "";
    card.querySelector(".front__quote-fold").open = false;
    var label = card.querySelector(".front__quote-label"), when = card.querySelector(".front__quote-kicker time");
    if (label) label.textContent = daily ? "今日一句" : "再来一句";
    if (when) when.textContent = daily ? today() : (full ? "全库 " : "") + (full || pool).length + " 句";
    remember(q.id);
  }

  // today's line: the day count since the epoch in the reader's clock, modulo the pool
  var day = Math.floor((Date.now() - new Date().getTimezoneOffset() * 60000) / 86400000);
  var todays = pool[((day % pool.length) + pool.length) % pool.length];

  function show() {
    if (shown) return;
    shown = true;
    render(todays, true);
    card.hidden = false;
    window.dispatchEvent(new Event("resize"));      // the masonry below re-measures
  }

  // when: back after a long gap (or the first visit is not enough - the record starts now),
  // or idle on the page for a while; × keeps it away for the session
  var last = parseInt(load(VISIT_KEY) || "0", 10);
  store(VISIT_KEY, String(Date.now()));
  var away = false;
  try { away = sessionStorage.getItem(AWAY_KEY) === "1"; } catch (e) {}
  if (location.hash === "#quote") {                 // asked for by link
    show();
  } else if (!away) {
    if (last && Date.now() - last >= LONG_GAP_MS) {
      show();
    } else {
      var timer = null;
      var arm = function () { if (shown) return; if (timer) clearTimeout(timer); timer = setTimeout(show, IDLE_MS); };
      ["scroll", "mousemove", "keydown", "pointerdown", "touchstart"].forEach(function (ev) { window.addEventListener(ev, arm, {passive: true}); });
      arm();
    }
  }

  function draw() {
    var from = full || pool, s = seen();
    var fresh = from.filter(function (q) { return s.indexOf(q.id) < 0; });
    var src = fresh.length ? fresh : from;
    var pick = src[Math.floor(Math.random() * src.length)];
    if (pick) render(pick, false);
  }
  var btn = card.querySelector("[data-quote-next]");
  if (btn) btn.addEventListener("click", function () {
    draws += 1;
    if (draws >= 5 && !full && !loading && card.dataset.quotes) {
      loading = true;
      fetch(card.dataset.quotes).then(function (r) { return r.json(); }).then(function (d) { full = d.quotes || null; }).catch(function () {}).finally(function () { loading = false; draw(); });
      return;
    }
    draw();
  });
  var close = card.querySelector("[data-quote-close]");
  if (close) close.addEventListener("click", function () {
    card.hidden = true;
    try { sessionStorage.setItem(AWAY_KEY, "1"); } catch (e) {}
    window.dispatchEvent(new Event("resize"));
  });
})();
