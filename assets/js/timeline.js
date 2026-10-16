/* Server-rendered chronicle. Search, filtering and jump navigation enhance
   complete HTML; there is no network request, masonry or content replacement. */
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
      if (link) { link.hidden = !count; link.querySelector("[data-tl-nav-count]").textContent = count; }
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
      link.hidden = !blogCount;
      var count = link.querySelector("span");
      if (count && count.textContent.trim() !== "↓") count.textContent = blogCount;
    });
    if (empty) empty.hidden = visible > 0 || items.length === 0;
    if (status) status.textContent = visible + " / " + items.length + " 篇记录 · " + (terms.length ? "搜索结果" : "按发表日期从早到晚排列");
    if (clear) clear.hidden = !query.value;
    if (writeURL) syncURL();
    markSection();
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
  try {
    array(".tl-enhance").forEach(function (element) { element.hidden = false; });
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
      requestAnimationFrame(function () { scheduled = false; markSection(); });
    }, { passive: true });
    readURL();
    markSection();
    root.classList.add("is-ready");
  } catch (error) {
    items.forEach(function (item) { item.hidden = false; });
    months.forEach(function (month) { month.hidden = false; });
    streams.forEach(function (stream) { stream.hidden = false; });
    array("[data-tl-month-link], [data-tl-blog-link], [data-tl-streams]").forEach(function (element) { element.hidden = false; });
    array(".tl-enhance").forEach(function (element) { element.hidden = true; });
    if (empty) empty.hidden = true;
    if (status) status.textContent = "筛选暂时无法使用，已显示全部资料。年份、月份与文章链接仍可正常使用。";
  }
})();
