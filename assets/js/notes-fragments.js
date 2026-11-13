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
    var opener;
    cards.forEach(function (c) {
      c.classList.add("fr-can-open");
      var button = document.createElement("button");
      button.type = "button";
      button.className = "fr-read";
      button.textContent = "展开 ↗";
      button.setAttribute("aria-label", c.getAttribute("data-d") + "的微博，展开阅读");
      button.setAttribute("aria-haspopup", "dialog");
      button.setAttribute("aria-controls", "fr-reader");
      var action = document.createElement("span");
      action.className = "fr-read-action";
      action.appendChild(document.createTextNode(" · "));
      action.appendChild(button);
      c.querySelector(".fr-foot").appendChild(action);
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
      // Enlarge the actual designed card: keep its paper, inline colour/rotation,
      // stickers, photo treatments, captions, and interleaved text/image layout.
      var copy = card.cloneNode(true);
      copy.removeAttribute("id");
      copy.classList.remove("fr-can-open");
      copy.classList.add("fr-expanded");
      copy.querySelectorAll(".fr-read-action").forEach(function (el) { el.remove(); });
      var extra = copy.querySelector("template.fr-extra-images");
      if (extra) {
        var layout = copy.querySelector(".fr-mag, .fr-spread-body, .im-mosaic");
        var photos = Array.prototype.slice.call(extra.content.querySelectorAll("a.fr-ph"));
        if (layout && layout.matches(".fr-mag, .fr-spread-body")) {
          photos.forEach(function (photo, index) {
            var figure = document.createElement("div");
            figure.className = "fr-figure fr-fig-" + (index % 2);
            figure.appendChild(photo.cloneNode(true));
            layout.appendChild(figure);
          });
        } else if (layout) {
          for (var i = 0; i < photos.length; i += 3) {
            var row = document.createElement("div");
            row.className = "fr-row";
            photos.slice(i, i + 3).forEach(function (photo) { row.appendChild(photo.cloneNode(true)); });
            layout.appendChild(row);
          }
        }
        extra.remove();
        copy.querySelectorAll(".fr-more").forEach(function (el) { el.remove(); });
      }
      readerContent.appendChild(copy);
      reader.setAttribute("aria-label", card.getAttribute("data-d") + "的微博，放大阅读");
      opener = button;
      document.documentElement.classList.add("fr-reading");
      reader.showModal();
      readerContent.scrollTop = 0;
    }
    wall.addEventListener("click", function (e) {
      var button = e.target.closest(".fr-read");
      if (button) {
        openReader(button.closest(".fr"), button);
        return;
      }
      // Keep links and text selection working; the rest of the paper can open it.
      if (e.target.closest("a, button, input, select, label")) return;
      var selection = window.getSelection();
      if (selection && !selection.isCollapsed) return;
      var card = e.target.closest(".fr");
      if (card) openReader(card, card.querySelector(".fr-read"));
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
