/* The relationship graph (/resource-graph/): from assets/js/graph.json - one row per entry
   with its people, works and date - the browser builds the people network (a line where two
   people share an entry, its weight the number of entries), finds its communities, lays it
   out, and draws the people x works matrix, the timeline and the index of the strongest
   ties. Everything derives from the entries' entities, the same data the catalogue uses. */
(function() {
  "use strict";

  const root = document.querySelector("[data-graph]");
  if (!root) return;
  const $ = function(sel) { return root.querySelector(sel); };
  const els = {
    stats: $("[data-graph-stats]"), min: $("[data-graph-min]"), scope: $("[data-graph-scope]"), find: $("[data-graph-find]"),
    list: root.querySelector("#graph-people"), reset: $("[data-graph-reset]"), canvas: $("[data-graph-canvas]"), tip: $("[data-graph-tip]"),
    loading: $("[data-graph-loading]"), panel: $("[data-graph-panel]"), legend: $("[data-graph-legend]"), matrix: $("[data-graph-matrix]"),
    timeline: $("[data-graph-timeline]"), index: $("[data-graph-index]")
  };
  const WORKS = window.pokeamiceWorks || [];
  const WORK_ORDER = new Map(WORKS.map(function(w, i) { return [w.name, i]; }));
  const WORK_BY = new Map(WORKS.map(function(w) { return [w.name, w]; }));
  const PEOPLE_BASE = window.pokeamicePeopleBase || "/people/";
  const SEARCH_BASE = window.pokeamiceSearchBase || "/search/";
  const PALETTE = ["#2b6cb0", "#c05621", "#2f855a", "#6b46c1", "#b7791f", "#0f766e", "#b83280", "#4a5568", "#c53030", "#2c7a7b", "#805ad5", "#975a16"];

  function esc(v) { return String(v == null ? "" : v).replace(/[&<>"']/g, function(c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function searchUrl(q) { return SEARCH_BASE + "?" + q; }

  // ---------------------------------------------------------------- the model
  let entries = [];
  let model = null;         // the network for the current scope and threshold
  let selected = null;      // a person's name
  let hovered = null;
  const images = new Map(); // avatar url -> Image

  function inScope(e, scope) {
    return scope === "all" || e.k !== "Game Freak 博客";
  }

  function build(scope, minWeight) {
    const persons = new Map();
    const pairs = new Map();
    let nEntries = 0;
    const worksSeen = new Map();
    entries.forEach(function(e, idx) {
      if (!inScope(e, scope)) return;
      const people = (e.p || []).filter(function(p) { return p[2] === "person" || p[2] === "unknown"; });
      if (!people.length) return;
      nEntries += 1;
      const year = parseInt(String(e.d || "").slice(0, 4), 10) || 0;
      people.forEach(function(p) {
        let node = persons.get(p[0]);
        if (!node) {
          node = { name: p[0], slug: p[1], kind: p[2], avatar: p[3], n: 0, years: new Map(), works: new Map(), orgs: new Map(), entries: [], co: new Map(), sources: new Map() };
          persons.set(p[0], node);
        }
        node.n += 1;
        node.entries.push(idx);
        if (year) node.years.set(year, (node.years.get(year) || 0) + 1);
        (e.w || []).forEach(function(w) { if (WORK_BY.has(w)) { node.works.set(w, (node.works.get(w) || 0) + 1); worksSeen.set(w, (worksSeen.get(w) || 0) + 1); } });
        (e.o || []).forEach(function(o) { node.orgs.set(o, (node.orgs.get(o) || 0) + 1); });
        if (e.s) node.sources.set(e.s, (node.sources.get(e.s) || 0) + 1);
      });
      for (let i = 0; i < people.length; i++) {
        for (let j = i + 1; j < people.length; j++) {
          const a = people[i][0], b = people[j][0];
          if (a === b) continue;
          const key = a < b ? a + "" + b : b + "" + a;
          pairs.set(key, (pairs.get(key) || 0) + 1);
          persons.get(a).co.set(b, (persons.get(a).co.get(b) || 0) + 1);
          persons.get(b).co.set(a, (persons.get(b).co.get(a) || 0) + 1);
        }
      }
    });
    // the drawn network: the ties at or above the threshold, the people on them, and the
    // people met often enough to stand alone
    const edges = [];
    pairs.forEach(function(w, key) {
      if (w < minWeight) return;
      const k = key.split("");
      edges.push({ a: k[0], b: k[1], w: w });
    });
    const linked = new Set();
    edges.forEach(function(ed) { linked.add(ed.a); linked.add(ed.b); });
    const nodes = [];
    persons.forEach(function(node) {
      if (linked.has(node.name) || node.n >= 3) nodes.push(node);
    });
    const byName = new Map(nodes.map(function(n) { return [n.name, n]; }));
    nodes.forEach(function(n) { n.degree = 0; n.strength = 0; n.adj = []; });
    edges.forEach(function(ed) {
      const a = byName.get(ed.a), b = byName.get(ed.b);
      a.degree += 1; b.degree += 1; a.strength += ed.w; b.strength += ed.w;
      a.adj.push([b, ed.w]); b.adj.push([a, ed.w]);
    });
    const groups = communities(nodes);
    return { persons: persons, nodes: nodes, edges: edges, byName: byName, groups: groups, nEntries: nEntries, works: worksSeen, pairs: pairs };
  }

  // label propagation on the weighted network, in a fixed order so the result repeats;
  // then the groups named by their three most-covered members
  function communities(nodes) {
    const order = nodes.slice().sort(function(a, b) { return b.n - a.n || a.name.localeCompare(b.name, "zh"); });
    order.forEach(function(n, i) { n.label = i; });
    for (let round = 0; round < 40; round++) {
      let changed = 0;
      order.forEach(function(n) {
        if (!n.adj.length) return;
        const votes = new Map();
        n.adj.forEach(function(pair) { votes.set(pair[0].label, (votes.get(pair[0].label) || 0) + pair[1]); });
        let best = n.label, bestW = -1;
        votes.forEach(function(w, label) { if (w > bestW || (w === bestW && label < best)) { best = label; bestW = w; } });
        if (best !== n.label) { n.label = best; changed += 1; }
      });
      if (!changed) break;
    }
    const groups = new Map();
    order.forEach(function(n) {
      if (!groups.has(n.label)) groups.set(n.label, { members: [], n: 0 });
      const g = groups.get(n.label); g.members.push(n); g.n += n.n;
    });
    let list = Array.from(groups.values()).filter(function(g) { return g.members.length > 1; })
      .sort(function(a, b) { return b.members.length - a.members.length || b.n - a.n; });
    const alone = { members: order.filter(function(n) { return !n.adj.length; }), n: 0, rim: true };
    list.forEach(function(g, i) {
      g.id = i;
      g.color = i < PALETTE.length ? PALETTE[i] : "#9aa5b1";
      g.title = g.members.slice(0, 3).map(function(m) { return m.name; }).join(" · ");
      g.members.forEach(function(m) { m.group = g; });
    });
    if (alone.members.length) {
      alone.id = list.length; alone.color = "#a0aec0"; alone.title = "独立出现（无同场记录）";
      alone.members.forEach(function(m) { m.group = alone; m.n_alone = true; });
      list.push(alone);
    }
    return list;
  }

  // ---------------------------------------------------------------- the layout
  // Fruchterman-Reingold with the communities pulled towards their own corner, so the
  // clusters read as clusters; a few hundred nodes settle in a couple of hundred rounds
  function layout(m, W, H) {
    const nodes = m.nodes, edges = m.edges;
    const n = nodes.length;
    if (!n) return;
    const area = W * H;
    const k = Math.min(110, Math.sqrt(area / n) * 0.55);
    // each community gets a place on an inner ring, the bigger ones spread first; the
    // people with no ties stand on the rim, each at their own spot
    const centers = new Map();
    const real = m.groups.filter(function(g) { return !g.rim; });
    const G = real.length;
    real.forEach(function(g, i) {
      const ang = (i / Math.max(1, G)) * Math.PI * 2 - Math.PI / 2;
      const r = Math.min(W, H) * (G > 1 ? (i < 2 ? 0.24 : 0.3) : 0);
      centers.set(g.id, [W / 2 + Math.cos(ang) * r, H / 2 + Math.sin(ang) * r]);
    });
    const rim = m.groups.find(function(g) { return g.rim; });
    const anchors = new Map();
    if (rim) rim.members.forEach(function(nd, i) {
      const ang = (i / rim.members.length) * Math.PI * 2 + 0.3;
      anchors.set(nd.name, [W / 2 + Math.cos(ang) * W * 0.46, H / 2 + Math.sin(ang) * H * 0.44]);
    });
    nodes.forEach(function(nd, i) {
      const c = anchors.get(nd.name) || centers.get(nd.group.id) || [W / 2, H / 2];
      const a = (i * 2.399963), rr = anchors.has(nd.name) ? 0 : 20 + (i % 7) * 12;
      nd.x = c[0] + Math.cos(a) * rr; nd.y = c[1] + Math.sin(a) * rr;
      nd.r = Math.min(26, 4 + 2.4 * Math.sqrt(nd.n));
    });
    const byName = m.byName;
    let t = Math.max(W, H) / 10;
    const rounds = 300;
    const pad = 36;
    for (let it = 0; it < rounds; it++) {
      for (let i = 0; i < n; i++) { nodes[i].dx = 0; nodes[i].dy = 0; }
      for (let i = 0; i < n; i++) {
        const a = nodes[i];
        for (let j = i + 1; j < n; j++) {
          const b = nodes[j];
          let dx = a.x - b.x, dy = a.y - b.y;
          let d2 = dx * dx + dy * dy;
          if (d2 < 0.01) { dx = (Math.random() - 0.5); dy = (Math.random() - 0.5); d2 = dx * dx + dy * dy; }
          const d = Math.sqrt(d2);
          const f = (k * k) / d * (1 + (a.r + b.r) / 40) * (a.group === b.group ? 1 : 0.55);
          const fx = dx / d * f, fy = dy / d * f;
          a.dx += fx; a.dy += fy; b.dx -= fx; b.dy -= fy;
        }
      }
      edges.forEach(function(ed) {
        const a = byName.get(ed.a), b = byName.get(ed.b);
        const dx = a.x - b.x, dy = a.y - b.y;
        const d = Math.sqrt(dx * dx + dy * dy) || 0.01;
        const f = (d * d / k) * Math.min(3, 0.6 + Math.log(1 + ed.w) * 0.5);
        const fx = dx / d * f, fy = dy / d * f;
        a.dx -= fx; a.dy -= fy; b.dx += fx; b.dy += fy;
      });
      nodes.forEach(function(nd) {
        const c = anchors.get(nd.name) || centers.get(nd.group.id) || [W / 2, H / 2];
        const pull = anchors.has(nd.name) ? 0.35 : 0.09;
        nd.dx += (c[0] - nd.x) * pull;
        nd.dy += (c[1] - nd.y) * pull;
        nd.dx += (W / 2 - nd.x) * 0.02; nd.dy += (H / 2 - nd.y) * 0.02;
        const d = Math.sqrt(nd.dx * nd.dx + nd.dy * nd.dy) || 0.01;
        const step = Math.min(d, t);
        nd.x += nd.dx / d * step; nd.y += nd.dy / d * step;
        // a soft frame: past the padding the node is drawn back, not pinned to the edge
        if (nd.x < pad + nd.r) nd.x += (pad + nd.r - nd.x) * 0.5;
        if (nd.x > W - pad - nd.r) nd.x -= (nd.x - (W - pad - nd.r)) * 0.5;
        if (nd.y < pad + nd.r) nd.y += (pad + nd.r - nd.y) * 0.5;
        if (nd.y > H - pad - nd.r) nd.y -= (nd.y - (H - pad - nd.r)) * 0.5;
      });
      t = Math.max(0.6, t * 0.975);
    }
  }

  // ---------------------------------------------------------------- the canvas
  const view = { scale: 1, tx: 0, ty: 0, w: 0, h: 0 };
  let ctx = null;
  let raf = 0;

  function sizeCanvas() {
    const wrap = els.canvas.parentElement;
    const w = wrap.clientWidth;
    const h = Math.max(380, Math.min(760, Math.round(w * 0.62)));
    const dpr = window.devicePixelRatio || 1;
    els.canvas.width = Math.round(w * dpr); els.canvas.height = Math.round(h * dpr);
    els.canvas.style.height = h + "px";
    view.w = w; view.h = h;
    ctx = els.canvas.getContext("2d");
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function schedule() { if (!raf) raf = requestAnimationFrame(function() { raf = 0; draw(); }); }

  function loadAvatar(url) {
    if (!url || images.has(url)) return images.get(url);
    const im = new Image();
    im.decoding = "async";
    im.onload = schedule;
    im.src = url;
    images.set(url, im);
    return im;
  }

  function neighbourSet(name) {
    const s = new Set();
    if (!name) return s;
    const nd = model.byName.get(name);
    if (nd) nd.adj.forEach(function(p) { s.add(p[0].name); });
    return s;
  }

  function draw() {
    if (!ctx || !model) return;
    const W = view.w, H = view.h;
    ctx.clearRect(0, 0, W, H);
    ctx.save();
    ctx.translate(view.tx, view.ty); ctx.scale(view.scale, view.scale);
    const focus = selected || hovered;
    const near = neighbourSet(focus);
    const byName = model.byName;
    // the ties
    model.edges.forEach(function(ed) {
      const a = byName.get(ed.a), b = byName.get(ed.b);
      const on = focus && (ed.a === focus || ed.b === focus);
      let alpha = focus ? (on ? 0.85 : 0.05) : Math.min(0.6, 0.12 + ed.w * 0.06);
      ctx.strokeStyle = on ? a.group.color : "#5b6a7a";
      ctx.globalAlpha = alpha;
      ctx.lineWidth = Math.min(8, 0.6 + Math.log(1 + ed.w) * 1.3) / Math.sqrt(view.scale);
      ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
    });
    ctx.globalAlpha = 1;
    // the people
    const labelled = [];
    model.nodes.forEach(function(nd) {
      const on = !focus || nd.name === focus || near.has(nd.name);
      const r = nd.r;
      ctx.globalAlpha = on ? 1 : 0.18;
      ctx.beginPath(); ctx.arc(nd.x, nd.y, r, 0, Math.PI * 2);
      ctx.fillStyle = nd.group.color; ctx.fill();
      const im = r >= 9 && nd.avatar ? loadAvatar(nd.avatar) : null;
      if (im && im.complete && im.naturalWidth) {
        ctx.save(); ctx.beginPath(); ctx.arc(nd.x, nd.y, r - 1.5, 0, Math.PI * 2); ctx.clip();
        ctx.drawImage(im, nd.x - r, nd.y - r, r * 2, r * 2); ctx.restore();
      }
      if (nd.name === selected) { ctx.lineWidth = 3 / view.scale; ctx.strokeStyle = "#111"; ctx.stroke(); }
      else if (nd.name === hovered) { ctx.lineWidth = 2 / view.scale; ctx.strokeStyle = "#111"; ctx.stroke(); }
      if (on && (r >= 8 || nd.name === focus || near.has(nd.name) || view.scale > 1.6)) labelled.push(nd);
    });
    ctx.globalAlpha = 1;
    const fs = Math.max(9, 12 / Math.sqrt(view.scale));
    ctx.font = "600 " + fs + "px system-ui, 'Noto Sans SC', sans-serif";
    ctx.textAlign = "center"; ctx.textBaseline = "top";
    labelled.forEach(function(nd) {
      const y = nd.y + nd.r + 2;
      ctx.lineWidth = 3; ctx.strokeStyle = "rgba(255,255,255,0.9)"; ctx.lineJoin = "round";
      ctx.strokeText(nd.name, nd.x, y);
      ctx.fillStyle = "#1a202c"; ctx.fillText(nd.name, nd.x, y);
    });
    ctx.restore();
  }

  function toWorld(px, py) { return [(px - view.tx) / view.scale, (py - view.ty) / view.scale]; }

  function nodeAt(px, py) {
    const p = toWorld(px, py);
    let best = null, bestD = Infinity;
    model.nodes.forEach(function(nd) {
      const dx = nd.x - p[0], dy = nd.y - p[1];
      const d = Math.sqrt(dx * dx + dy * dy) - nd.r;
      if (d < 4 / view.scale && d < bestD) { best = nd; bestD = d; }
    });
    return best;
  }

  function fitView() { view.scale = 1; view.tx = 0; view.ty = 0; }

  function focusOn(name) {
    const nd = model.byName.get(name);
    if (!nd) return;
    view.scale = 1.7;
    view.tx = view.w / 2 - nd.x * view.scale; view.ty = view.h / 2 - nd.y * view.scale;
  }

  function bindCanvas() {
    let dragging = null;
    els.canvas.addEventListener("mousemove", function(ev) {
      const rect = els.canvas.getBoundingClientRect();
      const px = ev.clientX - rect.left, py = ev.clientY - rect.top;
      if (dragging) {
        view.tx = dragging.tx + (px - dragging.x); view.ty = dragging.ty + (py - dragging.y);
        dragging.moved = true; schedule(); return;
      }
      const nd = nodeAt(px, py);
      const name = nd ? nd.name : null;
      els.canvas.style.cursor = nd ? "pointer" : "grab";
      if (name !== hovered) { hovered = name; schedule(); }
      if (nd) {
        els.tip.hidden = false;
        els.tip.innerHTML = "<b>" + esc(nd.name) + "</b> " + nd.n + " 篇 · 同场 " + nd.degree + " 人";
        els.tip.style.left = Math.min(px + 14, view.w - 180) + "px"; els.tip.style.top = (py + 14) + "px";
      } else els.tip.hidden = true;
    });
    els.canvas.addEventListener("mouseleave", function() { hovered = null; els.tip.hidden = true; schedule(); });
    els.canvas.addEventListener("mousedown", function(ev) {
      const rect = els.canvas.getBoundingClientRect();
      dragging = { x: ev.clientX - rect.left, y: ev.clientY - rect.top, tx: view.tx, ty: view.ty, moved: false };
    });
    window.addEventListener("mouseup", function(ev) {
      if (!dragging) return;
      const d = dragging; dragging = null;
      if (!d.moved) {
        const rect = els.canvas.getBoundingClientRect();
        const nd = nodeAt(ev.clientX - rect.left, ev.clientY - rect.top);
        select(nd ? nd.name : null);
      }
    });
    els.canvas.addEventListener("wheel", function(ev) {
      ev.preventDefault();
      const rect = els.canvas.getBoundingClientRect();
      const px = ev.clientX - rect.left, py = ev.clientY - rect.top;
      const factor = ev.deltaY < 0 ? 1.15 : 1 / 1.15;
      const next = Math.max(0.5, Math.min(4, view.scale * factor));
      const w = toWorld(px, py);
      view.scale = next;
      view.tx = px - w[0] * next; view.ty = py - w[1] * next;
      schedule();
    }, { passive: false });
    // a finger: pan; a tap: select
    let touch = null;
    els.canvas.addEventListener("touchstart", function(ev) {
      if (ev.touches.length !== 1) return;
      const rect = els.canvas.getBoundingClientRect();
      touch = { x: ev.touches[0].clientX - rect.left, y: ev.touches[0].clientY - rect.top, tx: view.tx, ty: view.ty, moved: false };
    }, { passive: true });
    els.canvas.addEventListener("touchmove", function(ev) {
      if (!touch || ev.touches.length !== 1) return;
      const rect = els.canvas.getBoundingClientRect();
      const px = ev.touches[0].clientX - rect.left, py = ev.touches[0].clientY - rect.top;
      if (Math.abs(px - touch.x) + Math.abs(py - touch.y) > 6) touch.moved = true;
      if (touch.moved) { view.tx = touch.tx + (px - touch.x); view.ty = touch.ty + (py - touch.y); schedule(); ev.preventDefault(); }
    }, { passive: false });
    els.canvas.addEventListener("touchend", function() {
      if (!touch) return;
      if (!touch.moved) { const nd = nodeAt(touch.x, touch.y); select(nd ? nd.name : null); }
      touch = null;
    });
  }

  // ---------------------------------------------------------------- the panel
  function personCard(nd) {
    const partners = Array.from(nd.co.entries()).filter(function(p) { return model.byName.has(p[0]) || model.persons.has(p[0]); })
      .sort(function(a, b) { return b[1] - a[1] || a[0].localeCompare(b[0], "zh"); }).slice(0, 10);
    const works = Array.from(nd.works.entries()).sort(function(a, b) { return b[1] - a[1] || (WORK_ORDER.get(a[0]) || 0) - (WORK_ORDER.get(b[0]) || 0); }).slice(0, 8);
    const years = Array.from(nd.years.keys()).sort();
    const sources = Array.from(nd.sources.entries()).sort(function(a, b) { return b[1] - a[1]; }).slice(0, 4);
    const orgs = Array.from(nd.orgs.entries()).sort(function(a, b) { return b[1] - a[1]; }).slice(0, 3);
    const link = nd.slug ? PEOPLE_BASE + nd.slug + "/" : null;
    const head = "<div class='graph__person'>" + (nd.avatar ? "<img src='" + esc(nd.avatar) + "' alt=''>" : "<i style='background:" + nd.group.color + "'></i>") +
      "<div><h3>" + (link ? "<a href='" + esc(link) + "'>" + esc(nd.name) + "</a>" : esc(nd.name)) + "</h3>" +
      "<p>" + nd.n + " 篇资料" + (years.length ? " · " + years[0] + (years.length > 1 ? "–" + years[years.length - 1] : "") : "") + " · 同场 " + nd.degree + " 人</p>" +
      "<p class='graph__group-tag'><i style='background:" + nd.group.color + "'></i>群落：" + esc(nd.group.title) + "</p></div></div>";
    const yearBar = years.length ? "<div class='graph__years'>" + years.map(function(y) { return "<span title='" + y + "：" + nd.years.get(y) + " 篇' style='--h:" + Math.min(1, nd.years.get(y) / 8) + "'><b>" + String(y).slice(2) + "</b></span>"; }).join("") + "</div>" : "";
    const partnerList = partners.length ? "<h4>同场最多</h4><ul class='graph__partners'>" + partners.map(function(p) {
      const other = model.persons.get(p[0]);
      const av = other && other.avatar ? "<img src='" + esc(other.avatar) + "' alt=''>" : "<i style='background:" + (model.byName.get(p[0]) ? model.byName.get(p[0]).group.color : "#cbd5e0") + "'></i>";
      return "<li><button type='button' data-pick='" + esc(p[0]) + "'>" + av + esc(p[0]) + "</button><b>" + p[1] + "</b></li>";
    }).join("") + "</ul>" : "<p class='graph__empty'>没有同场记录——这个人的资料里只有他自己。</p>";
    const workList = works.length ? "<h4>谈到的作品</h4><ul class='graph__works'>" + works.map(function(w) {
      const wi = WORK_BY.get(w[0]) || {};
      return "<li><a href='" + esc(searchUrl("person=" + encodeURIComponent(nd.name) + "&work=" + encodeURIComponent(w[0]))) + "'>" + (wi.icon ? "<img src='" + esc(wi.icon) + "' alt=''>" : "") + esc(w[0].replace(/^宝可梦 /, "")) + "<b>" + w[1] + "</b></a></li>";
    }).join("") + "</ul>" : "";
    const meta = (orgs.length ? "<p class='graph__meta'>组织：" + orgs.map(function(o) { return esc(o[0]); }).join("、") + "</p>" : "") +
      (sources.length ? "<p class='graph__meta'>来源：" + sources.map(function(s) { return esc(s[0]) + " " + s[1]; }).join("、") + "</p>" : "");
    const foot = "<p class='graph__links'><a href='" + esc(searchUrl("person=" + encodeURIComponent(nd.name))) + "'>在目录里看他的 " + nd.n + " 篇 →</a>" + (link ? " <a href='" + esc(link) + "'>人物页 →</a>" : "") + "</p>";
    return head + yearBar + partnerList + workList + meta + foot;
  }

  function overviewCard() {
    const top = model.nodes.slice().sort(function(a, b) { return b.degree - a.degree || b.n - a.n; }).slice(0, 8);
    return "<h3>怎么看</h3><p>圆点大小是出现篇数，线是同场，颜色是群落。点一个人看他的关系；滚轮缩放、拖动平移。</p>" +
      "<h4>同场者最多的人</h4><ul class='graph__partners'>" + top.map(function(nd) {
        const av = nd.avatar ? "<img src='" + esc(nd.avatar) + "' alt=''>" : "<i style='background:" + nd.group.color + "'></i>";
        return "<li><button type='button' data-pick='" + esc(nd.name) + "'>" + av + esc(nd.name) + "</button><b>" + nd.degree + " 人</b></li>";
      }).join("") + "</ul>" +
      "<h4>群落</h4><ul class='graph__groups'>" + model.groups.filter(function(g) { return !g.rim; }).slice(0, 10).map(function(g) {
        return "<li><i style='background:" + g.color + "'></i><span>" + esc(g.title) + "</span><b>" + g.members.length + " 人</b></li>";
      }).join("") + "</ul>";
  }

  function renderPanel() {
    const nd = selected ? model.byName.get(selected) : null;
    els.panel.innerHTML = nd ? personCard(nd) : overviewCard();
  }

  function renderLegend() {
    const alone = model.persons.size - model.nodes.length;
    const rim = model.groups.find(function(g) { return g.rim; });
    els.legend.innerHTML = model.groups.filter(function(g) { return !g.rim; }).slice(0, 12).map(function(g) {
      return "<span><i style='background:" + g.color + "'></i>" + esc(g.title) + " <b>" + g.members.length + "</b></span>";
    }).join("") + (rim ? "<span><i style='background:" + rim.color + "'></i>边缘的灰点：出现 3 篇以上但没有同场记录 <b>" + rim.members.length + "</b></span>" : "") +
      (alone > 0 ? "<span class='graph__legend-note'>另有 " + alone + " 人只出现过一两次、没有同场记录，未画入图中</span>" : "");
  }

  function renderStats() {
    const cells = els.stats.querySelectorAll("strong");
    if (cells.length < 4) return;
    cells[0].textContent = model.nodes.length;
    cells[1].textContent = model.edges.length;
    cells[2].textContent = model.works.size;
    cells[3].textContent = model.nEntries;
  }

  function select(name) {
    selected = name && model.byName.has(name) ? name : null;
    if (selected) focusOn(selected);
    renderPanel();
    schedule();
    if (selected && window.matchMedia && window.matchMedia("(max-width: 900px)").matches) els.panel.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  // ---------------------------------------------------------------- the matrix, the timeline, the index
  function renderMatrix() {
    const people = model.nodes.slice().sort(function(a, b) { return b.n - a.n; }).slice(0, 28);
    const works = Array.from(model.works.entries()).filter(function(w) { return w[1] >= 3; })
      .sort(function(a, b) { return (WORK_ORDER.get(a[0]) || 0) - (WORK_ORDER.get(b[0]) || 0); }).map(function(w) { return w[0]; });
    if (!people.length || !works.length) { els.matrix.innerHTML = "<p class='graph__empty'>没有可以对上的作品标注。</p>"; return; }
    let max = 1;
    people.forEach(function(p) { works.forEach(function(w) { max = Math.max(max, p.works.get(w) || 0); }); });
    const head = "<tr><th></th>" + works.map(function(w) {
      const wi = WORK_BY.get(w) || {};
      const short = w.replace(/^宝可梦 /, "").replace(/^Pokémon /, "");
      return "<th title='" + esc(w) + "'>" + (wi.icon ? "<img src='" + esc(wi.icon) + "' alt=''>" : "") + "<span>" + esc(short) + "</span></th>";
    }).join("") + "</tr>";
    const rows = people.map(function(p) {
      return "<tr><th><button type='button' data-pick='" + esc(p.name) + "'>" + (p.avatar ? "<img src='" + esc(p.avatar) + "' alt=''>" : "") + esc(p.name) + "</button></th>" + works.map(function(w) {
        const v = p.works.get(w) || 0;
        const a = v ? 0.12 + 0.88 * Math.sqrt(v / max) : 0;
        return v ? "<td style='--a:" + a.toFixed(2) + "'" + (a > 0.55 ? " class='is-deep'" : "") + "><a href='" + esc(searchUrl("person=" + encodeURIComponent(p.name) + "&work=" + encodeURIComponent(w))) + "' title='" + esc(p.name) + " × " + esc(w) + "：" + v + " 篇'>" + v + "</a></td>" : "<td></td>";
      }).join("") + "</tr>";
    }).join("");
    els.matrix.innerHTML = "<table class='graph__matrix'><thead>" + head + "</thead><tbody>" + rows + "</tbody></table>";
  }

  function renderTimeline() {
    const people = model.nodes.slice().sort(function(a, b) { return b.n - a.n; }).slice(0, 30);
    let y0 = 9999, y1 = 0;
    people.forEach(function(p) { p.years.forEach(function(v, y) { y0 = Math.min(y0, y); y1 = Math.max(y1, y); }); });
    if (y1 < y0) { els.timeline.innerHTML = ""; return; }
    const years = []; for (let y = y0; y <= y1; y++) years.push(y);
    const head = "<div class='graph__tl-row graph__tl-head'><span></span><div>" + years.map(function(y) { return "<i" + (y % 5 === 0 ? " class='is-tick'" : "") + ">" + (y % 5 === 0 ? y : "") + "</i>"; }).join("") + "</div></div>";
    const rows = people.map(function(p) {
      const ys = Array.from(p.years.keys()).sort();
      return "<div class='graph__tl-row'><span><button type='button' data-pick='" + esc(p.name) + "'>" + esc(p.name) + "</button></span><div>" + years.map(function(y) {
        const v = p.years.get(y) || 0;
        const size = v ? Math.min(14, 5 + Math.sqrt(v) * 2.4) : 0;
        const span = ys.length > 1 && y >= ys[0] && y <= ys[ys.length - 1] ? " class='in-span'" : "";
        return "<i" + span + ">" + (v ? "<b style='width:" + size + "px;height:" + size + "px;background:" + p.group.color + "' title='" + y + "：" + v + " 篇'></b>" : "") + "</i>";
      }).join("") + "</div></div>";
    }).join("");
    els.timeline.innerHTML = "<div class='graph__tl'>" + head + rows + "</div>";
  }

  function renderIndex() {
    const pairs = model.edges.slice().sort(function(a, b) { return b.w - a.w; }).slice(0, 40);
    const ties = "<div class='graph__ties'><h3>同场最多的搭档</h3><ol>" + pairs.map(function(ed) {
      const a = model.byName.get(ed.a), b = model.byName.get(ed.b);
      return "<li><button type='button' data-pick='" + esc(ed.a) + "'>" + esc(ed.a) + "</button><span>×</span><button type='button' data-pick='" + esc(ed.b) + "'>" + esc(ed.b) + "</button><b>" + ed.w + " 篇</b>" +
        "<a href='" + esc(searchUrl("person=" + encodeURIComponent(ed.a))) + "' title='在目录里看'>→</a></li>";
    }).join("") + "</ol></div>";
    const groups = "<div class='graph__groups-index'><h3>群落成员</h3>" + model.groups.filter(function(g) { return !g.rim; }).slice(0, 12).map(function(g) {
      return "<section><h4><i style='background:" + g.color + "'></i>" + esc(g.title) + " <b>" + g.members.length + " 人</b></h4><p>" + g.members.map(function(m) {
        return "<button type='button' data-pick='" + esc(m.name) + "'>" + esc(m.name) + "<b>" + m.n + "</b></button>";
      }).join("") + "</p></section>";
    }).join("") + "</div>";
    els.index.innerHTML = ties + groups;
  }

  // ---------------------------------------------------------------- run
  function rebuild() {
    model = build(els.scope.value, parseInt(els.min.value, 10) || 1);
    if (!model.byName.has(selected)) selected = null;
    sizeCanvas();
    layout(model, view.w, view.h);
    fitView();
    renderStats(); renderLegend(); renderPanel(); renderMatrix(); renderTimeline(); renderIndex();
    els.list.innerHTML = model.nodes.slice().sort(function(a, b) { return b.n - a.n; }).map(function(n) { return "<option value='" + esc(n.name) + "'>"; }).join("");
    schedule();
  }

  root.addEventListener("click", function(ev) {
    const b = ev.target.closest ? ev.target.closest("[data-pick]") : null;
    if (!b) return;
    select(b.getAttribute("data-pick"));
    if (!b.closest("[data-graph-panel]")) document.getElementById("graph-network").scrollIntoView({ behavior: "smooth", block: "start" });
  });
  els.min.addEventListener("change", rebuild);
  els.scope.addEventListener("change", rebuild);
  els.reset.addEventListener("click", function() { selected = null; fitView(); renderPanel(); schedule(); });
  els.find.addEventListener("change", function() { if (model.byName.has(els.find.value.trim())) select(els.find.value.trim()); });
  els.find.addEventListener("keydown", function(ev) { if (ev.key === "Enter") { ev.preventDefault(); if (model.byName.has(els.find.value.trim())) select(els.find.value.trim()); } });
  let resizeTimer = 0;
  window.addEventListener("resize", function() { clearTimeout(resizeTimer); resizeTimer = setTimeout(function() { if (model) { const s = selected; rebuild(); if (s) select(s); } }, 200); });

  fetch(window.pokeamiceGraphData || "/assets/js/graph.json", { credentials: "same-origin" }).then(function(r) {
    if (!r.ok) throw new Error(String(r.status));
    return r.json();
  }).then(function(data) {
    entries = Array.isArray(data) ? data : [];
    els.loading.hidden = true;
    bindCanvas();
    rebuild();
    const q = new URLSearchParams(window.location.search).get("person");
    if (q && model.byName.has(q)) select(q);
  }).catch(function() {
    els.loading.textContent = "目录读取失败，请刷新重试。";
  });
})();
