import cv2
import numpy as np
from core.io import to_bgr, to_gray
from core.denoise import median_filter
from core.mask import apply_circular_mask


def run_pipeline(file_bytes: bytes):
    # 1. Load and convert
    bgr = to_bgr(file_bytes)
    gray = to_gray(bgr)

    # 2. Denoise
    gray_blurred = median_filter(gray, 25)

    circles = cv2.HoughCircles(
        image=gray_blurred,
        method=cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=1000,
        param1=100,
        param2=80,
        minRadius=800,
        maxRadius=1200
    )

    final_image = apply_circular_mask(bgr, circles)

    return final_image