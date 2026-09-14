import os
import cv2
import numpy as np

folder = r"E:\Pokeamice\scan\DREAM 2012.10"
scratch = r"C:\Users\2144j\.gemini\antigravity\brain\c01b4c66-5dcf-4279-a3dd-5000421d0334\scratch"

pages = [
    {"src": "page001.jpg", "side": "single", "p": 1, "stem": "p001_cover"},
    {"src": "page002.jpg", "side": "odd", "p": 3, "stem": "p003_contents"},
    {"src": "page004.jpg", "side": "even", "p": 22, "stem": "p022_b2w2_legendary"},
    {"src": "page005.jpg", "side": "odd", "p": 23, "stem": "p023_b2w2_legendary"},
    {"src": "page006.jpg", "side": "even", "p": 24, "stem": "p024_b2w2_pickup", "manual": (18, 223, 2341, 3300)},
    {"src": "page007.jpg", "side": "odd", "p": 25, "stem": "p025_b2w2_pokewood"},
    {"src": "page008.jpg", "side": "even", "p": 26, "stem": "p026_b2w2_pwt"},
    {"src": "page012.jpg", "side": "odd", "p": 27, "stem": "p027_b2w2_join_avenue"},
    {"src": "page010.jpg", "side": "even", "p": 28, "stem": "p028_sound_interview"},
    {"src": "page011.jpg", "side": "odd", "p": 29, "stem": "p029_sound_interview"},
    {"src": "page013.jpg", "side": "even", "p": 30, "stem": "p030_pokemon_next_genesect"},
    {"src": "page015.jpg", "side": "odd", "p": 31, "stem": "p031_pokemon_next_contest"},
    {"src": "page016.jpg", "side": "even", "p": 126, "stem": "p126_sales_ranking"},
    {"src": "page017.jpg", "side": "single", "p": 999, "stem": "p999_back_cover"},
]

def find_crop(im300, side, manual=None):
    h, w = im300.shape[:2]
    if manual:
        return manual
    if side == "even":
        left = 18
        right = w - 140
    elif side == "odd":
        left = 115
        right = w - 18
    else:
        left = 18
        right = w - 18

    gray = cv2.cvtColor(im300, cv2.COLOR_BGR2GRAY)
    sobely = np.abs(cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3))

    top_z = sobely[10:500, 40:w-40]
    grad_top = (np.percentile(top_z, 90, axis=1) + np.mean(top_z, axis=1)) / 2.0
    btm_z = sobely[2800:h-10, 40:w-40]
    grad_btm = (np.percentile(btm_z, 90, axis=1) + np.mean(btm_z, axis=1)) / 2.0

    top_peaks = [y + 10 for y in np.where(grad_top > np.max(grad_top)*0.15)[0]]
    btm_peaks = [y + 2800 for y in np.where(grad_btm > np.max(grad_btm)*0.15)[0]]

    best_pair = None
    best_score = -1e9
    for tp in top_peaks:
        for bp in btm_peaks:
            dist = bp - tp
            if 3055 <= dist <= 3085:
                s = grad_top[tp - 10] + grad_btm[bp - 2800] - abs(dist - 3070)*0.5
                if s > best_score:
                    best_score = s
                    best_pair = (tp, bp, dist)

    if best_pair:
        top, btm, dist = best_pair
    else:
        top, btm = 220, 3290
    return left, top, right, btm

cropped_list = []
for p in pages:
    im = cv2.imread(os.path.join(folder, p["src"]))
    im300 = cv2.resize(im, (im.shape[1]//2, im.shape[0]//2), interpolation=cv2.INTER_AREA)
    l, t, r, b = find_crop(im300, p["side"], p.get("manual"))
    crop = im300[t:b, l:r]
    cropped_list.append((p["stem"], crop, (l, t, r, b)))
    print(f"{p['stem']:28s} | crop: [{l:4d}, {t:4d}, {r:4d}, {b:4d}] | size: {crop.shape[1]}x{crop.shape[0]} (H={b-t})")
