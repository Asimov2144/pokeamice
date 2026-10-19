/* 各作团队按职能 on /credits/ (_layouts/credits-index.html): one bar per game, its development team
   split by each person's main 职能 (assets/data/credits-orgmap/index.json, from tools/build-atlas-pages.py -
   the same 主职 the game pages' Development Atlas counts). 人数 draws every bar against the biggest team,
   so the growth shows; 比例 draws each at full width, so the mix shows. A bar opens the game's org map. */
(function () {
  "use strict";
  var root = document.querySelector("[data-credits-roles]");
  if (!root) return;
  var list = root.querySelector("[data-cr-list]");
  var legend = root.querySelector("[data-cr-legend]");
  var state = { mode: "count", spin: false };
  var data = null;
  var DEV = ["Dir", "Plan", "Prog", "Art", "Sound", "Mgmt", "Debug", "Other"];

  function esc(v) { return String(v == null ? "" : v).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }

  function render() {
    var zh = {};
    data.cats.forEach(function (c) { zh[c[0]] = c[1]; });
    var games = data.games.filter(function (g) { return g.dev > 0 && (state.spin || g.core); });
    var max = games.reduce(function (m, g) { return Math.max(m, g.dev); }, 1);
    legend.innerHTML = DEV.filter(function (c) { return games.some(function (g) { return g.roles[c]; }); }).map(function (c) {
      return "<span><i class='cat-" + c + "'></i>" + esc(zh[c]) + "</span>";
    }).join("");
    list.innerHTML = games.map(function (g) {
      var width = state.mode === "count" ? Math.max(2, g.dev / max * 100) : 100;
      var segs = DEV.filter(function (c) { return g.roles[c]; }).map(function (c) {
        var n = g.roles[c];
        return "<i class='cat-" + c + "' style='flex-grow:" + n + "' title='" + esc(zh[c]) + " " + n + " 人（" + Math.round(n / g.dev * 100) + "%）'>" + (n / g.dev >= 0.12 && (state.mode !== "count" || g.dev / max > 0.25) ? n : "") + "</i>";
      }).join("");
      return "<a class='cr-row" + (g.core ? "" : " is-spin") + "' href='/credits/" + esc(g.slug) + "/#orgmap'><span class='cr-year'>" + g.year + "</span><span class='cr-title'>" + esc(g.title) + (g.nested ? " <em>有部门</em>" : "") + "</span>" +
        "<span class='cr-bar'><span class='cr-fill' style='width:" + width.toFixed(1) + "%'>" + segs + "</span></span><b>" + g.dev + "</b></a>";
    }).join("");
    root.querySelectorAll("[data-cr-mode]").forEach(function (b) { b.classList.toggle("is-on", b.getAttribute("data-cr-mode") === state.mode); });
    root.querySelectorAll("[data-cr-spin]").forEach(function (b) { b.classList.toggle("is-on", (b.getAttribute("data-cr-spin") === "1") === state.spin); });
  }

  root.addEventListener("click", function (e) {
    var b = e.target.closest ? e.target.closest("button") : null;
    if (!b) return;
    if (b.hasAttribute("data-cr-mode")) state.mode = b.getAttribute("data-cr-mode");
    if (b.hasAttribute("data-cr-spin")) state.spin = b.getAttribute("data-cr-spin") === "1";
    if (data) render();
  });

  fetch(root.getAttribute("data-src"), { credentials: "same-origin" }).then(function (r) {
    if (!r.ok) throw new Error(String(r.status));
    return r.json();
  }).then(function (d) { data = d; render(); }).catch(function () { list.innerHTML = "<p class='om-empty'>读取失败，请刷新重试。</p>"; });
})();
