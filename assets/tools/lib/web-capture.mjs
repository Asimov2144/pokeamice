/* Turning a captured web page into a site draft.
   ==========================================================================
   This transform used to live inside web-interview-capture.html, which meant
   it existed only in a browser tab: anything else driving the pipeline could
   fetch a page but could not turn one into a post. It is a module now, and the
   tool and POST /api/build-web-capture both call it, so a draft built by hand
   and a draft built by a script are the same draft.

   One deliberate change came with the move. The tool used DOMParser to strip
   markup, which Node does not have. Injecting a different implementation on
   each side would put the two back out of step - the thing this move exists to
   prevent - so both now use the regex cleaner below, which is also how the
   rest of the server already handles HTML (stripTags/decodeEntities in
   import-wizard-server.mjs). It is less forgiving of malformed markup than a
   real parser; producing the same output on both sides is worth more here than
   surviving broken HTML, and the input is usually copied article text. */

const BLOCK_TAGS = "p|div|section|article|h1|h2|h3|h4|h5|h6|li|tr|blockquote|pre|figcaption";
const DROP_TAGS = "script|style|nav|footer|header|aside|iframe|noscript|form|svg";

const ENTITIES = {
  "&nbsp;": " ", "&amp;": "&", "&lt;": "<", "&gt;": ">",
  "&quot;": '"', "&#39;": "'", "&apos;": "'", "&mdash;": "—",
  "&ndash;": "–", "&hellip;": "…", "&middot;": "·"
};

