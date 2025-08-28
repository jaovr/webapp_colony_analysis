from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware   # <-- IMPORT CORS
import cv2, io
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========= OPS =========

def to_bgr(np_bytes: bytes) -> np.ndarray:
    array = np.frombuffer(np_bytes, np.uint8)
    image = cv2.imdecode(array, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Fail to image decode")
    return image

def to_gray(bgr: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

def box_blur(image: np.ndarray, k=10) -> np.ndarray:
    if isinstance(k, int):
        k = (k, k)
    return cv2.blur(image, k)

def to_jpeg_bytes(image: np.ndarray) -> bytes:
    ok, buf = cv2.imencode(".jpg", image)      # <-- ENCODE, não decode
    if not ok:
        raise ValueError("Fail to convert image to JPEG")
    return buf.tobytes()                        # <-- tobytes()

def stream(image: np.ndarray) -> StreamingResponse:   # <-- ndarray
    return StreamingResponse(io.BytesIO(to_jpeg_bytes(image)), media_type="image/jpeg")

# ======== PIPELINE ========

def pipeline_gray(bgr_img: np.ndarray):
    g = to_gray(bgr_img)
    return {"gray": g}

# ======== ENDPOINTS ========

@app.post("/gray/")
async def gray(imagem: UploadFile = File(...)):
    try:
        content = await imagem.read()
        bgr = to_bgr(content)
        out = pipeline_gray(bgr)
        return stream(out["gray"])
    except Exception as e:
        # transforma em erro HTTP legível no /docs
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/blur/")
async def blur_endpoint(imagem: UploadFile = File(...), k: int = 10):
    try:
        content = await imagem.read()
        bgr = to_bgr(content)
        blurred = box_blur(bgr, k)
        return stream(blurred)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
