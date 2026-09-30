/* The outlet buttons of /overseas/ (_pages/overseas.md): they show and hide the cards that are
   already on the page, and a region with nothing left folds away. The card walls re-pack nothing
   here (plain grids), so no resize nudge is needed. ?o=<outlet key> opens with one outlet chosen. */
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
  var want = /[?&]o=([a-z0-9]+)\b/.exec(location.search);
  if (want && bar.querySelector('[data-hub-filter="' + want[1] + '"]')) show(want[1]);
})();
