/* 今日一句 on the home page (home-quote.html).
   The page carries a pool of ninety quotes; today's is pool[dayIndex % pool.length], the
   same for every reader on the same day, whatever day the site was built. 换一句 draws
   another from the pool, avoiding the twenty most recently seen (localStorage); after
   five draws the whole pool (assets/js/quotes.json) is fetched once and drawn from. */
(function () {
  "use strict";
  var card = document.getElementById("frontQuote");
  var poolEl = document.getElementById("quotePool");
  if (!card || !poolEl) return;
  var pool;
  try { pool = JSON.parse(poolEl.textContent || "[]"); } catch (e) { return; }
  if (!pool.length) return;
  var SEEN_KEY = "pokeamice.quotes.seen";
  var draws = 0, full = null, loading = false;

  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]; }); }
  function seen() { try { return JSON.parse(localStorage.getItem(SEEN_KEY) || "[]"); } catch (e) { return []; } }
  function remember(id) {
    try {
      var s = seen().filter(function (x) { return x !== id; });
      s.unshift(id);
      localStorage.setItem(SEEN_KEY, JSON.stringify(s.slice(0, 20)));
    } catch (e) { /* private mode */ }
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

  function render(q) {
    card.className = "front__quote is-kind-" + (q.k || "quote") + (q.c ? " has-cover cover-" + (q.ck || "own") : "");
    var cover = card.querySelector(".front__quote-cover");
    cover.href = q.u;
    cover.innerHTML = q.c ? '<img src="' + esc(q.c) + '" alt="" decoding="async">' : "";
    card.querySelector(".front__quote-hook").innerHTML = '<a href="' + esc(q.u) + '">' + esc(q.h) + '</a>';
    card.querySelector(".front__quote-zh").textContent = q.z || "";
    var ja = card.querySelector(".front__quote-ja p");
    if (ja) ja.textContent = q.j || "";
    var det = card.querySelector(".front__quote-ja");
    if (det) det.open = false;
    card.querySelector(".front__quote-src").innerHTML =
      (q.a ? '<img src="' + esc(q.a) + '" alt="" width="20" height="20" loading="lazy">' : "") +
      (q.w ? "<b>" + esc(q.w) + "</b> · " : "") +
      '<a href="' + esc(q.u) + '">' + esc(q.t) + "</a>" + (q.p ? " · " + esc(q.p) : "") + " · " + esc(q.y) +
      (q.r ? " <small>（报道文字）</small>" : "");
    var why = card.querySelector(".front__quote-why"), more = card.querySelector(".front__quote-more");
    if (q.e) { if (!why) { why = document.createElement("p"); why.className = "front__quote-why"; card.querySelector(".front__quote-src").after(why); } why.innerHTML = "<b>解析</b>" + esc(q.e); }
    else if (why) why.remove();
    if (q.m) { if (!more) { more = document.createElement("p"); more.className = "front__quote-more"; card.querySelector(".front__quote-body").appendChild(more); } more.innerHTML = "<b>扩展</b>" + withLinks(q.m, q.l); }
    else if (more) more.remove();
    remember(q.id);
  }

  // today's line: the day count since the epoch in the reader's clock, modulo the pool
  var day = Math.floor((Date.now() - new Date().getTimezoneOffset() * 60000) / 86400000);
  var todays = pool[((day % pool.length) + pool.length) % pool.length];
  var label = card.querySelector(".front__quote-label"), when = card.querySelector(".front__quote-kicker time");
  if (todays && todays.id !== (card.dataset.current || "")) render(todays);
  if (when) { var now = new Date(); when.textContent = now.getFullYear() + "-" + String(now.getMonth() + 1).padStart(2, "0") + "-" + String(now.getDate()).padStart(2, "0"); }

  function draw() {
    var from = full || pool, s = seen(), pick = null;
    var fresh = from.filter(function (q) { return s.indexOf(q.id) < 0; });
    var src = fresh.length ? fresh : from;
    pick = src[Math.floor(Math.random() * src.length)];
    if (pick) { render(pick); if (label) label.textContent = "再来一句"; if (when) when.textContent = (full ? "全库 " : "") + (full || pool).length + " 句"; }
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
})();
