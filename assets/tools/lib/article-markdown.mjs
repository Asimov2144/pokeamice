/* Turning translated blocks into a site article.
   ==========================================================================
   Same reason as lib/web-capture.mjs: this transform lived inside
   article-translation-editor.html, so it existed only in a browser tab and
   nothing else driving the pipeline could produce an article from blocks it
   had already translated. The tool and POST /api/build-article-markdown call
   this module, so a file written by hand and one written by a script are the
   same file.

   The only change made in the move is that the two front-matter builders take
   a `meta` object instead of reading form fields directly. Everything else is
   the tool's own logic, moved verbatim - a rewrite here would have been a
   second implementation to keep in step, which is the problem, not the fix.

   A block is:
     { type: "paragraph" | "heading" | "image",
       source, translation, note, fontSize, level, original, replacement,
       alt, caption } */

export function cleanMarkdownLine(value) {
  return String(value || "").replace(/\s+/g, " ").trim();
}

export function escapeComment(value) {
  return String(value || "").replaceAll("--", "- -").trim();
}

export function normalizeFontSize(value) {
  const size = String(value || "").trim();
  return ["", "small", "normal", "large", "xlarge"].includes(size) ? size : "";
}

export function fontSizeLabel(value) {
  return {
    "": "默认",
    small: "小号",
    normal: "正文",
    large: "大号",
    xlarge: "特大"
  }[normalizeFontSize(value)] || "默认";
}

export function yamlScalar(value, indent = 0) {
  const pad = " ".repeat(indent);
  const text = String(value || "").trim();
  if (!text) return "''";
  if (!/[\n\r]/.test(text) && text.length <= 72 && !/[:#{}\[\],&*?|<>=!%@`]/.test(text)) {
    return JSON.stringify(text);
  }
  return `|-\n${text.split(/\r?\n/).map((line) => `${pad}  ${line}`).join("\n")}`;
}

/* Blocks arriving from JSON may be missing the string fields the builders
   assume are always present; normalise once at the edge rather than guarding
   at every use. */
function normalizeBlock(block) {
  return {
    type: block?.type || "paragraph",
    source: String(block?.source ?? ""),
    translation: String(block?.translation ?? ""),
    note: String(block?.note ?? ""),
    fontSize: block?.fontSize ?? "",
    level: block?.level,
    original: block?.original ?? "",
    replacement: block?.replacement ?? "",
    alt: block?.alt ?? "",
    caption: block?.caption ?? ""
  };
}

function headingLevel(block) {
  return Math.min(Math.max(Number(block.level) || 2, 2), 4);
}

export function parallelTextBlock(block) {
  const source = cleanMarkdownLine(block.source);
  const translation = cleanMarkdownLine(block.translation);
  const lines = [];
  const size = normalizeFontSize(block.fontSize);
  if (size) lines.push(`<!-- 字号：${fontSizeLabel(size)} -->`);
  if (source) lines.push(`> 原文：${source}`);
  lines.push(translation ? `译文：${translation}` : "译文：");
  if (block.note.trim()) lines.push(`> 译注：${block.note.trim()}`);
  return lines.join("\n\n");
}

export function displayTextBlock(block) {
  const lines = [];
  const size = normalizeFontSize(block.fontSize);
  if (size) lines.push(`<div class="paragraph-size-${size}">`);
  if (block.translation.trim()) lines.push(block.translation.trim());
  if (block.note.trim()) lines.push(`> 译注：${block.note.trim()}`);
  if (block.source.trim()) lines.push(`<!-- 原文：${escapeComment(block.source)} -->`);
  if (size) lines.push("</div>");
  return lines.join("\n\n");
}

export function frontMatter(meta = {}) {
  const title = String(meta.title || "").trim() || "未命名翻译";
  return [
    "---",
    `title: "${title.replaceAll('"', '\\"')}"`,
    `date: ${meta.date || ""}`,
    "categories:",
    "  - 翻译",
    "tags:",
    "  - Pokemon",
    "  - translation",
    `source: ${String(meta.sourceUrl || "").trim()}`,
    "---",
    ""
  ].join("\n");
}

export function templateFrontMatter(meta = {}, blocks = []) {
  const title = String(meta.title || "").trim() || "未命名翻译";
  const lines = [
    "---",
    "layout: parallel-translation",
    `title: ${JSON.stringify(title)}`,
    `date: ${meta.date || ""}`,
    "toc: true",
    "toc_sticky: true",
    "parallel_view: translation",
    "categories:",
    "  - 翻译",
    "tags:",
    "  - Pokemon",
    "  - translation",
    `source: ${JSON.stringify(String(meta.sourceUrl || "").trim())}`,
    "parallel_items:"
  ];

  blocks.forEach((block) => {
    if (block.type === "heading") {
      lines.push("  - type: heading");
      lines.push(`    level: ${headingLevel(block)}`);
      lines.push(`    original: ${yamlScalar(block.source, 4)}`);
      lines.push(`    translation: ${yamlScalar(block.translation || block.source, 4)}`);
      if (block.note.trim()) lines.push(`    note: ${yamlScalar(block.note, 4)}`);
      return;
    }
    if (block.type === "image") {
      const image = block.replacement || block.original;
      if (!image) return;
      lines.push("  - type: image");
      lines.push(`    image: ${JSON.stringify(image)}`);
      if (block.alt || block.caption) lines.push(`    alt: ${yamlScalar(block.alt || block.caption, 4)}`);
      if (block.caption) lines.push(`    caption: ${yamlScalar(block.caption, 4)}`);
      return;
    }
    lines.push("  - type: paragraph");
    lines.push(`    original: ${yamlScalar(block.source, 4)}`);
    lines.push(`    translation: ${yamlScalar(block.translation, 4)}`);
    if (normalizeFontSize(block.fontSize)) {
      lines.push(`    font_size: ${JSON.stringify(normalizeFontSize(block.fontSize))}`);
    }
    if (block.note.trim()) lines.push(`    note: ${yamlScalar(block.note, 4)}`);
  });

  lines.push("---", "");
  return lines.join("\n");
}

/* mode: "template" emits parallel_items front matter and no body;
   "parallel" keeps the original beside each translation in the body;
   anything else renders the translation for display. */
export function buildArticleMarkdown({ mode = "display", blocks = [], meta = {} } = {}) {
  const normalized = blocks.map(normalizeBlock);
  if (mode === "template") return templateFrontMatter(meta, normalized);

  const body = normalized.map((block) => {
    if (block.type === "heading") {
      const headingText = cleanMarkdownLine(block.translation || block.source || "未命名小标题");
      const marks = "#".repeat(headingLevel(block));
      const lines = [`${marks} ${headingText}`];
      if (mode === "parallel" && block.source.trim()) {
        lines.push(`> 原文标题：${cleanMarkdownLine(block.source)}`);
      }
      if (mode === "display" && block.source.trim()) {
        lines.push(`<!-- 原文标题：${escapeComment(block.source)} -->`);
      }
      if (block.note.trim()) lines.push(`> 译注：${block.note.trim()}`);
      return lines.join("\n\n");
    }
    if (block.type === "image") {
      const url = block.replacement || block.original;
      if (!url) return "";
      const alt = block.alt || block.caption || "image";
      const caption = block.caption ? `\n*${block.caption.trim()}*` : "";
      return `![${alt}](${url})${caption}`;
    }
    return mode === "parallel" ? parallelTextBlock(block) : displayTextBlock(block);
  }).filter(Boolean).join("\n\n");

  return `${frontMatter(meta)}${body}\n`;
}
