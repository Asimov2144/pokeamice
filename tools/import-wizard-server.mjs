#!/usr/bin/env node
import { spawn } from "node:child_process";
/* the same transform the capture tool runs in the browser, so a draft built
   by hand and one built through the API come out identical */
import { buildWebCapture } from "../assets/tools/lib/web-capture.mjs";
import { buildArticleMarkdown } from "../assets/tools/lib/article-markdown.mjs";
import { randomUUID } from "node:crypto";
import { createServer } from "node:http";
import {
  readdir,
  mkdir,
  readFile,
  rename,
  stat,
  writeFile
} from "node:fs/promises";
import {
  basename,
  dirname,
  extname,
  isAbsolute,
  join,
  relative,
  resolve
} from "node:path";

const root = resolve(process.cwd());
const host = "127.0.0.1";
const port = Number(process.env.PORT || 4175);
const selectedImageFolders = new Map();

const mimeTypes = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  /* without this an ES module is served as octet-stream and the browser
     refuses to execute it, which breaks every tool that imports lib/ */
  ".mjs": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".md": "text/markdown; charset=utf-8",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".gif": "image/gif",
  ".webp": "image/webp",
  ".svg": "image/svg+xml"
};

function send(res, status, body, type = "text/plain; charset=utf-8") {
  res.writeHead(status, {
    "Content-Type": type,
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type"
  });
  res.end(body);
}

function sendJson(res, status, payload) {
  send(res, status, `${JSON.stringify(payload, null, 2)}\n`, "application/json; charset=utf-8");
}

async function listImagesInFolder(folder) {
  const results = [];
  const supported = new Set([".png", ".jpg", ".jpeg", ".gif", ".webp", ".tif", ".tiff"]);
  async function walk(current) {
    const entries = await readdir(current, { withFileTypes: true });
    entries.sort((a, b) => a.name.localeCompare(b.name, undefined, { numeric: true }));
    for (const entry of entries) {
      const fullPath = join(current, entry.name);
      if (entry.isDirectory()) {
        await walk(fullPath);
      } else if (entry.isFile() && supported.has(extname(entry.name).toLowerCase())) {
        results.push({
          name: entry.name,
          relativePath: relative(folder, fullPath).replace(/\\/g, "/")
        });
      }
      if (results.length >= 500) return;
    }
  }
  await walk(folder);
  return results;
}

async function pickWindowsImageFolder() {
  if (process.platform !== "win32") throw new Error("本机文件夹选择目前仅支持 Windows");
  const script = [
    "Add-Type -AssemblyName System.Windows.Forms",
    "[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()",
    "$dialog = New-Object System.Windows.Forms.FolderBrowserDialog",
    "$dialog.Description = '选择杂志原图所在文件夹'",
    "$dialog.ShowNewFolderButton = $false",
    "if ($dialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) { Write-Output $dialog.SelectedPath }"
  ].join("; ");
  const result = await runCommand("powershell.exe", ["-NoProfile", "-STA", "-Command", script]);
  return result.stdout.trim();
}

async function prepareImageFolder(requestedPath = "") {
  const folder = requestedPath ? resolve(String(requestedPath)) : await pickWindowsImageFolder();
  if (!folder) return { cancelled: true, files: [] };
  const info = await stat(folder);
  if (!info.isDirectory()) throw new Error("选择的路径不是文件夹");
  const token = randomUUID();
  const files = await listImagesInFolder(folder);
  selectedImageFolders.set(token, folder);
  return {
    cancelled: false,
    token,
    folder,
    folderName: basename(folder),
    files: files.map((file) => ({
      ...file,
      url: `/api/local-image?token=${encodeURIComponent(token)}&path=${encodeURIComponent(file.relativePath)}`
    }))
  };
}

async function resolveSourceImage(pageName) {
  const wanted = basename(String(pageName || "")).toLowerCase();
  if (!wanted) throw new Error("Missing page name");
  const topLevel = await readdir(root, { withFileTypes: true });
  const searchRoots = topLevel
    .filter((entry) => entry.isDirectory() && (/^ocr-output/i.test(entry.name) || entry.name === "ocr-ab-tests"))
    .map((entry) => join(root, entry.name));
  const manifests = [];

  async function walk(dir, depth = 0) {
    if (depth > 4 || manifests.length >= 240) return;
    let entries = [];
    try {
      entries = await readdir(dir, { withFileTypes: true });
    } catch {
      return;
    }
    for (const entry of entries) {
      const file = join(dir, entry.name);
      if (entry.isDirectory()) await walk(file, depth + 1);
      else if (entry.isFile() && entry.name === "region-manifest.json") {
        const info = await stat(file);
        manifests.push({ file, modified: info.mtimeMs });
      }
    }
  }

  for (const dir of searchRoots) await walk(dir);
  manifests.sort((a, b) => b.modified - a.modified);
  for (const manifest of manifests) {
    try {
      const rows = JSON.parse(await readFile(manifest.file, "utf8"));
      const row = rows.find((item) => basename(String(item.page_name || item.source_image || "")).toLowerCase() === wanted);
      if (!row?.source_image) continue;
      const sourceImage = resolve(String(row.source_image));
      const info = await stat(sourceImage);
      if (!info.isFile()) continue;
      const folderData = await prepareImageFolder(dirname(sourceImage));
      return { ...folderData, sourceImage, manifest: displayPath(manifest.file) };
    } catch {}
  }
  return { found: false, files: [] };
}

async function listOcrProjectQueues() {
  const queues = [];
  const ignored = new Set([".git", "node_modules", "vendor", "_site", ".venv-ocr", ".venv-ocr-gpu"]);
  async function walk(dir, depth = 0) {
    if (depth > 6 || queues.length >= 200) return;
    let entries = [];
    try {
      entries = await readdir(dir, { withFileTypes: true });
    } catch {
      return;
    }
    for (const entry of entries) {
      if (entry.isDirectory()) {
        if (!ignored.has(entry.name)) await walk(join(dir, entry.name), depth + 1);
        continue;
      }
      if (!entry.isFile() || entry.name !== "project-queue.json") continue;
      const file = join(dir, entry.name);
      try {
        const data = JSON.parse(await readFile(file, "utf8"));
        const info = await stat(file);
        queues.push({
          path: displayPath(file),
          title: data?.project?.title || basename(dirname(file)),
          outputDir: data?.project?.output_dir || dirname(file),
          sourceFolder: data?.project?.source_folder || "",
          createdAt: data?.created_at || info.mtime.toISOString(),
          modifiedAt: info.mtime.toISOString(),
          summary: data?.summary || {}
        });
      } catch {}
    }
  }
  await walk(root);
  return queues.sort((a, b) => String(b.modifiedAt).localeCompare(String(a.modifiedAt)));
}

async function readOcrProjectQueue(input) {
  const file = resolveProjectPath(input);
  if (basename(file) !== "project-queue.json") throw new Error("只允许读取 project-queue.json");
  const data = JSON.parse(await readFile(file, "utf8"));
  return { path: displayPath(file), queue: data };
}

function selectedImagePath(token, requestedPath) {
  const folder = selectedImageFolder(token);
  const file = resolve(folder, String(requestedPath || ""));
  const relativePath = relative(folder, file);
  if (!relativePath || relativePath.startsWith("..") || isAbsolute(relativePath)) {
    throw new Error("原图路径超出所选文件夹");
  }
  return file;
}

function selectedImageFolder(token) {
  const folder = selectedImageFolders.get(String(token || ""));
  if (!folder) throw new Error("原图文件夹会话已失效，请重新选择文件夹");
  return folder;
}

async function readJson(req, maxBytes = 120 * 1024 * 1024) {
  const chunks = [];
  let total = 0;
  for await (const chunk of req) {
    total += chunk.length;
    if (total > maxBytes) {
      throw new Error("Request body is too large");
    }
    chunks.push(chunk);
  }
  const raw = Buffer.concat(chunks).toString("utf8");
  return raw ? JSON.parse(raw) : {};
}

function safeInsideRoot(file) {
  const resolved = resolve(file);
  if (resolved !== root && !resolved.startsWith(`${root}\\`) && !resolved.startsWith(`${root}/`)) {
    throw new Error(`Refusing path outside project: ${file}`);
  }
  return resolved;
}

function slugify(input) {
  const value = String(input || "")
    .normalize("NFKC")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/&/g, " and ")
    .replace(/[^a-z0-9\u4e00-\u9fff\u3040-\u30ff]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .replace(/-{2,}/g, "-");
  return value || `article-${new Date().toISOString().slice(0, 10)}`;
}

function displayPath(file) {
  return relative(root, file).replace(/\\/g, "/");
}

function resolveProjectPath(input, fallback = "") {
  const value = String(input || fallback || "").trim();
  if (!value) throw new Error("Missing project path");
  return safeInsideRoot(resolve(root, value));
}

function stripTags(value) {
  return String(value).replace(/<[^>]+>/g, "");
}

