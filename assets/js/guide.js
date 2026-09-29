/* The 使用指南 pages (_layouts/guide.html): the small amount of behaviour a
   documentation page needs, none of it required to read the text.

   - h2 / h3 in the body get an id (kept if the author wrote one; kramdown makes
     "section-1" for Chinese headings, which is replaced by the heading's own
     words) and a # link, and the same headings make the contents on the right,
     the one being read marked as you scroll
   - 复制链接 copies this page's address; every code block gets a 复制 button
   - [data-guide-tabs]: the buttons of .guide-tabs__list show the panels of the
     same position
   - a note of a guide/shot lights its pin on the picture, and the pin its note
   - the contents drawer is open on a wide window and folded on a narrow one
   - "/" goes to the search box */
(function () {
  "use strict";

  var root = document.querySelector("[data-guide]");
  if (!root) return;
  var body = root.querySelector(".guide__body");
  var used = {};

  function slug(text) {
    var s = text.trim().toLowerCase().replace(/[\s　]+/g, "-");
    try { s = s.replace(new RegExp("[^\\p{L}\\p{N}_-]+", "gu"), ""); }
    catch (e) { s = s.replace(/[^\w぀-ヿ一-鿿-]+/g, ""); }
    return s.replace(/-+/g, "-").replace(/^-|-$/g, "") || "section";
  }

  function flash(button, text) {
    var was = button.textContent;
    button.textContent = text;
    setTimeout(function () { button.textContent = was; }, 1600);
  }

  function copy(text, done) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, function () {});
      return;
    }
    var area = document.createElement("textarea");
    area.value = text;
    area.style.position = "fixed";
    area.style.opacity = "0";
    document.body.appendChild(area);
    area.select();
    try { document.execCommand("copy"); done(); } catch (e) {}
    document.body.removeChild(area);
  }

  /* ---- headings, anchors, the contents on the right ---- */
  var heads = body ? Array.prototype.slice.call(body.querySelectorAll("h2, h3")) : [];
  heads.forEach(function (h) {
    var id = h.id;
    if (!id || /^section(-\d+)?$/.test(id)) {
      var base = slug(h.textContent), n = 1;
      id = base;
      while (used[id] || (document.getElementById(id) && document.getElementById(id) !== h)) { n += 1; id = base + "-" + n; }
      h.id = id;
    }
    used[id] = true;
    var a = document.createElement("a");
    a.className = "guide__anchor";
    a.href = "#" + id;
    a.setAttribute("aria-label", "链接到本节");
    a.textContent = "#";
    h.appendChild(a);
  });

  var toc = root.querySelector("[data-guide-toc]");
  var links = [];
  if (toc) {
    var list = toc.querySelector("ol");
    if (heads.length < 2) {
      toc.hidden = true;
    } else {
      heads.forEach(function (h) {
        var li = document.createElement("li");
        if (h.tagName === "H3") li.className = "is-sub";
        var a = document.createElement("a");
        a.href = "#" + h.id;
        a.textContent = h.textContent.replace(/#$/, "");
        li.appendChild(a);
        list.appendChild(li);
        links.push({ head: h, link: a });
      });
    }
  }

  /* where the contents sit above the article (under 1180px) they start folded */
  var narrow = window.matchMedia ? window.matchMedia("(max-width: 1180px)") : null;
  if (toc && narrow && links.length) {
    if (narrow.matches) toc.classList.add("is-fold");
    toc.querySelector(".guide__toc-title").addEventListener("click", function () { if (narrow.matches) toc.classList.toggle("is-fold"); });
    toc.addEventListener("click", function (e) { if (narrow.matches && e.target.tagName === "A") toc.classList.add("is-fold"); });
  }

  /* a timer, not requestAnimationFrame: a page in a background tab gets no frames,
     and a "waiting for a frame" flag would then never be cleared */
  var timer = 0;
  function spy() {
    timer = 0;
    var cur = null;
    links.forEach(function (x) { if (x.head.getBoundingClientRect().top <= 120) cur = x; });
    if (!cur && links.length) cur = links[0];
    links.forEach(function (x) { x.link.classList.toggle("is-on", x === cur); });
  }
  if (links.length) {
    window.addEventListener("scroll", function () { if (!timer) timer = setTimeout(spy, 60); }, { passive: true });
    spy();
  }

  /* the ids are made after the browser has already looked for the hash */
  if (location.hash.length > 1) {
    var target = document.getElementById(decodeURIComponent(location.hash.slice(1)));
    if (target) target.scrollIntoView();
  }

  /* ---- copying ---- */
  var linkBtn = root.querySelector("[data-guide-copy]");
  if (linkBtn) linkBtn.addEventListener("click", function () { copy(location.href.split("#")[0], function () { flash(linkBtn, "已复制"); }); });

  if (body) Array.prototype.forEach.call(body.querySelectorAll("pre"), function (pre) {
    var b = document.createElement("button");
    b.type = "button";
    b.className = "guide__copy";
    b.textContent = "复制";
    b.addEventListener("click", function () {
      var code = pre.querySelector("code");
      copy((code || pre).textContent.replace(/\n$/, ""), function () { flash(b, "已复制"); });
    });
    pre.appendChild(b);
  });

  /* ---- tabs ---- */
  Array.prototype.forEach.call(root.querySelectorAll("[data-guide-tabs]"), function (box) {
    var tabs = Array.prototype.slice.call(box.querySelectorAll(":scope > .guide-tabs__list > button"));
    var panels = Array.prototype.slice.call(box.querySelectorAll(":scope > .guide-tabs__panel"));
    function show(i) {
      tabs.forEach(function (t, k) { t.setAttribute("aria-selected", k === i ? "true" : "false"); t.tabIndex = k === i ? 0 : -1; });
      panels.forEach(function (p, k) { p.hidden = k !== i; });
    }
    tabs.forEach(function (t, i) {
      t.setAttribute("role", "tab");
      t.addEventListener("click", function () { show(i); });
      t.addEventListener("keydown", function (e) {
        var to = e.key === "ArrowRight" ? i + 1 : e.key === "ArrowLeft" ? i - 1 : null;
        if (to === null || !tabs[to]) return;
        show(to);
        tabs[to].focus();
        e.preventDefault();
      });
    });
    panels.forEach(function (p) { p.setAttribute("role", "tabpanel"); });
    show(0);
  });

  /* ---- pins and their notes ---- */
  Array.prototype.forEach.call(root.querySelectorAll(".guide-shot"), function (fig) {
    function light(n, on) {
      Array.prototype.forEach.call(fig.querySelectorAll('[data-pin="' + n + '"]'), function (el) { el.classList.toggle("is-hot", on); });
    }
    Array.prototype.forEach.call(fig.querySelectorAll("[data-pin]"), function (el) {
      var n = el.getAttribute("data-pin");
      el.addEventListener("mouseenter", function () { light(n, true); });
      el.addEventListener("mouseleave", function () { light(n, false); });
    });
  });

  /* ---- the drawer, the search key ---- */
  var drawer = root.querySelector(".guide__drawer");
  if (drawer && window.matchMedia) {
    var wide = window.matchMedia("(min-width: 901px)");
    var sync = function () { drawer.open = wide.matches; };
    sync();
    if (wide.addEventListener) wide.addEventListener("change", sync); else if (wide.addListener) wide.addListener(sync);
  }
  document.addEventListener("keydown", function (e) {
    if (e.key !== "/" || e.ctrlKey || e.metaKey || e.altKey) return;
    var t = e.target, tag = t && t.tagName;
    if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" || (t && t.isContentEditable)) return;
    var input = root.querySelector(".guide__search input");
    if (!input) return;
    if (drawer && !drawer.open) drawer.open = true;
    e.preventDefault();
    input.focus();
  });
})();
