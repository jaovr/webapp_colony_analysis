import cv2
import numpy as np


def _enhance_contrast(channel: np.ndarray) -> np.ndarray:
    """Enhance local contrast and suppress slow-varying illumination."""

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(channel)

    # Remove the low-frequency background to emphasise colonies.
    blurred_background = cv2.GaussianBlur(enhanced, (0, 0), sigmaX=21, sigmaY=21)
    high_pass = cv2.subtract(enhanced, blurred_background)
    normalized = cv2.normalize(high_pass, None, 0, 255, cv2.NORM_MINMAX)

    return normalized.astype(np.uint8)


def detect_colony_regions(
    masked_bgr: np.ndarray,
    min_area_ratio: float = 2e-4,
    max_area_ratio: float = 1.5e-2,
    min_circularity: float = 0.25,
    min_extent: float = 0.45,
    max_axis_ratio: float = 2.2,
    min_solidity: float = 0.8,
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
    min_extent:
        Minimum ratio between the contour area and its bounding box area.
    max_axis_ratio:
        Maximum ratio between the major and minor axes derived from the contour moments.
    min_solidity:
        Minimum ratio between the contour area and its convex hull area.

    Returns
    -------
    colony_mask: np.ndarray
        Binary mask (uint8) with detected colony regions set to 255.
    annotated: np.ndarray
        BGR image with an overlay highlighting the detected colonies.
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

    lab = cv2.cvtColor(masked_bgr, cv2.COLOR_BGR2LAB)
    lightness = lab[:, :, 0]
    enhanced = _enhance_contrast(lightness)

    enhanced = cv2.GaussianBlur(enhanced, (5, 5), 0)
    _, binary = cv2.threshold(
        enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    binary = cv2.bitwise_and(binary, binary, mask=dish_mask)

    # Otsu sometimes favours the bright agar instead of the darker colonies.
    # If most of the dish turned white we flip the polarity and treat the
    # darker spots as foreground instead.
    foreground_ratio = (
        float(cv2.countNonZero(binary)) / float(dish_area) if dish_area else 0.0
    )
    if foreground_ratio > 0.35:
        _, binary = cv2.threshold(
            enhanced, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )
        binary = cv2.bitwise_and(binary, binary, mask=dish_mask)

    kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel_open, iterations=1)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel_close, iterations=1)

    if cv2.countNonZero(cleaned) == 0:
        return np.zeros_like(cleaned), masked_bgr, []

    sure_bg = cv2.dilate(cleaned, kernel_close, iterations=1)
    distance = cv2.distanceTransform(cleaned, cv2.DIST_L2, 3)
    if distance.max() > 0:
        _, sure_fg = cv2.threshold(distance, 0.35 * distance.max(), 1.0, cv2.THRESH_BINARY)
    else:
        sure_fg = np.zeros_like(distance)
    sure_fg = sure_fg.astype(np.uint8)
    unknown = cv2.subtract(sure_bg, sure_fg * 255)

    _, markers = cv2.connectedComponents(sure_fg)
    markers = markers + 1
    markers[unknown == 255] = 0

    # Watershed expects a 3-channel image and modifies the marker array in place.
    watershed_input = cv2.cvtColor(masked_bgr, cv2.COLOR_BGR2RGB)
    cv2.watershed(watershed_input, markers)

    min_area = max(30, int(dish_area * min_area_ratio))
    max_area = int(dish_area * max_area_ratio) if max_area_ratio else None

    colony_mask = np.zeros_like(cleaned)
    colonies: list[dict] = []

    unique_labels = np.unique(markers)
    for label in unique_labels:
        if label <= 1:
            # Background and watershed boundaries are labelled with values <= 1.
            continue

        component_mask = np.uint8(markers == label) * 255
        component_mask = cv2.bitwise_and(component_mask, component_mask, mask=dish_mask)

        contours, _ = cv2.findContours(
            component_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        if not contours:
            continue

        contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(contour)
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

        x, y, w, h = cv2.boundingRect(contour)
        bounding_area = w * h
        if bounding_area == 0:
            continue
        extent = area / bounding_area
        if extent < min_extent:
            continue

        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        if hull_area == 0:
            continue
        solidity = area / hull_area
        if solidity < min_solidity:
            continue

        moments = cv2.moments(contour)
        if moments["m00"] == 0:
            continue

        cov_xx = moments["mu20"] / moments["m00"]
        cov_yy = moments["mu02"] / moments["m00"]
        cov_xy = moments["mu11"] / moments["m00"]
        covariance = np.array([[cov_xx, cov_xy], [cov_xy, cov_yy]])
        eigenvalues = np.linalg.eigvalsh(covariance)
        if not np.all(np.isfinite(eigenvalues)) or eigenvalues[0] <= 0:
            continue
        axis_ratio = np.sqrt(eigenvalues[1] / eigenvalues[0])
        if axis_ratio > max_axis_ratio:
            continue

        cv2.drawContours(colony_mask, [contour], -1, 255, thickness=cv2.FILLED)

        cx = int(moments["m10"] / moments["m00"])
        cy = int(moments["m01"] / moments["m00"])

        colonies.append(
            {
                "area": int(round(area)),
                "centroid": (cx, cy),
                "bbox": (int(x), int(y), int(w), int(h)),
                "circularity": float(round(circularity, 3)),
            }
        )

    annotated = masked_bgr.copy()
    if colonies:
        overlay = annotated.copy()
        contours, _ = cv2.findContours(
            colony_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        cv2.drawContours(overlay, contours, -1, (70, 220, 70), thickness=cv2.FILLED)
        annotated = cv2.addWeighted(overlay, 0.4, annotated, 0.6, 0)

        for colony in colonies:
            cx, cy = colony["centroid"]
            cv2.circle(annotated, (cx, cy), 3, (0, 0, 255), -1)

    return colony_mask, annotated, colonies
