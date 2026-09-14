import sys
from pathlib import Path

p = Path("_posts/2000-07-01-interview-nom-special-dialogue-tajiri-ishihara.md")
content = p.read_text(encoding="utf-8")

replacements = [
    (
        "- type: dialogue\n  speaker: N.O.M采访者\n  original: === 前篇第1节：二人的相遇（在爱普生与Game Boy连接线触电般的灵感） ===\n  translation: === 前篇第1节：二人的相遇（在爱普生与Game Boy连接线触电般的灵感） ===\n  note: ''",
        "- type: heading\n  level: 2\n  original: スペシャル対談／前編１・二人の出会い\n  translation: 前篇第1节：二人的相遇（在爱普生与Game Boy通信线触电般的灵感）"
    ),
    (
        "- type: dialogue\n  speaker: N.O.M采访者\n  original: === 前篇第2节：制作宝可梦之前（昆虫采集、《Game Freak》同人志与街机黄金时代） ===\n  translation: === 前篇第2节：制作宝可梦之前（昆虫采集、《Game Freak》同人志与街机黄金时代） ===\n  note: ''",
        "- type: heading\n  level: 2\n  original: スペシャル対談／前編２・ポケモンを作る前\n  translation: 前篇第2节：制作宝可梦之前（昆虫采集、《Game Freak》同人志与街机黄金时代）"
    ),
    (
        "- type: dialogue\n  speaker: N.O.M采访者\n  original: === 前篇第3节：跨越语言之壁的游戏（把人与人真正连接起来的魔法） ===\n  translation: === 前篇第3节：跨越语言之壁的游戏（把人与人真正连接起来的魔法） ===\n  note: ''",
        "- type: heading\n  level: 2\n  original: スペシャル対談／前編３・言葉の壁を越えるゲーム\n  translation: 前篇第3节：跨越语言之壁的游戏（把人与人真正连接起来的魔法）"
    ),
    (
        "- type: dialogue\n  speaker: N.O.M采访者\n  original: === 前篇第4节：放之四海皆准的童年冒险（哪怕身处异国也共通的成长渴望） ===\n  translation: === 前篇第4节：放之四海皆准的童年冒险（哪怕身处异国也共通的成长渴望） ===\n  note: ''",
        "- type: heading\n  level: 2\n  original: スペシャル対談／前編４・世界共通の少年期\n  translation: 前篇第4节：放之四海皆准的童年冒险（哪怕身处异国也共通的成长渴望）"
    ),
    (
        "- type: dialogue\n  speaker: N.O.M采访者\n  original: === 后篇第1节：田尻智与石原恒和的六年（长达六年的漫长艰苦研发与执念） ===\n  translation: === 后篇第1节：田尻智与石原恒和的六年（长达六年的漫长艰苦研发与执念） ===\n  note: ''",
        "- type: heading\n  level: 2\n  original: スペシャル対談／後編１・田尻智と石原恒和の６年\n  translation: 后篇第1节：田尻智与石原恒和的六年（长达六年的漫长艰苦研发与执念）"
    ),
    (
        "- type: dialogue\n  speaker: N.O.M采访者\n  original: === 后篇第2节：宝可梦们的生命感（不是冰冷机械，而是拥有生态与温度的生物） ===\n  translation: === 后篇第2节：宝可梦们的生命感（不是冰冷机械，而是拥有生态与温度的生物） ===\n  note: ''",
        "- type: heading\n  level: 2\n  original: スペシャル対談／後編２・ポケモンたちのリアリティ\n  translation: 后篇第2节：宝可梦们的真实生命感（不是冰冷机械，而是拥有生态与温度的生物）"
    ),
    (
        "- type: dialogue\n  speaker: N.O.M采访者\n  original: === 后篇第3节：多媒体跨界联动（卡牌、动画与衍生周边如何丰满世界观） ===\n  translation: === 后篇第3节：多媒体跨界联动（卡牌、动画与衍生周边如何丰满世界观） ===\n  note: ''",
        "- type: heading\n  level: 2\n  original: スペシャル対談／後編３・複数のメディアが世界観を豊かにする\n  translation: 后篇第3节：多媒体跨界联动（卡牌、动画与衍生周边如何丰满世界观）"
    ),
    (
        "- type: dialogue\n  speaker: N.O.M采访者\n  original: === 後篇第4節：気になる未来（ポケモンシリーズは止まらない新たな挑戦） ===\n  translation: === 后篇第4节：令人瞩目的未来（宝可梦系列永不停步的新挑战） ===\n  note: ''",
        "- type: heading\n  level: 2\n  original: スペシャル対談／後編４・さて気になる続編は……？\n  translation: 后篇第4节：备受瞩目的续作与未来（宝可梦系列永不止步的新征程）"
    )
]

for old, new in replacements:
    assert old in content, f"Could not find: {old[:50]}"
    content = content.replace(old, new, 1)

p.write_text(content, encoding="utf-8")
print("Successfully replaced all 8 headings in taidan post!")
