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
  cards.forEach(function (c) {
    var t = c.querySelector(".fr-text");
    if (t && t.scrollHeight <= t.clientHeight + 4) t.classList.add("short");
  });
  wall.addEventListener("click", function (e) {
    var t = e.target.closest(".fr-text");
    if (t && !e.target.closest("a")) t.classList.toggle("open");
  });
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
