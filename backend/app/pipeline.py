import cv2
import numpy as np
from typing import Dict, Optional, Tuple

from core.io import to_bgr, to_gray
from core.denoise import median_filter
from core.mask import apply_circular_mask


def _resize(image: np.ndarray, output_size: Tuple[int, int]) -> np.ndarray:
    """Resize the provided image to the desired output size."""
    if image is None:
        return image

    width, height = output_size
    return cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)


def run_pipeline(
    file_bytes: bytes,
    output_size: Optional[Tuple[int, int]] = (224, 224),
) -> Dict[str, np.ndarray]:
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

    masked_bgr = apply_circular_mask(bgr, circles)
    masked_gray = apply_circular_mask(gray, circles)

    if output_size is not None:
        masked_bgr = _resize(masked_bgr, output_size)
        masked_gray = _resize(masked_gray, output_size)

    rgb_image = cv2.cvtColor(masked_bgr, cv2.COLOR_BGR2RGB)
    rgb_image = rgb_image.astype(np.float32) / 255.0

    gray_image = masked_gray.astype(np.float32) / 255.0

    return {"rgb": rgb_image, "gray": gray_image}
