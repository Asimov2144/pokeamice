import urllib.request, re, html, sys, json
sys.stdout.reconfigure(encoding='utf-8')
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

print("=== 1. PARSING PKMN-0043 (GI HGSS) ===")
u1 = "https://www.gameinformer.com/b/features/archive/2010/03/19/game-freak-pokemon-interview.aspx"
raw1 = urllib.request.urlopen(urllib.request.Request(u1, headers=headers)).read().decode('utf-8')
# Find field-body
m_body = re.search(r'<div class=["\']field-body["\'][^>]*>(.*?)</div>\s*<div class=["\']field-tags["\']', raw1, re.DOTALL | re.I)
body1 = m_body.group(1) if m_body else raw1

# Split by questions and speaker tags
# Questions:
# Q1: "The Pokémon franchise is no stranger to remakes..."
# Q2: "The Pokémon brand is obviously still very alive..."
# Q3: "Where did you get the idea for the pedometer peripheral..."
# Q4: "For fans who have already played Gold and Silver, what surprises can they expect to discover?"
# Q5: "There are tons of Pokémon in existence now. What’s the process internally for creating new Pokémon? How do you come up with concepts and names for each new creature?"
# Q6: "Do you think there’s still room for new players to jump into the Pokémon franchise?..."

# Let's write a clean splitter
raw_text1 = re.sub(r'<[^>]+>', '\n', body1)
raw_text1 = html.unescape(raw_text1)

turns1 = []
# Intro
m_intro = re.search(r'With the exciting release.*?(?=The Pokémon franchise)', raw_text1, re.DOTALL)
if m_intro:
    turns1.append({"speaker": "Game Informer 编者按", "text": m_intro.group(0).strip()})

# Split Q&As
questions = [
    ("The Pokémon franchise is no stranger to remakes.", "Morimoto: This is the second time"),
    ("The Pokémon brand is obviously still very alive and well in Japan", "Morimoto: Because we always add"),
    ("Where did you get the idea for the pedometer peripheral bundled with HeartGold and SoulSilver?", "Ohmori:"),
    ("For fans who have already played Gold and Silver, what surprises can they expect to discover?", "Morimoto:"),
    ("There are tons of Pokémon in existence now. What’s the process internally for creating new Pokémon?", "Unno:"),
    ("Do you think there’s still room for new players to jump into the", "Morimoto:")
]

for q_start, ans_start in questions:
    pos_q = raw_text1.find(q_start)
    if pos_q != -1:
        # Find where answer starts
        pos_a = raw_text1.find(ans_start, pos_q)
        # Find next question or end
        next_pos = len(raw_text1)
        for nq_start, _ in questions:
            p = raw_text1.find(nq_start, pos_a + 10)
            if p != -1 and p < next_pos:
                next_pos = p
        
        q_text = raw_text1[pos_q:pos_a].strip()
        a_text = raw_text1[pos_a:next_pos].strip()
        
        # Strip footer noise from last answer
        for noise in ["Still on the fence", "View the discussion", "Game Informer. All Rights"]:
            if noise in a_text:
                a_text = a_text.split(noise)[0].strip()
                
        turns1.append({"speaker": "Game Informer", "text": q_text})
        
        # Split individual speaker answers inside a_text
        spk_matches = list(re.finditer(r'(Morimoto|Masuda|Ohmori|Unno|Matsushima|Mori):\s*', a_text))
        if spk_matches:
            for idx, sm in enumerate(spk_matches):
                spk = sm.group(1)
                start_idx = sm.end()
                end_idx = spk_matches[idx+1].start() if idx+1 < len(spk_matches) else len(a_text)
                speaker_body = a_text[start_idx:end_idx].strip()
                turns1.append({"speaker": spk, "text": speaker_body})
        else:
            turns1.append({"speaker": "Game Freak 团队", "text": a_text})

print(f"GI HGSS processed into {len(turns1)} distinct turns:")
for t in turns1[:5]:
    print(f"  [{t['speaker']}] {t['text'][:60]}...")
print(f"  ...")
for t in turns1[-3:]:
    print(f"  [{t['speaker']}] {t['text'][:60]}...")
