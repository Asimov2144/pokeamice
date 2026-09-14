# -*- coding: utf-8 -*-
import cv2
import numpy as np
from PIL import Image

def load_img(path):
    return cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)

p1 = r"E:\Pokeamice\scan\DREAM 2011.1改\DREAM 2011.1改\page024.jpg"
p2 = r"E:\Pokeamice\scan\DREAM 2011.1改\DREAM 2011.1改\page025.jpg"

img1 = load_img(p1)
img2 = load_img(p2)

print(f"page024 shape: {img1.shape}")
print(f"page025 shape: {img2.shape}")

lap1 = cv2.Laplacian(cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()
lap2 = cv2.Laplacian(cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()

print(f"page024 sharpness: {lap1:.2f}")
print(f"page025 sharpness: {lap2:.2f}")
