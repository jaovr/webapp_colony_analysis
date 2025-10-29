import cv2
import numpy as np


def detect_colony_regions(
    masked_bgr: np.ndarray,
    min_area_ratio: float = 3e-4,
    max_area_ratio: float = 5e-2,
):
    """Detect connected regions that resemble colonies inside a masked Petri dish.

    Parameters
    ----------
    masked_bgr:
        Image already masked so that pixels outside the dish are zeroed.
    min_area_ratio:
        Minimum area for a component, relative to the disk area.
    max_area_ratio:
        Maximum area for a component, relative to the disk area.

    Returns
    -------
    colony_mask: np.ndarray
        Binary mask (uint8) with detected colony regions set to 255.
    annotated: np.ndarray
        BGR image with contours of the detected colonies drawn for visualization.
    colonies: list[dict]
        Metadata for each colony (area, centroid and bounding box).
    """

    if masked_bgr is None or masked_bgr.size == 0:
        return np.zeros((0, 0), dtype=np.uint8), masked_bgr, []

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

    colony_mask = np.zeros_like(gray)
    colonies = []

    for label in range(1, num_labels):
        area = stats[label, cv2.CC_STAT_AREA]
        if area < min_area:
            continue
        if max_area is not None and area > max_area:
            continue

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
        contours, _ = cv2.findContours(
            colony_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        for contour in contours:
            cv2.drawContours(annotated, [contour], -1, (0, 255, 0), 2)

        for colony in colonies:
            cx, cy = colony["centroid"]
            cv2.circle(annotated, (cx, cy), 3, (0, 0, 255), -1)

    return colony_mask, annotated, colonies
