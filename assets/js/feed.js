/* The resource hub's stream (_pages/keys.md): what the browser adds to the posts the
   build wrote.
   - the dates become 今天 / 昨天 / N 天前 / M 月 D 日; today's posts get a mark
   - the filter chips show one kind of post at a time (remembered)
   - three posts are written here for the day of the visit, from what the page carries:
     今日一句 from the inlined window of quotes (the same day-index rule as quote.js on the
     home page, so both show the same line), 历史上的今天 from feed-days.json (the entries
     published on this month and day, or the nearest day before it), 人物聚焦 from the
     inlined pool of people
   - a post fades in as it scrolls into view, unless motion is reduced */
(function () {
  "use strict";
  var feed = document.querySelector("[data-feed]");
  if (!feed) return;
  var stream = feed.querySelector("[data-feed-stream]");
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]; }); }
  function store(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  function load(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  var now = new Date();
  var todayKey = now.getFullYear() + "-" + String(now.getMonth() + 1).padStart(2, "0") + "-" + String(now.getDate()).padStart(2, "0");
  // the day count since the epoch in the reader's clock: the same number quote.js uses
  var day = Math.floor((Date.now() - now.getTimezoneOffset() * 60000) / 86400000);

  // ---- when ------------------------------------------------------------------
  function since(d) {
    var then = new Date(d + "T00:00:00");
    var days = Math.round((new Date(todayKey + "T00:00:00") - then) / 86400000);
    if (days <= 0) return "今天";
    if (days === 1) return "昨天";
    if (days < 7) return days + " 天前";
    if (then.getFullYear() === now.getFullYear()) return (then.getMonth() + 1) + " 月 " + then.getDate() + " 日";
    return then.getFullYear() + " 年 " + (then.getMonth() + 1) + " 月 " + then.getDate() + " 日";
  }
  Array.prototype.forEach.call(feed.querySelectorAll("[data-feed-when]"), function (t) {
    var d = t.getAttribute("datetime");
    if (!d) return;
    t.title = d;
    t.textContent = since(d);
    if (d === todayKey) { var item = t.closest(".feed-item"); if (item) item.classList.add("is-today"); }
  });

  // ---- the filter chips ---------------------------------------------------------
  var chips = Array.prototype.slice.call(document.querySelectorAll("[data-feed-kind]"));
  function filter(kind) {
    Array.prototype.forEach.call(stream.querySelectorAll(".feed-item"), function (it) {
      it.hidden = kind !== "all" && it.getAttribute("data-kind") !== kind;
    });
    chips.forEach(function (c) { c.classList.toggle("is-on", c.getAttribute("data-feed-kind") === kind); });
    stream.setAttribute("data-feed-filter", kind);
    store("feedKind", kind);
  }
  chips.forEach(function (c) { c.addEventListener("click", function () { filter(c.getAttribute("data-feed-kind")); }); });
  var stored = load("feedKind");
  if (stored && stored !== "all" && chips.some(function (c) { return c.getAttribute("data-feed-kind") === stored; })) filter(stored);

  // ---- 今日一句 -------------------------------------------------------------------
  var qBox = feed.querySelector("[data-feed-quote]");
  var qPoolEl = feed.querySelector("[data-feed-quotes]");
  if (qBox && qPoolEl) {
    var pool = [];
    try { pool = JSON.parse(qPoolEl.textContent || "[]"); } catch (e) {}
    var seen = [];
    function drawQuote(q, daily) {
      if (!q) return;
      var cover = q.c ? '<a class="feed__quote-cover' + (q.ck === "portrait" ? " is-portrait" : "") + '" href="' + esc(q.u) + '" tabindex="-1" aria-hidden="true"><img src="' + esc(q.c) + '" alt="" loading="lazy" decoding="async"></a>' : "";
      var src = (q.a ? '<img class="feed__quote-avatar" src="' + esc(q.a) + '" alt="" loading="lazy">' : "") + (q.w ? "<b>" + esc(q.w) + "</b> · " : "") + '<a href="' + esc(q.u) + '">' + esc(q.t) + "</a>" + (q.p ? " · " + esc(q.p) : "") + " · " + esc(q.y) + (q.r ? "（报道文字）" : "");
      qBox.innerHTML = cover + '<div class="feed__quote-body"><p class="feed__quote-hook' + (q.k === "question" ? " is-question" : "") + '"><a href="' + esc(q.u) + '">' + esc(q.h) + "</a></p><p class=\"feed__quote-zh\">" + esc(q.z) + '</p><p class="feed__quote-src">' + src + "</p>" + (q.e ? '<p class="feed__quote-why"><b>解析</b>' + esc(q.e) + "</p>" : "") + "</div>";
      qBox.classList.toggle("is-daily", !!daily);
      seen.unshift(q.id);
    }
    if (pool.length) {
      drawQuote(pool[((day % pool.length) + pool.length) % pool.length], true);
      var next = feed.querySelector("[data-feed-quote-next]");
      if (next) next.addEventListener("click", function () {
        var fresh = pool.filter(function (q) { return seen.indexOf(q.id) < 0; });
        var from = fresh.length ? fresh : pool;
        drawQuote(from[Math.floor(Math.random() * from.length)], false);
      });
    } else {
      qBox.innerHTML = '<p class="feed__muted">今天没有句子。</p>';
    }
  }

  // ---- 历史上的今天 -------------------------------------------------------------
  var tBox = feed.querySelector("[data-feed-today]");
  if (tBox && tBox.dataset.src) {
    fetch(tBox.dataset.src, { credentials: "same-origin" }).then(function (r) { if (!r.ok) throw new Error(String(r.status)); return r.json(); }).then(function (days) {
      var d = new Date(now), key, hits = [], tries = 0;
      // this day; failing that, the nearest day before it
      while (tries < 45) {
        key = String(d.getMonth() + 1).padStart(2, "0") + String(d.getDate()).padStart(2, "0");
        hits = days[key] || [];
        if (hits.length) break;
        d.setDate(d.getDate() - 1); tries += 1;
      }
      if (!hits.length) { tBox.innerHTML = '<p class="feed__muted">日历上这几天是空的。</p>'; return; }
      hits = hits.slice().sort(function (a, b) { return a.y - b.y; });
      var label = tries === 0 ? "今天，" + (d.getMonth() + 1) + " 月 " + d.getDate() + " 日" : "最近的一天：" + (d.getMonth() + 1) + " 月 " + d.getDate() + " 日";
      var more = hits.length > 5 ? '<p class="feed__muted">还有 ' + (hits.length - 5) + " 条同一天的。</p>" : "";
      tBox.innerHTML = '<p class="feed__today-label">' + esc(label) + "，这些年刊出过：</p><ul class=\"feed__today-list\">" + hits.slice(0, 5).map(function (h) {
        return "<li>" + (h.c ? '<a class="feed__today-thumb" href="' + esc(h.u) + '" tabindex="-1" aria-hidden="true"><img src="' + esc(h.c) + '" alt="" loading="lazy" decoding="async"></a>' : '<span class="feed__today-thumb is-blank"></span>') + '<span class="feed__today-year">' + esc(h.y) + '</span><span class="feed__today-kind">' + esc(h.k) + '</span><a class="feed__today-title" href="' + esc(h.u) + '">' + esc(h.t) + "</a></li>";
      }).join("") + "</ul>" + more;
    }).catch(function () { tBox.innerHTML = '<p class="feed__muted">日历没读到，稍后再试。</p>'; });
  }

  // ---- 人物聚焦 ---------------------------------------------------------------
  var pBox = feed.querySelector("[data-feed-person]");
  var pPoolEl = feed.querySelector("[data-feed-people]");
  if (pBox && pPoolEl) {
    var people = [];
    try { people = JSON.parse(pPoolEl.textContent || "[]"); } catch (e) {}
    // the forty most interviewed take turns, one a day
    people = people.slice().sort(function (a, b) { return (b.e || 0) - (a.e || 0); }).slice(0, 40);
    if (people.length) {
      var p = people[((day % people.length) + people.length) % people.length];
      var href = (feed.querySelector("[data-feed-quote]") || {}).dataset ? (feed.querySelector("[data-feed-quote]").dataset.peopleBase || "/people/") : "/people/";
      href = href + p.s + "/";
      pBox.innerHTML = (p.a ? '<a class="feed__person-avatar" href="' + esc(href) + '" tabindex="-1" aria-hidden="true"><img src="' + esc(p.a) + '" alt="" loading="lazy" decoding="async"></a>' : "") +
        '<div class="feed__person-body"><p class="feed__person-name"><a href="' + esc(href) + '">' + esc(p.n) + "</a></p>" +
        (p.r ? '<p class="feed__person-role">' + esc(p.r) + "</p>" : "") +
        (p.m ? '<p class="feed__person-sum">' + esc(p.m) + "</p>" : "") +
        '<p class="feed__person-facts"><a href="' + esc(href) + '">' + esc(p.e) + " 篇访谈" + (p.y ? " · " + esc(p.y) : "") + " →</a></p></div>";
    } else {
      pBox.innerHTML = '<p class="feed__muted">今天没有人物。</p>';
    }
  }

  // ---- the fade-in --------------------------------------------------------------
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var items = Array.prototype.slice.call(stream.querySelectorAll(".feed-item"));
  if (!reduce && "IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("is-in"); io.unobserve(en.target); } });
    }, { rootMargin: "0px 0px -8% 0px" });
    items.forEach(function (it) { it.classList.add("will-in"); io.observe(it); });
    // a tab that is not being drawn gets no intersections; nothing may stay invisible
    setTimeout(function () { items.forEach(function (it) { it.classList.add("is-in"); }); }, 2500);
  }
})();
