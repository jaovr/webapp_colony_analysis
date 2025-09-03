import cv2
from core.io import to_bgr, to_gray
from core.denoise import gaussian_filter, median_filter
from core.contrast import equalize


def run_pipeline(file_bytes: bytes):
    # 1) decode + grayscale
    bgr  = to_bgr(file_bytes)
    gray = to_gray(bgr)

    # 2) gaussian blur (ruído geral)
    g = gaussian_filter(gray, 5)

    # 3) median blur (sal e pimenta)
    m = median_filter(g, 5)

    # 4) histogram equalization (global)
    eq = equalize(m)

    return eq
