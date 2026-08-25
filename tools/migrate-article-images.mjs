#!/usr/bin/env node
import { createHash } from "node:crypto";
import { mkdir, readFile, writeFile, copyFile, stat } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const rootDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const defaultDate = new Date().toISOString().slice(0, 10);

function parseArgs(argv) {
  const args = {
    date: defaultDate,
    categories: "整理",
    tags: "",
    maxWidth: 1600,
    quality: 78,
    outFormat: "webp",
    postsDir: "_posts",
    siteImageRoot: "assets/img/posts",
    rawImageRoot: "archive/raw-images",
    download: true,
    write: true
  };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (!arg.startsWith("--")) continue;
    const key = arg.slice(2);
    if (key === "help") args.help = true;
    else if (key === "dry-run") args.write = false;
    else if (key === "no-download") args.download = false;
    else if (key === "draft") args.draft = true;
    else {
      const value = argv[i + 1];
      if (value == null || value.startsWith("--")) {
        throw new Error(`Missing value for --${key}`);
      }
      i += 1;
      if (key === "max-width") args.maxWidth = Number(value);
      else if (key === "quality") args.quality = Number(value);
      else if (key === "input") args.input = value;
      else if (key === "title") args.title = value;
      else if (key === "date") args.date = value;
      else if (key === "slug") args.slug = value;
      else if (key === "categories") args.categories = value;
      else if (key === "tags") args.tags = value;
      else if (key === "source-title") args.sourceTitle = value;
      else if (key === "source-url") args.sourceUrl = value;
      else if (key === "base-url") args.baseUrl = value;
      else if (key === "format") args.outFormat = value;
      else throw new Error(`Unknown option --${key}`);
    }
  }
  return args;
}

function printHelp() {
  console.log(`Usage:
  node tools/migrate-article-images.mjs --input migration/inbox/article.html --title "文章标题" --date 2026-07-16 --slug article-slug

Options:
  --input <file>          HTML or Markdown source file
  --title <text>          Post title. Defaults to source filename
  --date <YYYY-MM-DD>     Post date. Defaults to today
  --slug <text>           URL/image folder slug. Defaults to title slug
  --categories <a,b,c>    Jekyll categories. Defaults to 整理
  --tags <a,b,c>          Jekyll tags
  --source-title <text>   Original platform/source name
  --source-url <url>      Original article URL
  --base-url <url>        Resolve relative image URLs from copied HTML
  --max-width <number>    Display image max width. Defaults to 1600
  --quality <number>      WebP/JPEG quality when sharp is installed. Defaults to 78
  --format <webp|jpg|png> Display image format. Defaults to webp
  --draft                 Write to _drafts instead of _posts
  --no-download           Do not fetch remote images; keep original URLs
  --dry-run               Print report without writing files

Optional optimizer:
  npm install --no-save sharp
`);
}

function slugify(input) {
  const text = String(input || "")
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/&/g, " and ")
    .replace(/[^a-z0-9\u4e00-\u9fff\u3040-\u30ff]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .replace(/-{2,}/g, "-");
  return text || `post-${defaultDate}`;
}

