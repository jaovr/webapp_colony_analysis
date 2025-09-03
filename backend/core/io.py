import cv2, numpy as np

# Decodes raw image bytes into a BGR color image (3 channels).
def to_bgr(np_bytes: bytes):
    arr = np.frombuffer(np_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Error: Fail to decode the image.")
    return img

# Converts a BGR color image into a single-channel grayscale image.
def to_gray(bgr: np.ndarray):
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