export function decodeEntities(text) {
  return String(text || "")
    .replace(/&(?:nbsp|amp|lt|gt|quot|apos|mdash|ndash|hellip|middot|#39);/g,
      (match) => ENTITIES[match] ?? match)
    .replace(/&#(\d+);/g, (_, code) => String.fromCodePoint(Number(code)))
    .replace(/&#x([0-9a-f]+);/gi, (_, code) => String.fromCodePoint(parseInt(code, 16)));
}

export function cleanHtmlToText(input) {
  const raw = String(input || "").trim();
  if (!raw) return "";
  /* plain text passes through untouched - people paste article bodies far more
     often than they paste markup */
  if (!/<[a-zA-Z!/]/.test(raw)) return raw;
  let text = raw;
  text = text.replace(new RegExp(`<(${DROP_TAGS})\\b[^>]*>[\\s\\S]*?</\\1>`, "gi"), "");
  text = text.replace(/<!--[\s\S]*?-->/g, "");
  text = text.replace(/<br\s*\/?>/gi, "\n");
  text = text.replace(new RegExp(`</(${BLOCK_TAGS})>`, "gi"), "\n\n");
  text = text.replace(/<[^>]+>/g, "");
  return decodeEntities(text);
}

export function splitParagraphs(source) {
  const cleaned = cleanHtmlToText(source)
    .replace(/\r/g, "\n")
    .replace(/[ \t]+\n/g, "\n")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
  return cleaned.split(/\n{2,}/).map((paragraph) => paragraph.trim()).filter(Boolean);
}

export function splitList(value) {
  return String(value || "").split(/[,，、\n]/).map((item) => item.trim()).filter(Boolean);
}

export function yamlString(value) {
  const text = String(value || "").replaceAll("\\", "\\\\").replaceAll('"', '\\"');
  return `"${text}"`;
}

export function yamlList(key, items) {
  if (!items.length) return `${key}: []`;
  return `${key}:\n${items.map((item) => `  - ${yamlString(item)}`).join("\n")}`;
}

export function nestedYamlList(key, items, indent = "  ") {
  if (!items.length) return `${indent}${key}: []`;
  return `${indent}${key}:\n${items.map((item) => `${indent}  - ${yamlString(item)}`).join("\n")}`;
}

export function slugify(text) {
  const ascii = String(text || "")
    .normalize("NFKD")
    .replace(/[^\w\s-]/g, "")
    .trim()
    .replace(/\s+/g, "-")
    .toLowerCase();
  return ascii || "web-interview";
}

export function today(now = new Date()) {
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function markdownParagraph(text) {
  return String(text || "").replace(/\n+/g, "\n").trim();
}

/* `accessedOn` is a parameter rather than a call to today() inside, so the same
   fields always produce the same bytes. Without it this transform would differ
   from one day to the next, and no caller could tell a real change from the
   calendar moving - which is also what makes /api/build-web-capture safe to
   re-run. */
export function buildWebCapture(fields = {}) {
  const paragraphs = Array.isArray(fields.paragraphs) && fields.paragraphs.length
    ? fields.paragraphs
    : splitParagraphs(fields.source);

  const title = String(fields.title || "").trim() || "未命名网页访谈";
  const date = String(fields.date || "").trim() || today();
  const accessed = String(fields.accessedOn || "").trim() || date;
  const sourceUrl = String(fields.sourceUrl || "").trim();
  const publication = String(fields.publication || "").trim();
  const author = String(fields.author || "").trim();
  const interviewee = String(fields.interviewee || "").trim();
  const people = splitList(fields.people || interviewee);
  const works = splitList(fields.works);
  const organizations = splitList(fields.organizations);
  const tags = splitList(fields.tags || "web-archive, interview");
  const summary = String(fields.summary || "").trim();
  const template = fields.template === "parallel" ? "parallel" : "single";
  const sourceId = "source-web";
  const categories = template === "parallel" ? ["访谈翻译", "网页收录"] : ["文档", "网页收录"];

  const lines = [
    "---",
    `title: ${yamlString(title)}`,
    `date: ${date}`,
    `layout: ${template === "parallel" ? "parallel-translation" : "single"}`,
    yamlList("categories", categories),
    yamlList("tags", tags),
    `archive_type: ${template === "parallel" ? "interview_translation" : "article"}`,
    "source:",
    `  title: ${yamlString(publication || title)}`,
    sourceUrl ? `  url: ${yamlString(sourceUrl)}` : "  url:",
    "  source_type: web_article",
    "  language: ja",
    publication ? `publication: ${yamlString(publication)}` : "publication:",
    author ? `author: ${yamlString(author)}` : "author:",
    interviewee ? `interviewee: ${yamlString(interviewee)}` : "interviewee:",
    summary ? `summary: ${yamlString(summary)}` : "summary:",
    "workflow:",
    "  capture: done",
    "  translation: draft",
    "  proofreading: pending",
    "  published: draft",
    "entities:",
    nestedYamlList("people", people),
    nestedYamlList("works", works),
    nestedYamlList("organizations", organizations),
    "references:",
    `  - id: ${sourceId}`,
    "    type: web_article",
    author ? `    author: ${yamlString(author)}` : "",
    `    year: ${date.slice(0, 4)}`,
    `    title: ${yamlString(title)}`,
    publication ? `    publication: ${yamlString(publication)}` : "",
    sourceUrl ? `    url: ${yamlString(sourceUrl)}` : "",
    `    accessed: ${yamlString(accessed)}`,
    "---",
    ""
  ].filter((line) => line !== "");

  if (summary) {
    lines.push(summary + `{% include citation-ref.html id="${sourceId}" %}`, "");
  }

  if (template === "parallel") {
    lines.push("parallel_items:");
    paragraphs.forEach((paragraph) => {
      lines.push("  - type: paragraph");
      lines.push("    original: |-");
      markdownParagraph(paragraph).split("\n").forEach((line) => lines.push(`      ${line}`));
      lines.push("    translation: |-");
      lines.push("      ");
    });
  } else {
    paragraphs.forEach((paragraph, index) => {
      lines.push(markdownParagraph(paragraph) +
        (index === 0 ? `{% include citation-ref.html id="${sourceId}" %}` : ""), "");
    });
  }

  return {
    markdown: lines.join("\n"),
    filename: `${date}-[网页收录]-${slugify(title)}.md`,
    directory: "_posts",
    paragraphs
  };
}
