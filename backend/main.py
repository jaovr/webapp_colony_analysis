from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import io
import cv2
import numpy as np


# =========================
# App & CORS
# =========================
app = FastAPI(title="Colony Analysis Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # seu frontend (Vite/React)
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# Utilidades / OPS (funções puras)
# =========================
def to_bgr(np_bytes: bytes) -> np.ndarray:
    """Decodifica bytes (upload) -> imagem BGR (uint8)."""
    arr = np.frombuffer(np_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Falha ao decodificar a imagem (arquivo inválido?).")
    return img


def to_gray(bgr: np.ndarray) -> np.ndarray:
    """BGR -> escala de cinza."""
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)


def box_blur(img: np.ndarray, k: int | tuple[int, int] = 10) -> np.ndarray:
    """Blur caixa. Aceita k=int (vira kxk) ou (kx, ky)."""
    if isinstance(k, int):
        k = (k, k)
    return cv2.blur(img, k)


def median_blur(gray: np.ndarray, k: int = 3) -> np.ndarray:
    """Filtro da mediana. k precisa ser ímpar >= 3."""
    if k < 3:
        k = 3
    if k % 2 == 0:
        k += 1
    return cv2.medianBlur(gray, k)


def clahe(gray: np.ndarray, clip: float = 2.0, tile: tuple[int, int] = (8, 8)) -> np.ndarray:
    """Equalização adaptativa (CLAHE) em imagem 8-bit (grayscale)."""
    tx, ty = tile
    tx = max(1, int(tx))
    ty = max(1, int(ty))
    c = cv2.createCLAHE(clipLimit=float(clip), tileGridSize=(tx, ty))
    return c.apply(gray)


def adaptive_thresh(gray: np.ndarray, block: int = 35, C: int = 5) -> np.ndarray:
    """Limiarização adaptativa gaussiana."""
    if block < 3:
        block = 3
    if block % 2 == 0:
        block += 1
    return cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        int(block),
        int(C),
    )


def to_jpeg_bytes(img: np.ndarray) -> bytes:
    """Imagem (NumPy) -> bytes JPEG."""
    ok, buf = cv2.imencode(".jpg", img)
    if not ok:
        raise ValueError("Erro ao converter a imagem para JPEG.")
    return buf.tobytes()


def stream(img: np.ndarray) -> StreamingResponse:
    """Envia imagem como image/jpeg."""
    return StreamingResponse(io.BytesIO(to_jpeg_bytes(img)), media_type="image/jpeg")


# =========================
# Pipelines (composições de ops)
# =========================
def pipeline_gray(bgr_img: np.ndarray) -> dict[str, np.ndarray]:
    g = to_gray(bgr_img)
    return {"gray": g}


def pipeline_advanced(
        bgr_img: np.ndarray,
        *,
        median_k: int = 3,
        clahe_clip: float = 2.0,
        clahe_tile_x: int = 8,
        clahe_tile_y: int = 8,
        block: int = 35,
        C: int = 5,
) -> dict[str, np.ndarray]:
    """Cinza -> mediana -> CLAHE -> threshold adaptativo."""
    g = to_gray(bgr_img)
    g = median_blur(g, median_k)
    g = clahe(g, clahe_clip, (clahe_tile_x, clahe_tile_y))
    bw = adaptive_thresh(g, block, C)
    return {"gray": g, "binary": bw}


# =========================
# Endpoints
# =========================
@app.get("/")
def root():
    return JSONResponse({"ok": True, "message": "Colony Analysis Backend ativo."})


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/gray/")
async def gray_endpoint(imagem: UploadFile = File(...)):
    """Retorna a imagem em escala de cinza."""
    try:
        content = await imagem.read()
        bgr = to_bgr(content)
        out = pipeline_gray(bgr)
        return stream(out["gray"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/blur/")
async def blur_endpoint(imagem: UploadFile = File(...), k: int = 10):
    """Retorna a imagem borrada (blur caixa)."""
    try:
        content = await imagem.read()
        bgr = to_bgr(content)
        blurred = box_blur(bgr, k)
        return stream(blurred)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/advanced/")
async def advanced_endpoint(
        imagem: UploadFile = File(...),
        median_k: int = 3,
        clahe_clip: float = 2.0,
        clahe_tile_x: int = 8,
        clahe_tile_y: int = 8,
        block: int = 35,
        C: int = 5,
):
    """
    Pipeline avançada:
      BGR -> Gray -> Median(median_k) -> CLAHE(clip, tile_x,y) -> Adaptive Threshold(block, C)
    Retorna o binário final (preto/branco).
    """
    try:
        content = await imagem.read()
        bgr = to_bgr(content)
        out = pipeline_advanced(
            bgr,
            median_k=median_k,
            clahe_clip=clahe_clip,
            clahe_tile_x=clahe_tile_x,
            clahe_tile_y=clahe_tile_y,
            block=block,
            C=C,
        )
        return stream(out["binary"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
