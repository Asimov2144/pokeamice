(function () {
  var wall = document.getElementById("fr-wall");
  if (!wall) return;
  var cards = Array.prototype.slice.call(wall.querySelectorAll(".fr"));
  var months = Array.prototype.slice.call(wall.querySelectorAll(".fr-month, .fr-group"));
  var q = document.getElementById("fr-q"), y = document.getElementById("fr-y");
  var img = document.getElementById("fr-img"), rs = document.getElementById("fr-r");
  var n = document.getElementById("fr-n"), empty = document.getElementById("fr-empty");
  var chips = Array.prototype.slice.call(document.querySelectorAll(".fr-chip"));
  var on = {}, onK = {};
  var sbtn = Array.prototype.slice.call(document.querySelectorAll(".st-b"));
  sbtn.forEach(function (b) {
    b.addEventListener("click", function () {
      var k = b.getAttribute("data-k");
      onK[k] = !onK[k]; b.classList.toggle("on", !!onK[k]); apply();
    });
  });
  var reader = document.getElementById("fr-reader");
  if (reader && typeof reader.showModal === "function") {
    var readerContent = document.getElementById("fr-reader-content");
    var readerDate = document.getElementById("fr-reader-date");
    var readerSource = document.getElementById("fr-reader-source");
    var opener;
    wall.classList.add("fr-reader-ready");
    cards.forEach(function (c) {
      var button = document.createElement("button");
      button.type = "button";
      button.className = "fr-read";
      button.textContent = "展开阅读";
      button.setAttribute("aria-label", c.getAttribute("data-d") + "的微博，展开阅读");
      button.setAttribute("aria-haspopup", "dialog");
      button.setAttribute("aria-controls", "fr-reader");
      c.querySelector(".fr-meta").appendChild(button);
    });
    // Measure only text near the viewport; off-screen months use content-visibility.
    var textObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          var t = entry.target;
          t.classList.toggle("short", t.scrollHeight <= t.clientHeight + 4);
        }
      });
    });
    wall.querySelectorAll(".fr-text").forEach(function (t) { textObserver.observe(t); });

    function openReader(card, button) {
      readerContent.replaceChildren();
      var body = card.querySelector(".fr-text, .fr-flow, .fr-mag, .fr-spread-body");
      if (body) {
        var text = body.cloneNode(true);
        // The collage interleaves images automatically. Read the original text in
        // one column, followed by the complete album in its original order.
        text.querySelectorAll(".fr-imgs, .fr-figure, .fr-row, .stk").forEach(function (el) { el.remove(); });
        text.className = "fr-reader-text";
        readerContent.appendChild(text);
      }
      var photos = Array.prototype.slice.call(card.querySelectorAll("a.fr-ph"));
      var extra = card.querySelector("template.fr-extra-images");
      if (extra) photos = photos.concat(Array.prototype.slice.call(extra.content.querySelectorAll("a.fr-ph")));
      if (photos.length) {
        var heading = document.createElement("h3");
        heading.className = "fr-reader-gallery-title";
        heading.textContent = "配图 · " + photos.length + " 张";
        readerContent.appendChild(heading);
        var gallery = document.createElement("div");
        gallery.className = "fr-reader-gallery";
        photos.forEach(function (photo, index) {
          var link = photo.cloneNode(true);
          link.className = "fr-reader-photo";
          link.removeAttribute("style");
          link.setAttribute("aria-label", "查看第 " + (index + 1) + " 张配图");
          link.querySelector("img").alt = "微博配图 " + (index + 1);
          gallery.appendChild(link);
        });
        readerContent.appendChild(gallery);
      }
      var videoNote = card.querySelector(".fr-vnote");
      if (videoNote) readerContent.appendChild(videoNote.cloneNode(true));
      var source = card.querySelector(".fr-foot a");
      readerSource.hidden = !source;
      if (source) readerSource.href = source.href;
      readerDate.textContent = card.getAttribute("data-d") + " " + card.querySelector("time").textContent.slice(-5);
      opener = button;
      document.documentElement.classList.add("fr-reading");
      reader.showModal();
      readerContent.scrollTop = 0;
    }
    wall.addEventListener("click", function (e) {
      var button = e.target.closest(".fr-read");
      if (button) openReader(button.closest(".fr"), button);
    });
    reader.querySelector(".fr-reader-close").addEventListener("click", function () { reader.close(); });
    reader.addEventListener("click", function (e) {
      var rect = reader.getBoundingClientRect();
      if (e.target === reader && (e.clientX < rect.left || e.clientX > rect.right ||
          e.clientY < rect.top || e.clientY > rect.bottom)) reader.close();
    });
    reader.addEventListener("close", function () {
      document.documentElement.classList.remove("fr-reading");
      if (opener) opener.focus({ preventScroll: true });
      readerContent.replaceChildren();
    });
  }
  chips.forEach(function (b) {
    b.addEventListener("click", function () {
      var c = b.getAttribute("data-c");
      on[c] = !on[c]; b.classList.toggle("on", !!on[c]); apply();
    });
  });
  var timer;
  q.addEventListener("input", function () { clearTimeout(timer); timer = setTimeout(apply, 120); });
  [y, img, rs].forEach(function (el) { el.addEventListener("change", apply); });
  function apply() {
    var words = q.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
    var cats = Object.keys(on).filter(function (k) { return on[k]; });
    var ks = Object.keys(onK).filter(function (k) { return onK[k]; });
    var yr = y.value, shown = 0, seen = {};
    cards.forEach(function (c) {
      var ok = true;
      if (cats.length && cats.indexOf(c.getAttribute("data-c")) < 0) ok = false;
      if (ok && ks.length) {
        var have = (c.getAttribute("data-k") || "").split(" "), hit = false;
        for (var j = 0; j < ks.length; j++) if (have.indexOf(ks[j]) >= 0) { hit = true; break; }
        if (!hit) ok = false;
      }
      if (ok && yr && c.getAttribute("data-d").slice(0, 4) !== yr) ok = false;
      if (ok && img.checked && c.getAttribute("data-i") !== "1") ok = false;
      if (ok && rs.checked && +c.getAttribute("data-r") < 2) ok = false;
      if (ok && words.length) {
        var s = c.getAttribute("data-s");
        for (var i = 0; i < words.length; i++) if (s.indexOf(words[i]) < 0) { ok = false; break; }
      }
      c.hidden = !ok;
      if (ok) { shown++; seen[c.getAttribute("data-d").slice(0, 7)] = 1; }
    });
    months.forEach(function (m) { m.hidden = !seen[m.getAttribute("data-m")]; });
    n.textContent = "显示 " + shown + " / " + cards.length;
    empty.hidden = shown > 0;
  }
  apply();
})();