function decodeEntities(value) {
  return String(value)
    .replace(/&nbsp;/gi, " ")
    .replace(/&amp;/gi, "&")
    .replace(/&lt;/gi, "<")
    .replace(/&gt;/gi, ">")
    .replace(/&quot;/gi, "\"")
    .replace(/&#39;/g, "'");
}

function getAttr(attrs, name) {
  const re = new RegExp(`${name}\\s*=\\s*("([^"]*)"|'([^']*)'|([^\\s"'>]+))`, "i");
  const match = String(attrs).match(re);
  return match ? (match[2] || match[3] || match[4] || "").trim() : "";
}

function encodeMarkdownUrl(value) {
  return String(value)
    .replace(/ /g, "%20")
    .replace(/\(/g, "%28")
    .replace(/\)/g, "%29");
}

function normalizeMarkdown(text) {
  return String(text || "")
    .replace(/\r\n/g, "\n")
    .replace(/\n{3,}/g, "\n\n")
    .replace(/[ \t]+\n/g, "\n")
    .trim();
}

function extractTitleFromHtml(text) {
  const match = String(text).match(/<title[^>]*>([\s\S]*?)<\/title>/i)
    || String(text).match(/<h1[^>]*>([\s\S]*?)<\/h1>/i);
  return match ? decodeEntities(stripTags(match[1]).trim()) : "";
}

function extractTitleFromMarkdown(text) {
  const match = String(text).match(/^#\s+(.+)$/m);
  return match ? match[1].trim() : "";
}

function convertHtmlToMarkdown(html) {
  let text = String(html || "");
  const body = text.match(/<body[^>]*>([\s\S]*?)<\/body>/i);
  if (body) text = body[1];
  text = text.replace(/<!--[\s\S]*?-->/g, "");
  text = text.replace(/<script[\s\S]*?<\/script>/gi, "");
  text = text.replace(/<style[\s\S]*?<\/style>/gi, "");
  text = text.replace(/<figure[^>]*>/gi, "\n\n");
  text = text.replace(/<\/figure>/gi, "\n\n");
  text = text.replace(/<figcaption[^>]*>([\s\S]*?)<\/figcaption>/gi, (_, caption) => `\n\n*${stripTags(decodeEntities(caption)).trim()}*\n\n`);
  text = text.replace(/<img\b([^>]*?)>/gi, (_, attrs) => {
    const src = getAttr(attrs, "src") || getAttr(attrs, "data-src") || getAttr(attrs, "data-original") || getAttr(attrs, "data-lazy-src");
    const alt = getAttr(attrs, "alt") || "";
    return src ? `\n\n![${decodeEntities(alt)}](${encodeMarkdownUrl(decodeEntities(src))})\n\n` : "";
  });
  text = text.replace(/<a\b([^>]*?)>([\s\S]*?)<\/a>/gi, (_, attrs, label) => {
    const href = getAttr(attrs, "href");
    const cleanLabel = stripTags(decodeEntities(label)).trim();
    return href && cleanLabel ? `[${cleanLabel}](${decodeEntities(href)})` : cleanLabel;
  });
  for (let level = 6; level >= 1; level -= 1) {
    const re = new RegExp(`<h${level}[^>]*>([\\s\\S]*?)<\\/h${level}>`, "gi");
    text = text.replace(re, (_, content) => `\n\n${"#".repeat(level)} ${stripTags(decodeEntities(content)).trim()}\n\n`);
  }
  text = text.replace(/<(strong|b)[^>]*>([\s\S]*?)<\/\1>/gi, (_, __, content) => `**${stripTags(decodeEntities(content)).trim()}**`);
  text = text.replace(/<(em|i)[^>]*>([\s\S]*?)<\/\1>/gi, (_, __, content) => `*${stripTags(decodeEntities(content)).trim()}*`);
  text = text.replace(/<br\s*\/?>/gi, "\n");
  text = text.replace(/<\/p>/gi, "\n\n");
  text = text.replace(/<p[^>]*>/gi, "");
  text = text.replace(/<\/(div|section|article|header|footer|blockquote)>/gi, "\n\n");
  text = text.replace(/<(div|section|article|header|footer|blockquote)[^>]*>/gi, "\n\n");
  text = text.replace(/<li[^>]*>/gi, "\n- ");
  text = text.replace(/<\/li>/gi, "");
  text = text.replace(/<\/?(ul|ol)[^>]*>/gi, "\n");
  text = stripTags(text);
  text = decodeEntities(text);
  return normalizeMarkdown(text);
}

function looksLikeHtml(text) {
  return /<\/?[a-z][\s\S]*>/i.test(String(text || ""));
}

function sanitizeFileName(name, fallback = "image") {
  const base = basename(String(name || fallback))
    .replace(/[<>:"/\\|?*\x00-\x1f]/g, "-")
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-+|-+$/g, "");
  return base || fallback;
}

function extFromMime(mime) {
  const type = String(mime || "").split(";")[0].toLowerCase();
  if (type === "image/jpeg") return ".jpg";
  if (type === "image/png") return ".png";
  if (type === "image/gif") return ".gif";
  if (type === "image/webp") return ".webp";
  if (type === "image/svg+xml") return ".svg";
  return ".bin";
}

function parseDataUrl(dataUrl) {
  const match = String(dataUrl || "").match(/^data:([^;,]+)?(;base64)?,([\s\S]*)$/);
  if (!match) throw new Error("Invalid data URL");
  const mime = match[1] || "application/octet-stream";
  const isBase64 = Boolean(match[2]);
  const data = isBase64 ? Buffer.from(match[3], "base64") : Buffer.from(decodeURIComponent(match[3]), "utf8");
  return { mime, data };
}

async function readArticleUrl(url) {
  const response = await fetch(url, {
    headers: {
      "User-Agent": "PokeAmiceImportWizard/1.0",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,text/plain;q=0.8,*/*;q=0.5"
    }
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const html = await response.text();
  return {
    finalUrl: response.url,
    contentType: response.headers.get("content-type") || "",
    title: extractTitleFromHtml(html),
    html
  };
}

function sessionPath(sessionId) {
  if (!/^[a-z0-9-]+$/i.test(String(sessionId || ""))) {
    throw new Error("Invalid session id");
  }
  return safeInsideRoot(join(root, "migration", "import-wizard", sessionId));
}

async function maybeReadMarkdown(file) {
  try {
    return await readFile(file, "utf8");
  } catch {
    return "";
  }
}

async function listMarkdownFiles() {
  const topLevel = await readdir(root, { withFileTypes: true });
  const roots = topLevel
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .filter((name) => /^ocr-output/i.test(name) || name === "migration");
  const files = [];
  const maxFiles = 160;

  async function walk(dir, depth = 0) {
    if (files.length >= maxFiles || depth > 4) return;
    let entries = [];
    try {
      entries = await readdir(dir, { withFileTypes: true });
    } catch {
      return;
    }
    for (const entry of entries) {
      if (files.length >= maxFiles) break;
      const file = join(dir, entry.name);
      if (entry.isDirectory()) {
        await walk(file, depth + 1);
      } else if (/\.(md|markdown|txt)$/i.test(entry.name)) {
        const info = await stat(file);
        files.push({
          path: displayPath(file),
          name: entry.name,
          folder: displayPath(dirname(file)),
          sizeKB: Math.round(info.size / 102.4) / 10,
          modified: info.mtime.toISOString()
        });
      }
    }
  }

  for (const dir of roots) {
    await walk(join(root, dir));
  }
  files.sort((a, b) => b.modified.localeCompare(a.modified));
  return files;
}

async function writeUploadedImages(sessionDir, uploads) {
  const uploadDir = join(sessionDir, "uploads");
  await mkdir(uploadDir, { recursive: true });
  const refs = [];
  const seen = new Set();
  for (let i = 0; i < (uploads || []).length; i += 1) {
    const item = uploads[i];
    if (!item || !item.dataUrl) continue;
    const parsed = parseDataUrl(item.dataUrl);
    const ext = extname(item.name || "") || extFromMime(parsed.mime);
    const stem = sanitizeFileName((item.name || `image-${i + 1}`).replace(new RegExp(`${ext}$`, "i"), ""), `image-${i + 1}`);
    let fileName = `${String(i + 1).padStart(2, "0")}-${stem}${ext}`;
    let counter = 2;
    while (seen.has(fileName.toLowerCase())) {
      fileName = `${String(i + 1).padStart(2, "0")}-${stem}-${counter}${ext}`;
      counter += 1;
    }
    seen.add(fileName.toLowerCase());
    await writeFile(join(uploadDir, fileName), parsed.data);
    refs.push({
      name: item.name || fileName,
      fileName,
      mime: parsed.mime,
      size: parsed.data.length,
      markdown: `![${item.alt || item.name || `图 ${i + 1}`}](uploads/${encodeMarkdownUrl(fileName)})`
    });
  }
  return refs;
}

function appendImageSection(markdown, uploadedRefs) {
  if (!uploadedRefs.length) return markdown;
  const imageBlock = uploadedRefs
    .map((item) => `${item.markdown}\n\n> 图片说明 / OCR / 译文待补充`)
    .join("\n\n");
  return normalizeMarkdown(`${markdown}\n\n## 图片素材\n\n${imageBlock}`);
}

async function stageImport(body) {
  const sessionId = `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
  const sessionDir = sessionPath(sessionId);
  await mkdir(sessionDir, { recursive: true });

  const pasted = body.html || body.markdown || body.text || "";
  const sourceIsHtml = body.html ? true : (body.mode === "html" || looksLikeHtml(pasted));
  let markdown = sourceIsHtml ? convertHtmlToMarkdown(pasted) : normalizeMarkdown(pasted);
  const uploaded = await writeUploadedImages(sessionDir, body.uploads || []);
  markdown = appendImageSection(markdown, uploaded);

  const title = body.title
    || (sourceIsHtml ? extractTitleFromHtml(pasted) : extractTitleFromMarkdown(markdown))
    || "未命名文章";
  const slug = slugify(body.slug || title);
  const inputFile = join(sessionDir, "article.md");
  await writeFile(inputFile, `${markdown}\n`, "utf8");
  await writeFile(join(sessionDir, "session.json"), `${JSON.stringify({
    sessionId,
    title,
    slug,
    sourceUrl: body.sourceUrl || "",
    sourceTitle: body.sourceTitle || "",
    uploads: uploaded
  }, null, 2)}\n`, "utf8");

  return {
    sessionId,
    title,
    slug,
    markdown,
    inputFile: relative(root, inputFile),
    uploads: uploaded.map((item) => ({
      name: item.name,
      fileName: item.fileName,
      sizeKB: Math.round(item.size / 102.4) / 10
    }))
  };
}

function runCommand(command, args) {
  return new Promise((resolvePromise, rejectPromise) => {
    const child = spawn(command, args, {
      cwd: root,
      windowsHide: true
    });
    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (chunk) => { stdout += chunk.toString(); });
    child.stderr.on("data", (chunk) => { stderr += chunk.toString(); });
    child.on("error", rejectPromise);
    child.on("close", (code) => {
      if (code !== 0) {
        const error = new Error(stderr || stdout || `Command failed with code ${code}`);
        error.stdout = stdout;
        error.stderr = stderr;
        rejectPromise(error);
        return;
      }
      resolvePromise({ stdout, stderr });
    });
  });
}

async function publishImport(body) {
  const sessionDir = sessionPath(body.sessionId);
  const inputFile = join(sessionDir, "article.md");
  await writeFile(inputFile, `${normalizeMarkdown(body.markdown)}\n`, "utf8");

  const args = [
    "tools/migrate-article-images.mjs",
    "--input", inputFile,
    "--title", body.title || "未命名文章",
    "--date", body.date || new Date().toISOString().slice(0, 10),
    "--slug", slugify(body.slug || body.title),
    "--categories", body.categories || "整理"
  ];
  if (body.tags) args.push("--tags", body.tags);
  if (body.sourceTitle) args.push("--source-title", body.sourceTitle);
  if (body.sourceUrl) args.push("--source-url", body.sourceUrl);
  if (body.maxWidth) args.push("--max-width", String(body.maxWidth));
  if (body.quality) args.push("--quality", String(body.quality));
  if (body.format) args.push("--format", body.format);
  if (body.outputMode === "draft") args.push("--draft");

  const result = await runCommand(process.execPath, args);
  let report = null;
  try {
    report = JSON.parse(result.stdout);
  } catch {
    report = { stdout: result.stdout };
  }
  return {
    ok: true,
    mode: body.outputMode === "draft" ? "draft" : "post",
    report,
    stderr: result.stderr
  };
}

function bestOcrMarkdownPath(outDir) {
  return [
    join(outDir, "regions-ocr-llm.md"),
    join(outDir, "regions-ocr.md")
  ];
}

const DEFAULT_LAYOUT_MODEL = "qwen3.7-plus";
const PAGE_ORIENTATION_THRESHOLD = 0.72;

function cleanModelJson(text) {
  let value = String(text || "").trim();
  value = value.replace(/^```(?:json)?\s*/i, "").replace(/\s*```$/i, "").trim();
  const first = value.indexOf("{");
  const last = value.lastIndexOf("}");
  if (first >= 0 && last > first) value = value.slice(first, last + 1);
  return value;
}

function layoutRegionType(type) {
  const value = String(type || "").toLowerCase();
  if (["image", "photo", "illustration", "screenshot", "figure"].includes(value)) return "image";
  if (value === "caption") return "caption";
  if (["callout", "footer"].includes(value)) return "note";
  return "body";
}

function normalizeLayoutResponse(raw, width, height) {
  const layout = typeof raw === "string" ? JSON.parse(cleanModelJson(raw)) : raw;
  const regions = Array.isArray(layout?.regions) ? layout.regions : [];
  return {
    pageType: layout?.page_type || "mixed",
    readingDirection: layout?.reading_direction || "left_to_right",
    regions: regions
      .map((region, index) => {
        const bbox = Array.isArray(region?.bbox) ? region.bbox.map(Number) : [];
        if (bbox.length !== 4 || bbox.some((value) => !Number.isFinite(value))) return null;
        const [x1, y1, x2, y2] = bbox;
        const left = Math.round(Math.max(0, Math.min(1000, Math.min(x1, x2))) * width / 1000);
        const top = Math.round(Math.max(0, Math.min(1000, Math.min(y1, y2))) * height / 1000);
        const right = Math.round(Math.max(0, Math.min(1000, Math.max(x1, x2))) * width / 1000);
        const bottom = Math.round(Math.max(0, Math.min(1000, Math.max(y1, y2))) * height / 1000);
        if (right - left < 16 || bottom - top < 16) return null;
        return {
          id: `qwen-${region.id || `r${index + 1}`}`,
          type: layoutRegionType(region.type),
          box: [left, top, right, bottom],
          order: Number(region.order) || index + 1,
          angle: Number.isFinite(Number(region.angle)) ? Number(region.angle) : 0,
          writingDirection: ["horizontal", "vertical"].includes(region.writing_direction) ? region.writing_direction : "auto",
          confidence: Number.isFinite(Number(region.confidence)) ? Number(region.confidence) : null,
          contentMix: ["text_only", "image_only", "mixed", "uncertain"].includes(region.content_mix) ? region.content_mix : "",
          reviewFlags: Array.isArray(region.review_flags) ? region.review_flags.map(String) : [],
          sourceType: region.type || "body",
          imageRef: region.caption_for ? `qwen-${region.caption_for}` : "",
          note: region.note || "Qwen 自动分区建议"
        };
      })
      .filter(Boolean)
      .sort((a, b) => a.order - b.order)
  };
}

function layoutQualityIssues(layout, width, height) {
  const regions = Array.isArray(layout?.regions) ? layout.regions : [];
  const textRegions = regions.filter((region) => region.type !== "image");
  const verticalBodies = regions.filter((region) =>
    region.sourceType === "interview_body" && region.writingDirection === "vertical"
  );
  const narrowTallBodies = verticalBodies.filter((region) => {
    const [left, top, right, bottom] = region.box || [];
    return (right - left) / Math.max(width, 1) < 0.045 && (bottom - top) / Math.max(height, 1) > 0.18;
  });
  const issues = [];
  if (textRegions.length > 32) issues.push(`文字領域が多すぎます（${textRegions.length}個）`);
  if (narrowTallBodies.length >= 3) {
    issues.push(
      `縦書き本文を1列ずつ切っています（${narrowTallBodies.length}個）。` +
      "横罫線・大きな横空白ごとに段を分け、同じ段の連続2〜6列を1領域にまとめてください"
    );
  }
  return issues;
}

function normalizePageOrientation(raw) {
  const value = typeof raw === "string" ? JSON.parse(cleanModelJson(raw)) : raw;
  const rotation = Number(value?.rotation_cw);
  const confidence = Math.max(0, Math.min(1, Number(value?.confidence) || 0));
  if (![0, 90, 180, 270].includes(rotation)) throw new Error("页面方向返回了无效角度");
  return {
    rotation: confidence >= PAGE_ORIENTATION_THRESHOLD ? rotation : 0,
    suggestedRotation: rotation,
    confidence,
    applied: confidence >= PAGE_ORIENTATION_THRESHOLD && rotation !== 0,
    uncertain: confidence < PAGE_ORIENTATION_THRESHOLD,
    hasReadableText: value?.has_readable_text !== false,
    reason: String(value?.reason || "").slice(0, 80),
    threshold: PAGE_ORIENTATION_THRESHOLD
  };
}

async function requestQwenPageOrientation(page) {
  const apiKey = process.env.VLM_OCR_API_KEY || process.env.DASHSCOPE_API_KEY || process.env.QWEN_API_KEY || "";
  if (!apiKey) throw new Error("未找到 Qwen API Key");
  const apiUrl = (process.env.VLM_OCR_API_URL || "https://dashscope.aliyuncs.com/compatible-mode/v1").replace(/\/+$/, "");
  const prompt = await readFile(join(root, "tools", "prompts", "magazine-page-orientation-ja.txt"), "utf8");
  const payload = {
    model: process.env.VLM_LAYOUT_MODEL || DEFAULT_LAYOUT_MODEL,
    messages: [{ role: "user", content: [
      { type: "image_url", image_url: { url: page.dataUrl, detail: "high" } },
      { type: "text", text: prompt }
    ] }],
    temperature: 0,
    max_tokens: 256,
    enable_thinking: false
  };
  const response = await fetch(`${apiUrl}/chat/completions`, {
    method: "POST",
    headers: { Authorization: `Bearer ${apiKey}`, "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    signal: AbortSignal.timeout(Number(process.env.VLM_ORIENTATION_TIMEOUT_MS || 120000))
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data?.error?.message || `页面方向请求失败（${response.status}）`);
  const content = data?.choices?.[0]?.message?.content;
  if (!content) throw new Error("页面方向返回为空");
  return normalizePageOrientation(content);
}

async function analyzePageOrientation(body) {
  const pages = Array.isArray(body.pages) ? body.pages : [];
  if (!pages.length || pages.length > 4) throw new Error("页面方向检测一次支持 1–4 页");
  const results = [];
  for (const page of pages) {
    if (!page?.dataUrl) throw new Error(`图片数据不完整：${page?.name || "未命名图片"}`);
    results.push({ name: page.name || "未命名图片", ...(await requestQwenPageOrientation(page)) });
  }
  return { model: process.env.VLM_LAYOUT_MODEL || DEFAULT_LAYOUT_MODEL, pages: results };
}

async function requestQwenLayout(page) {
  const apiKey = process.env.VLM_OCR_API_KEY || process.env.DASHSCOPE_API_KEY || process.env.QWEN_API_KEY || "";
  if (!apiKey) throw new Error("未找到 VLM_OCR_API_KEY / DASHSCOPE_API_KEY，请先配置 Qwen API Key");
  const apiUrl = (process.env.VLM_OCR_API_URL || "https://dashscope.aliyuncs.com/compatible-mode/v1").replace(/\/+$/, "");
  const prompt = await readFile(join(root, "tools", "prompts", "magazine-layout-segmentation-strict-ja.txt"), "utf8");
  let parseError = null;
  for (let attempt = 0; attempt < 3; attempt += 1) {
    const retryInstruction = attempt
      ? `\n\n前回の応答は品質検査に失敗しました：${parseError?.message || "JSON解析失敗"}。` +
        "省略記号やコメントを使わず、上記の問題を修正した完全なJSONを最初から最後まで出力してください。"
      : "";
    const payload = {
      model: process.env.VLM_LAYOUT_MODEL || DEFAULT_LAYOUT_MODEL,
      messages: [{
        role: "user",
        content: [
          { type: "image_url", image_url: { url: page.dataUrl, detail: "high" } },
          { type: "text", text: `${prompt}${retryInstruction}` }
        ]
      }],
      temperature: 0,
      max_tokens: 4096,
      enable_thinking: false
    };
    const response = await fetch(`${apiUrl}/chat/completions`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(Number(process.env.VLM_LAYOUT_TIMEOUT_MS || 300000))
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data?.error?.message || `Qwen 布局请求失败（${response.status}）`);
    const content = data?.choices?.[0]?.message?.content;
    if (!content) throw new Error("Qwen 布局返回为空");
    try {
      const normalized = normalizeLayoutResponse(content, page.width, page.height);
      const issues = layoutQualityIssues(normalized, page.width, page.height);
      if (issues.length) throw new Error(issues.join("；"));
      return normalized;
    } catch (error) {
      parseError = error;
    }
  }
  throw new Error(`Qwen 布局连续三次未通过结构检查：${parseError?.message || parseError}`);
}

async function analyzeLayout(body) {
  const pages = Array.isArray(body.pages) ? body.pages : [];
  if (!pages.length) throw new Error("Missing pages");
  if (pages.length > 4) throw new Error("一次最多分析 4 页，请分批运行");
  const results = [];
  for (const page of pages) {
    if (!page?.dataUrl || !page?.width || !page?.height) throw new Error(`图片数据不完整：${page?.name || "未命名图片"}`);
    const layout = await requestQwenLayout(page);
    results.push({
      name: page.name || "未命名图片",
      width: Number(page.width),
      height: Number(page.height),
      ...layout
    });
  }
  return { model: process.env.VLM_LAYOUT_MODEL || DEFAULT_LAYOUT_MODEL, pages: results };
}

async function runOcrImport(body) {
  const engine = body.engine === "paddle" ? "paddle" : "vlm";
  const sessionDir = body.sessionId ? sessionPath(body.sessionId) : "";
  const imageDir = body.imageDir
    ? resolveProjectPath(body.imageDir)
    : sessionDir
      ? join(sessionDir, "uploads")
      : "";
  if (!imageDir) throw new Error("Missing image directory");

  const annotationJson = resolveProjectPath(body.annotationJson || "magazine-regions.json");
  const outDir = resolveProjectPath(
    body.out || `ocr-output-import-wizard/${body.sessionId || Date.now().toString(36)}`
  );
  const script = engine === "paddle"
    ? join(root, "tools", "run-paddle-region-ocr.ps1")
    : join(root, "tools", "run-region-vlm-api-ocr.ps1");
  const args = [
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-File", script,
    "-AnnotationJson", annotationJson,
    "-ImageDir", imageDir,
    "-Out", outDir,
    "-SkipExisting"
  ];
  if (engine === "vlm") {
    args.push("-PromptFile", resolveProjectPath(body.promptFile || "tools/prompts/pokemon-magazine-ja-ocr.txt"));
    args.push("-ContinueOnError");
    if (body.model) args.push("-Model", String(body.model));
  }
  if (body.deepSeek) args.push("-DeepSeek");

  const result = await runCommand("powershell.exe", args);
  let markdown = "";
  let markdownFile = "";
  for (const file of bestOcrMarkdownPath(outDir)) {
    markdown = await maybeReadMarkdown(file);
    if (markdown) {
      markdownFile = file;
      break;
    }
  }
  return {
    ok: true,
    engine,
    out: displayPath(outDir),
    markdownFile: markdownFile ? displayPath(markdownFile) : "",
    markdown,
    stdout: result.stdout,
    stderr: result.stderr
  };
}

async function rerunSingleRegionOcr(body) {
  const pageName = basename(String(body.pageName || body.page_name || ""));
  if (!pageName) throw new Error("缺少原图文件名");
  let sourceImage = "";
  if (body.sourceImage) {
    try {
      const explicit = resolve(String(body.sourceImage));
      if (basename(explicit).toLowerCase() === pageName.toLowerCase() && (await stat(explicit)).isFile()) sourceImage = explicit;
    } catch {}
  }
  if (body.sourceFolderToken) {
    try {
      sourceImage = selectedImagePath(body.sourceFolderToken, pageName);
    } catch {}
  }
  if (!sourceImage) {
    const resolvedSource = await resolveSourceImage(pageName);
    sourceImage = resolvedSource.sourceImage || "";
  }
  if (!sourceImage) throw new Error(`找不到 ${pageName} 的原图，请先选择校对原图文件夹`);
  const sourceInfo = await stat(sourceImage);
  if (!sourceInfo.isFile()) throw new Error("原图路径不是文件");

  const box = Array.isArray(body.scanBox) ? body.scanBox.map(Number) : [];
  if (box.length !== 4 || box.some((value) => !Number.isFinite(value))) throw new Error("当前选框坐标无效");
  const [rawX1, rawY1, rawX2, rawY2] = box;
  const normalizedBox = [Math.min(rawX1, rawX2), Math.min(rawY1, rawY2), Math.max(rawX1, rawX2), Math.max(rawY1, rawY2)].map(Math.round);
  if (normalizedBox[2] - normalizedBox[0] < 12 || normalizedBox[3] - normalizedBox[1] < 12) throw new Error("当前选框太小");

  const runId = `region-rerun-${Date.now().toString(36)}-${randomUUID().slice(0, 8)}`;
  const runDir = sessionPath(runId);
  const outDir = join(runDir, "output");
  await mkdir(runDir, { recursive: true });
  const annotationFile = join(runDir, "annotation.json");
  const regionId = String(body.regionId || "rerun-region").replace(/[^A-Za-z0-9_-]/g, "-");
  const annotation = {
    version: 1,
    pages: [{
      name: pageName,
      regions: [{
        id: regionId,
        type: String(body.regionType || "body"),
        speaker: String(body.speaker || "返工区域"),
        order: 1,
        box: normalizedBox,
        angle: Number(body.angle || 0),
        writingDirection: ["horizontal", "vertical"].includes(body.writingDirection) ? body.writingDirection : "auto",
        exclusions: Array.isArray(body.exclusions) ? body.exclusions : []
      }]
    }]
  };
  await writeFile(annotationFile, JSON.stringify(annotation, null, 2), "utf8");

  const args = [
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-File", join(root, "tools", "run-region-vlm-api-ocr.ps1"),
    "-AnnotationJson", annotationFile,
    "-ImageDir", dirname(sourceImage),
    "-Out", outDir,
    "-Model", String(body.model || "qwen-vl-ocr-latest"),
    "-CropMaxPixels", "900000",
    "-MaxTokens", "1024",
    "-Retries", "2",
    "-RetryDelaySeconds", "4",
    "-PromptFile", join(root, "tools", "prompts", "pokemon-magazine-ja-ocr.txt"),
    "-ContinueOnError",
    "-SkipQueue"
  ];
  const result = await runCommand("powershell.exe", args);
  const ocrDir = join(outDir, "ocr-vlm-api");
  const files = await readdir(ocrDir, { withFileTypes: true });
  const textFile = files.find((entry) => entry.isFile() && entry.name.toLowerCase().endsWith(".txt") && !entry.name.startsWith("_"));
  if (!textFile) throw new Error("单区 OCR 没有返回文字文件");
  const text = (await readFile(join(ocrDir, textFile.name), "utf8")).trim();
  let ocrResult = {};
  try {
    ocrResult = JSON.parse(await readFile(join(ocrDir, textFile.name.replace(/\.txt$/i, ".json")), "utf8"));
  } catch {}
  return {
    ok: true,
    text,
    sourceImage,
    scanBox: normalizedBox,
    runFolder: displayPath(runDir),
    ocrResult,
    stdout: result.stdout,
    stderr: result.stderr
  };
}

function pythonExecutable() {
  const candidates = [
    join(root, ".venv-ocr", "Scripts", "python.exe"),
    join(root, ".venv-ocr-gpu", "Scripts", "python.exe")
  ];
  return candidates[0];
}

async function prepareScanPages(body) {
  const sourceFolder = selectedImageFolder(body.sourceFolderToken);
  const sourceInfo = await stat(sourceFolder);
  if (!sourceInfo.isDirectory()) throw new Error("原图文件夹不存在或不可读取");

  const binding = body.binding === "left" ? "left" : "right";
  const vlm = ["auto", "always", "never"].includes(body.vlm) ? body.vlm : "auto";
  const outerTrim = String(body.outerTrim || "off").trim().toLowerCase();
  if (!/^(off|auto|\d+(?:\.\d+)?%?)$/.test(outerTrim)) {
    throw new Error("外缘裁切只接受关闭、自动、像素数或百分比");
  }
  const limit = Math.max(0, Math.min(500, Number.parseInt(body.limit || 0, 10) || 0));
  const model = String(body.model || DEFAULT_LAYOUT_MODEL).trim().slice(0, 100) || DEFAULT_LAYOUT_MODEL;
  const sourceSlug = slugify(basename(sourceFolder)).slice(0, 64);
  const jobId = `${sourceSlug}-${Date.now().toString(36)}-${randomUUID().slice(0, 6)}`;
  const outDir = safeInsideRoot(join(root, "scan-prepared", jobId));
  await mkdir(outDir, { recursive: true });

  const args = [
    join(root, "tools", "prepare_scan_pages.py"),
    "--source", sourceFolder,
    "--out", outDir,
    "--vlm", vlm,
    "--model", model,
    "--binding", binding,
    "--profiles", "archive,web",
    "--outer-trim", outerTrim,
  ];
  if (body.noTone) args.push("--no-tone");
  if (body.noStraighten) args.push("--no-straighten");
  if (limit) args.push("--limit", String(limit));

  const result = await runCommand(pythonExecutable(), args);
  const manifestFile = join(outDir, "scan-manifest.json");
  const manifest = JSON.parse(await readFile(manifestFile, "utf8"));
  if (!Number(manifest.summary?.processed_count || 0)) {
    throw new Error("扫描预处理没有生成可用页面，请查看清单中的失败记录");
  }
  const archiveFolder = join(outDir, "archive");
  const webFolder = join(outDir, "web");
  const archiveSelection = await prepareImageFolder(archiveFolder);
  const webSelection = await prepareImageFolder(webFolder);
  archiveSelection.folderName = `${basename(sourceFolder)}-prepared`;
  webSelection.folderName = `${basename(sourceFolder)}-preview`;
  const reviewPages = (manifest.pages || [])
    .filter((page) => page.workflow_status === "review")
    .map((page) => ({
      source: page.source,
      reasons: page.review_reasons || [],
      decision: page.decision || {},
    }));

  return {
    ok: true,
    jobId,
    outputDir: displayPath(outDir),
    manifestPath: displayPath(manifestFile),
    summary: manifest.summary || {},
    reviewPages,
    errors: manifest.errors || [],
    archiveSelection,
    webSelection,
    stdout: result.stdout,
  };
}

async function evaluateOcrReplacement(oldText, firstText, secondText, proposal) {
  const runId = `rework-eval-${Date.now().toString(36)}-${randomUUID().slice(0, 8)}`;
  const runDir = sessionPath(runId);
  await mkdir(runDir, { recursive: true });
  const input = join(runDir, "evaluation.json");
  await writeFile(input, `${JSON.stringify({ old_text: oldText, first_text: firstText, second_text: secondText, proposal }, null, 2)}\n`, "utf8");
  const result = await runCommand(pythonExecutable(), [join(root, "tools", "ocr_rework_loop.py"), "--evaluate", input]);
  return JSON.parse(result.stdout.trim());
}

async function targetedOcrPass(item, proposal) {
  const parts = [...(proposal.parts || [])].sort((a, b) => Number(a.reading_order || 0) - Number(b.reading_order || 0));
  const results = [];
  for (const part of parts) {
    results.push(await rerunSingleRegionOcr({
      pageName: item.page_name,
      sourceImage: item.segment?.source_image,
      scanBox: part.scan_box,
      regionId: `${item.region_id || "region"}-${part.id || results.length + 1}`,
      regionType: item.segment?.region_type || "body",
      speaker: item.speaker,
      angle: item.segment?.angle || 0,
      writingDirection: proposal.writing_direction || item.segment?.writing_direction || "auto",
      exclusions: item.segment?.exclusions || [],
      model: "qwen-vl-ocr-latest"
    }));
  }
  return {
    text: results.map((result) => result.text).filter(Boolean).join("\n"),
    parts: results.map((result, index) => ({
      id: parts[index]?.id || `part-${index + 1}`,
      scanBox: result.scanBox,
      text: result.text,
      warnings: result.ocrResult?.quality_warnings || [],
      preprocessing: result.ocrResult?.preprocessing || {},
      postprocessing: result.ocrResult?.postprocessing || {},
      runFolder: result.runFolder
    }))
  };
}

function candidateMetadataGates(pass, proposal) {
  const gates = [];
  for (const part of pass.parts || []) {
    if ((part.warnings || []).length) gates.push("candidate_metadata_warning");
    if (part.preprocessing?.too_many_columns) gates.push("column_split_still_too_large");
    const lengths = part.postprocessing?.column_text_lengths_visual_left_to_right || [];
    if (lengths.some((value) => Number(value || 0) <= 0)) gates.push("candidate_column_empty");
    const expected = proposal.writing_direction;
    const actual = part.preprocessing?.effective_direction;
    const orientation = part.preprocessing?.orientation || {};
    if (expected && actual && expected !== actual && Number(orientation.confidence || 0) >= 0.6) gates.push("candidate_direction_conflict");
  }
  return [...new Set(gates)];
}

function applyCandidateMetadataGates(evaluation, first, second, proposal) {
  const extra = [...new Set([...candidateMetadataGates(first, proposal), ...candidateMetadataGates(second, proposal)])];
  const chosen = String(evaluation.chosen_text || "").replace(/\s+/g, "");
  const belongsToPass = [first.text, second.text].some((text) => String(text || "").replace(/\s+/g, "") === chosen);
  if (!belongsToPass) extra.push("candidate_transfer_mismatch");
  if (extra.length) {
    evaluation.gates = [...new Set([...(evaluation.gates || []), ...extra])];
    evaluation.reliable = false;
    evaluation.decision = "human_review";
    evaluation.confidence = Math.max(0, Number(evaluation.confidence || 0) - 0.15);
    evaluation.explanation = "文字本身通过检查，但 OCR 结构元数据仍有异常，已转交人工确认。";
  }
  return evaluation;
}

async function saveReworkOverride(queueFile, queue, item, chosenText, evaluation, source = "automatic") {
  const outputDir = safeInsideRoot(queue.project?.output_dir || dirname(queueFile));
  const overrideFile = join(outputDir, "ocr-rework-overrides.json");
  let overrides = {};
  try { overrides = JSON.parse(await readFile(overrideFile, "utf8")); } catch {}
  overrides[item.crop_name] = {
    text: chosenText,
    accepted_at: new Date().toISOString(),
    source,
    confidence: evaluation?.confidence ?? null,
    previous_text: item.segment?.original || "",
    evaluation: evaluation || {},
    resolved_reason_codes: (item.reasons || []).map((reason) => reason.code).filter(Boolean)
  };
  await writeFile(overrideFile, `${JSON.stringify(overrides, null, 2)}\n`, "utf8");
  item.segment.original = chosenText;
  item.status = "ready";
  item.route = "translation";
  item.resolved_reasons = item.reasons || [];
  item.reasons = [];
  item.rework = { ...(item.rework || {}), state: source === "automatic" ? "auto_replaced" : "manually_accepted", accepted_at: new Date().toISOString() };
  queue.summary = queue.summary || {};
  queue.summary.ready = (queue.regions || []).filter((region) => region.status === "ready").length;
  queue.summary.review = (queue.regions || []).filter((region) => region.status === "review").length;
  queue.summary.auto_replaced = (queue.regions || []).filter((region) => region.rework?.state === "auto_replaced").length;
  queue.summary.reason_counts = (queue.regions || []).flatMap((region) => region.reasons || []).reduce((counts, reason) => {
    const code = reason.code || "unknown";
    counts[code] = (counts[code] || 0) + 1;
    return counts;
  }, {});
  await writeFile(queueFile, `${JSON.stringify(queue, null, 2)}\n`, "utf8");
}

async function runOcrRework(body) {
  const queueFile = resolveProjectPath(body.path);
  if (basename(queueFile) !== "project-queue.json") throw new Error("只允许返工项目队列中的区域");
  const queue = JSON.parse(await readFile(queueFile, "utf8"));
  const item = (queue.regions || []).find((region) => region.key === body.key);
  if (!item) throw new Error("项目队列中找不到这个区域");
  const proposal = item.repair_proposal;
  if (!proposal?.can_run) throw new Error(proposal?.detail || "这个区域需要先人工调整选框");

  const oldText = item.segment?.original || "";
  const first = await targetedOcrPass(item, proposal);
  const second = await targetedOcrPass(item, proposal);
  const evaluation = applyCandidateMetadataGates(await evaluateOcrReplacement(oldText, first.text, second.text, proposal), first, second, proposal);
  item.rework = {
    state: evaluation.reliable ? "auto_replaced" : "awaiting_human",
    attempted_at: new Date().toISOString(),
    proposal,
    old_text: oldText,
    first,
    second,
    evaluation
  };
  if (evaluation.reliable) {
    await saveReworkOverride(queueFile, queue, item, evaluation.chosen_text, evaluation, "automatic");
  } else {
    await writeFile(queueFile, `${JSON.stringify(queue, null, 2)}\n`, "utf8");
  }
  return { ok: true, item, evaluation, automaticallyReplaced: evaluation.reliable };
}

async function acceptOcrRework(body) {
  const queueFile = resolveProjectPath(body.path);
  if (basename(queueFile) !== "project-queue.json") throw new Error("只允许修改项目队列");
  const queue = JSON.parse(await readFile(queueFile, "utf8"));
  const item = (queue.regions || []).find((region) => region.key === body.key);
  if (!item?.rework?.evaluation?.chosen_text) throw new Error("没有可接受的返工候选");
  await saveReworkOverride(queueFile, queue, item, item.rework.evaluation.chosen_text, item.rework.evaluation, "human");
  return { ok: true, item };
}

function resolveWorkbenchAsset(value) {
  const raw = String(value || "").trim();
  if (!raw) return "";
  if (isAbsolute(raw)) return safeInsideRoot(raw);
  return safeInsideRoot(resolve(root, raw.replace(/^[/\\]+/, "")));
}

async function exportWorkbenchWordPress(body) {
  const segments = Array.isArray(body.segments) ? body.segments.slice(0, 500) : [];
  if (!segments.length) throw new Error("工作台里没有可导出的段落");
  const pageName = String(body.pageName || segments.find((item) => item.pageName)?.pageName || "");
  let sourceImage = "";
  if (body.sourceFolderToken && (body.sourceRelativePath || pageName)) {
    sourceImage = selectedImagePath(body.sourceFolderToken, body.sourceRelativePath || basename(pageName));
  } else if (body.sourceImage) {
    const candidate = String(body.sourceImage);
    if (isAbsolute(candidate)) {
      throw new Error("请先在工作台选择原图文件夹，确保导出只读取已授权的扫描图");
    }
    sourceImage = resolveWorkbenchAsset(candidate);
  }
  if (!sourceImage) throw new Error("找不到原始扫描图，请先选择原图文件夹");
  const sourceInfo = await stat(sourceImage);
  if (!sourceInfo.isFile()) throw new Error("原始扫描图不是有效文件");

  const resolvedSegments = [];
  for (const segment of segments) {
    const next = { ...segment };
    if (next.kind === "image" && next.imagePath) {
      try {
        next.resolvedImagePath = resolveWorkbenchAsset(next.imagePath);
      } catch {
        next.resolvedImagePath = "";
      }
    }
    resolvedSegments.push(next);
  }
  const exportRoot = safeInsideRoot(join(root, "automation-tests", "workbench-wordpress-exports"));
  await mkdir(exportRoot, { recursive: true });
  const baseSlug = slugify(body.meta?.title || "ocr-wordpress-case").slice(0, 72);
  const exportId = `${baseSlug}-${Date.now().toString(36)}-${randomUUID().slice(0, 6)}`;
  const outDir = safeInsideRoot(join(exportRoot, exportId));
  const requestDir = sessionPath(`wordpress-${Date.now().toString(36)}-${randomUUID().slice(0, 8)}`);
  await mkdir(requestDir, { recursive: true });
  const payloadFile = join(requestDir, "workbench-export.json");
  const payload = {
    meta: body.meta || {},
    workflow: {
      sourceQueue: String(body.workflow?.sourceQueue || ""),
      projectOutputDir: String(body.workflow?.projectOutputDir || ""),
      exportedAt: new Date().toISOString()
    },
    resolvedSourceImage: sourceImage,
    segments: resolvedSegments
  };
  await writeFile(payloadFile, `${JSON.stringify(payload, null, 2)}\n`, "utf8");
  const result = await runCommand(pythonExecutable(), [
    join(root, "tools", "export_workbench_wordpress_case.py"),
    "--payload", payloadFile,
    "--out", outDir
  ]);
  const lines = result.stdout.trim().split(/\r?\n/).filter(Boolean);
  const report = JSON.parse(lines.at(-1) || "{}");
  const previewPath = displayPath(join(outDir, "public", "index.html"));
  const zipPath = `${displayPath(outDir)}.zip`;
  return {
    ok: true,
    exportId,
    outputDir: displayPath(outDir),
    previewPath,
    previewUrl: `/${previewPath}`,
    zipPath,
    zipUrl: `/${zipPath}`,
    wordpressPath: displayPath(join(outDir, "public", "wordpress-paste.html")),
    qaPath: displayPath(join(outDir, "docs", "qa-report.md")),
    issues: report.issues || [],
    stats: report.stats || {}
  };
}

async function handleApi(req, res, requestUrl) {
  if (req.method === "OPTIONS") {
    send(res, 204, "");
    return true;
  }
  if (requestUrl.pathname === "/api/read-url" && req.method === "POST") {
    const body = await readJson(req);
    if (!body.url || !/^https?:\/\//i.test(body.url)) {
      sendJson(res, 400, { error: "Missing http(s) url" });
      return true;
    }
    sendJson(res, 200, await readArticleUrl(body.url));
    return true;
  }
  if (requestUrl.pathname === "/api/select-image-folder" && req.method === "POST") {
    const body = await readJson(req);
    sendJson(res, 200, await prepareImageFolder(body.path || ""));
    return true;
  }
  if (requestUrl.pathname === "/api/resolve-source-image" && req.method === "POST") {
    const body = await readJson(req);
    sendJson(res, 200, await resolveSourceImage(body.pageName || body.page_name || ""));
    return true;
  }
  if (requestUrl.pathname === "/api/prepare-scan-pages" && req.method === "POST") {
    const body = await readJson(req);
    sendJson(res, 200, await maybeAsync("/api/prepare-scan-pages", body, () => prepareScanPages(body)));
    return true;
  }
  if (requestUrl.pathname === "/api/local-image" && req.method === "GET") {
    const file = selectedImagePath(requestUrl.searchParams.get("token"), requestUrl.searchParams.get("path"));
    const data = await readFile(file);
    send(res, 200, data, mimeTypes[extname(file).toLowerCase()] || "application/octet-stream");
    return true;
  }
  if (requestUrl.pathname === "/api/read-url" && req.method === "GET") {
    const url = requestUrl.searchParams.get("url");
    if (!url || !/^https?:\/\//i.test(url)) {
      sendJson(res, 400, { error: "Missing http(s) url" });
      return true;
    }
    sendJson(res, 200, await readArticleUrl(url));
    return true;
  }
  if (requestUrl.pathname === "/api/list-import-sources" && req.method === "GET") {
    sendJson(res, 200, { files: await listMarkdownFiles() });
    return true;
  }
  if (requestUrl.pathname === "/api/list-ocr-project-queues" && req.method === "GET") {
    sendJson(res, 200, { projects: await listOcrProjectQueues() });
    return true;
  }
  if (requestUrl.pathname === "/api/read-ocr-project-queue" && req.method === "POST") {
    const body = await readJson(req);
    sendJson(res, 200, await readOcrProjectQueue(body.path));
    return true;
  }
  if (requestUrl.pathname === "/api/read-local-file" && req.method === "POST") {
    const body = await readJson(req);
    const file = resolveProjectPath(body.path);
    const markdown = await readFile(file, "utf8");
    sendJson(res, 200, {
      path: displayPath(file),
      title: extractTitleFromMarkdown(markdown) || basename(file, extname(file)),
      slug: slugify(extractTitleFromMarkdown(markdown) || basename(file, extname(file))),
      markdown
    });
    return true;
  }
  if (requestUrl.pathname === "/api/stage" && req.method === "POST") {
    sendJson(res, 200, await stageImport(await readJson(req)));
    return true;
  }
  if (requestUrl.pathname === "/api/run-ocr" && req.method === "POST") {
    const body = await readJson(req);
    sendJson(res, 200, await maybeAsync("/api/run-ocr", body, () => runOcrImport(body)));
    return true;
  }
  if (requestUrl.pathname === "/api/rerun-region-ocr" && req.method === "POST") {
    sendJson(res, 200, await rerunSingleRegionOcr(await readJson(req)));
    return true;
  }
  if (requestUrl.pathname === "/api/run-ocr-rework" && req.method === "POST") {
    const body = await readJson(req);
    sendJson(res, 200, await maybeAsync("/api/run-ocr-rework", body, () => runOcrRework(body)));
    return true;
  }
  if (requestUrl.pathname === "/api/accept-ocr-rework" && req.method === "POST") {
    sendJson(res, 200, await acceptOcrRework(await readJson(req)));
    return true;
  }
  if (requestUrl.pathname === "/api/export-wordpress-workbench" && req.method === "POST") {
    sendJson(res, 200, await exportWorkbenchWordPress(await readJson(req)));
    return true;
  }
  if (requestUrl.pathname === "/api/analyze-layout" && req.method === "POST") {
    sendJson(res, 200, await analyzeLayout(await readJson(req)));
    return true;
  }
  if (requestUrl.pathname === "/api/analyze-page-orientation" && req.method === "POST") {
    sendJson(res, 200, await analyzePageOrientation(await readJson(req)));
    return true;
  }
  if (requestUrl.pathname === "/api/workflow-state" && req.method === "GET") {
    sendJson(res, 200, await readWorkflowState());
    return true;
  }
  if (requestUrl.pathname === "/api/workflow-state" && req.method === "POST") {
    const result = await writeWorkflowState(await readJson(req));
    sendJson(res, result.ok ? 200 : 400, result);
    return true;
  }
  if (requestUrl.pathname.startsWith("/api/job/") && req.method === "GET") {
    const id = decodeURIComponent(requestUrl.pathname.slice("/api/job/".length));
    const found = describeJob(id);
    sendJson(res, found.ok ? 200 : 404, found);
    return true;
  }
  if (requestUrl.pathname === "/api/jobs" && req.method === "GET") {
    sendJson(res, 200, { ok: true, jobs: [...jobs.values()].map(({ result, ...rest }) => rest) });
    return true;
  }
  if (requestUrl.pathname === "/api/manifest" && req.method === "GET") {
    sendJson(res, 200, buildManifest());
    return true;
  }
  if (requestUrl.pathname === "/api/build-web-capture" && req.method === "POST") {
    const body = await readJson(req);
    if (!body || (!body.source && !Array.isArray(body.paragraphs))) {
      sendJson(res, 400, { error: "Missing source (or paragraphs)" });
      return true;
    }
    sendJson(res, 200, { ok: true, ...buildWebCapture(body) });
    return true;
  }
  if (requestUrl.pathname === "/api/build-article-markdown" && req.method === "POST") {
    const body = await readJson(req);
    if (!body || !Array.isArray(body.blocks)) {
      sendJson(res, 400, { error: "Missing blocks (array)" });
      return true;
    }
    sendJson(res, 200, { ok: true, markdown: buildArticleMarkdown(body) });
    return true;
  }
  if (requestUrl.pathname === "/api/publish" && req.method === "POST") {
    sendJson(res, 200, await publishImport(await readJson(req)));
    return true;
  }
  return false;
}

/* ---- workflow state -------------------------------------------------------
   The board in assets/tools/project-workflow-board.html was the only thing that
   knew which stage a project had reached, and it kept that in the browser's
   localStorage. An agent driving the pipeline over this API could run every
   step but could not see which ones were already done, so the two could not be
   handed work between them. The state lives on disk now; the board still keeps
   a localStorage copy so it works with the server stopped. */

const workflowStateFile = join(root, ".workflow-state", "projects.json");

function validateWorkflowState(value) {
  if (!value || typeof value !== "object") return "state must be an object";
  if (!Array.isArray(value.projects)) return "state.projects must be an array";
  for (const project of value.projects) {
    if (!project || typeof project !== "object") return "each project must be an object";
    if (typeof project.id !== "string" || !project.id) return "each project needs a string id";
  }
  if (value.activeId != null && typeof value.activeId !== "string") return "activeId must be a string";
  return null;
}

async function readWorkflowState() {
  try {
    const raw = await readFile(workflowStateFile, "utf8");
    const state = JSON.parse(raw);
    const problem = validateWorkflowState(state);
    if (problem) return { ok: true, state: null, corrupt: problem };
    const info = await stat(workflowStateFile);
    return { ok: true, state, savedAt: info.mtime.toISOString() };
  } catch (error) {
    if (error.code === "ENOENT") return { ok: true, state: null };
    throw error;
  }
}

async function writeWorkflowState(body) {
  const state = body && body.state;
  const problem = validateWorkflowState(state);
  if (problem) return { ok: false, error: problem };
  await mkdir(dirname(workflowStateFile), { recursive: true });
  /* write-then-rename: a crash mid-write leaves the previous state intact
     rather than a half-written file the board would refuse to load */
  const temp = `${workflowStateFile}.${randomUUID().slice(0, 8)}.tmp`;
  await writeFile(temp, `${JSON.stringify(state, null, 2)}
`, "utf8");
  await rename(temp, workflowStateFile);
  return { ok: true, savedAt: new Date().toISOString(), projects: state.projects.length };
}


/* ---- API description ------------------------------------------------------
   Anything driving this pipeline that is not the bundled HTML - a script, an
   agent - otherwise has to read 1300 lines of this file to learn what the
   endpoints are and what they want. GET /api/manifest answers that in one
   call.

   `required` and `optional` are the request-body keys each handler actually
   reads. They are declared rather than derived, so assertManifestMatchesRoutes()
   below fails at startup if a route is added without describing it, or
   described without existing: a manifest that has drifted from the routes is
   worse than none. */

/* ---- background jobs ------------------------------------------------------
   prepare-scan-pages, run-ocr and run-ocr-rework shell out to Python and can
   run for minutes. Answering them synchronously is fine for the bundled UI,
   which sits and waits, but a caller with a request timeout gets no answer and
   - worse - no way to find out whether the work actually happened.

   These endpoints keep their synchronous behaviour, so nothing that already
   calls them changes. Passing "async": true instead starts the work, answers
   immediately with a jobId, and leaves the result to be collected from
   GET /api/job/<id>. */

const jobs = new Map();
const JOB_HISTORY = 50;

function startJob(endpoint, work) {
  const id = `${endpoint.replace(/^\/api\//, "")}-${Date.now().toString(36)}-${randomUUID().slice(0, 6)}`;
  const job = { id, endpoint, status: "running", startedAt: new Date().toISOString(),
                finishedAt: null, result: null, error: null };
  jobs.set(id, job);
  /* trim oldest finished jobs; a long session should not grow without bound */
  if (jobs.size > JOB_HISTORY) {
    for (const [key, value] of jobs) {
      if (value.status !== "running") { jobs.delete(key); }
      if (jobs.size <= JOB_HISTORY) break;
    }
  }
  work()
    .then((result) => { job.status = "done"; job.result = result; })
    .catch((error) => { job.status = "failed"; job.error = error?.message || String(error); })
    .finally(() => { job.finishedAt = new Date().toISOString(); });
  return { ok: true, jobId: id, status: "running", poll: `/api/job/${id}` };
}

function describeJob(id) {
  const job = jobs.get(id);
  if (!job) return { ok: false, error: `Unknown job ${id}` };
  return { ok: true, ...job };
}

/* Run an endpoint's work either way, from one place, so the two paths cannot
   drift into doing different things. */
async function maybeAsync(endpoint, body, work) {
  if (body && body.async === true) return startJob(endpoint, work);
  return work();
}


const API_SPEC = [
  { path: "/api/manifest", method: "GET", effect: "read", summary: "这份接口说明。",
    optional: [] },
  { path: "/api/jobs", method: "GET", effect: "read",
    summary: "列出本次运行内的后台任务（不含结果体）。", optional: [] },
  { path: "/api/job/{id}", method: "GET", effect: "read", dynamic: "/api/job/",
    summary: "查询单个后台任务：status 为 running / done / failed，done 时 result 为该接口原本的返回值。",
    optional: [] },

  { path: "/api/workflow-state", method: "GET", effect: "read",
    summary: "读取编辑进度：每个项目走到哪一阶段、检查项完成情况。无记录时 state 为 null。",
    optional: [] },
  { path: "/api/workflow-state", method: "POST", effect: "replace",
    summary: "整份写回编辑进度。形状不合法时返回 400 并说明原因。",
    required: ["state"] },

  { path: "/api/list-import-sources", method: "GET", effect: "read",
    summary: "列出可导入的本地 Markdown 文件。", optional: [] },
  { path: "/api/read-local-file", method: "POST", effect: "read",
    summary: "读取仓库内某个文件的文本。", required: ["path"] },
  { path: "/api/read-url", method: "GET", effect: "read",
    summary: "抓取网页正文（查询参数 url）。", query: ["url"] },
  { path: "/api/read-url", method: "POST", effect: "read",
    summary: "抓取网页正文。", required: ["url"] },

  { path: "/api/select-image-folder", method: "POST", effect: "session",
    summary: "选定原图文件夹，返回后续接口使用的 token 与图片清单。", required: ["path"] },
  { path: "/api/local-image", method: "GET", effect: "read",
    summary: "读取已选文件夹内的一张图（查询参数 token、path）。", query: ["token", "path"] },
  { path: "/api/resolve-source-image", method: "POST", effect: "read",
    summary: "按页名定位原图。", required: ["pageName"] },
  { path: "/api/prepare-scan-pages", method: "POST", effect: "new-output",
    summary: "扫描件拆页、校正、调色、裁切。长任务，返回 jobId 与输出目录。",
    required: ["sourceFolderToken"],
    optional: ["async", "binding", "limit", "model", "noStraighten", "noTone", "outerTrim", "vlm"] },
  { path: "/api/analyze-layout", method: "POST", effect: "read",
    summary: "分析版面分区。pages 每项为 {name, width, height, dataUrl}，dataUrl 是 base64 图片（不接受路径），一次最多 4 页。返回的 pages[].regions 可直接写成 magazine-regions.json 供 run-ocr 使用。",
    required: ["pages"] },
  { path: "/api/analyze-page-orientation", method: "POST", effect: "read",
    summary: "判断页面文字方向。pages 每项为 {name, width, height, dataUrl}，同 analyze-layout。",
    required: ["pages"] },

  { path: "/api/run-ocr", method: "POST", effect: "new-output",
    summary: "按分区标注跑 OCR。annotationJson 是仓库内的路径，格式为 {version, createdAt, pages:[{name,width,height,regions:[{id,type,speaker,order,box,note}]}]}——与 analyze-layout 返回的 regions 字段兼容，但需要调用方自行落盘。长任务。",
    required: ["annotationJson", "imageDir"],
    optional: ["async", "deepSeek", "engine", "model", "out", "promptFile", "sessionId"] },
  { path: "/api/rerun-region-ocr", method: "POST", effect: "replace",
    summary: "重跑单个区域的 OCR。",
    required: ["pageName", "regionId"],
    optional: ["angle", "exclusions", "model", "regionType", "scanBox",
               "sourceFolderToken", "sourceImage", "speaker", "writingDirection"] },
  { path: "/api/list-ocr-project-queues", method: "GET", effect: "read",
    summary: "列出 OCR 项目队列。", optional: [] },
  { path: "/api/read-ocr-project-queue", method: "POST", effect: "read",
    summary: "读取某个队列，含需返工的区域。", required: ["path"] },
  { path: "/api/run-ocr-rework", method: "POST", effect: "replace",
    summary: "对队列中某一项跑返工。长任务。", required: ["path", "key"],
    optional: ["async"] },
  { path: "/api/accept-ocr-rework", method: "POST", effect: "replace",
    summary: "采纳返工结果。", required: ["path", "key"] },

  { path: "/api/stage", method: "POST", effect: "session",
    summary: "暂存一篇待发布文章，返回 sessionId。",
    required: ["mode"],
    optional: ["html", "markdown", "slug", "sourceTitle", "sourceUrl", "text", "title", "uploads"] },
  { path: "/api/build-web-capture", method: "POST", effect: "pure",
    summary: "把网页正文或 HTML 转成站点草稿，返回 markdown 与建议文件名。不写盘。",
    required: ["source"],
    optional: ["accessedOn", "author", "date", "interviewee", "organizations", "paragraphs",
               "people", "publication", "sourceUrl", "summary", "tags", "template", "title", "works"] },
  { path: "/api/build-article-markdown", method: "POST", effect: "pure",
    summary: "把翻译分块渲染成文章 Markdown。mode 取 template / parallel / display。不写盘。",
    required: ["blocks"],
    optional: ["meta", "mode"] },
  { path: "/api/publish", method: "POST", effect: "overwrite",
    summary: "把暂存内容写成站点文章。",
    required: ["sessionId", "title"],
    optional: ["categories", "date", "format", "markdown", "maxWidth", "outputMode",
               "quality", "slug", "sourceTitle", "sourceUrl", "tags"] },
  { path: "/api/export-wordpress-workbench", method: "POST", effect: "overwrite",
    summary: "把工作台内容导出为 WordPress 双语稿。",
    required: ["pageName", "segments"],
    optional: ["meta", "sourceFolderToken", "sourceImage", "sourceRelativePath", "workflow"] }
];

function buildManifest() {
  return {
    ok: true,
    service: "pokeamice import-wizard",
    root,
    baseUrl: `http://${host}:${port}`,
    contract: {
      request: "POST 接口收 JSON 请求体；GET 接口用查询参数。",
      response: "成功为 {ok:true, ...}；失败为 {error:\"...\"} 或 {ok:false, error:\"...\"}，并带非 200 状态码。",
      longRunning: "标注为长任务的接口默认同步执行，可能耗时数分钟。请求体带 \"async\": true 时立即返回 {jobId, poll}，再轮询 GET /api/job/{id} 取结果。",
      effects: {
        read: "只读，重跑安全。",
        pure: "纯计算不写盘；同样输入必得同样输出，重跑安全。",
        replace: "整体替换目标内容；重跑得到同一结果，重跑安全（幂等）。",
        "new-output": "每次生成一个新的输出目录并返回其 id；重跑安全但会留下多份产物，需要自行清理。",
        session: "创建或更新一个会话 / token；重跑会得到新的 id，旧的仍然有效。",
        overwrite: "按 slug 或页名写入站点文件，会覆盖同名内容；重跑安全但会覆盖此前的人工修改，请先确认目标。"
      }
    },
    endpoints: API_SPEC
  };
}

/* A manifest is only worth having if it cannot quietly go stale. */
function assertManifestMatchesRoutes(source) {
  const routed = new Set();
  const exact = /requestUrl\.pathname === "(\/api\/[a-z-]+)" && req\.method === "(GET|POST)"/g;
  let match;
  while ((match = exact.exec(source))) routed.add(`${match[2]} ${match[1]}`);
  /* Path-parameter routes are dispatched by prefix, not equality, so they are
     matched on the prefix a spec entry declares. */
  const prefixed = /requestUrl\.pathname\.startsWith\("(\/api\/[a-z-]+\/)"\) && req\.method === "(GET|POST)"/g;
  const prefixes = new Set();
  while ((match = prefixed.exec(source))) prefixes.add(`${match[2]} ${match[1]}`);
  for (const entry of API_SPEC) {
    if (entry.dynamic && prefixes.has(`${entry.method} ${entry.dynamic}`)) {
      routed.add(`${entry.method} ${entry.path}`);
    }
  }
  routed.add("GET /api/manifest");
  const described = new Set(API_SPEC.map((entry) => `${entry.method} ${entry.path}`));
  const undescribed = [...routed].filter((key) => !described.has(key));
  const missing = [...described].filter((key) => !routed.has(key));
  /* An endpoint whose re-run behaviour nobody wrote down is one a caller has
     to guess about, and callers that retry guess wrong. */
  const untagged = API_SPEC.filter((entry) => !entry.effect).map((e) => `${e.method} ${e.path}`);
  if (untagged.length) console.error("[manifest] no effect declared for:", untagged.join(", "));
  if (undescribed.length || missing.length) {
    console.error("[manifest] out of step with the routes:");
    if (undescribed.length) console.error("  routed but not described:", undescribed.join(", "));
    if (missing.length) console.error("  described but not routed:", missing.join(", "));
  }
}


const server = createServer(async (req, res) => {
  try {
    const requestUrl = new URL(req.url || "/", `http://${host}:${port}`);
    if (requestUrl.pathname.startsWith("/api/")) {
      const handled = await handleApi(req, res, requestUrl);
      if (!handled) sendJson(res, 404, { error: "Unknown API endpoint" });
      return;
    }

    const requestedPath = decodeURIComponent(requestUrl.pathname).replace(/^\/+/, "") || "assets/tools/editor-toolbox.html";
    const file = safeInsideRoot(resolve(root, requestedPath));
    const data = await readFile(file);
    send(res, 200, data, mimeTypes[extname(file).toLowerCase()] || "application/octet-stream");
  } catch (error) {
    if ((req.url || "").startsWith("/api/")) {
      sendJson(res, 500, { error: error.message || String(error), stdout: error.stdout, stderr: error.stderr });
    } else {
      send(res, 404, error.message || "Not found");
    }
  }
});

server.on("error", (error) => {
  if (error.code === "EADDRINUSE") {
    console.error(`Port ${port} is already in use.`);
    console.error(`Try another port: $env:PORT=4176; npm run import:wizard`);
    process.exit(1);
  }
  throw error;
});

server.listen(port, host, async () => {
  console.log(`Editor toolbox: http://${host}:${port}/assets/tools/editor-toolbox.html`);
  console.log(`Import wizard: http://${host}:${port}/assets/tools/import-wizard.html`);
  console.log(`API manifest:  http://${host}:${port}/api/manifest`);
  /* Check the description against the routes on every start, so a new endpoint
     that nobody described is noticed here rather than by whatever was relying
     on the manifest being complete. */
  try {
    assertManifestMatchesRoutes(await readFile(new URL(import.meta.url), "utf8"));
  } catch (error) {
    console.error("[manifest] could not self-check:", error.message);
  }
});