function yamlList(csv) {
  return String(csv || "")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function yamlQuote(value) {
  return JSON.stringify(String(value || ""));
}

function escapeRegExp(value) {
  return String(value).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function decodeEntities(value) {
  return String(value)
    .replace(/&nbsp;/gi, " ")
    .replace(/&amp;/gi, "&")
    .replace(/&lt;/gi, "<")
    .replace(/&gt;/gi, ">")
    .replace(/&quot;/gi, '"')
    .replace(/&#39;/g, "'");
}

function extractTitleFromHtml(text) {
  const match = text.match(/<title[^>]*>([\s\S]*?)<\/title>/i) || text.match(/<h1[^>]*>([\s\S]*?)<\/h1>/i);
  return match ? decodeEntities(stripTags(match[1]).trim()) : "";
}

function stripTags(value) {
  return String(value).replace(/<[^>]+>/g, "");
}

function convertHtmlToMarkdown(html) {
  let text = String(html);
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
  return String(text)
    .replace(/\r\n/g, "\n")
    .replace(/\n{3,}/g, "\n\n")
    .replace(/[ \t]+\n/g, "\n")
    .trim();
}

function extractImages(markdown) {
  const images = [];
  const re = /!\[([^\]]*)\]\((<([^>]+)>|[^)]+?)\)/g;
  let match;
  while ((match = re.exec(markdown))) {
    const src = decodeURIComponent((match[3] || match[2] || "").trim().replace(/^['"]|['"]$/g, ""));
    images.push({
      alt: match[1] || "",
      src,
      raw: match[0],
      index: images.length + 1
    });
  }
  return images;
}

async function maybeLoadSharp() {
  try {
    const mod = await import("sharp");
    return mod.default || mod;
  } catch {
    return null;
  }
}

function extensionFromContentType(contentType) {
  const type = String(contentType || "").split(";")[0].trim().toLowerCase();
  if (type === "image/jpeg") return ".jpg";
  if (type === "image/png") return ".png";
  if (type === "image/gif") return ".gif";
  if (type === "image/webp") return ".webp";
  if (type === "image/svg+xml") return ".svg";
  return "";
}

function extensionFromUrl(src) {
  try {
    const parsed = new URL(src);
    const ext = path.extname(parsed.pathname);
    return ext && ext.length <= 6 ? ext.toLowerCase() : "";
  } catch {
    const ext = path.extname(src.split(/[?#]/)[0]);
    return ext && ext.length <= 6 ? ext.toLowerCase() : "";
  }
}

function resolveImageSource(src, inputPath, baseUrl) {
  if (/^https?:\/\//i.test(src)) return { type: "remote", url: src };
  if (/^\/\//.test(src)) return { type: "remote", url: `https:${src}` };
  if (baseUrl) return { type: "remote", url: new URL(src, baseUrl).toString() };
  if (/^file:\/\//i.test(src)) return { type: "local", file: fileURLToPath(src) };
  const baseDir = path.dirname(inputPath);
  return { type: "local", file: path.resolve(baseDir, decodeURIComponent(src)) };
}

async function readImageBytes(image, inputPath, baseUrl, download) {
  const resolved = resolveImageSource(image.src, inputPath, baseUrl);
  if (resolved.type === "remote") {
    if (!download) return null;
    const response = await fetch(resolved.url, {
      headers: {
        "user-agent": "PokeAmiceArticleMigrator/1.0"
      }
    });
    if (!response.ok) throw new Error(`HTTP ${response.status} ${response.statusText}`);
    const contentType = response.headers.get("content-type") || "";
    const bytes = Buffer.from(await response.arrayBuffer());
    return { bytes, ext: extensionFromContentType(contentType) || extensionFromUrl(resolved.url) || ".bin", resolved: resolved.url };
  }
  const bytes = await readFile(resolved.file);
  return { bytes, ext: extensionFromUrl(resolved.file) || ".bin", resolved: resolved.file };
}

async function writeDisplayImage({ bytes, rawPath, displayPath, sharp, maxWidth, quality, outFormat }) {
  if (!sharp || rawPath.toLowerCase().endsWith(".gif") || rawPath.toLowerCase().endsWith(".svg")) {
    await copyFile(rawPath, displayPath);
    return { optimized: false, copied: true };
  }
  let pipeline = sharp(bytes, { animated: false }).rotate().resize({ width: maxWidth, withoutEnlargement: true });
  if (outFormat === "jpg" || outFormat === "jpeg") pipeline = pipeline.jpeg({ quality, mozjpeg: true });
  else if (outFormat === "png") pipeline = pipeline.png({ compressionLevel: 9, quality });
  else pipeline = pipeline.webp({ quality });
  await pipeline.toFile(displayPath);
  return { optimized: true, copied: false };
}

function displayExtension(sourceExt, outFormat, canOptimize) {
  const ext = sourceExt.toLowerCase();
  if (!canOptimize || ext === ".gif" || ext === ".svg") return ext === ".jpeg" ? ".jpg" : ext;
  if (outFormat === "jpg" || outFormat === "jpeg") return ".jpg";
  if (outFormat === "png") return ".png";
  return ".webp";
}

function buildFrontMatter(args, title, slug) {
  const lines = [
    "---",
    `title: ${yamlQuote(title)}`,
    `date: ${args.date}`,
    `categories: [${yamlList(args.categories).map(yamlQuote).join(", ")}]`
  ];
  const tags = yamlList(args.tags);
  if (tags.length) lines.push(`tags: [${tags.map(yamlQuote).join(", ")}]`);
  lines.push("archive_type: article");
  if (args.sourceTitle || args.sourceUrl) {
    lines.push("source:");
    if (args.sourceTitle) lines.push(`  title: ${yamlQuote(args.sourceTitle)}`);
    if (args.sourceUrl) lines.push(`  url: ${yamlQuote(args.sourceUrl)}`);
    lines.push("  source_type: web_article");
  }
  lines.push("workflow:");
  lines.push("  proofreading: draft");
  lines.push("  published: draft");
  lines.push(`migration:`);
  lines.push(`  image_folder: ${yamlQuote(`/assets/img/posts/${slug}/`)}`);
  lines.push("---");
  return lines.join("\n");
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help || !args.input) {
    printHelp();
    process.exit(args.help ? 0 : 1);
  }

  const inputPath = path.resolve(rootDir, args.input);
  const inputText = await readFile(inputPath, "utf8");
  const isHtml = /\.html?$/i.test(inputPath) || /<\/?[a-z][\s\S]*>/i.test(inputText);
  const inferredTitle = isHtml ? extractTitleFromHtml(inputText) : "";
  const title = args.title || inferredTitle || path.basename(inputPath, path.extname(inputPath));
  const slug = slugify(args.slug || title);
  const markdown = isHtml ? convertHtmlToMarkdown(inputText) : normalizeMarkdown(inputText);
  const images = extractImages(markdown);
  const sharp = await maybeLoadSharp();

  const siteImageDir = path.join(rootDir, args.siteImageRoot, slug);
  const rawImageDir = path.join(rootDir, args.rawImageRoot, slug);
  const postsDir = path.join(rootDir, args.draft ? "_drafts" : args.postsDir);
  const postFileName = args.draft ? `${slug}.md` : `${args.date}-${slug}.md`;
  const postPath = path.join(postsDir, postFileName);
  const report = {
    input: path.relative(rootDir, inputPath),
    post: path.relative(rootDir, postPath),
    siteImageDir: path.relative(rootDir, siteImageDir),
    rawImageDir: path.relative(rootDir, rawImageDir),
    optimizer: sharp ? "sharp" : "none",
    images: [],
    failures: []
  };

  let outputMarkdown = markdown;
  if (args.write) {
    await mkdir(siteImageDir, { recursive: true });
    await mkdir(rawImageDir, { recursive: true });
    await mkdir(postsDir, { recursive: true });
  }

  for (const image of images) {
    try {
      const loaded = await readImageBytes(image, inputPath, args.baseUrl || args.sourceUrl, args.download);
      if (!loaded) {
        report.images.push({ source: image.src, status: "kept-remote" });
        continue;
      }
      const hash = createHash("sha1").update(loaded.bytes).digest("hex").slice(0, 8);
      const sourceExt = loaded.ext || ".bin";
      const rawName = `${String(image.index).padStart(2, "0")}-${hash}${sourceExt}`;
      const displayExt = displayExtension(sourceExt, args.outFormat, Boolean(sharp));
      const displayName = `${String(image.index).padStart(2, "0")}-${hash}${displayExt}`;
      const rawPath = path.join(rawImageDir, rawName);
      const displayPath = path.join(siteImageDir, displayName);
      if (args.write) {
        await writeFile(rawPath, loaded.bytes);
        await writeDisplayImage({
          bytes: loaded.bytes,
          rawPath,
          displayPath,
          sharp,
          maxWidth: args.maxWidth,
          quality: args.quality,
          outFormat: args.outFormat
        });
      }
      const publicPath = `/${path.posix.join(args.siteImageRoot.replaceAll("\\", "/"), slug, displayName)}`;
      outputMarkdown = outputMarkdown.replace(new RegExp(escapeRegExp(image.raw), "g"), `![${image.alt || `图 ${image.index}`}](${publicPath})`);
      const rawSize = loaded.bytes.length;
      let displaySize = rawSize;
      if (args.write) {
        displaySize = (await stat(displayPath)).size;
      }
      report.images.push({
        source: image.src,
        resolved: loaded.resolved,
        raw: path.relative(rootDir, rawPath),
        display: path.relative(rootDir, displayPath),
        rawKB: Math.round(rawSize / 102.4) / 10,
        displayKB: Math.round(displaySize / 102.4) / 10
      });
    } catch (error) {
      report.failures.push({ source: image.src, message: error.message });
    }
  }

  const frontMatter = buildFrontMatter(args, title, slug);
  const finalPost = `${frontMatter}\n\n${outputMarkdown}\n`;
  const reportPath = path.join(rawImageDir, "migration-report.json");

  if (args.write) {
    await writeFile(postPath, finalPost, "utf8");
    await writeFile(reportPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
  }

  console.log(JSON.stringify(report, null, 2));
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
