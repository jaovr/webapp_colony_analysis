from core.io import to_bgr, to_gray
from core.denoise import median_filter
from core.contrast import  equalize


def run_pipeline(file_bytes: bytes):
    # 1. Load and convert
    bgr = to_bgr(file_bytes)
    gray = to_gray(bgr)

    # 2. Denoise
    denoised = median_filter(gray, 5)

    # 3. Enhance contrast
    enhanced = equalize(denoised)

    return enhanced