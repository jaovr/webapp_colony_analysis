import cv2

# Performs global histogram equalization to enhance overall contrast.
def equalize(gray):
    return cv2.equalizeHist(gray)


# Applies CLAHE (adaptive histogram equalization) for local contrast enhancement.
def clahe(gray, clip_limit: float = 2.0, tile_grid_size=(8,8)):
    c = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    return c.apply(gray)
