/* The 随手发的东西 card's cover (_includes/home-notes-banner.html, _pages/notes.md): three
   fragments drawn at random on each visit, each shown by one of its own stickers on a scrap of
   paper whose style is drawn too. A fragment without stickers shows its first words instead.
   Data: assets/data/weibo-covers.json (tools/build-weibo-covers.py). Without it the fixed
   stickers in the markup stay. */
(function () {
  var covers = Array.prototype.slice.call(document.querySelectorAll(".nb-stickers[data-covers]"));
  if (!covers.length || !window.fetch) return;
  var PREFIX = { "p:": "https://gallery.pokeamice.com/pokemon-assets/", "w:": "/assets/img/works/" };
  var STYLES = ["note", "polaroid", "stamp", "tag", "grid"];
  var data = null, pending = null;

  function src(s) {
    var k = s.slice(0, 2);
    return PREFIX[k] ? PREFIX[k] + s.slice(2) : s;
  }
  function pickN(list, n) {
    var a = list.slice(), out = [];
    while (out.length < n && a.length) out.push(a.splice(Math.floor(Math.random() * a.length), 1)[0]);
    return out;
  }
  function load(url) {
    if (!pending) pending = fetch(url).then(function (r) { if (!r.ok) throw r.status; return r.json(); })
      .then(function (d) { data = d; return d; });
    return pending;
  }
  // resolves with the sticker if its picture arrives in time, otherwise with nothing
  function ready(stk) {
    return new Promise(function (done) {
      if (!stk) return done(null);
      var im = new Image(), t = setTimeout(function () { done(null); }, 4000);
      im.onload = function () { clearTimeout(t); done(stk); };
      im.onerror = function () { clearTimeout(t); done(null); };
      im.src = src(stk[2]);
    });
  }
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text) e.textContent = text;
    return e;
  }

  function slip(post, stk, style, pos) {
    var cat = data.c[post[1]] || ["", "#999"];
    var s = el("span", "nb-slip nb-slip--" + style + " nb-slip--at" + pos);
    s.style.setProperty("--c", cat[1]);
    s.style.setProperty("--r", (Math.random() * 12 - 6).toFixed(1) + "deg");
    var pic = el("span", "nb-slip__pic");
    if (stk) {
      var im = el("img", stk[0] === "w" ? "is-work" : "is-mon");
      im.src = src(stk[2]); im.alt = ""; im.decoding = "async";
      pic.appendChild(im);
    } else {
      pic.appendChild(el("span", "nb-slip__words", (post[2] || cat[0] || "……").slice(0, 9)));
    }
    s.appendChild(pic);
    s.appendChild(el("span", "nb-slip__date", post[0].slice(5).replace("-", "·")));
    return s;
  }

  function deal(cover) {
    var posts = pickN(data.p, 3);
    var styles = pickN(STYLES, posts.length);
    // a sticker from each fragment's own (indices from position 3 on)
    var stks = posts.map(function (p) {
      var ks = p.slice(3);
      return ks.length ? data.s[ks[Math.floor(Math.random() * ks.length)]] : null;
    });
    Promise.all(stks.map(ready)).then(function (got) {
      var wrap = el("span", "nb-slips");
      // the front scrap (position 0) is drawn last so it sits on top
      for (var i = posts.length - 1; i >= 0; i--) wrap.appendChild(slip(posts[i], got[i], styles[i], i));
      var r = cover.getBoundingClientRect();
      var seen = r.bottom > 0 && r.top < (window.innerHeight || 0);
      cover.textContent = "";
      cover.appendChild(wrap);
      cover.classList.add("is-dealt");
      if (seen) wrap.classList.add("is-arriving");
      var pick = cover.parentNode.querySelector(".nb-pick");
      if (pick) {
        pick.textContent = "翻到一条 · " + posts[0][0].replace(/-/g, ".") + "：" + (posts[0][2] || "（一张图）");
        pick.hidden = false;
      }
    });
  }

  function start(cover) {
    if (cover.getAttribute("data-dealing")) return;
    cover.setAttribute("data-dealing", "1");
    load(cover.getAttribute("data-covers")).then(function () { deal(cover); }, function () {});
  }
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        io.unobserve(e.target);
        start(e.target);
      });
    }, { rootMargin: "600px 0px" });
    covers.forEach(function (c) { io.observe(c); });
  }
  // the observer only reports on painted frames (a page opened in the background, a headless
  // screenshot), so deal anyway a little after load
  window.addEventListener("load", function () {
    setTimeout(function () { covers.forEach(start); }, "IntersectionObserver" in window ? 2500 : 0);
  });
})();
