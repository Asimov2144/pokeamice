import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { extname, resolve } from "node:path";

const root = resolve(process.cwd());
const port = Number(process.env.PORT || 4173);
const host = "127.0.0.1";

const types = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".svg": "image/svg+xml"
};

function send(res, status, body, type = "text/plain; charset=utf-8") {
  res.writeHead(status, {
    "Content-Type": type,
    "Access-Control-Allow-Origin": "*"
  });
  res.end(body);
}

async function readArticleUrl(url) {
  const response = await fetch(url, {
    headers: {
      "User-Agent": "PokeamiceArticleTranslationEditor/1.0",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,text/plain;q=0.8,*/*;q=0.5"
    }
  });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  const contentType = response.headers.get("content-type") || "";
  return {
    finalUrl: response.url,
    contentType,
    html: await response.text()
  };
}

const server = createServer(async (req, res) => {
  try {
    const requestUrl = new URL(req.url || "/", `http://${host}:${port}`);

    if (requestUrl.pathname === "/api/read-url") {
      const url = requestUrl.searchParams.get("url");
      if (!url || !/^https?:\/\//i.test(url)) {
        send(res, 400, JSON.stringify({ error: "Missing http(s) url" }), "application/json; charset=utf-8");
        return;
      }
      const article = await readArticleUrl(url);
      send(res, 200, JSON.stringify(article), "application/json; charset=utf-8");
      return;
    }

    const cleanPath = decodeURIComponent(requestUrl.pathname).replace(/^\/+/, "") || "index.html";
    const file = resolve(root, cleanPath);
    if (!file.startsWith(root)) {
      send(res, 403, "Forbidden");
      return;
    }
    const data = await readFile(file);
    send(res, 200, data, types[extname(file).toLowerCase()] || "application/octet-stream");
  } catch (error) {
    send(res, 404, String(error.message || error));
  }
});

server.on("error", (error) => {
  if (error.code === "EADDRINUSE") {
    console.error(`Port ${port} is already in use.`);
    console.error(`Try another port, for example: $env:PORT=4174; node tools\\article-editor-server.mjs`);
    process.exit(1);
  }
  throw error;
});

server.listen(port, host, () => {
  console.log(`Article editor: http://${host}:${port}/assets/tools/article-translation-editor.html`);
});
