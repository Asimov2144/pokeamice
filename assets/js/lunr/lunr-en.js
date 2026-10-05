---
layout: none
---
/* The masthead search (the magnifier). Nothing heavy loads with the page any more.

   It used to load lunr-store.js (3.5 MB: every page's full text) on every page and build a lunr index over it
   right away - 2 to 8 seconds of a frozen page, on every page, for a search most visits never open. Now the first
   time the search is opened (the magnifier clicked, or the box focused) lunr-worker.js starts: it fetches the store
   and builds the index on a background thread, and the queries run there too. This file only sends the text and
   shows what comes back. If a worker cannot start, the old way - store and index on the page - still works.

   window.paLoadSearchStore() loads just the store, for the home page's quick search (_layouts/home.html). */
(function () {
  var base = "{{ '/assets/js/lunr/' | relative_url }}";
  var found = "{{ site.data.ui-text[site.locale].results_found | default: 'Result(s) found' }}";
  var storeLoad = null;

  function loadScript(src) {
    return new Promise(function (ok, fail) {
      var s = document.createElement("script");
      s.src = src;
      s.onload = ok;
      s.onerror = fail;
      document.body.appendChild(s);
    });
  }
  window.paLoadSearchStore = function () {
    return storeLoad || (storeLoad = Array.isArray(window.store) ? Promise.resolve() : loadScript(base + "lunr-store.js"));
  };

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  $(document).ready(function () {
    var input = document.getElementById("search");
    var resultdiv = $("#results");
    if (!input || !resultdiv.length) return;

    var engine = null;     // { ask(query, seq) } once something can answer
    var starting = false;
    var seq = 0, shown = 0, timer = null;

    function note(text) {
      resultdiv.html('<p class="results__found">' + esc(text) + "</p>");
    }
    function render(d) {
      if (d.seq < shown) return;  // an answer to an older keystroke
      shown = d.seq;
      if (!input.value.trim()) { resultdiv.empty(); return; }
      var html = ['<p class="results__found">' + d.total + " " + found + "</p>"];
      d.items.forEach(function (it) {
        html.push(
          '<div class="list__item"><article class="archive__item" itemscope itemtype="https://schema.org/CreativeWork">' +
          '<h2 class="archive__item-title" itemprop="headline"><a href="' + esc(it.url) + '" rel="permalink">' + esc(it.title) + "</a></h2>" +
          (it.teaser ? '<div class="archive__item-teaser"><img src="' + esc(it.teaser) + '" alt=""></div>' : "") +
          '<p class="archive__item-excerpt" itemprop="description">' + esc(it.excerpt) + "…</p>" +
          "</article></div>");
      });
      if (d.total > d.items.length) {
        html.push('<p class="results__found">只列出前 ' + d.items.length + " 条；更完整的检索请用<a href=\"{{ '/search/' | relative_url }}\">站内搜索页</a>。</p>");
      }
      resultdiv.html(html.join(""));
    }
    function ask() {
      if (!engine) return;
      seq += 1;
      engine.ask(input.value, seq);
    }

    // the old way, on the page: only if a worker cannot run here
    function onPage() {
      return Promise.all([loadScript(base + "lunr.min.js"), window.paLoadSearchStore()]).then(function () {
        var idx = lunr(function () {
          this.field("title"); this.field("excerpt"); this.field("categories"); this.field("tags"); this.ref("id");
          this.pipeline.remove(lunr.trimmer);
          for (var item in store) {
            this.add({ title: store[item].title, excerpt: store[item].excerpt, categories: store[item].categories, tags: store[item].tags, id: item });
          }
        });
        return {
          ask: function (q, n) {
            var query = String(q).toLowerCase(), result = [];
            try {
              result = !query.trim() ? [] : idx.query(function (qq) {
                query.split(lunr.tokenizer.separator).forEach(function (term) {
                  qq.term(term, { boost: 100 });
                  if (query.lastIndexOf(" ") != query.length - 1) qq.term(term, { usePipeline: false, wildcard: lunr.Query.wildcard.TRAILING, boost: 10 });
                  if (term != "") qq.term(term, { usePipeline: false, editDistance: 1, boost: 1 });
                });
              });
            } catch (e) { result = []; }
            render({ seq: n, total: result.length, items: result.slice(0, 60).map(function (r) {
              var s = store[r.ref];
              return { url: s.url, title: s.title, teaser: s.teaser, excerpt: String(s.excerpt || "").slice(0, 120) };
            }) });
          }
        };
      });
    }

    function start() {
      if (engine || starting) return;
      starting = true;
      note("正在载入搜索…（第一次打开要几秒）");
      var ready;
      try {
        var w = new Worker(base + "lunr-worker.js");
        ready = new Promise(function (ok, fail) {
          w.onmessage = function (e) {
            if (e.data && e.data.ready) { ok({ ask: function (q, n) { w.postMessage({ q: q, seq: n }); } }); return; }
            render(e.data);
          };
          w.onerror = function (e) { if (e && e.preventDefault) e.preventDefault(); fail(e); };
        }).catch(function () { w.terminate(); return onPage(); });
      } catch (e) {
        ready = onPage();
      }
      ready.then(function (eng) {
        engine = eng;
        if (input.value.trim()) ask(); else resultdiv.empty();
      }, function () {
        note("搜索载入失败，请改用站内搜索页。");
      });
    }

    $(document).on("click", ".search__toggle", start);
    input.addEventListener("focus", start);
    input.addEventListener("keyup", function () {
      start();
      clearTimeout(timer);
      timer = setTimeout(ask, 120);
    });
  });
})();
