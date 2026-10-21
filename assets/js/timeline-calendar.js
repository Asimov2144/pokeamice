/* 资料时间线 as a desk calendar (_pages/timeline.md). Everything here enhances a page that
   already reads without it:
   - the today sheet: the reader's date, time of day (morning / day / evening / night, with
     the evolution that belongs to it) and season (Deerling's form), and 历史上的今天 from
     feed-days.json (the nearest earlier day that has an entry when today has none);
   - the backdrop: each generation's cover legends cross-fade with the scroll, and the page
     tint mixes their version colours (--tlc-a / --tlc-b);
   - each year sheet turns in once as it arrives, and its speakers glide past;
   - the era tab under the reading line is marked current.
   One requestAnimationFrame per scroll; nothing is animated while the page is still. */
(function () {
  "use strict";
  var root = document.querySelector("[data-tlc-root]");
  if (!root) return;
  var art = root.getAttribute("data-art") || "/assets/img/timeline/";
  var $ = function (sel, el) { return (el || root).querySelector(sel); };
  var $$ = function (sel, el) { return Array.prototype.slice.call((el || root).querySelectorAll(sel)); };
  var esc = function (s) { return String(s || "").replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };

  // ---- today: time of day and season ----------------------------------------------
  var now = new Date();
  var h = now.getHours();
  var TOD = h >= 4 && h < 10 ? "morning" : h >= 10 && h < 17 ? "day" : h >= 17 && h < 19 ? "evening" : "night";
  var TOD_TEXT = {
    morning: ["MORNING · 清晨", "eevee", "伊布：亲密度够高时，白天升级进化成太阳伊布，夜里升级进化成月亮伊布。"],
    day: ["DAY · 白天", "espeon", "太阳伊布：白天进化的伊布。"],
    evening: ["EVENING · 傍晚", "lycanroc-dusk", "黄昏的鬃岩狼人：只在傍晚进化出来的形态。"],
    night: ["NIGHT · 夜里", "umbreon", "月亮伊布：夜里进化的伊布。"]
  };
  var m = now.getMonth() + 1, d = now.getDate();
  var SEASON = m >= 3 && m <= 5 ? ["spring", "SPRING · 春"] : m >= 6 && m <= 8 ? ["summer", "SUMMER · 夏"] : m >= 9 && m <= 11 ? ["autumn", "AUTUMN · 秋"] : ["winter", "WINTER · 冬"];
  var pad = function (n) { return (n < 10 ? "0" : "") + n; };
  var sky = $(".tlc-sky");
  if (sky) {
    sky.setAttribute("data-tod", TOD);
    $("[data-tlc-tod]").textContent = TOD_TEXT[TOD][0] + "  " + pad(h) + ":" + pad(now.getMinutes());
    $("[data-tlc-date]").textContent = pad(m) + "." + pad(d);
    $("[data-tlc-weekday]").textContent = "周" + "日一二三四五六".charAt(now.getDay());
    $("[data-tlc-season]").textContent = SEASON[1];
    $("[data-tlc-season-img]").src = art + "deerling-" + SEASON[0] + ".png";
    $("[data-tlc-actor]").src = art + TOD_TEXT[TOD][1] + ".png";
    $("[data-tlc-actor-note]").textContent = TOD_TEXT[TOD][2];
  }

  // ---- 历史上的今天 ------------------------------------------------------------------
  var otd = $("[data-tlc-otd]");
  var feed = root.getAttribute("data-feed");
  if (otd && feed && window.fetch) {
    fetch(feed).then(function (r) { return r.ok ? r.json() : {}; }).then(function (days) {
      for (var back = 0; back < 60; back++) {
        var day = new Date(now.getFullYear(), now.getMonth(), now.getDate() - back);
        var list = days[pad(day.getMonth() + 1) + pad(day.getDate())];
        if (!list || !list.length) continue;
        list = list.slice().sort(function (a, b) { return a.y - b.y; }).slice(0, 3);
        $("[data-tlc-otd-label]").textContent = back === 0 ? "历史上的今天" : "最近的一天 · " + (day.getMonth() + 1) + " 月 " + day.getDate() + " 日";
        otd.innerHTML = list.map(function (e) {
          return '<li><time>' + esc(e.y) + '</time><a href="' + esc(e.u) + '">' + esc(e.t) + "</a></li>";
        }).join("");
        return;
      }
    }).catch(function () {});
  }

  // ---- scroll: generations, tabs, passers ------------------------------------------
  var sheets = $$("[data-tlc-year]").map(function (el) { return { el: el, year: +el.getAttribute("data-tlc-year"), row: $("[data-tlc-passers]", el) }; });
  var gens = $$("[data-tlc-gen]").map(function (el) {
    return { el: el, from: +el.getAttribute("data-from"), to: +el.getAttribute("data-to"), a: hex(el.getAttribute("data-c1")), b: hex(el.getAttribute("data-c2")) };
  });
  var eras = $$("[data-tlc-era]");
  var tabs = $$("[data-tlc-tab]");
  var last = gens[gens.length - 1];
  function hex(s) { s = (s || "#888888").replace("#", ""); return [parseInt(s.substr(0, 2), 16), parseInt(s.substr(2, 2), 16), parseInt(s.substr(4, 2), 16)]; }
  function rgb(c) { return "rgb(" + c.map(Math.round).join(",") + ")"; }

  var ss = function (x) { x = Math.min(1, Math.max(0, x)); return x * x * (3 - 2 * x); };
  var SPAN = 1;          // a hand-over between generations takes one year of scrolling, centred on the boundary
  var ticking = false;
  function frame() {
    ticking = false;
    var vh = window.innerHeight, line = vh * 0.45;
    var rects = sheets.map(function (s) { return s.el.getBoundingClientRect(); });
    // the fractional year under the reading line, interpolated from one sheet's top to the next
    // (so a year with no sheet, 1998, is crossed smoothly); above the first sheet, `pre` runs
    // from 1 (today, the latest generation) down to 0 (1996)
    var fy = sheets.length ? sheets[0].year : 0, pre = 0;
    if (sheets.length && rects[0].top > line) pre = ss((rects[0].top - line) / (vh * 0.9));
    for (var i = 0; i < sheets.length; i++) {
      var r = rects[i];
      if (r.top <= line) {
        var nextTop = i + 1 < sheets.length ? rects[i + 1].top : r.bottom;
        var nextYear = i + 1 < sheets.length ? sheets[i + 1].year : sheets[i].year + 1;
        fy = sheets[i].year + (nextYear - sheets[i].year) * Math.min(1, Math.max(0, (line - r.top) / Math.max(1, nextTop - r.top)));
      }
      // passers glide from right to left while the sheet crosses the screen
      if (sheets[i].row && r.bottom > 0 && r.top < vh) {
        var p = Math.min(1, Math.max(0, (vh - r.top) / (vh + r.height)));
        var box = sheets[i].row.parentNode.clientWidth, w = sheets[i].row.scrollWidth;
        var x = box * 0.3 * (1 - p) - Math.max(0, w - box * 0.7) * p;
        sheets[i].row.style.setProperty("--x", x.toFixed(1) + "px");
      }
    }
    // each generation fades in over the year around its first year and out over the year around
    // the next one's; the two curves are complementary, so the weights always add up to one.
    // The outgoing set drifts up and shrinks a little, the incoming one rises from below, and a
    // generation on stage drifts slowly with its years - one hand-over at a time, no hard cut
    var wsum = 0, a = [0, 0, 0], b = [0, 0, 0];
    gens.forEach(function (g, gi) {
      var inW = gi === 0 ? 1 : ss((fy - (g.from - SPAN / 2)) / SPAN);
      var outW = g === last ? 0 : ss((fy - (g.to + 1 - SPAN / 2)) / SPAN);
      var op = inW * (1 - outW);
      var q = Math.min(1, Math.max(0, (fy - g.from) / (g.to + 1 - g.from)));
      var ty = (1 - inW) * 8 - outW * 8 - q * 3;
      if (gi === 0) { op *= 1 - pre; ty += pre * 8; }
      if (g === last && pre > 0) { op = Math.max(op, pre); ty = -(1 - pre) * 8; }
      var sc = 1 - 0.04 * Math.max(1 - inW, outW, g === last ? 1 - pre : 0) * (op < 1 ? 1 : 0);
      g.el.style.opacity = op.toFixed(3);
      g.el.style.transform = op > 0 ? "translate3d(0," + ty.toFixed(2) + "vh,0) scale(" + sc.toFixed(4) + ")" : "";
      g.el.classList.remove("is-on");
      if (op > 0) { wsum += op; for (var k = 0; k < 3; k++) { a[k] += g.a[k] * op; b[k] += g.b[k] * op; } }
    });
    if (wsum > 0) {
      root.style.setProperty("--tlc-a", rgb(a.map(function (v) { return v / wsum; })));
      root.style.setProperty("--tlc-b", rgb(b.map(function (v) { return v / wsum; })));
    }
    var cur = 0;
    eras.forEach(function (e, idx) { if (e.getBoundingClientRect().top <= line) cur = idx + 1; });
    tabs.forEach(function (t) {
      if (+t.getAttribute("data-tlc-tab") === cur) t.setAttribute("aria-current", "true"); else t.removeAttribute("aria-current");
    });
  }
  function request() { if (!ticking) { ticking = true; requestAnimationFrame(frame); } }
  window.addEventListener("scroll", request, { passive: true });
  window.addEventListener("resize", request);
  frame();

  // ---- a sheet turns in once, as it arrives from below -------------------------------
  if ("IntersectionObserver" in window && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting && en.boundingClientRect.top > 0) { en.target.classList.add("is-turning"); io.unobserve(en.target); }
      });
    }, { threshold: 0.12 });
    sheets.forEach(function (s) { if (s.el.getBoundingClientRect().top > window.innerHeight) io.observe(s.el); });
  }

  // ---- each year: its first pick, and two drawn at random from the rest -----------------
  // (the other picks and the pool, tools/build-timeline.py); a series shows at most twice,
  // new series first. The drawn ones say 随手翻到; 换几篇 draws again.
  function draw(list) {
    var rows = $$("li[data-series]", list);
    var rep = rows.filter(function (r) { return r.getAttribute("data-role") === "rep"; })[0];
    var rest = rows.filter(function (r) { return r !== rep; });
    for (var i = rest.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var t = rest[i]; rest[i] = rest[j]; rest[j] = t; }
    var shown = rep ? [rep] : [], count = {};
    if (rep) count[rep.getAttribute("data-series")] = 1;
    [function (s) { return !count[s]; }, function (s) { return (count[s] || 0) < 2; }].forEach(function (ok) {
      rest.forEach(function (r) {
        var s = r.getAttribute("data-series");
        if (shown.length < 3 && shown.indexOf(r) < 0 && ok(s)) { shown.push(r); count[s] = (count[s] || 0) + 1; }
      });
    });
    rows.forEach(function (r) {
      r.hidden = shown.indexOf(r) < 0;
      var tag = r.querySelector(".tlc-rand");
      if (tag) tag.hidden = r.getAttribute("data-role") !== "pool";
    });
    shown.forEach(function (r) { list.appendChild(r); });     // the first pick, then the drawn ones
  }
  $$("[data-tlc-picks]").forEach(function (list) {
    draw(list);
    var btn = $("[data-tlc-shuffle]", list.closest(".tlc-sheet"));
    if (btn) { btn.hidden = false; btn.addEventListener("click", function () { draw(list); }); }
  });

  // ---- Celebi: close the year list after a jump ---------------------------------------
  var jump = $("[data-tlc-jump]");
  if (jump) jump.addEventListener("click", function (ev) { if (ev.target.closest("a")) jump.open = false; });
})();
