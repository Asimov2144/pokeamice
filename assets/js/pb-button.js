/* The button on a catalogue card's footer rule (_sass/minimal-mistakes/_pokeball-cards.scss): a tap opens
   the card's quick look - the original title, where it ran, the summary, what its state means, and 打开全文 /
   分享 / 复制链接 - inside the card, and a second tap closes it; a long press shares the entry (the system
   sheet where there is one, else the link is copied). Everything comes from the card's own data-pb-*
   (_includes/entry-card.html, assets/js/catalogue.js), so nothing is fetched. One listener for the page,
   so the cards the catalogue draws later work too. */
(function () {
  "use strict";
  var HOLD = 550;            // the ring fills in this long (pb-hold in the stylesheet)
  var timer = 0, held = false, startX = 0, startY = 0;

  function esc(v) { return String(v == null ? "" : v).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function cardOf(el) { return el.closest ? el.closest(".search-result-card") : null; }
  function urlOf(card) { return new URL(card.getAttribute("data-pb-url") || "", location.href).href; }

  function toast(text, el) {
    var r = el.getBoundingClientRect();
    var t = document.createElement("div");
    t.className = "pb-toast";
    t.textContent = text;
    t.style.left = (r.left + r.width / 2) + "px";
    t.style.top = r.top + "px";
    document.body.appendChild(t);
    setTimeout(function () { t.remove(); }, 1700);
  }

  // the clipboard API, else the old way through a hidden field; a short word either way, never the long address
  function copy(card, el) {
    var url = urlOf(card);
    var fallback = function () {
      var f = document.createElement("textarea");
      f.value = url; f.setAttribute("readonly", ""); f.style.cssText = "position:fixed;left:-9999px;top:0";
      document.body.appendChild(f); f.select();
      var ok = false;
      try { ok = document.execCommand("copy"); } catch (err) { ok = false; }
      f.remove();
      toast(ok ? "已复制链接" : "没能复制，请从地址栏复制", el);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(url).then(function () { toast("已复制链接", el); }, fallback);
    else fallback();
  }

  function share(card, el) {
    var data = { title: card.getAttribute("data-pb-title") || document.title, url: urlOf(card) };
    if (navigator.share) {
      navigator.share(data).catch(function () { /* closed by the reader */ });
    } else {
      copy(card, el);
    }
  }

  function relayout(card) {
    var list = card.parentElement;
    if (list) list.dispatchEvent(new CustomEvent("pb:relayout"));
  }

  function look(card) {
    var btn = card.querySelector(".pb-btn");
    var title = card.getAttribute("data-pb-title") || "";
    var orig = card.getAttribute("data-pb-orig") || "";
    var pub = card.getAttribute("data-pb-pub") || "";
    var lead = card.getAttribute("data-pb-lead") || "";
    var state = btn && btn.classList.contains("is-done") ? "译文已经人工对着原文校过。"
      : btn && btn.classList.contains("is-draft") ? "这是大模型的初译，还没有人工逐句校对；引用前请对照原文。" : "";
    var box = document.createElement("div");
    box.className = "pb-look";
    box.innerHTML =
      (pub ? "<p class='pb-look__pub'>" + esc(pub) + "</p>" : "") +
      (orig && orig !== title ? "<p class='pb-look__orig'>原题：" + esc(orig) + "</p>" : "") +
      (lead && lead !== "暂无摘要" ? "<p>" + esc(lead) + "</p>" : "") +
      (state ? "<p class='pb-look__state'>" + state + "</p>" : "") +
      "<p class='pb-look__acts'><a href='" + esc(card.getAttribute("data-pb-url")) + "'>打开全文 →</a>" +
      "<button type='button' data-pb-act='share'>分享</button><button type='button' data-pb-act='copy'>复制链接</button></p>";
    return box;
  }

  function toggle(card) {
    var btn = card.querySelector(".pb-btn");
    var open = card.querySelector(":scope > .pb-look");
    if (open) {
      open.remove();
      card.classList.remove("is-open");
      if (btn) { btn.setAttribute("aria-expanded", "false"); btn.setAttribute("aria-label", "速览这一篇（长按分享）"); }
    } else {
      var facts = card.querySelector(":scope > .search-result-card__facts");
      card.insertBefore(look(card), facts || null);
      card.classList.add("is-open");
      if (btn) { btn.setAttribute("aria-expanded", "true"); btn.setAttribute("aria-label", "收起速览"); }
    }
    relayout(card);
  }

  function stopHold(btn) {
    clearTimeout(timer);
    timer = 0;
    if (btn) btn.classList.remove("is-holding");
  }

  document.addEventListener("pointerdown", function (e) {
    var btn = e.target.closest && e.target.closest(".pb-btn");
    if (!btn || (e.pointerType === "mouse" && e.button !== 0)) return;
    held = false;
    startX = e.clientX; startY = e.clientY;
    btn.classList.add("is-holding");
    timer = setTimeout(function () {
      held = true;
      btn.classList.remove("is-holding");
      if (navigator.vibrate) navigator.vibrate(12);
      share(cardOf(btn), btn);
    }, HOLD);
  });
  document.addEventListener("pointermove", function (e) {
    if (timer && (Math.abs(e.clientX - startX) > 8 || Math.abs(e.clientY - startY) > 8)) stopHold(document.querySelector(".pb-btn.is-holding"));
  });
  ["pointerup", "pointercancel", "pointerleave"].forEach(function (t) {
    document.addEventListener(t, function () { stopHold(document.querySelector(".pb-btn.is-holding")); }, true);
  });
  // a long press on a phone would also open the browser's own menu
  document.addEventListener("contextmenu", function (e) { if (e.target.closest && e.target.closest(".pb-btn")) e.preventDefault(); });

  document.addEventListener("click", function (e) {
    var act = e.target.closest && e.target.closest("[data-pb-act]");
    if (act) {
      var c = cardOf(act);
      if (act.getAttribute("data-pb-act") === "share") share(c, act); else copy(c, act);
      return;
    }
    var btn = e.target.closest && e.target.closest(".pb-btn");
    if (!btn) return;
    e.preventDefault();
    if (held) { held = false; return; }     // the press already shared
    toggle(cardOf(btn));
  });
})();
