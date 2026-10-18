/* Optional enhancements; the full article and heading links are server rendered. */
(function () {
  "use strict";
  const root = document.querySelector("[data-original-reader]");
  if (!root) return;
  const content = root.querySelector("[data-original-content]");
  const toc = root.querySelector("[data-original-toc]");
  const wide = window.matchMedia("(min-width: 1051px)");
  if (toc) {
    const setToc = () => { toc.open = wide.matches; };
    setToc();
    wide.addEventListener("change", setToc);
    const links = Array.from(toc.querySelectorAll('a[href^="#"]'));
    const targetId = link => { try { return decodeURIComponent(link.hash.slice(1)); } catch (_) { return link.hash.slice(1); } };
    const headings = links.map(link => document.getElementById(targetId(link))).filter(Boolean);
    const progress = root.querySelector("[data-original-progress]");
    const bar = progress && progress.querySelector("progress");
    const percent = progress && progress.querySelector("[data-original-percent]");
    if (progress) progress.hidden = false;
    let scheduled = false;
    const update = () => {
      scheduled = false;
      let current = headings[0];
      headings.forEach(heading => { if (heading.getBoundingClientRect().top <= 130) current = heading; });
      links.forEach(link => {
        if (current && targetId(link) === current.id) link.setAttribute("aria-current", "location");
        else link.removeAttribute("aria-current");
      });
      if (bar) {
        const bounds = content.getBoundingClientRect();
        const available = Math.max(1, bounds.height - window.innerHeight);
        const value = Math.max(0, Math.min(100, Math.round(-bounds.top / available * 100)));
        bar.value = value;
        percent.textContent = value + "%";
      }
    };
    const schedule = () => { if (!scheduled) { scheduled = true; window.requestAnimationFrame(update); } };
    window.addEventListener("scroll", schedule, { passive: true });
    window.addEventListener("resize", schedule);
    content.addEventListener("load", schedule, true);
    toc.addEventListener("click", event => {
      if (!wide.matches && event.target.closest('a[href^="#"]')) toc.open = false;
    });
    update();
  }

  const dialog = root.querySelector("[data-original-viewer]");
  const images = Array.from(content.querySelectorAll("img[src]"));
  if (!dialog || !images.length) return;
  const fullImage = dialog.querySelector("[data-original-full-image]");
  const caption = dialog.querySelector("[data-original-image-caption]");
  const source = dialog.querySelector("[data-original-image-source]");
  const status = dialog.querySelector("[data-original-image-status]");
  const previous = dialog.querySelector("[data-original-prev]");
  const next = dialog.querySelector("[data-original-next]");
  let selected = 0;
  let invoker = null;
  const show = index => {
    selected = index;
    const image = images[index];
    const figure = image.closest("figure");
    const label = figure && figure.querySelector("figcaption");
    fullImage.hidden = true;
    status.hidden = false;
    status.textContent = "正在载入原图…";
    fullImage.src = image.currentSrc || image.src;
    fullImage.alt = image.alt || "";
    source.href = image.src;
    caption.textContent = (index + 1) + " / " + images.length + (label ? " · " + label.textContent.trim() : "");
    previous.disabled = index === 0;
    next.disabled = index === images.length - 1;
  };
  fullImage.addEventListener("load", () => { fullImage.hidden = false; status.hidden = true; });
  fullImage.addEventListener("error", () => { status.hidden = false; status.textContent = "这张原图暂时无法载入，可通过下方链接打开。"; });
  images.forEach((image, index) => {
    if (image.closest("a")) return; // An author's existing link keeps its destination.
    const link = document.createElement("a");
    link.className = "original-image-link";
    link.href = image.src;
    link.target = "_blank";
    link.rel = "noopener";
    link.setAttribute("aria-label", "查看第 " + (index + 1) + " 张配图原图");
    image.parentNode.insertBefore(link, image);
    link.appendChild(image);
    link.addEventListener("click", event => {
      if (typeof dialog.showModal !== "function" || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      invoker = link;
      show(index);
      dialog.showModal();
    });
  });
  previous.addEventListener("click", () => { if (selected > 0) show(selected - 1); });
  next.addEventListener("click", () => { if (selected < images.length - 1) show(selected + 1); });
  dialog.addEventListener("keydown", event => {
    if (event.key === "ArrowLeft" && selected > 0) { event.preventDefault(); show(selected - 1); }
    if (event.key === "ArrowRight" && selected < images.length - 1) { event.preventDefault(); show(selected + 1); }
  });
  dialog.addEventListener("click", event => {
    if (event.target === dialog) {
      const bounds = dialog.getBoundingClientRect();
      if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
    }
  });
  dialog.addEventListener("close", () => { fullImage.removeAttribute("src"); if (invoker) invoker.focus({ preventScroll: true }); });
}());
