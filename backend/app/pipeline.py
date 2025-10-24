import cv2
from core.io import to_bgr, to_gray
from core.denoise import median_filter
from core.mask import apply_circular_mask


DEFAULT_DP = 1.2
DEFAULT_MIN_DIST_FRACTION = 0.5
DEFAULT_MIN_RADIUS_FRACTION = 0.35
DEFAULT_MAX_RADIUS_FRACTION = 0.65
DEFAULT_PARAM1 = 150
DEFAULT_PARAM2 = 50


def run_pipeline(
    file_bytes: bytes,
    *,
    dp: float = DEFAULT_DP,
    min_dist_fraction: float = DEFAULT_MIN_DIST_FRACTION,
    min_radius_fraction: float = DEFAULT_MIN_RADIUS_FRACTION,
    max_radius_fraction: float = DEFAULT_MAX_RADIUS_FRACTION,
    param1: float = DEFAULT_PARAM1,
    param2: float = DEFAULT_PARAM2,
):
    # 1. Load and convert
    bgr = to_bgr(file_bytes)
    gray = to_gray(bgr)

    # 2. Denoise
    gray_blurred = median_filter(gray, 25)

    height, width = gray_blurred.shape[:2]
    min_dimension = min(height, width)

    min_dist = min_dimension * min_dist_fraction
    min_radius = max(1.0, min_dimension * min_radius_fraction)
    max_radius = max(min_radius + 1.0, min_dimension * max_radius_fraction)

    min_radius_int = int(round(min_radius))
    max_radius_int = int(round(max_radius))
    if max_radius_int <= min_radius_int:
        max_radius_int = min_radius_int + 1

    circles = cv2.HoughCircles(
        image=gray_blurred,
        method=cv2.HOUGH_GRADIENT,
        dp=dp,
        minDist=min_dist,
        param1=param1,
        param2=param2,
        minRadius=min_radius_int,
        maxRadius=max_radius_int,
    )

    final_image = apply_circular_mask(bgr, circles)

    return final_image