/* Server-rendered chronicle. Search, filtering and jump navigation enhance
   complete HTML; there is no network request, masonry or content replacement.
   A year page is a sheet of the desk calendar (_includes/timeline-year.html): this also sets
   the reader's time of day and season on the sheet's head, points at this day or this month
   of the year, slides the year's speakers past as the head scrolls by, and keeps the kind
   and the search when Celebi jumps to another year. */
(function () {
  "use strict";
  var root = document.querySelector("[data-tl-root]");
  if (!root) return;
  var array = function (selector) { return Array.prototype.slice.call(root.querySelectorAll(selector)); };
  var items = array(".tl--year .tl-item");
  var months = array("[data-tl-month]");
  var streams = array("[data-tl-stream]");
  var buttons = array("[data-tl-filter]");
  var query = root.querySelector("[data-tl-query]");
  var status = root.querySelector("[data-tl-status]");
  var empty = root.querySelector("[data-tl-empty]");
  var clear = root.querySelector("[data-tl-clear-query]");
  var kind = "all";
  var savedOpen = null;
  var normalize = function (text) {
    text = String(text || "");
    if (text.normalize) text = text.normalize("NFKC");
    return text.toLocaleLowerCase().replace(/\s+/g, " ").trim();
  };
  var searches = items.map(function (item) { return normalize(item.getAttribute("data-tl-search")); });
  var validKind = function (value) { return value === "all" || buttons.some(function (button) { return button.dataset.tlFilter === value; }); };
  function syncURL() {
    var url = new URL(location.href);
    if (kind === "all") url.searchParams.delete("k"); else url.searchParams.set("k", kind);
    if (query && query.value.trim()) url.searchParams.set("q", query.value.trim()); else url.searchParams.delete("q");
    try { history.replaceState(null, "", url.pathname + url.search + url.hash); } catch (error) {}
  }
  function update(writeURL) {
    var terms = normalize(query && query.value).split(" ").filter(Boolean);
    var visible = 0;
    items.forEach(function (item, index) {
      var match = (kind === "all" || item.dataset.kind === kind) && terms.every(function (term) { return searches[index].indexOf(term) !== -1; });
      item.hidden = !match;
      if (match) visible++;
    });
    buttons.forEach(function (button) {
      var on = button.dataset.tlFilter === kind;
      button.classList.toggle("is-on", on);
      button.setAttribute("aria-pressed", on ? "true" : "false");
    });
    months.forEach(function (month) {
      var count = month.querySelectorAll(".tl-item:not([hidden])").length;
      month.hidden = count === 0;
      month.querySelector("[data-tl-count]").textContent = count;
      var link = root.querySelector('[data-tl-month-link="' + month.id + '"]');
      if (link) { dim(link, !count); link.querySelector("[data-tl-nav-count]").textContent = count; }
    });
    var openMatches = terms.length > 0 || kind === "stream";
    if (openMatches && !savedOpen) savedOpen = streams.map(function (stream) { return stream.open; });
    var blogCount = 0;
    streams.forEach(function (stream, index) {
      var count = stream.querySelectorAll(".tl-item:not([hidden])").length;
      blogCount += count;
      stream.hidden = !count;
      stream.querySelector("[data-tl-stream-count]").textContent = count;
      if (openMatches && count) stream.open = true;
      else if (!openMatches && savedOpen) stream.open = savedOpen[index];
    });
    if (!openMatches) savedOpen = null;
    var blogSection = root.querySelector("[data-tl-streams]");
    if (blogSection) { blogSection.hidden = !blogCount; blogSection.querySelector("[data-tl-blog-count]").textContent = blogCount; }
    array("[data-tl-blog-link]").forEach(function (link) {
      dim(link, !blogCount);
      var count = link.querySelector("span");
      if (count && count.textContent.trim() !== "↓") count.textContent = blogCount;
    });
    if (empty) empty.hidden = visible > 0 || items.length === 0;
    if (status) status.textContent = visible + " / " + items.length + " 篇记录 · " + (terms.length ? "搜索结果" : "按发表日期从早到晚排列");
    if (clear) clear.hidden = !query.value;
    if (writeURL) syncURL();
    markSection();
  }
  // the month index is a fixed row of twelve tabs: a month the filter empties greys out in place
  function dim(link, off) {
    link.classList.toggle("is-empty", off);
    if (off) { link.setAttribute("aria-disabled", "true"); link.tabIndex = -1; }
    else { link.removeAttribute("aria-disabled"); link.removeAttribute("tabindex"); }
  }
  function readURL() {
    var params = new URL(location.href).searchParams;
    var requested = params.get("k") || "all";
    kind = validKind(requested) ? requested : "all";
    if (query) query.value = (params.get("q") || "").slice(0, 160);
    if (status) update(false);
  }
  function markSection() {
    var sections = array("[data-tl-section]").filter(function (section) { return !section.hidden; });
    var active = null;
    sections.forEach(function (section) {
      if (section.getBoundingClientRect().top <= 160) active = section;
    });
    if (!active && sections.length) active = sections[0];
    array("[data-tl-section-link]").forEach(function (link) {
      if (active && link.getAttribute("href") === "#" + active.id) link.setAttribute("aria-current", "location");
      else link.removeAttribute("aria-current");
    });
  }
  // ---- the calendar sheet --------------------------------------------------------------
  var pad = function (n) { return (n < 10 ? "0" : "") + n; };
  var esc = function (s) { return String(s || "").replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
  var passers = root.querySelector("[data-tl-passers]");
  function sheet() {
    var now = new Date(), h = now.getHours(), m = now.getMonth() + 1, d = now.getDate();
    var art = root.getAttribute("data-art") || "/assets/img/timeline/";
    // the reader's time of day and season, as on the overview's today sheet (timeline-calendar.js)
    var tod = h >= 4 && h < 10 ? ["morning", "MORNING · 清晨"] : h >= 10 && h < 17 ? ["day", "DAY · 白天"] : h >= 17 && h < 19 ? ["evening", "EVENING · 傍晚"] : ["night", "NIGHT · 夜里"];
    var season = m >= 3 && m <= 5 ? ["spring", "春"] : m >= 6 && m <= 8 ? ["summer", "夏"] : m >= 9 && m <= 11 ? ["autumn", "秋"] : ["winter", "冬"];
    var sky = root.querySelector("[data-tl-sky]");
    if (sky) {
      sky.setAttribute("data-tod", tod[0]);
      var label = root.querySelector("[data-tl-tod]");
      if (label) label.textContent = tod[1] + " " + pad(h) + ":" + pad(now.getMinutes());
    }
    // this day, or this month, of the year on the sheet
    var year = +root.getAttribute("data-tl-year"), ago = now.getFullYear() - year;
    var when = ago > 0 ? ago + " 年前的" : "";
    var tab = root.querySelector('.tlc-months [data-month="' + m + '"]');
    if (tab) tab.classList.add("is-now");
    var line = root.querySelector("[data-tl-thismonth]");
    var month = root.querySelector('[data-tl-month][data-month="' + m + '"]');
    if (!line || !month) return;
    var today = Array.prototype.slice.call(month.querySelectorAll(".tl-entry")).filter(function (item) {
      return (item.querySelector("time") || {}).getAttribute("datetime") === year + "-" + pad(m) + "-" + pad(d);
    });
    var img = '<img src="' + esc(art) + "deerling-" + season[0] + '.png" alt="" width="14" height="22">';
    if (today.length) {
      var a = today[0].querySelector(".tl-entry__title a");
      line.innerHTML = img + "<span>" + (when ? when + "今天" : "今天") + "：</span>" + '<a href="' + esc(a.getAttribute("href")) + '">' + esc(a.textContent) + "</a>";
    } else {
      var n = month.querySelectorAll(".tl-entry").length;
      line.innerHTML = img + "<span>" + (when ? when + "这个月" : "这个月") + "：</span>" + '<a href="#' + month.id + '">' + m + " 月的 " + n + " 篇 ↓</a>";
    }
    line.hidden = false;
  }
  // the speakers glide from right to left while the sheet's head crosses the screen
  function glide() {
    if (!passers) return;
    var box = passers.parentNode, r = box.getBoundingClientRect(), vh = window.innerHeight;
    if (r.bottom < 0 || r.top > vh) return;
    var p = Math.min(1, Math.max(0, (vh - r.top) / vh));
    var w = passers.scrollWidth, bw = box.clientWidth;
    passers.style.setProperty("--x", (bw * 0.12 * (1 - p) - Math.max(0, w - bw * 0.85) * p).toFixed(1) + "px");
  }
  try {
    array(".tl-enhance").forEach(function (element) { element.hidden = false; });
    sheet();
    if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) glide(); else passers = null;
    var jump = root.querySelector("[data-tl-jump]");
    if (jump) jump.addEventListener("click", function (event) {
      var link = event.target.closest("a");
      if (!link) return;
      var url = new URL(link.href);
      if (kind !== "all") url.searchParams.set("k", kind);
      if (query && query.value.trim()) url.searchParams.set("q", query.value.trim());
      link.href = url.href;
      jump.open = false;
    });
    var desktopNavigation = window.matchMedia("(min-width: 761px)");
    var navigationTools = array("[data-tl-nav-tools]");
    var setNavigation = function () { navigationTools.forEach(function (tools) { tools.open = desktopNavigation.matches; }); };
    setNavigation();
    if (desktopNavigation.addEventListener) desktopNavigation.addEventListener("change", setNavigation);
    array("[data-tl-year-picker]").forEach(function (form) {
      form.addEventListener("submit", function (event) {
        event.preventDefault();
        var select = form.querySelector("[data-tl-year-select]");
        if (!select.value) { select.focus(); return; }
        var url = new URL(select.value, location.href);
        if (url.origin !== location.origin) return;
        if (kind !== "all") url.searchParams.set("k", kind);
        if (query && query.value.trim()) url.searchParams.set("q", query.value.trim());
        location.assign(url.href);
      });
    });
    buttons.forEach(function (button) { button.addEventListener("click", function () { kind = button.dataset.tlFilter; update(true); }); });
    if (query) { query.maxLength = 160; query.addEventListener("input", function () { update(true); }); }
    if (clear) clear.addEventListener("click", function () { query.value = ""; update(true); query.focus(); });
    array("[data-tl-reset]").forEach(function (button) { button.addEventListener("click", function () { kind = "all"; if (query) query.value = ""; update(true); if (query) query.focus(); }); });
    window.addEventListener("popstate", readURL);
    var scheduled = false;
    window.addEventListener("scroll", function () {
      if (scheduled) return;
      scheduled = true;
      requestAnimationFrame(function () { scheduled = false; markSection(); glide(); });
    }, { passive: true });
    readURL();
    markSection();
    root.classList.add("is-ready");
  } catch (error) {
    items.forEach(function (item) { item.hidden = false; });
    months.forEach(function (month) { month.hidden = false; });
    streams.forEach(function (stream) { stream.hidden = false; });
    array("[data-tl-month-link], [data-tl-blog-link], [data-tl-streams]").forEach(function (element) { element.hidden = false; element.classList.remove("is-empty"); });
    array(".tl-enhance").forEach(function (element) { element.hidden = true; });
    if (empty) empty.hidden = true;
    if (status) status.textContent = "筛选暂时无法使用，已显示全部资料。年份、月份与文章链接仍可正常使用。";
  }
})();
