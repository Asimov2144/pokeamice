/* The catalogue: the entries of the library as cards, narrowed by the rail's
   filters. Used by /search/ (which inlines the data as window.pokeamiceSearchSeed)
   and by the home page (which renders its first cards at build time and fetches
   the data from /assets/js/catalogue.json when the reader touches a filter, or
   after the page has settled). The two pages share the markup ids. */
(function() {
  "use strict";

  function init() {
    const queryInput = document.getElementById("filteredSearchQuery");
    const resultList = document.getElementById("filteredSearchResults");
    const status = document.getElementById("searchStatus");
    if (!queryInput || !resultList) return;
    const form = document.querySelector("[data-search-lab-form]");
    const resetButton = document.querySelector("[data-search-reset]");
    const modeButtons = Array.from(document.querySelectorAll("[data-search-mode]"));
    const dimButtons = Array.from(document.querySelectorAll("[data-dim]"));
    const aiButton = document.getElementById("deepseekSearchButton");
    const aiEndpoint = document.getElementById("deepseekEndpoint");
    const aiOutput = document.getElementById("deepseekOutput");
    const filterEls = {
      person: document.getElementById("searchPersonFilter"),
      work: document.getElementById("searchWorkFilter"),
      year: document.getElementById("searchYearFilter"),
      source: document.getElementById("searchSourceFilter"),
      type: document.getElementById("searchTypeFilter")
    };
    const PEOPLE_BASE = window.pokeamicePeopleBase || "/people/";
    const PAGE = parseInt(resultList.dataset.pageSize || "60", 10) || 60;
    const dataUrl = resultList.dataset.catalogue || "";
    const prerendered = resultList.dataset.prerendered === "true";
    const compact = resultList.dataset.compact === "true";
    let items = (window.pokeamiceSearchSeed || []).slice();
    let loaded = items.length > 0;
    let loading = null;
    let pendingParams = null;
    let lastResults = [];
    let shown = PAGE;
    let touched = false;
    const sortEl = document.getElementById("searchSort");
    const moreButton = document.getElementById("searchMore");

    function escapeHtml(value) {
      return String(value || "").replace(/[&<>"']/g, function(char) {
        return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char];
      });
    }

    function normalize(value) {
      return String(value || "").toLowerCase().trim();
    }

    function itemHaystack(item) {
      return [
        item.title,
        item.excerpt,
        item.body,
        item.date,
        item.source,
        item.type,
        (item.categories || []).join(" "),
        (item.tags || []).join(" "),
        (item.people || []).join(" "),
        (item.works || []).join(" ")
      ].join(" ").toLowerCase();
    }

    function contentType(raw) {
      const text = String(raw || "");
      if (/gamefreak_director_column|gamefreak_masuda_lineblog|gamefreak_legacy_blog|game freak 博客/i.test(text)) return "Game Freak 博客";
      if (/scan|扫描/i.test(text)) return "扫描翻译";
      if (/interview|访谈/i.test(text)) return "访谈翻译";
      if (/translation|翻译/i.test(text)) return "翻译";
      if (/document|文档/i.test(text)) return "文档";
      return text || "文章";
    }

    // the class that colours a card by its type
    function typeClass(label) {
      return { "扫描翻译": "scan", "访谈翻译": "interview", "Game Freak 博客": "blog", "文档": "doc" }[label] || "article";
    }

    // ---- the feed: the 综合推荐 order. Every entry is scored - freshness (40 down to 5 with
    // age), popularity (0-30 from its hits), chance (0-30, drawn once per visit) and kinship
    // (+20 when it shares a person or a work with the lead: the entries the reader opened
    // lately, else the three newest; the names that are everywhere not counting) - the same
    // arithmetic as _includes/home-feed.html, which orders the cards built into the page.
    const feedSeed = Date.now() % 100000;
    const RECENT_KEY = "pokeamice.recent";

    function recentReads() {
      try { return JSON.parse(window.localStorage.getItem(RECENT_KEY) || "[]"); } catch (e) { return []; }
    }

    function rememberRead(entry) {
      try {
        const list = recentReads().filter(function(r) { return r.url !== entry.url; });
        list.unshift(entry);
        window.localStorage.setItem(RECENT_KEY, JSON.stringify(list.slice(0, 10)));
      } catch (e) { /* no storage: the feed just leads with the newest */ }
    }

    function feedLead() {
      const tally = new Map();
      items.forEach(function(it) {
        (it.people || []).concat(it.works || []).forEach(function(n) { tally.set(n, (tally.get(n) || 0) + 1); });
      });
      const many = items.length / 4;
      const recent = recentReads();
      const names = [];
      if (recent.length) {
        recent.slice(0, 8).forEach(function(r) { names.push.apply(names, (r.people || []).concat(r.works || [])); });
      } else {
        items.slice().sort(function(a, b) { return String(b.date || "").localeCompare(String(a.date || "")); }).slice(0, 3)
          .forEach(function(it) { names.push.apply(names, (it.people || []).concat(it.works || [])); });
      }
      return new Set(names.filter(function(n) { return (tally.get(n) || 0) <= many; }));
    }

    function feedScores() {
      const lead = feedLead();
      const now = Date.now();
      const scores = new Map();
      items.forEach(function(it, i) {
        const age = (now - (Date.parse(it.date) || now)) / 86400000;
        let s = age < 8 ? 40 : age < 31 ? 32 : age < 91 ? 24 : age < 366 ? 16 : age < 1096 ? 10 : 5;
        const h = it.hits || 0;
        s += h >= 200 ? 30 : h >= 100 ? 26 : h >= 50 ? 22 : h >= 20 ? 16 : h >= 10 ? 10 : h >= 3 ? 5 : 0;
        s += ((i * 104729 + feedSeed * 7919) % 1009) % 31;
        if ((it.people || []).some(function(n) { return lead.has(n); }) || (it.works || []).some(function(n) { return lead.has(n); })) s += 20;
        scores.set(it, s);
      });
      return scores;
    }

    function getFilters() {
      return {
        query: normalize(queryInput.value),
        person: filterEls.person ? filterEls.person.value : "",
        work: filterEls.work ? filterEls.work.value : "",
        year: filterEls.year ? filterEls.year.value : "",
        source: filterEls.source ? filterEls.source.value : "",
        type: filterEls.type ? filterEls.type.value : ""
      };
    }

    function isDefault(filters) {
      return !filters.query && !filters.person && !filters.work && !filters.year && !filters.source && !filters.type
        && (!sortEl || sortEl.value === "date-desc");
    }

    function matches(item, filters) {
      const terms = filters.query.split(/\s+/).filter(Boolean);
      const haystack = itemHaystack(item);
      if (terms.length && !terms.every(function(term) { return haystack.includes(term); })) return false;
      if (filters.person && !(item.people || []).includes(filters.person)) return false;
      if (filters.work && !(item.works || []).includes(filters.work)) return false;
      if (filters.year && String(item.year) !== filters.year) return false;
      if (filters.source && String(item.source || "未注明来源") !== filters.source) return false;
      if (filters.type && contentType(item.type) !== filters.type) return false;
      return true;
    }

    function optionList(values, fallback) {
      return `<option value="">${fallback}</option>` + values.map(function(value) {
        return `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`;
      }).join("");
    }

    function setSelect(select, value, allowNew) {
      if (!select) return;
      const known = !value || Array.from(select.options).some(function(o) { return o.value === value; });
      if (!known) {
        if (!allowNew) return;               // a stale link names a person or work the library no longer has
        const o = document.createElement("option");
        o.value = value; o.textContent = value;
        select.appendChild(o);
      }
      select.value = value || "";
    }

    function populateFilters() {
      const people = new Set();
      const works = new Set();
      const years = new Set();
      const sources = new Set();
      const types = new Set();
      items.forEach(function(item) {
        (item.people || []).forEach(function(value) { if (value) people.add(value); });
        (item.works || []).forEach(function(value) { if (value) works.add(value); });
        if (item.year) years.add(String(item.year));
        if (item.source) sources.add(item.source);
        types.add(contentType(item.type));
      });
      const keep = getFilters();
      if (filterEls.person) filterEls.person.innerHTML = optionList(Array.from(people).sort(), "全部人物");
      if (filterEls.work) filterEls.work.innerHTML = optionList(Array.from(works).sort(), "全部作品");
      if (filterEls.year) filterEls.year.innerHTML = optionList(Array.from(years).sort().reverse(), "全部年份");
      if (filterEls.source) filterEls.source.innerHTML = optionList(Array.from(sources).sort(), "全部来源");
      if (filterEls.type) filterEls.type.innerHTML = optionList(Array.from(types).sort(), "全部类型");
      setSelect(filterEls.person, keep.person, true);
      setSelect(filterEls.work, keep.work, true);
      setSelect(filterEls.year, keep.year, true);
      setSelect(filterEls.source, keep.source, true);
      setSelect(filterEls.type, keep.type, true);
      if (pendingParams) {
        ["type", "work", "person", "year", "source"].forEach(function(k) {
          if (pendingParams.get(k) && filterEls[k]) setSelect(filterEls[k], pendingParams.get(k), false);
        });
        pendingParams = null;
      }
    }

    function chips(values, cls, limit) {
      return (values || []).slice(0, limit).map(function(value) {
        return `<span class="${cls}">${escapeHtml(value)}</span>`;
      }).join("");
    }

    function proofLabel(value) {
      const v = String(value || "");
      if (/master|professional|manual|verified|done/.test(v)) return "已校对";
      if (/pending|machine|deepseek|draft/.test(v)) return "初译待校";
      return "";
    }

    // the shape of a compact card: its picture lies across the top when wide, stands at the
    // side when tall (or of unknown size), and an entry without one is a text card
    function shape(item) {
      if (!item.cover) return "text";
      const s = item.size;
      return (s && s[0] > s[1] * 1.4) ? "wide" : "tall";
    }

    function coverBlock(item) {
      const label = item.publication || item.source || contentType(item.type);
      if (item.cover) {
        const s = item.size;
        const size = s ? ` width="${parseInt(s[0], 10)}" height="${parseInt(s[1], 10)}"` : "";
        // a borrowed picture (the collection's tile, a portrait) is styled apart from the entry's own
        const kind = item.cover_kind === "tile" || item.cover_kind === "portrait" ? ` search-result-card__cover--${item.cover_kind}` : "";
        return `<a class="search-result-card__cover${kind}" href="${escapeHtml(item.url)}" tabindex="-1" aria-hidden="true"><img src="${escapeHtml(item.cover)}" alt=""${size} loading="lazy" decoding="async"></a>`;
      }
      if (compact) return "";
      const initials = String(label).replace(/[（(].*$/, "").slice(0, 12);
      return `<a class="search-result-card__cover search-result-card__cover--blank" href="${escapeHtml(item.url)}" tabindex="-1" aria-hidden="true"><span>${escapeHtml(initials)}</span><small>${escapeHtml(item.year || "")}</small></a>`;
    }

    function card(item) {
      const type = contentType(item.type);
      const pub = compact ? String(item.publication || item.source || "").replace(/\s*[（(].*$/, "") : (item.publication || item.source);
      const kicker = [type, compact ? pub : (item.publication ? (item.issue ? `${item.publication} ${item.issue}` : item.publication) : item.source)]
        .filter(Boolean).map(function(v) { return `<span>${escapeHtml(v)}</span>`; }).join("");
      const facts = [];
      if (item.pages) facts.push(`${item.pages} 页扫描`);
      if (item.date) facts.push(item.date);
      const proof = proofLabel(item.proof);
      if (proof) facts.push(proof);
      const lead = item.excerpt || item.dek || item.body || "暂无摘要";
      const people = (item.people || []).slice(0, 4).map(function(name, i) {
        const av = (item.avatars || [])[i];
        const slug = (item.slugs || [])[i];
        const inner = `${av ? `<img src="${escapeHtml(av)}" alt="" loading="lazy">` : ""}${escapeHtml(name)}`;
        const cls = `is-person${av ? " has-avatar" : ""}`;
        return slug ? `<a class="${cls}" href="${escapeHtml(PEOPLE_BASE + slug + "/")}">${inner}</a>` : `<span class="${cls}">${inner}</span>`;
      }).join("");
      // the works the entry mentions, beside the date: the HOME icon, else the cover
      // legendary on the version colours, else a coloured tile with the short name
      const marks = compact ? (item.works || []).slice(0, 4).map(function(name, i) {
        const ic = (item.work_icons || [])[i] || "";
        const short = String(name).replace(/^宝可梦[ ：]/, "").replace(/^Pokémon /, "").slice(0, 2);
        if (ic.indexOf("color:") === 0) {
          const cs = ic.slice(6).split("|");
          const grad = `background: linear-gradient(135deg, ${escapeHtml(cs[0])} 50%, ${escapeHtml(cs[1] || cs[0])} 50%)`;
          if (cs[2]) return `<i class="is-mark is-mark--mascot" title="${escapeHtml(name)}" style="${grad}"><img src="${escapeHtml(cs[2])}" alt="${escapeHtml(name)}" loading="lazy"></i>`;
          return `<i class="is-mark is-mark--swatch" title="${escapeHtml(name)}" style="${grad}"><b>${escapeHtml(short)}</b></i>`;
        }
        const icons = ic.split("|").filter(Boolean);
        if (!icons.length) return `<i class="is-mark is-mark--text" title="${escapeHtml(name)}">${escapeHtml(short)}</i>`;
        return `<i class="is-mark" title="${escapeHtml(name)}">${icons.map(function(u, j) { return `<img src="${escapeHtml(u)}" alt="${j ? "" : escapeHtml(name)}" loading="lazy">`; }).join("")}</i>`;
      }).join("") : "";
      const works = compact ? "" : (item.works || []).slice(0, 3).map(function(name, i) {
        const ic = (item.work_icons || [])[i] || "";
        const label = escapeHtml(name);
        if (ic.indexOf("color:") === 0) {
          const cs = ic.slice(6).split("|");
          const c2 = cs[1] || cs[0];
          return `<span class="is-work has-swatch"><i class="work-swatch" style="background: linear-gradient(90deg, ${escapeHtml(cs[0])} 50%, ${escapeHtml(c2)} 50%)"></i>${label}</span>`;
        }
        const icons = ic.split("|").filter(Boolean);
        const before = icons[0] ? `<img src="${escapeHtml(icons[0])}" alt="" loading="lazy">` : "";
        const after = icons[1] ? `<img src="${escapeHtml(icons[1])}" alt="" loading="lazy">` : "";
        return `<span class="is-work${icons.length ? " has-icon" : ""}">${before}${label}${after}</span>`;
      }).join("");
      const topics = compact ? "" : chips(item.topics, "is-topic", 4);
      return `
        <article class="search-result-card search-result-card--${escapeHtml(item.card || item.kind)} is-type-${typeClass(type)}${compact ? ` search-result-card--compact search-result-card--${shape(item)}` : ""}">
          ${coverBlock(item)}
          <div class="search-result-card__body">
            <div class="search-result-card__kicker">${kicker}</div>
            <h2><a href="${escapeHtml(item.url)}">${escapeHtml(item.title)}</a></h2>
            ${compact ? "" : `<p>${escapeHtml(lead)}</p>`}
            ${(people || works) ? `<div class="search-result-card__tags">${people}${works}</div>` : ""}
            ${topics ? `<div class="search-result-card__topics">${topics}</div>` : ""}
            <div class="search-result-card__facts">${facts.map(function(v) { return `<span>${escapeHtml(v)}</span>`; }).join("")}${marks ? `<span class="search-result-card__works" aria-label="提到的作品">${marks}</span>` : ""}</div>
          </div>
        </article>
      `;
    }

    function render() {
      if (!loaded) { load().then(function() { if (loaded) render(); }); return; }
      const filters = getFilters();
      lastResults = items.filter(function(item) { return matches(item, filters); });
      const sort = sortEl ? sortEl.value : "date-desc";
      const scores = sort === "feed" ? feedScores() : null;
      lastResults.sort(function(a, b) {
        if (scores) return (scores.get(b) || 0) - (scores.get(a) || 0) || String(b.date || "").localeCompare(String(a.date || ""));
        if (sort === "title") return String(a.title).localeCompare(String(b.title), "zh");
        const d = String(a.date || "").localeCompare(String(b.date || ""));
        return sort === "date-asc" ? d : -d;
      });
      if (status) status.textContent = `显示 ${Math.min(shown, lastResults.length)} / ${lastResults.length} 条，库内共 ${items.length} 条`;
      if (moreButton) moreButton.hidden = lastResults.length <= shown;
      resultList.dataset.prerendered = "false";
      dimButtons.forEach(function(b) {
        const el = filterEls[b.dataset.dim];
        b.classList.toggle("is-on", !!el && el.value === b.dataset.value);
      });
      if (!lastResults.length) {
        resultList.innerHTML = "<p class='search-lab__empty'>没有找到匹配结果。可以放宽筛选，或先只按年份、类型过滤。</p>";
        masonry();
        return;
      }
      resultList.innerHTML = lastResults.slice(0, shown).map(card).join("");
      masonry();
    }

    // the masonry: the compact cards are of different heights (a wide picture, a tall one,
    // none), so each one spans as many 4px rows of the grid as it is tall (plus its 8px
    // margin - the grid's own row gap is off) and the next card moves up under it. One
    // column (a phone) needs none of it. Measured again when the width changes, a picture
    // or the fonts arrive, or the list is redrawn.
    let masonryFrame = 0;
    function masonry() {
      if (!compact) return;
      if (masonryFrame) return;
      masonryFrame = window.requestAnimationFrame(function() {
        masonryFrame = 0;
        if (!resultList.clientWidth) return;     // hidden (another tab): measured when it shows
        const cards = Array.from(resultList.children);
        const columns = getComputedStyle(resultList).gridTemplateColumns.split(" ").length;
        if (columns < 2) {
          resultList.classList.remove("is-masonry");
          cards.forEach(function(c) { c.style.gridRowEnd = ""; });
          return;
        }
        resultList.classList.add("is-masonry");
        const gap = 8;
        const unit = 4;
        cards.forEach(function(c) {
          c.style.gridRowEnd = "span " + Math.max(1, Math.ceil((c.getBoundingClientRect().height + gap) / unit));
        });
      });
    }
    if (compact) {
      if (window.ResizeObserver) new ResizeObserver(masonry).observe(resultList);
      else window.addEventListener("resize", masonry);
      resultList.addEventListener("load", masonry, true);
      if (document.fonts && document.fonts.ready) document.fonts.ready.then(masonry);
      masonry();
    }

    function load() {
      if (loaded) return Promise.resolve();
      if (loading) return loading;
      if (!dataUrl) {
        if (status && touched) status.textContent = "目录读取失败，请刷新重试。";
        return Promise.resolve();
      }
      if (status && touched) status.textContent = "正在读取目录...";
      // one attempt per reader action: a failure is reported and waits for the next action,
      // it never retries on its own
      loading = fetch(dataUrl, { credentials: "same-origin" }).then(function(r) {
        if (!r.ok) throw new Error(String(r.status));
        return r.json();
      }).then(function(data) {
        items = Array.isArray(data) ? data : [];
        loaded = true;
        populateFilters();
      }).catch(function() {
        if (status && touched) status.textContent = "目录读取失败，请刷新重试。";
        loading = null;
      });
      return loading;
    }

    function change() {
      touched = true;
      shown = PAGE;
      render();
    }

    function setMode(mode) {
      Object.values(filterEls).forEach(function(select) { if (select) select.value = ""; });
      if (mode === "interview" && filterEls.type) setSelect(filterEls.type, "访谈翻译");
      if (mode === "scan" && filterEls.type) setSelect(filterEls.type, "扫描翻译");
      change();
    }

    function applyQueryParams() {
      const params = new URLSearchParams(window.location.search);
      let any = false;
      if (params.get("q")) { queryInput.value = params.get("q"); any = true; }
      const keys = ["type", "work", "person", "year", "source"].filter(function(k) { return params.get(k) && filterEls[k]; });
      if (keys.length) {
        any = true;
        if (loaded) keys.forEach(function(k) { setSelect(filterEls[k], params.get(k), false); });
        else pendingParams = params;       // applied once the options exist
      }
      return any;
    }

    // an entry the reader opens leads the feed's kinship next time (its people and works)
    resultList.addEventListener("click", function(event) {
      const link = event.target.closest ? event.target.closest("a[href]") : null;
      const cardEl = link && link.closest(".search-result-card");
      if (!cardEl) return;
      const url = link.getAttribute("href");
      const item = items.find(function(it) { return it.url === url; });
      rememberRead(item ? { url: url, people: item.people || [], works: item.works || [] } : {
        url: url,
        people: Array.from(cardEl.querySelectorAll(".is-person")).map(function(el) { return el.textContent.trim(); }),
        works: Array.from(cardEl.querySelectorAll(".is-mark[title], .is-work")).map(function(el) { return el.getAttribute("title") || el.textContent.trim(); })
      });
    });

    if (form) form.addEventListener("submit", function(event) { event.preventDefault(); change(); });
    queryInput.addEventListener("input", change);
    Object.values(filterEls).forEach(function(select) { if (select) select.addEventListener("change", change); });
    if (sortEl) sortEl.addEventListener("change", change);
    if (moreButton) moreButton.addEventListener("click", function() { shown += PAGE; render(); });
    if (resetButton) resetButton.addEventListener("click", function() {
      queryInput.value = "";
      Object.values(filterEls).forEach(function(select) { if (select) select.value = ""; });
      change();
    });
    modeButtons.forEach(function(button) {
      button.addEventListener("click", function() { setMode(button.dataset.searchMode); });
    });
    // the dimension panel: a year bar, a person, a work, a type - each one is a filter
    dimButtons.forEach(function(button) {
      button.addEventListener("click", function(event) {
        const el = filterEls[button.dataset.dim];
        if (!el) return;
        event.preventDefault();
        const next = el.value === button.dataset.value ? "" : button.dataset.value;
        // a tile on the shelf opens a collection: it starts from a clean slate, a panel button narrows
        if (button.closest("[data-topics]")) {
          queryInput.value = "";
          Object.values(filterEls).forEach(function(select) { if (select) select.value = ""; });
        }
        setSelect(el, next, true);
        change();
        const anchor = document.getElementById("overview") || resultList;
        if (window.matchMedia && window.matchMedia("(max-width: 900px)").matches) anchor.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    });

    // a collection chip with data-q searches the catalogue on this page instead of leaving it
    Array.from(document.querySelectorAll("[data-q]")).forEach(function(el) {
      el.addEventListener("click", function(event) {
        event.preventDefault();
        Object.values(filterEls).forEach(function(select) { if (select) select.value = ""; });
        queryInput.value = queryInput.value.trim() === el.dataset.q ? "" : el.dataset.q;
        change();
        const anchor = document.getElementById("filteredSearchResults");
        if (anchor && window.matchMedia && window.matchMedia("(max-width: 900px)").matches) anchor.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    });

    if (aiButton && aiEndpoint && aiOutput) {
      aiButton.addEventListener("click", function() {
        const query = queryInput.value.trim();
        const context = lastResults.slice(0, 12).map(function(item) {
          return { title: item.title, type: contentType(item.type), source: item.source, date: item.date, excerpt: item.excerpt || item.body };
        });
        aiOutput.hidden = false;
        aiOutput.textContent = "正在连接本地 DeepSeek 代理...";
        fetch(aiEndpoint.value, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query, filters: getFilters(), context })
        }).then(function(response) {
          return response.json().then(function(data) {
            if (!response.ok) throw new Error(data.error || "AI 检索失败");
            aiOutput.textContent = data.answer || "没有返回内容。";
          });
        }).catch(function() {
          aiOutput.textContent = "尚未连接本地 AI 代理。可在本地运行 tools/deepseek-search-proxy.mjs 后重试。详情见编辑工作台。";
        });
      });
    }

    if (loaded) {
      populateFilters();
      applyQueryParams();
      render();
    } else if (applyQueryParams() || !prerendered) {
      load().then(function() { if (loaded) render(); });
    } else {
      // the first cards are on the page already; fetch the rest once the page has settled,
      // so the first filter the reader touches answers at once
      const idle = window.requestIdleCallback ? function(fn) { window.requestIdleCallback(fn, { timeout: 4000 }); } : function(fn) { setTimeout(fn, 1200); };
      idle(function() { if (!touched) load(); });
    }
  }

  // the collection shelf: scrolls sideways; left alone it drifts a chip at a time and wraps,
  // stops under the pointer or a finger, and holds still for readers who asked for less motion
  function shelf() {
    const row = document.querySelector("[data-topics]");
    if (!row || (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches)) return;
    let hold = false, timer = 0;
    const step = function() {
      if (hold || row.scrollWidth <= row.clientWidth + 4) return;
      const chip = row.querySelector("a");
      const by = chip ? chip.getBoundingClientRect().width + 8 : 180;
      if (row.scrollLeft + row.clientWidth >= row.scrollWidth - 2) row.scrollTo({ left: 0, behavior: "smooth" });
      else row.scrollBy({ left: by, behavior: "smooth" });
    };
    const start = function() { if (!timer) timer = setInterval(step, 4500); };
    ["pointerenter", "focusin", "touchstart"].forEach(function(ev) { row.addEventListener(ev, function() { hold = true; }, { passive: true }); });
    ["pointerleave", "focusout", "touchend"].forEach(function(ev) { row.addEventListener(ev, function() { hold = false; }, { passive: true }); });
    document.addEventListener("visibilitychange", function() { hold = document.hidden; });
    setTimeout(start, 3000);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", function() { init(); shelf(); });
  else { init(); shelf(); }
})();
