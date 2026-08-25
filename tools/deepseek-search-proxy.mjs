import { createServer } from "node:http";

const host = "127.0.0.1";
const port = Number(process.env.PORT || 8787);
const apiKey = process.env.DEEPSEEK_API_KEY;
const model = process.env.DEEPSEEK_MODEL || "deepseek-chat";

function send(res, status, body) {
  res.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type"
  });
  res.end(JSON.stringify(body));
}

function readJson(req) {
  return new Promise((resolve, reject) => {
    let body = "";
    req.on("data", (chunk) => {
      body += chunk;
      if (body.length > 1_000_000) {
        req.destroy();
        reject(new Error("Request body too large"));
      }
    });
    req.on("end", () => {
      try {
        resolve(body ? JSON.parse(body) : {});
      } catch (error) {
        reject(new Error("Invalid JSON"));
      }
    });
    req.on("error", reject);
  });
}

function buildPrompt(payload) {
  const query = payload.query || "总结当前检索结果";
  const filters = payload.filters || {};
  const context = Array.isArray(payload.context) ? payload.context.slice(0, 12) : [];
  return [
    "你是 PokeAmice 本地资料站的检索助手。",
    "请只基于提供的站内检索结果回答，不要编造外部事实。",
    "优先帮助用户判断哪些文章、微博或访谈值得打开。",
    "",
    `检索词：${query || "未填写"}`,
    `筛选：${JSON.stringify(filters, null, 2)}`,
    "",
    "候选结果：",
    JSON.stringify(context, null, 2),
    "",
    "请用中文输出：1. 结果概览；2. 推荐打开的 3-5 条；3. 可能还需要补充的关键词。"
  ].join("\n");
}

const server = createServer(async (req, res) => {
  if (req.method === "OPTIONS") {
    send(res, 200, { ok: true });
    return;
  }

  if (req.method !== "POST" || req.url !== "/search") {
    send(res, 404, { error: "Use POST /search" });
    return;
  }

  if (!apiKey) {
    send(res, 500, { error: "Missing DEEPSEEK_API_KEY environment variable" });
    return;
  }

  try {
    const payload = await readJson(req);
    const response = await fetch("https://api.deepseek.com/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${apiKey}`
      },
      body: JSON.stringify({
        model,
        messages: [
          { role: "system", content: "你是谨慎的本地资料检索助手，只根据用户提供的上下文回答。" },
          { role: "user", content: buildPrompt(payload) }
        ],
        temperature: 0.2
      })
    });

    const data = await response.json();
    if (!response.ok) {
      send(res, response.status, { error: data.error?.message || "DeepSeek request failed" });
      return;
    }

    send(res, 200, {
      answer: data.choices?.[0]?.message?.content || "",
      model
    });
  } catch (error) {
    send(res, 500, { error: error.message || String(error) });
  }
});

server.listen(port, host, () => {
  console.log(`DeepSeek search proxy: http://${host}:${port}/search`);
});
