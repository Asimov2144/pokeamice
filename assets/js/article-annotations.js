(function () {
  function ready(callback) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", callback);
    } else {
      callback();
    }
  }

  ready(function () {
    var refs = Array.prototype.slice.call(document.querySelectorAll("[data-annotation-ref]"));
    var cards = Array.prototype.slice.call(document.querySelectorAll("[data-annotation-card]"));
    var annotationList = document.querySelector(".article-annotations__list");
    var contentArea = document.querySelector(".page__content");
    if (!refs.length || !cards.length) return;

    var byId = new Map();
    cards.forEach(function (card) {
      byId.set(card.getAttribute("data-annotation-card"), card);
    });

    function setActive(id, shouldScroll) {
      refs.forEach(function (ref) {
        ref.classList.toggle("is-active", ref.getAttribute("data-annotation-ref") === id);
      });
      cards.forEach(function (card) {
        card.classList.toggle("is-active", card.getAttribute("data-annotation-card") === id);
      });
      if (shouldScroll && byId.has(id)) {
        byId.get(id).scrollIntoView({ behavior: "smooth", block: "nearest" });
      }
    }

    refs.forEach(function (ref) {
      ref.setAttribute("tabindex", "0");
      ref.setAttribute("role", "button");
      ref.addEventListener("click", function () {
        setActive(ref.getAttribute("data-annotation-ref"), true);
      });
      ref.addEventListener("keydown", function (event) {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          setActive(ref.getAttribute("data-annotation-ref"), true);
        }
      });
    });

    cards.forEach(function (card) {
      card.addEventListener("click", function () {
        var id = card.getAttribute("data-annotation-card");
        setActive(id, false);
        var ref = document.querySelector('[data-annotation-ref="' + CSS.escape(id) + '"]');
        if (ref) ref.scrollIntoView({ behavior: "smooth", block: "center" });
      });
    });

    function resetAnnotationPositions() {
      if (!annotationList) return;
      annotationList.classList.remove("is-positioned");
      annotationList.style.minHeight = "";
      cards.forEach(function (card) {
        card.style.top = "";
      });
    }

    function layoutAnnotationPositions() {
      if (!annotationList || !contentArea) return;
      if (!window.matchMedia("(min-width: 64em)").matches) {
        resetAnnotationPositions();
        return;
      }

      resetAnnotationPositions();

      window.requestAnimationFrame(function () {
        var listTop = annotationList.getBoundingClientRect().top + window.pageYOffset;
        var contentTop = contentArea.getBoundingClientRect().top + window.pageYOffset;
        var contentHeight = contentArea.getBoundingClientRect().height;
        var nextTop = 0;
        var gap = 14;

        cards.forEach(function (card) {
          var id = card.getAttribute("data-annotation-card");
          var ref = document.querySelector('[data-annotation-ref="' + CSS.escape(id) + '"]');
          if (!ref) return;

          var refTop = ref.getBoundingClientRect().top + window.pageYOffset;
          var desiredTop = Math.max(0, refTop - listTop - 8);
          var top = Math.max(desiredTop, nextTop);
          card.style.top = top + "px";
          nextTop = top + card.offsetHeight + gap;
        });

        annotationList.style.minHeight = Math.max(nextTop, contentTop + contentHeight - listTop) + "px";
        annotationList.classList.add("is-positioned");
      });
    }

    var layoutTimer;
    function scheduleLayout() {
      window.clearTimeout(layoutTimer);
      layoutTimer = window.setTimeout(layoutAnnotationPositions, 80);
    }

    layoutAnnotationPositions();
    window.addEventListener("resize", scheduleLayout);
    window.addEventListener("load", scheduleLayout);
  });
})();
