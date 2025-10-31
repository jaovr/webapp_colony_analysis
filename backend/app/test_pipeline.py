# test_pipeline.py
import cv2, sys
from app.pipeline import run_pipeline

img_path = sys.argv[1] if len(sys.argv)>1 else "./app/971.jpg"
with open(img_path, "rb") as f:
    out, meta = run_pipeline(f.read(), debug_dir="debug")

print(">> círculo da placa:", meta["circle"])
print(">> colônias:", meta["n_colonies"])
print(">> pasta de debug:", meta["debug_dir"])

cv2.namedWindow("result", cv2.WINDOW_NORMAL)
cv2.imshow("result", out)
cv2.waitKey(0)
cv2.destroyAllWindows()
