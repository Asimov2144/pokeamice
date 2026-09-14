#!/usr/bin/env python3
"""Remediate all identified translation and formatting quality issues:
1. Strip scraper footer noise from legacy translated posts.
2. Clean HTML entities (&quot;, &#39;, &amp;) in titles and translations.
3. Fix speaker prefix leaks into dialogue text.
4. Batch-translate all untranslated Japanese captions across 22 posts using DeepSeek API.
"""

import os
import re
import sys
import json
import time
import urllib.request
import ssl
from pathlib import Path
from collections import defaultdict
import yaml

sys.stdout.reconfigure(encoding="utf-8")

POSTS_DIR = Path("_posts")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

NOISE_SUBSTRINGS = [
    "This page has been viewed",
    "本页面已被浏览",
    "此页面已被浏览",
    "Last updated",
    "最后更新：",
    "Revision #",
    "修订版本 #",
    "Pokémon, all assorted characters, images and audio are ©",
    "宝可梦、所有相关角色、图像和音频均©",
    "宝可梦、所有相关角色、图像和音频版权均归 ©",
    "About Us | Contact Us",
    "关于我们 | 联系我们",
    "Interactive: #Pocketmonsters",
    "互动：#Pocketmonsters",
    "Official Sites/Stores:",
    "官方网站/商店：",
    "Affiliates:",
    "合作伙伴：",
]

KANA = re.compile(r"[\u3040-\u309f\u30a0-\u30ff]")


def clean_noise_and_entities_and_speakers():
    posts = sorted(POSTS_DIR.glob("*interview*.md"))
    modified_count = 0

    for p in posts:
        content = p.read_text(encoding="utf-8")
        parts = content.split("---", 2)
        if len(parts) < 3:
            continue

        try:
            fm = yaml.safe_load(parts[1])
        except Exception as e:
            print(f"YAML load error {p.name}: {e}")
            continue

        changed = False

        # 1. Clean HTML entities in title
        title = fm.get("title", "")
        if "&quot;" in title or "&#39;" in title or "&amp;" in title:
            clean_title = (
                title.replace("&quot;", "“")
                .replace("&#39;", "'")
                .replace("&amp;", "&")
            )
            fm["title"] = clean_title
            changed = True
            print(f"[{p.name}] Fixed title entity: {clean_title}")

        items = fm.get("parallel_items", [])
        clean_items = []

        for idx, it in enumerate(items):
            if not isinstance(it, dict):
                clean_items.append(it)
                continue

            orig = str(it.get("original", "")).strip()
            trans = str(it.get("translation", "")).strip()
            spk = str(it.get("speaker", "")).strip()
            itype = it.get("type", "paragraph")

            # Check noise
            is_noise = False
            for ns in NOISE_SUBSTRINGS:
                if ns.lower() in orig.lower() or ns.lower() in trans.lower():
                    is_noise = True
                    break
            if is_noise:
                changed = True
                print(f"[{p.name}] Removed footer noise item: {trans[:50]}")
                continue

            # Clean entities in trans
            if "&quot;" in trans or "&#39;" in trans:
                trans = trans.replace("&quot;", "“").replace("&#39;", "'")
                it["translation"] = trans
                changed = True

            # Fix speaker prefix leaks
            if itype == "paragraph" and not spk:
                m = re.match(r"^([^\s:：]{2,6})[:：]\s*(.*)$", trans)
                if m:
                    cand_spk = m.group(1)
                    rest_text = m.group(2).strip()
                    if cand_spk in ["增田", "大森", "杉森", "石原", "田尻", "森本", "海野", "岩尾", "西野", "西田"]:
                        full_name_map = {
                            "增田": "增田顺一",
                            "大森": "大森滋",
                            "杉森": "杉森建",
                            "石原": "石原恒和",
                            "田尻": "田尻智",
                            "森本": "森本茂树",
                            "海野": "海野隆雄",
                            "岩尾": "岩尾和昌",
                            "西野": "西野弘二",
                            "西田": "西田敦子",
                        }
                        it["speaker"] = full_name_map.get(cand_spk, cand_spk)
                        it["translation"] = rest_text
                        orig_m = re.match(r"^([^\s:：]{1,6})[:：]\s*(.*)$", orig)
                        if orig_m:
                            it["original"] = orig_m.group(2).strip()
                        changed = True
                        print(f"[{p.name}] Normalized speaker {it['speaker']}: {rest_text[:40]}")

            clean_items.append(it)

        if changed:
            fm["parallel_items"] = clean_items
            new_yaml = yaml.dump(fm, allow_unicode=True, sort_keys=False, width=1000)
            p.write_text(f"---\n{new_yaml}---\n{parts[2].lstrip()}", encoding="utf-8")
            modified_count += 1

    print(f"\nCompleted cleanup of noise, entities, and speaker leaks. Modified {modified_count} posts.\n")


