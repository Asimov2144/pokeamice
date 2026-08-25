const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
const postsDir = path.join(root, "_posts");
const required = ["archive_type", "source", "workflow", "entities"];

function walk(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) return walk(fullPath);
    return entry.isFile() && entry.name.endsWith(".md") ? [fullPath] : [];
  });
}

function readFrontMatter(filePath) {
  const text = fs.readFileSync(filePath, "utf8");
  const match = text.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  return match ? match[1] : "";
}

const rows = walk(postsDir).map((filePath) => {
  const fm = readFrontMatter(filePath);
  const missing = required.filter((key) => !new RegExp(`^${key}:`, "m").test(fm));
  return {
    file: path.relative(root, filePath),
    missing,
  };
});

const incomplete = rows.filter((row) => row.missing.length);

if (!incomplete.length) {
  console.log("All posts include the base metadata fields.");
  process.exit(0);
}

console.log("Posts missing metadata fields:\n");
incomplete.forEach((row) => {
  console.log(`- ${row.file}`);
  console.log(`  missing: ${row.missing.join(", ")}`);
});

process.exitCode = 1;
