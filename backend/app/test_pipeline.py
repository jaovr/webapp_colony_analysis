import cv2
from app.pipeline import run_pipeline

img_path = "./app/11890.jpg"

with open(img_path, "rb") as f:
    file_bytes = f.read()

result = run_pipeline(file_bytes)

cv2.namedWindow("Result", cv2.WINDOW_NORMAL)
cv2.imshow("Result", result)
cv2.waitKey(0)
cv2.destroyAllWindows()
