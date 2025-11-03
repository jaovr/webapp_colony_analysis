# test_pipeline.py
import cv2
from app.pipeline import run_pipeline

img_path = "./app/971.jpg"  # coloca o caminho da imagem aqui

with open(img_path, "rb") as f:
    result, meta = run_pipeline(f.read(), debug_dir="debug")

cv2.namedWindow("Result", cv2.WINDOW_NORMAL)
cv2.imshow("Result", result)
cv2.waitKey(0)
cv2.destroyAllWindows()
