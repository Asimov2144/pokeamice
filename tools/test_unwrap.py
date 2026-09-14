"""Test paragraph unwrapping logic.
"""
import re

def clean_paragraph_text(text: str, is_chinese: bool = False) -> str:
    if not text:
        return ""
    # Normalize nbsp
    text = text.replace("\xa0", " ").replace("\u3000", " ")
    lines = [l.strip() for l in text.split("\n")]
    lines = [l for l in lines if l]
    if not lines:
        return ""
    
    # Determine if text is primarily CJK
    cjk_count = len(re.findall(r"[\u4e00-\u9fa5\u3040-\u30ff]", text))
    total_len = len("".join(lines))
    is_cjk = (cjk_count / max(total_len, 1)) > 0.25

    if is_cjk:
        # For CJK text, join with no space
        result = "".join(lines)
    else:
        # For English/Western text, join with space
        result = " ".join(lines)
        # Collapse multiple spaces
        result = re.sub(r"\s+", " ", result)
    return result

sample_trans = """这个“社长问”系列，原本是从向公司内部人员提问开始的，


    虽然今天二位并不是任天堂内部的人员，


    但我与石原先生也是长年“并肩作战的战友”呢（笑）。


    我自己对于《宝可梦》这款商品也有着非常深厚的缘分，


    因为多年来我一直与石原先生共同制作产品。


     


    当然，今天我们也会聊关于新《宝可梦》的事情，


    不过我觉得从过去的《宝可梦》聊起，


    才能更好地衔接到这次的《心金·魂银》。"""

sample_orig = """社内の人から話を訊くということから


    この「社長が訊く」シリーズははじまりましたが、


    今日は社内の人ではありませんけど、


    石原さんとは、長年“共に戦った仲間”でもあります（笑）。


    わたし自身、『ポケットモンスター』という商品には


    とても深い縁がありまして、


    石原さんとは長年、いっしょにモノをつくってきたからです。


     


    もちろん今日は、新しい『ポケモン』のことも訊きますけど、


    昔の『ポケモン』の話からはじめたほうが、


    今回の『ハートゴールド・ソウルシルバー』に


    つながるように思っています。"""

print("Cleaned Trans:")
print(clean_paragraph_text(sample_trans))
print("\nCleaned Orig:")
print(clean_paragraph_text(sample_orig))
