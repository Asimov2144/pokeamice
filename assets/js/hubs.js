/* The outlet buttons of /overseas/ (_pages/overseas.md): they show and hide the cards that are
   already on the page, and a region with nothing left folds away. The card walls re-pack nothing
   here (plain grids), so no resize nudge is needed. ?o=<outlet key> opens with one outlet chosen.
   按媒体 / 按地区 switch between the outlet boards and the regional sections (the same cards twice);
   ?view=region opens on the regions. */
(function () {
  "use strict";
  var bar = document.querySelector("[data-hub-bar]");
  if (!bar) return;
  var items = Array.prototype.slice.call(document.querySelectorAll("[data-hub-item]"));
  var regions = Array.prototype.slice.call(document.querySelectorAll("[data-hub-region]"));
  function show(key) {
    Array.prototype.forEach.call(bar.querySelectorAll("button[data-hub-filter]"), function (b) {
      b.classList.toggle("is-on", b.getAttribute("data-hub-filter") === key);
    });
    items.forEach(function (it) { it.hidden = key !== "all" && it.getAttribute("data-hub-item") !== key; });
    regions.forEach(function (r) {
      var n = r.querySelectorAll("[data-hub-item]:not([hidden])").length;
      r.hidden = n === 0;
      var c = r.querySelector("[data-hub-count]");
      if (c) c.textContent = n;
    });
  }
  bar.addEventListener("click", function (e) {
    var b = e.target.closest("button[data-hub-filter]");
    if (b) show(b.getAttribute("data-hub-filter"));
  });
  var panes = Array.prototype.slice.call(document.querySelectorAll("[data-hub-pane]"));
  var viewButtons = Array.prototype.slice.call(document.querySelectorAll("button[data-hub-view]"));
  function view(name) {
    panes.forEach(function (p) { p.hidden = p.getAttribute("data-hub-pane") !== name; });
    viewButtons.forEach(function (b) { b.classList.toggle("is-on", b.getAttribute("data-hub-view") === name); });
  }
  viewButtons.forEach(function (b) {
    b.addEventListener("click", function () { view(b.getAttribute("data-hub-view")); });
  });
  if (/[?&]view=region\b/.test(location.search)) view("region");
  var want = /[?&]o=([a-z0-9]+)\b/.exec(location.search);
  if (want && bar.querySelector('[data-hub-filter="' + want[1] + '"]')) show(want[1]);
})();
