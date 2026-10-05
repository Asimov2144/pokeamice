/* The masthead search's index, built and queried off the main thread.

   lunr-store.js carries every page's title and full text (search_full_content), 3.5 MB; building a lunr index over
   it took 2 to 8 seconds of a frozen page, and every page used to do it on load. Now lunr-en.js starts this worker
   the first time the search is opened; the index lives here, a query comes in as text and goes back as the items to
   show, so the page never waits on lunr. The query is the one the theme ran (exact term, trailing wildcard, one edit
   away), unchanged. */
importScripts("lunr.min.js", "lunr-store.js");

var idx = lunr(function () {
  this.field("title");
  this.field("excerpt");
  this.field("categories");
  this.field("tags");
  this.ref("id");
  this.pipeline.remove(lunr.trimmer);
  for (var item in store) {
    this.add({
      title: store[item].title,
      excerpt: store[item].excerpt,
      categories: store[item].categories,
      tags: store[item].tags,
      id: item
    });
  }
});

function search(query) {
  return idx.query(function (q) {
    query.split(lunr.tokenizer.separator).forEach(function (term) {
      q.term(term, { boost: 100 });
      if (query.lastIndexOf(" ") != query.length - 1) {
        q.term(term, { usePipeline: false, wildcard: lunr.Query.wildcard.TRAILING, boost: 10 });
      }
      if (term != "") {
        q.term(term, { usePipeline: false, editDistance: 1, boost: 1 });
      }
    });
  });
}

postMessage({ ready: true });

onmessage = function (e) {
  var query = String(e.data.q || "").toLowerCase();
  var result = [];
  try {
    result = query.trim() ? search(query) : [];
  } catch (err) {
    result = [];  // a half-typed query lunr cannot parse (a lone "+", ":") finds nothing rather than throwing
  }
  // the text is Chinese, with no spaces to split on: the excerpt is cut by characters, not words
  var items = result.slice(0, 60).map(function (r) {
    var s = store[r.ref];
    return { url: s.url, title: s.title, teaser: s.teaser, excerpt: String(s.excerpt || "").slice(0, 120) };
  });
  postMessage({ seq: e.data.seq, total: result.length, items: items });
};
