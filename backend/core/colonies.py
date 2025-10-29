import cv2
import numpy as np


def _enhance_contrast(channel: np.ndarray) -> np.ndarray:
    """Enhance local contrast to make colonies stand out."""

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(channel)

    background = cv2.GaussianBlur(enhanced, (0, 0), sigmaX=11, sigmaY=11)
    subtracted = cv2.addWeighted(enhanced, 1.5, background, -0.5, 0)
    normalized = cv2.normalize(subtracted, None, 0, 255, cv2.NORM_MINMAX)
    return normalized.astype(np.uint8)


def detect_colony_regions(
    masked_bgr: np.ndarray,
    min_area_ratio: float = 5e-4,
    max_area_ratio: float = 2e-2,
    min_circularity: float = 0.35,
):
    """Detect colony-like regions inside a masked Petri dish.

    Parameters
    ----------
    masked_bgr:
        Image already masked so that pixels outside the dish are zeroed.
    min_area_ratio:
        Minimum area for a component, relative to the disk area.
    max_area_ratio:
        Maximum area for a component, relative to the disk area.
    min_circularity:
        Minimum circularity (4π·area / perimeter²) to keep a component.

    Returns
    -------
    colony_mask: np.ndarray
        Binary mask (uint8) with detected colony regions set to 255.
    annotated: np.ndarray
        BGR image with an overlay highlighting the detected colonies.
        BGR image with contours of the detected colonies drawn for visualization.
    colonies: list[dict]
        Metadata for each colony (area, centroid and bounding box).
    """

    if masked_bgr is None or masked_bgr.size == 0:
        return np.zeros((0, 0), dtype=np.uint8), masked_bgr, []

    lab = cv2.cvtColor(masked_bgr, cv2.COLOR_BGR2LAB)
    a_channel = lab[:, :, 1]

    dish_mask = (a_channel > 0).astype(np.uint8) * 255
    dish_area = int(np.count_nonzero(dish_mask))
    if dish_area == 0:
        return np.zeros_like(a_channel), masked_bgr, []

    enhanced = _enhance_contrast(a_channel)

    adaptive = cv2.adaptiveThreshold(
        enhanced,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        35,
        2,
    )

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    opened = cv2.morphologyEx(adaptive, cv2.MORPH_OPEN, kernel, iterations=1)
    closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel, iterations=2)
    cleaned = cv2.bitwise_and(closed, closed, mask=dish_mask)

    contours, _ = cv2.findContours(
        cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    gray = cv2.cvtColor(masked_bgr, cv2.COLOR_BGR2GRAY)

    dish_mask = (gray > 0).astype(np.uint8) * 255
    dish_area = int(np.count_nonzero(dish_mask))
    if dish_area == 0:
        return np.zeros_like(gray), masked_bgr, []

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    _, colonies_binary = cv2.threshold(
        blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    colonies_binary = cv2.bitwise_and(colonies_binary, colonies_binary, mask=dish_mask)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    cleaned = cv2.morphologyEx(colonies_binary, cv2.MORPH_OPEN, kernel, iterations=2)

    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(cleaned)

    min_area = max(30, int(dish_area * min_area_ratio))
    max_area = int(dish_area * max_area_ratio) if max_area_ratio else None

    colony_mask = np.zeros_like(cleaned)
    colonies = []

    for contour in contours:
        area = cv2.contourArea(contour)
    colony_mask = np.zeros_like(gray)
    colonies = []

    for label in range(1, num_labels):
        area = stats[label, cv2.CC_STAT_AREA]
        if area < min_area:
            continue
        if max_area is not None and area > max_area:
            continue

        perimeter = cv2.arcLength(contour, True)
        if perimeter == 0:
            continue
        circularity = 4 * np.pi * area / (perimeter * perimeter)
        if circularity < min_circularity:
            continue

        mask = np.zeros_like(cleaned)
        cv2.drawContours(mask, [contour], -1, 255, thickness=cv2.FILLED)

        non_zero = cv2.bitwise_and(mask, mask, mask=dish_mask)
        colony_mask = cv2.bitwise_or(colony_mask, non_zero)

        x, y, w, h = cv2.boundingRect(contour)
        moments = cv2.moments(contour)
        if moments["m00"] == 0:
            continue
        cx = int(moments["m10"] / moments["m00"])
        cy = int(moments["m01"] / moments["m00"])

        colonies.append(
            {
                "area": int(round(area)),
                "centroid": (cx, cy),
                "bbox": (int(x), int(y), int(w), int(h)),
                "circularity": float(round(circularity, 3)),
        component_mask = labels == label
        colony_mask[component_mask] = 255

        x = int(stats[label, cv2.CC_STAT_LEFT])
        y = int(stats[label, cv2.CC_STAT_TOP])
        w = int(stats[label, cv2.CC_STAT_WIDTH])
        h = int(stats[label, cv2.CC_STAT_HEIGHT])
        cx, cy = centroids[label]

        colonies.append(
            {
                "area": int(area),
                "centroid": (int(round(cx)), int(round(cy))),
                "bbox": (x, y, w, h),
            }
        )

    annotated = masked_bgr.copy()
    if colonies:
        overlay = annotated.copy()
        contours, _ = cv2.findContours(
            colony_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        cv2.drawContours(overlay, contours, -1, (60, 200, 60), thickness=cv2.FILLED)
        annotated = cv2.addWeighted(overlay, 0.35, annotated, 0.65, 0)
        contours, _ = cv2.findContours(
            colony_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        for contour in contours:
            cv2.drawContours(annotated, [contour], -1, (0, 255, 0), 2)

        for colony in colonies:
            cx, cy = colony["centroid"]
            cv2.circle(annotated, (cx, cy), 3, (0, 0, 255), -1)

    return colony_mask, annotated, colonies
