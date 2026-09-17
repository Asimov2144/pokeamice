/* Development Atlas 区块的切换：按钮 data-set / data-value 写到卡片的 data-<set>，
   卡片里带同名 data 属性的列表只留匹配的那组。内容全是预渲染的，这里不取数据。 */
(function () {
  document.querySelectorAll(".atlas__card").forEach(function (card) {
    card.querySelectorAll(".atlas__toggle button").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var set = btn.getAttribute("data-set"), val = btn.getAttribute("data-value");
        card.setAttribute("data-" + set, val);
        card.querySelectorAll('.atlas__toggle button[data-set="' + set + '"]').forEach(function (b) { b.classList.toggle("is-on", b === btn); });
        card.querySelectorAll(".atlas__list").forEach(function (list) {
          var show = true;
          ["scope", "view"].forEach(function (k) {
            var want = card.getAttribute("data-" + k), has = list.getAttribute("data-" + k);
            if (want && has && want !== has) show = false;
          });
          list.hidden = !show;
        });
      });
    });
  });
})();
