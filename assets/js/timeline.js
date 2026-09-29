/* The timeline's year page (_includes/timeline-year.html): the type buttons show and hide the
   cards that are already on the page, and a month with nothing left folds away. The card walls
   re-pack themselves (assets/js/card-grid.js) when the window is resized, so the script nudges it. */
(function () {
  "use strict";
  var bar = document.querySelector(".tl-filters");
  if (!bar) return;
  var items = Array.prototype.slice.call(document.querySelectorAll(".tl-item"));
  var months = Array.prototype.slice.call(document.querySelectorAll("[data-tl-month]"));
  function show(kind) {
    Array.prototype.forEach.call(bar.querySelectorAll("button[data-tl-filter]"), function (b) {
      b.classList.toggle("is-on", b.getAttribute("data-tl-filter") === kind);
    });
    items.forEach(function (it) { it.hidden = kind !== "all" && it.getAttribute("data-kind") !== kind; });
    months.forEach(function (m) {
      var n = m.querySelectorAll(".tl-item:not([hidden])").length;
      m.hidden = n === 0;
      var c = m.querySelector("[data-tl-count]");
      if (c) c.textContent = n;
    });
    window.dispatchEvent(new Event("resize"));
  }
  bar.addEventListener("click", function (e) {
    var b = e.target.closest("button[data-tl-filter]");
    if (b) show(b.getAttribute("data-tl-filter"));
  });
  var want = /[?&]k=(interview|scan|topic|article)\b/.exec(location.search);
  if (want && bar.querySelector('[data-tl-filter="' + want[1] + '"]')) show(want[1]);
})();
