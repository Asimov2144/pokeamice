/* 部门与职能图 on a game's staff-roll page (_layouts/credits-game.html): from
   assets/data/credits-orgmap/<game>.json (tools/build-atlas-pages.py). Each block is a department -
   or, for a roll with no Section / Team levels, a 职能 - sized by headcount; each tile in it is one
   block of the roll, coloured by 职能. A tile opens its people; 找人 lights up every seat a person
   holds; the legend dims all but one 职能. Only the development team by default: localisation and
   thanks can be switched on. The full text of the structure stays below (文字版组织结构). */
(function () {
  "use strict";
  var root = document.querySelector("[data-orgmap]");
  if (!root) return;
  var stage = root.querySelector("[data-om-stage]");
  var panel = root.querySelector("[data-om-panel]");
  var bar = root.querySelector("[data-om-bar]");
  var data = null;
  var state = { view: "role", scope: "dev", cat: "", who: "", sel: -1 };

  function esc(v) { return String(v == null ? "" : v).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function catZh(c) { var x = data.cats.find(function (p) { return p[0] === c; }); return x ? x[1] : c; }
  function inScope(t) { return state.scope === "all" || t.k === "dev"; }
  function holds(t, q) {
    if (!q) return false;
    return t.m.some(function (m) { return String(m[0]).toLowerCase().indexOf(q) >= 0 || String(m[3]).toLowerCase().indexOf(q) >= 0; });
  }
  function tileName(t) { return t.z || t.l; }

  function blocks() {
    var list = state.view === "dept" && data.dept.length ? data.dept : data.role.map(function (r) { return { l: catZh(r.c), z: "", s: "", o: [], n: r.n, t: r.t, c: r.c }; });
    return list.map(function (b) {
      var ids = b.t.filter(function (i) { return inScope(data.tiles[i]); });
      var n = ids.reduce(function (a, i) { return a + data.tiles[i].n; }, 0);
      return { b: b, ids: ids, n: n };
    }).filter(function (x) { return x.ids.length; });
  }

  function renderBar() {
    var cats = {};
    data.tiles.forEach(function (t) { if (inScope(t)) cats[t.c] = (cats[t.c] || 0) + t.n; });
    var views = data.nested
      ? "<div class='om-seg' role='group' aria-label='怎么分'><button type='button' data-om-view='dept'" + (state.view === "dept" ? " class='is-on'" : "") + ">按部门</button><button type='button' data-om-view='role'" + (state.view === "role" ? " class='is-on'" : "") + ">按职能</button></div>"
      : "<p class='om-flat'>这部作品的名单没有部门层级，按职能分组。</p>";
    var scope = "<div class='om-seg' role='group' aria-label='范围'><button type='button' data-om-scope='dev'" + (state.scope === "dev" ? " class='is-on'" : "") + ">开发团队</button><button type='button' data-om-scope='all'" + (state.scope === "all" ? " class='is-on'" : "") + ">含本地化与鸣谢</button></div>";
    var legend = "<div class='om-legend' role='group' aria-label='只看一种职能'>" + data.cats.filter(function (c) { return cats[c[0]]; }).map(function (c) {
      return "<button type='button' class='cat-" + esc(c[0]) + (state.cat === c[0] ? " is-on" : "") + "' data-om-cat='" + esc(c[0]) + "'>" + esc(c[1]) + " <b>" + cats[c[0]] + "</b></button>";
    }).join("") + "</div>";
    var names = {};
    data.tiles.forEach(function (t) { if (inScope(t)) t.m.forEach(function (m) { names[m[0]] = 1; }); });
    var find = "<label class='om-find'><span>找人</span><input type='search' list='om-names' placeholder='姓名或罗马字' value='" + esc(state.who) + "' data-om-find><datalist id='om-names'>" +
      Object.keys(names).sort().map(function (n) { return "<option value='" + esc(n) + "'>"; }).join("") + "</datalist></label>";
    bar.innerHTML = "<div class='om-row'>" + views + scope + find + "</div>" + legend;
  }

  function renderStage() {
    var q = state.who.trim().toLowerCase();
    var lastScope = null;
    var html = "";
    blocks().forEach(function (x) {
      var b = x.b;
      if (state.view === "dept" && data.dept.length && b.s !== lastScope) {
        if (lastScope !== null) html += "</div>";
        html += "<div class='om-group'><h4>" + esc(data.scopes[b.s] || (b.s ? b.s : "开发本体")) + "</h4>";
        lastScope = b.s;
      }
      var org = b.o && b.o.length && !(b.o.length === 1 && b.o[0] === "Game Freak") ? "<em>" + esc(b.o.join(" · ")) + "</em>" : "";
      // a block's width follows its headcount (square root, so a hundred-person department is wide but not the whole row)
      html += "<section class='om-block' style='flex-basis:" + Math.round(140 + Math.sqrt(x.n) * 26) + "px'>" +
        "<header><b>" + esc(b.l) + "</b>" + (b.z ? "<small>" + esc(b.z) + "</small>" : "") + org + "<span>" + x.n + "</span></header><div class='om-tiles'>" +
        x.ids.map(function (i) {
          var t = data.tiles[i];
          var cls = "om-tile cat-" + t.c;
          if (state.cat && t.c !== state.cat) cls += " is-dim";
          if (q) cls += holds(t, q) ? " is-hit" : " is-dim";
          if (state.sel === i) cls += " is-sel";
          var leads = t.m.filter(function (m) { return m[2] >= 1; }).slice(0, 2).map(function (m) { return m[0]; });
          return "<button type='button' class='" + cls + "' style='flex-grow:" + Math.max(1, t.n) + "' data-om-tile='" + i + "' title='" + esc(t.p + (t.z ? "（" + t.z + "）" : "") + " · " + t.n + " 人" + (leads.length ? " · " + leads.join("、") : "")) + "'>" +
            "<span>" + esc(tileName(t)) + "</span><b>" + (t.n || (t.co ? t.co + " 家" : "")) + "</b></button>";
        }).join("") + "</div></section>";
    });
    if (lastScope !== null) html += "</div>";
    stage.innerHTML = html || "<p class='om-empty'>这个范围里没有区块。</p>";
  }

  function person(m) {
    var name = m[1] ? "<a href='/people/" + esc(m[1]) + "/'>" + esc(m[0]) + "</a>" : esc(m[0]);
    return "<li" + (m[2] >= 1 ? " class='is-lead'" : "") + ">" + name + (m[3] && m[3] !== m[0] ? "<small>" + esc(m[3]) + "</small>" : "") + (m[2] >= 1 ? "<i>" + (m[2] >= 3 ? "总监级" : m[2] === 2 ? "部门负责人" : "Lead") + "</i>" : "") + "</li>";
  }

  function renderPanel() {
    var q = state.who.trim().toLowerCase();
    if (state.sel >= 0) {
      var t = data.tiles[state.sel];
      panel.innerHTML = "<h4>" + esc(tileName(t)) + "</h4><p class='om-path'>" + esc(t.p) + (t.j ? "<br>" + esc(t.j) : "") + "</p>" +
        "<p class='om-tags'><i class='cat-" + esc(t.c) + "'>" + esc(catZh(t.c)) + "</i>" + (t.d ? "<em>" + esc(t.d) + "</em>" : "") + "<b>" + t.n + " 人</b>" + (t.o ? " · " + esc(t.o) : "") + "</p>" +
        (t.m.length ? "<ul class='om-people'>" + t.m.map(person).join("") + "</ul>" : "<p class='om-empty'>这一块只列了公司名（" + t.co + " 家）。</p>") +
        "<p class='om-links'><button type='button' data-om-locate='" + state.sel + "'>在下面的名单里定位 ↓</button></p>";
      return;
    }
    if (q) {
      var seats = [];
      data.tiles.forEach(function (t, i) { if (inScope(t) && holds(t, q)) seats.push(i); });
      panel.innerHTML = seats.length
        ? "<h4>「" + esc(state.who) + "」在这一作的 " + seats.length + " 个位置</h4><ul class='om-seats'>" + seats.map(function (i) {
            var t = data.tiles[i];
            return "<li><button type='button' data-om-tile='" + i + "'><i class='cat-" + esc(t.c) + "'></i>" + esc(tileName(t)) + "<small>" + esc(t.p) + "</small></button></li>";
          }).join("") + "</ul>"
        : "<h4>没找到「" + esc(state.who) + "」</h4><p>换成罗马字试试，或者打开「含本地化与鸣谢」。</p>";
      return;
    }
    var bl = blocks();
    var total = bl.reduce(function (a, x) { return a + x.n; }, 0);
    var biggest = bl.slice().sort(function (a, b) { return b.n - a.n; }).slice(0, 4).map(function (x) { return esc(x.b.l) + (x.b.z ? "（" + esc(x.b.z) + "）" : "") + " " + x.n; });
    panel.innerHTML = "<h4>怎么看</h4><p>" + (state.view === "dept" && data.dept.length ? "每一块是一个部门，" : "每一块是一种职能，") + "块越大人越多；里面的小格是名单上的一个区块，颜色是职能。点一格看这一组的人，「找人」看一个人坐在哪几格。</p>" +
      "<p class='om-sum'>" + total + " 人次" + (biggest.length ? "，最大的几块：" + biggest.join("、") : "") + "。</p>" +
      "<p class='om-note'>人次按区块算：一个人在两个区块里署名，就算两次。这是名单呈现的结构，不是正式的组织架构图。</p>";
  }

  function render() { renderBar(); renderStage(); renderPanel(); }

  root.addEventListener("click", function (e) {
    var el = e.target.closest ? e.target.closest("button") : null;
    if (!el || !root.contains(el)) return;
    if (el.hasAttribute("data-om-view")) { state.view = el.getAttribute("data-om-view"); state.sel = -1; render(); }
    else if (el.hasAttribute("data-om-scope")) { state.scope = el.getAttribute("data-om-scope"); state.sel = -1; render(); }
    else if (el.hasAttribute("data-om-cat")) { var c = el.getAttribute("data-om-cat"); state.cat = state.cat === c ? "" : c; renderBar(); renderStage(); }
    else if (el.hasAttribute("data-om-tile")) {
      var i = parseInt(el.getAttribute("data-om-tile"), 10);
      state.sel = state.sel === i ? -1 : i;
      renderStage(); renderPanel();
      if (state.sel >= 0 && window.matchMedia && window.matchMedia("(max-width: 900px)").matches) panel.scrollIntoView({ behavior: "smooth", block: "nearest" });
    } else if (el.hasAttribute("data-om-locate")) {
      var t = data.tiles[parseInt(el.getAttribute("data-om-locate"), 10)];
      var heads = Array.prototype.slice.call(document.querySelectorAll(".credits__roll h3"));
      var h = heads.find(function (x) { return x.textContent.trim().indexOf(t.p) === 0; }) || heads.find(function (x) { return x.textContent.indexOf(t.l) >= 0; });
      if (h) { h.scrollIntoView({ behavior: "smooth", block: "start" }); h.classList.add("om-flash"); setTimeout(function () { h.classList.remove("om-flash"); }, 2200); }
    }
  });
  var findTimer = 0;
  root.addEventListener("input", function (e) {
    if (!e.target.hasAttribute || !e.target.hasAttribute("data-om-find")) return;
    clearTimeout(findTimer);
    var v = e.target.value;
    findTimer = setTimeout(function () { state.who = v; state.sel = -1; renderStage(); renderPanel(); }, 150);
  });

  fetch(root.getAttribute("data-src"), { credentials: "same-origin" }).then(function (r) {
    if (!r.ok) throw new Error(String(r.status));
    return r.json();
  }).then(function (d) {
    data = d;
    state.view = d.nested && d.dept.length ? "dept" : "role";
    render();
  }).catch(function () { stage.innerHTML = "<p class='om-empty'>组织图读取失败，请刷新重试。</p>"; });
})();
