param(
  [string]$ApiUrl = "",
  [string]$ApiKey = "",
  [string]$Model = "qwen3-vl-flash",
  [string]$ImagePath = "",
  [string]$ImageUrl = "https://img.alicdn.com/imgextra/i1/O1CN01gDEY8M1W114Hi3XcN_!!6000000002727-0-tps-1024-406.jpg",
  [string]$Prompt = "请只回答：连接测试成功。",
  [int]$MaxTokens = 128
)

$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$python = Join-Path $root ".venv-ocr\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
  $python = Join-Path $root ".venv-ocr-gpu\Scripts\python.exe"
}

if (-not $ApiUrl) { $ApiUrl = $env:VLM_OCR_API_URL }
if (-not $ApiKey) { $ApiKey = $env:VLM_OCR_API_KEY }
if (-not $ApiKey) { $ApiKey = $env:DASHSCOPE_API_KEY }
if (-not $ApiKey) { $ApiKey = $env:QWEN_API_KEY }
if (-not $ApiUrl) { throw "Missing ApiUrl." }
if (-not $ApiKey) { throw "Missing ApiKey." }

$env:TEST_QWEN_API_URL = $ApiUrl
$env:TEST_QWEN_API_KEY = $ApiKey
$env:TEST_QWEN_MODEL = $Model
$env:TEST_QWEN_IMAGE_PATH = $ImagePath
$env:TEST_QWEN_IMAGE_URL = $ImageUrl
$env:TEST_QWEN_PROMPT = $Prompt
$env:TEST_QWEN_MAX_TOKENS = [string]$MaxTokens

@'
import base64
import json
import mimetypes
import os
from pathlib import Path

import httpx

api_url = os.environ["TEST_QWEN_API_URL"].rstrip("/")
api_key = os.environ["TEST_QWEN_API_KEY"]
model = os.environ["TEST_QWEN_MODEL"]
image_path = os.environ.get("TEST_QWEN_IMAGE_PATH", "")
image_url = os.environ.get("TEST_QWEN_IMAGE_URL", "")
prompt = os.environ.get("TEST_QWEN_PROMPT", "请只回答：连接测试成功。")
max_tokens = int(os.environ.get("TEST_QWEN_MAX_TOKENS", "128"))

if image_path:
    path = Path(image_path)
    mime = mimetypes.guess_type(path.name)[0] or "image/jpeg"
    image_url = "data:%s;base64,%s" % (mime, base64.b64encode(path.read_bytes()).decode("ascii"))

payload = {
    "model": model,
    "messages": [
        {
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": image_url}},
                {"type": "text", "text": prompt},
            ],
        }
    ],
    "max_tokens": max_tokens,
    "temperature": 0,
    "enable_thinking": False,
}

print("POST", api_url + "/chat/completions")
print("model", model)
print("image", "local base64" if image_path else image_url)
with httpx.Client(timeout=180, http2=False, follow_redirects=True) as client:
    response = client.post(
        api_url + "/chat/completions",
        headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"},
        content=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
    )
print("status", response.status_code)
print(response.text[:2000])
response.raise_for_status()
'@ | & $python -
