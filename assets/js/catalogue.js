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

    function setSelect(select, value) {
      if (!select) return;
      if (value && !Array.from(select.options).some(function(o) { return o.value === value; })) {
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
      setSelect(filterEls.person, keep.person);
      setSelect(filterEls.work, keep.work);
      setSelect(filterEls.year, keep.year);
      setSelect(filterEls.source, keep.source);
      setSelect(filterEls.type, keep.type);
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

    function coverBlock(item) {
      const label = item.publication || item.source || contentType(item.type);
      if (item.cover) {
        return `<a class="search-result-card__cover" href="${escapeHtml(item.url)}" tabindex="-1" aria-hidden="true"><img src="${escapeHtml(item.cover)}" alt="" loading="lazy" decoding="async"></a>`;
      }
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
      const marks = compact ? (item.works || []).slice(0, 4).map(function(name, i) {
        const ic = (item.work_icons || [])[i] || "";
        const short = String(name).replace(/^宝可梦[ ：]/, "").replace(/^Pokémon /, "").slice(0, 2);
        if (ic.indexOf("color:") === 0) {
          const cs = ic.slice(6).split("|");
          return `<span class="is-mark is-mark--swatch" title="${escapeHtml(name)}" style="background: linear-gradient(135deg, ${escapeHtml(cs[0])} 50%, ${escapeHtml(cs[1] || cs[0])} 50%)"><b>${escapeHtml(short)}</b></span>`;
        }
        const icons = ic.split("|").filter(Boolean);
        if (!icons.length) return `<span class="is-mark is-mark--text" title="${escapeHtml(name)}">${escapeHtml(short)}</span>`;
        return `<span class="is-mark" title="${escapeHtml(name)}">${icons.map(function(u, j) { return `<img src="${escapeHtml(u)}" alt="${j ? "" : escapeHtml(name)}" loading="lazy">`; }).join("")}</span>`;
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
        <article class="search-result-card search-result-card--${escapeHtml(item.card || item.kind)}${compact ? " search-result-card--compact" : ""}">
          ${compact ? `<div class="search-result-card__side">${coverBlock(item)}${marks ? `<div class="search-result-card__marks">${marks}</div>` : ""}</div>` : coverBlock(item)}
          <div class="search-result-card__body">
            <div class="search-result-card__kicker">${kicker}</div>
            <h2><a href="${escapeHtml(item.url)}">${escapeHtml(item.title)}</a></h2>
            ${compact ? "" : `<p>${escapeHtml(lead)}</p>`}
            ${(people || works) ? `<div class="search-result-card__tags">${people}${works}</div>` : ""}
            ${topics ? `<div class="search-result-card__topics">${topics}</div>` : ""}
            <div class="search-result-card__facts">${facts.map(function(v) { return `<span>${escapeHtml(v)}</span>`; }).join("")}</div>
          </div>
        </article>
      `;
    }

    function render() {
      if (!loaded) { load().then(render); return; }
      const filters = getFilters();
      lastResults = items.filter(function(item) { return matches(item, filters); });
      const sort = sortEl ? sortEl.value : "date-desc";
      lastResults.sort(function(a, b) {
        if (sort === "title") return String(a.title).localeCompare(String(b.title), "zh");
        const d = String(a.date || "").localeCompare(String(b.date || ""));
        return sort === "date-asc" ? d : -d;
      });
      if (status) status.textContent = `显示 ${Math.min(shown, lastResults.length)} / ${lastResults.length} 条，库内共 ${items.length} 条`;
      if (moreButton) moreButton.hidden = lastResults.length <= shown;
      resultList.dataset.prerendered = "false";
      if (!lastResults.length) {
        resultList.innerHTML = "<p class='search-lab__empty'>没有找到匹配结果。可以放宽筛选，或先只按年份、类型过滤。</p>";
        return;
      }
      resultList.innerHTML = lastResults.slice(0, shown).map(card).join("");
      dimButtons.forEach(function(b) {
        const el = filterEls[b.dataset.dim];
        b.classList.toggle("is-on", !!el && el.value === b.dataset.value);
      });
    }

    function load() {
      if (loaded) return Promise.resolve();
      if (loading) return loading;
      if (status && touched) status.textContent = "正在读取目录...";
      loading = fetch(dataUrl, { credentials: "same-origin" }).then(function(r) { return r.json(); }).then(function(data) {
        items = Array.isArray(data) ? data : [];
        loaded = true;
        populateFilters();
      }).catch(function() {
        if (status) status.textContent = "目录读取失败，请刷新重试。";
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
      ["type", "work", "person", "year", "source"].forEach(function(k) {
        if (params.get(k) && filterEls[k]) { setSelect(filterEls[k], params.get(k)); any = true; }
      });
      return any;
    }

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
        setSelect(el, next);
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

    const fromUrl = applyQueryParams();
    if (loaded) {
      populateFilters();
      applyQueryParams();
      render();
    } else if (fromUrl || !prerendered) {
      load().then(render);
    } else {
      // the first cards are on the page already; fetch the rest once the page has settled,
      // so the first filter the reader touches answers at once
      const idle = window.requestIdleCallback || function(fn) { return setTimeout(fn, 1200); };
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
      const by = chip ? chip.getBoundingClientRect().width + 6 : 120;
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