def translate_captions():
    posts = sorted(POSTS_DIR.glob("*interview*.md"))
    
    # Collect all captions needing translation
    to_translate = []
    for p in posts:
        content = p.read_text(encoding="utf-8")
        parts = content.split("---", 2)
        if len(parts) < 3:
            continue
        try:
            fm = yaml.safe_load(parts[1])
        except:
            continue
            
        items = fm.get("parallel_items", [])
        for idx, it in enumerate(items):
            if not isinstance(it, dict):
                continue
            cap = it.get("caption", "")
            if cap and len(KANA.findall(cap)) > 4:
                to_translate.append((p.name, idx, cap))

    print(f"Found {len(to_translate)} Japanese captions to translate across posts.")
    if not to_translate:
        return

    # Batch translate using DeepSeek
    batch_size = 25
    translated_map = {}

    for i in range(0, len(to_translate), batch_size):
        chunk = to_translate[i : i + batch_size]
        print(f"Translating chunk {i+1} to {min(i+batch_size, len(to_translate))}...")
        
        prompt_items = []
        for c_idx, (pname, item_idx, text) in enumerate(chunk):
            prompt_items.append(f"[{c_idx}] {text}")
            
        system_prompt = """你是一位精通宝可梦（Pokémon）系列官方设定与游戏开发的资深汉化翻译专家。
请将以下来自宝可梦官方访谈、开发幕后报道中的图片说明文字（Caption）翻译为自然、准确、符合官方规范的简体中文。
要求：
1. 采用官方简体中文译名（如：宝可梦、皮卡丘、增田顺一、杉森建、大森滋、海野隆雄、石原恒和、黑／白、红／绿、金／银、心金／魂银、剑／盾、朱／紫等）。
2. 保留原意与语气，专有名词（如系统名称、PWT、ポケウッド、メガシンカ等）翻译准确。
3. 严格以 JSON 格式输出，返回一个包含所有序号对应译文的 JSON 对象，形如：{"0": "译文0", "1": "译文1", ...}。不要输出任何额外的解释或 Markdown 格式以外的文字。"""

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "\n".join(prompt_items)},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
        }

        req = urllib.request.Request(
            DEEPSEEK_URL,
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
            },
            data=json.dumps(payload).encode("utf-8"),
        )

        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, context=ssl_ctx, timeout=60) as resp:
                    resp_data = json.loads(resp.read().decode("utf-8"))
                    res_str = resp_data["choices"][0]["message"]["content"]
                    res_json = json.loads(res_str)
                    
                    for c_idx, (pname, item_idx, orig_text) in enumerate(chunk):
                        trans = res_json.get(str(c_idx)) or res_json.get(c_idx)
                        if trans:
                            translated_map[(pname, item_idx)] = trans.strip()
                    break
            except Exception as e:
                print(f"  Attempt {attempt+1} error: {e}")
                time.sleep(2)

    print(f"Successfully translated {len(translated_map)} / {len(to_translate)} captions.")

    # Write back to files
    posts_to_update = defaultdict(dict)
    for (pname, idx), trans in translated_map.items():
        posts_to_update[pname][idx] = trans

    for pname, idx_map in posts_to_update.items():
        p = POSTS_DIR / pname
        content = p.read_text(encoding="utf-8")
        parts = content.split("---", 2)
        if len(parts) < 3:
            continue
        fm = yaml.safe_load(parts[1])
        items = fm.get("parallel_items", [])
        for idx, trans in idx_map.items():
            if idx < len(items) and isinstance(items[idx], dict):
                items[idx]["caption"] = trans
        fm["parallel_items"] = items
        new_yaml = yaml.dump(fm, allow_unicode=True, sort_keys=False, width=1000)
        p.write_text(f"---\n{new_yaml}---\n{parts[2].lstrip()}", encoding="utf-8")
        print(f"Updated {len(idx_map)} captions in {pname}")


if __name__ == "__main__":
    print("=== Step 1: Cleaning noise, HTML entities, and speaker leaks ===")
    clean_noise_and_entities_and_speakers()
    print("=== Step 2: Translating Japanese captions with DeepSeek ===")
    translate_captions()
    print("=== Remediation Completed ===")
