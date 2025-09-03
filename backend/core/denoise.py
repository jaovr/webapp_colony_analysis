import cv2

# Applies median blur to reduce salt-and-pepper noise while preserving edges.
def median_filter(gray, ksize: int = 5):
    return cv2.medianBlur(gray, ksize)

# Applies Gaussian blur to smooth the image and reduce general noise.
def gaussian_filter(gray, ksize: int = 5, sigma: float = 0):
    return cv2.GaussianBlur(gray, (ksize, ksize), sigma)

# Applies bilateral filtering to reduce noise while keeping sharp edges.
def bilateral_filter(gray, d: int = 9, sigma_color: float = 75, sigma_space: float = 75):
    return cv2.bilateralFilter(gray, d, sigma_color, sigma_space)