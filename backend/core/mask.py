import cv2
import numpy as np

def apply_circular_mask(bgr_image, circles):

    if circles is None:
        return bgr_image


    circles = np.round(circles[0,:]).astype("int")
    (x, y, r) = circles[0]

    mask = np.zeros(bgr_image.shape[:2], dtype=np.uint8)

    cv2.circle(mask, (x, y), r, 255, -1)

    masked_image = cv2.bitwise_and(bgr_image, bgr_image, mask=mask)

    return masked_image
