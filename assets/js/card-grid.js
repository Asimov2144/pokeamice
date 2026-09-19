/* The card walls of the library pages (_layouts/library.html): the compact entry
   cards are of different heights - a wide picture, a tall one, none - so each one
   spans as many 4px rows of its grid as it is tall (plus the 8px margin; the grid's
   own row gap is off) and the next card moves up under it. The same packing
   assets/js/catalogue.js does for the home page. One column (a phone) needs none
   of it. Measured again when the width changes, a picture or the fonts arrive. */
(function () {
  "use strict";
  var walls = Array.prototype.slice.call(document.querySelectorAll("[data-card-grid]"));
  if (!walls.length) return;
  walls.forEach(function (wall) {
    var frame = 0;
    function pack() {
      if (frame) return;
      frame = window.requestAnimationFrame(function () {
        frame = 0;
        if (!wall.clientWidth) return;
        var cards = Array.prototype.slice.call(wall.children);
        var columns = getComputedStyle(wall).gridTemplateColumns.split(" ").length;
        if (columns < 2) {
          wall.classList.remove("is-masonry");
          cards.forEach(function (c) { c.style.gridRowEnd = ""; });
          return;
        }
        wall.classList.add("is-masonry");
        cards.forEach(function (c) {
          c.style.gridRowEnd = "span " + Math.max(1, Math.ceil((c.getBoundingClientRect().height + 8) / 4));
        });
      });
    }
    if (window.ResizeObserver) new ResizeObserver(pack).observe(wall);
    else window.addEventListener("resize", pack);
    wall.addEventListener("load", pack, true);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(pack);
    pack();
  });
})();
