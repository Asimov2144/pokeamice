# -*- coding: utf-8 -*-
import os
import glob
import cv2
import numpy as np

def load_img(path):
    return cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)

folder = r"E:\Pokeamice\scan\DREAM 2011.1改\DREAM 2011.1改"
files = sorted(glob.glob(os.path.join(folder, "*.jpg")))

# Exclude page024 (duplicate of page025)
files = [f for f in files if os.path.basename(f) != "page024.jpg"]

print(f"Analyzing {len(files)} files for border crop...")

for f in files:
    fname = os.path.basename(f)
    img = load_img(f)
    h, w = img.shape[:2]
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Check 10 pixels on each edge: mean brightness
    top_bar = np.mean(gray[:10, :])
    btm_bar = np.mean(gray[-10:, :])
    left_bar = np.mean(gray[:, :10])
    right_bar = np.mean(gray[:, -10:])
    
    # Check if there is black border (< 35) or white scanner edge (> 240)
    print(f"{fname:<12} | shape: {w}x{h} | T: {top_bar:5.1f} | B: {btm_bar:5.1f} | L: {left_bar:5.1f} | R: {right_bar:5.1f}")
