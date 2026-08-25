const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
const sourcePath = path.join(root, "weibo", "2144jx WeBook-By含光.md");
const outputPath = path.join(root, "assets", "data", "weibo-archive.json");

const source = fs.readFileSync(sourcePath, "utf8").replace(/\r\n/g, "\n");
const lines = source.split("\n");

function pad(value) {
  return String(value).padStart(2, "0");
}

function cleanText(value) {
  return value
    .replace(/&amp;/g, "&")
    .replace(/\u00a0/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function parseMeta(line) {
  const meta = line.match(/^\[(.+?)\]\s+来自：(.+?)\s+获得：(\d+)\s+转发\s+(\d+)\s+评论\s+(\d+)\s+点赞/);
  if (!meta) return null;

  return {
    type: meta[1],
    source: cleanText(meta[2]),
    reposts: Number(meta[3]),
    comments: Number(meta[4]),
    likes: Number(meta[5]),
  };
}

function parseBody(bodyLines) {
  const images = [];
  const videos = [];
  const text = [];

  for (const line of bodyLines) {
    const image = line.match(/^!\[[^\]]*\]\((img\/[^)]+)\)/);
    if (image) {
      images.push(`/weibo/${image[1]}`);
      continue;
    }

    const video = line.match(/\((https?:\/\/f\.video\.weibocdn\.com\/[^)]+)\)/);
    if (video) {
      videos.push(video[1]);
      text.push(cleanText(line.replace(/\]\(https?:\/\/f\.video\.weibocdn\.com\/[^)]+\)/, "]")));
      continue;
    }

    if (line.trim() && !line.startsWith("##") && !line.startsWith("###")) {
      text.push(cleanText(line));
    }
  }

  return {
    text: text.filter(Boolean).join("\n\n"),
    images,
    videos,
  };
}

const posts = [];

for (let index = 0; index < lines.length; index += 1) {
  const header = lines[index].match(/^#### \*\*(.+?)\*\*\s+(\d{4})年(\d{1,2})月(\d{1,2})日\s+(\d{2}:\d{2}:\d{2})/);
  if (!header) continue;

  const [, author, year, month, day, time] = header;
  let cursor = index + 1;
  while (cursor < lines.length && !lines[cursor].trim()) cursor += 1;

  const meta = parseMeta(lines[cursor] || "") || {
    type: "微博",
    source: "",
    reposts: 0,
    comments: 0,
    likes: 0,
  };

  if (parseMeta(lines[cursor] || "")) cursor += 1;

  const bodyLines = [];
  while (cursor < lines.length && !lines[cursor].startsWith("#### **")) {
    bodyLines.push(lines[cursor]);
    cursor += 1;
  }

  const date = `${year}-${pad(month)}-${pad(day)}`;
  const dateTime = `${date} ${time}`;
  const body = parseBody(bodyLines);

  posts.push({
    id: `${date.replace(/-/g, "")}-${time.replace(/:/g, "")}-${posts.length + 1}`,
    author: cleanText(author),
    date,
    time,
    dateTime,
    year: Number(year),
    month: Number(month),
    day: Number(day),
    ...meta,
    ...body,
  });

  index = cursor - 1;
}

posts.sort((a, b) => b.dateTime.localeCompare(a.dateTime));

const summary = posts.reduce(
  (acc, post) => {
    acc.total += 1;
    acc.years[post.year] = (acc.years[post.year] || 0) + 1;
    const monthKey = `${post.year}-${pad(post.month)}`;
    acc.months[monthKey] = (acc.months[monthKey] || 0) + 1;
    return acc;
  },
  { total: 0, years: {}, months: {} }
);

fs.mkdirSync(path.dirname(outputPath), { recursive: true });
fs.writeFileSync(
  outputPath,
  JSON.stringify(
    {
      generatedAt: new Date().toISOString(),
      source: "weibo/2144jx WeBook-By含光.md",
      user: {
        uid: "6306512172",
        name: "2144jx",
        avatar: "/weibo/img/006SNtUgly8gr0709hq80j30ig0igmxu.jpg",
        bio: "Pokémonstrum, ergo sum",
      },
      summary,
      posts,
    },
    null,
    2
  )
);

console.log(`Generated ${posts.length} weibo posts at ${path.relative(root, outputPath)}`);
