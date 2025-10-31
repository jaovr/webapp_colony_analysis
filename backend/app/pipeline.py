# pipeline.py
import cv2, os, uuid
import numpy as np
from core.io import to_bgr, to_gray
from core.denoise import median_filter
from core.mask import apply_circular_mask


def _save(path, img):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cv2.imwrite(path, img)


def run_pipeline(file_bytes: bytes, debug_dir: str | None = None):
    """Detecta o círculo da placa e retorna a imagem mascarada."""
    run_id = (str(uuid.uuid4())[:8])
    ddir = None if debug_dir is None else os.path.join(debug_dir, run_id)

    # 1) Carregar e converter
    bgr = to_bgr(file_bytes)
    gray = to_gray(bgr)
    if ddir:
        _save(f"{ddir}/00_input.jpg", bgr)
        _save(f"{ddir}/10_gray.png", gray)

    # 2) Filtro e contraste
    gray_blurred = median_filter(gray, 25)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray_eq = clahe.apply(gray_blurred)
    if ddir:
        _save(f"{ddir}/20_median.png", gray_blurred)
        _save(f"{ddir}/30_clahe.png", gray_eq)

    # 3) Parâmetros do Hough
    h, w = gray.shape[:2]
    s = min(h, w)
    dp = 1.2
    minDist = int(s * 0.70)
    minRadius = int(s * 0.25)
    maxRadius = int(s * 0.65)
    param1 = 120
    param2 = 60
    print(f"[Hough] h×w={h}×{w}  s={s}  dp={dp}  minDist={minDist}  r∈[{minRadius},{maxRadius}]  p1={param1} p2={param2}")

    # 4) Detectar o círculo da placa
    circles = cv2.HoughCircles(
        image=gray_eq,
        method=cv2.HOUGH_GRADIENT,
        dp=dp,
        minDist=minDist,
        param1=param1,
        param2=param2,
        minRadius=minRadius,
        maxRadius=maxRadius,
    )

    # 5) Visualizar detecção
    preview = bgr.copy()
    if circles is not None and len(circles[0]) > 0:
        circles = np.uint16(np.around(circles))
        x, y, r = map(int, circles[0][0])
        cv2.circle(preview, (x, y), r, (0, 255, 0), 3)
        cv2.circle(preview, (x, y), 2, (0, 0, 255), -1)
        print(f"[Hough] círculo detectado: x={x}, y={y}, r={r}")
    else:
        print("[Hough] nenhum círculo detectado")
        if ddir:
            _save(f"{ddir}/40_hough_preview_FAIL.jpg", bgr)
        return bgr, {"circle": None, "debug_dir": ddir}

    if ddir:
        _save(f"{ddir}/40_hough_preview.jpg", preview)

    # 6) Aplicar máscara circular
    masked = apply_circular_mask(bgr, circles)
    if ddir:
        _save(f"{ddir}/50_masked.jpg", masked)

    return masked, {"circle": [x, y, r], "debug_dir": ddir}
