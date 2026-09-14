(function () {
  "use strict";

  const root = document.querySelector("[data-jl-app]");
  if (!root) return;

  document.documentElement.classList.remove("no-js");
  document.documentElement.classList.add("jl-enhanced");

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const selectors = Array.from(document.querySelectorAll("[data-jl-select]"));
  const stories = Array.from(document.querySelectorAll("[data-jl-story]"));
  const storyIds = stories.map((story) => story.dataset.jlStory);
  const cover = document.querySelector(".jl-cover");
  const coverImage = document.getElementById("jl-cover-image");
  const coverCount = document.getElementById("jl-cover-count");
  const coverPair = document.getElementById("jl-cover-pair");
  const coverKicker = document.getElementById("jl-cover-kicker");
  const dialog = document.querySelector("[data-jl-lightbox-dialog]");
  const dialogImage = document.querySelector("[data-jl-lightbox-image]");
  const dialogCaption = document.querySelector("[data-jl-lightbox-caption]");
  const dialogClose = document.querySelector("[data-jl-lightbox-close]");
  const originalTitle = document.title;
  let activeId = storyIds[0];
  let lastLightboxTrigger = null;

  function selectorFor(id) {
    return selectors.find((item) => item.dataset.jlSelect === id);
  }

  function storyFor(id) {
    return stories.find((item) => item.dataset.jlStory === id);
  }

  function updateCover(selector) {
    if (!selector) return;

    const nextSource = selector.dataset.cover;
    const nextAlt = selector.dataset.coverAlt || "联动主视觉";

    root.style.setProperty("--accent", selector.dataset.accent || "#0669a9");
    coverCount.textContent = `${selector.dataset.number} / ${selectors.length}`;
    coverPair.textContent = `${selector.dataset.team} × ${selector.dataset.pokemon}`;
    coverKicker.textContent = selector.dataset.kicker;

    if (coverImage.getAttribute("src") !== nextSource) {
      cover.classList.add("is-loading");
      coverImage.alt = nextAlt;
      coverImage.src = nextSource;
    }
  }

  function updateHistory(id, mode) {
    const url = new URL(window.location.href);
    url.hash = id;
    if (mode === "replace") {
      window.history.replaceState({ jlPairing: id }, "", url);
    } else if (mode !== "none") {
      window.history.pushState({ jlPairing: id }, "", url);
    }
  }

  function activate(id, options) {
    const settings = Object.assign({ scroll: false, history: "push", focus: false }, options);
    if (!storyIds.includes(id)) id = storyIds[0];

    const nextStory = storyFor(id);
    const nextSelector = selectorFor(id);
    activeId = id;

    stories.forEach((story) => {
      const isActive = story === nextStory;
      story.classList.toggle("is-active", isActive);
      story.setAttribute("aria-hidden", String(!isActive));
    });

    selectors.forEach((selector) => {
      const isActive = selector === nextSelector;
      selector.classList.toggle("is-active", isActive);
      if (isActive) selector.setAttribute("aria-current", "true");
      else selector.removeAttribute("aria-current");
    });

    updateCover(nextSelector);
    updateHistory(id, settings.history);
    document.title = `${nextSelector.dataset.team} × ${nextSelector.dataset.pokemon} - ${originalTitle}`;

    if (settings.focus) {
      const heading = nextStory.querySelector("h2");
      if (heading) heading.focus({ preventScroll: true });
    }

    if (settings.scroll) {
      nextStory.scrollIntoView({
        behavior: reducedMotion.matches ? "auto" : "smooth",
        block: "start"
      });
    }
  }

  function move(step) {
    const index = storyIds.indexOf(activeId);
    const nextIndex = (index + step + storyIds.length) % storyIds.length;
    activate(storyIds[nextIndex], { scroll: true, history: "push", focus: true });
  }

  selectors.forEach((selector, index) => {
    selector.addEventListener("click", (event) => {
      event.preventDefault();
      activate(selector.dataset.jlSelect, { scroll: true, history: "push", focus: true });
    });

    selector.addEventListener("keydown", (event) => {
      if (!['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(event.key)) return;
      event.preventDefault();
      const columns = window.innerWidth <= 560 ? 2 : window.innerWidth <= 820 ? 3 : window.innerWidth <= 1180 ? 4 : 5;
      const delta = event.key === "ArrowLeft" ? -1 : event.key === "ArrowRight" ? 1 : event.key === "ArrowUp" ? -columns : columns;
      const target = selectors[(index + delta + selectors.length) % selectors.length];
      target.focus();
    });
  });

  document.querySelectorAll("[data-jl-prev]").forEach((button) => {
    button.addEventListener("click", () => move(-1));
  });

  document.querySelectorAll("[data-jl-next]").forEach((button) => {
    button.addEventListener("click", () => move(1));
  });

  coverImage.addEventListener("load", () => {
    cover.classList.remove("is-loading", "has-error");
  });

  coverImage.addEventListener("error", () => {
    cover.classList.remove("is-loading");
    cover.classList.add("has-error");
    coverImage.alt = "主视觉载入失败";
  });

  document.querySelectorAll(".jl-term-figure img, .jl-selector img").forEach((image) => {
    image.addEventListener("error", () => {
      image.classList.add("jl-image-error");
      image.alt = image.alt || "图片载入失败";
    });
  });

  document.querySelectorAll("[data-jl-lightbox]").forEach((button) => {
    button.addEventListener("click", () => {
      if (!dialog || typeof dialog.showModal !== "function") return;
      lastLightboxTrigger = button;
      dialogImage.src = button.dataset.src;
      dialogImage.alt = button.dataset.alt || "放大图片";
      dialogCaption.textContent = button.dataset.caption || "";
      dialog.showModal();
      document.body.style.overflow = "hidden";
      dialogClose.focus();
    });
  });

  function closeLightbox() {
    if (!dialog || !dialog.open) return;
    dialog.close();
    document.body.style.overflow = "";
    dialogImage.removeAttribute("src");
    if (lastLightboxTrigger) lastLightboxTrigger.focus();
  }

  if (dialogClose) dialogClose.addEventListener("click", closeLightbox);

  if (dialog) {
    dialog.addEventListener("click", (event) => {
      if (event.target === dialog) closeLightbox();
    });
    dialog.addEventListener("cancel", (event) => {
      event.preventDefault();
      closeLightbox();
    });
    dialog.addEventListener("close", () => {
      document.body.style.overflow = "";
    });
  }

  window.addEventListener("popstate", () => {
    const id = window.location.hash.slice(1);
    activate(storyIds.includes(id) ? id : storyIds[0], { scroll: true, history: "none", focus: false });
  });

  const initialHash = window.location.hash.slice(1);
  activate(storyIds.includes(initialHash) ? initialHash : storyIds[0], {
    scroll: false,
    history: initialHash ? "none" : "replace",
    focus: false
  });
})();
