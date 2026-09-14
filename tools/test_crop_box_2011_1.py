# -*- coding: utf-8 -*-
import os
import glob
import cv2
import numpy as np

def load_img(path):
    return cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)

folder = r"E:\Pokeamice\scan\DREAM 2011.1改\DREAM 2011.1改"
files = sorted(glob.glob(os.path.join(folder, "*.jpg")))
files = [f for f in files if os.path.basename(f) != "page024.jpg"]

def detect_crop_box(img, fname):
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Check top for black bars (mean brightness < 30) or extreme white (> 253 across line)
    t = 0
    while t < min(150, h // 10):
        row_mean = np.mean(gray[t, :])
        # if it's very dark (black scanner edge)
        if row_mean < 35:
            t += 1
        else:
            break
            
    b = h
    while b > max(h - 150, h * 9 // 10):
        row_mean = np.mean(gray[b - 1, :])
        if row_mean < 35:
            b -= 1
        else:
            break
            
    l = 0
    while l < min(150, w // 10):
        col_mean = np.mean(gray[:, l])
        if col_mean < 35:
            l += 1
        else:
            break
            
    r = w
    while r > max(w - 150, w * 9 // 10):
        col_mean = np.mean(gray[:, r - 1])
        if col_mean < 35:
            r -= 1
        else:
            break
            
    return (l, t, r, b)

print(f"{'Filename':<12} | {'Orig WxH':<12} | {'Crop (L, T, R, B)':<25} | {'New WxH':<12}")
print("-" * 70)
for f in files:
    fname = os.path.basename(f)
    img = load_img(f)
    h, w = img.shape[:2]
    l, t, r, b = detect_crop_box(img, fname)
    print(f"{fname:<12} | {w}x{h:<8} | ({l:3d}, {t:3d}, {r:4d}, {b:4d}) | {r-l}x{b-t}")
