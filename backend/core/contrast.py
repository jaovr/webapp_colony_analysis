import cv2

# Performs global histogram equalization to enhance overall contrast.
def equalize(gray):
    return cv2.equalizeHist(gray)


