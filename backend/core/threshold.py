import cv2

# Applies Otsu's method to find a global threshold that best separates foreground and background.
def otsu(gray):
    _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return th

# Performs adaptive thresholding using a weighted Gaussian mean of local neighborhoods.
def adaptive_gaussian(gray, block_size: int = 11, C: int = 2):
    return cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        block_size, C
    )

# Performs adaptive thresholding using the simple mean of local neighborhoods.
def adaptive_mean(gray, block_size: int = 11, C: int = 2):
    return cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY,
        block_size, C
    )
