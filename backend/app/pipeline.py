import cv2
import numpy as np
from core.io import to_bgr, to_gray
from core.denoise import median_filter
from core.mask import apply_circular_mask

def run_pipeline(file_bytes: bytes):
    # 1) Load & gray
    bgr  = to_bgr(file_bytes)
    gray = to_gray(bgr)

    # 2) Denoise + contraste (ajuda muito nessa foto clara)
    gray_blurred = median_filter(gray, 25)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray_eq = clahe.apply(gray_blurred)

    # 3) Dimensões -> parametros adaptativos
    h, w = gray.shape[:2]
    s = min(h, w)
    dp = 1.2
    minDist   = int(s * 0.70)        # um pouco menor que 0.8
    minRadius = int(s * 0.25)        # ampliado p/ essa foto
    maxRadius = int(s * 0.65)        # ampliado p/ essa foto
    param1    = 120                  # Canny alto (baixo = metade)
    param2s   = [70, 60, 50]         # vamos relaxando se não achar

    circles = None

    # 4) Tenta primeiro na imagem equalizada
    for p2 in param2s:
        circles = cv2.HoughCircles(
            image=gray_eq,
            method=cv2.HOUGH_GRADIENT,
            dp=dp,
            minDist=minDist,
            param1=param1,
            param2=p2,
            minRadius=minRadius,
            maxRadius=maxRadius
        )
        if circles is not None and len(circles[0]) > 0:
            break

    # 5) Se ainda não achou, tenta nas bordas Canny (fallback)
    if circles is None:
        edges = cv2.Canny(gray_eq, 60, 120)
        for p2 in param2s:
            circles = cv2.HoughCircles(
                image=edges,
                method=cv2.HOUGH_GRADIENT,
                dp=dp,
                minDist=minDist,
                param1=param1,
                param2=p2,
                minRadius=minRadius,
                maxRadius=maxRadius
            )
            if circles is not None and len(circles[0]) > 0:
                break

    # 6) Aplica máscara só se achou círculo; senão devolve original (ou loga/raise)
    if circles is not None and len(circles[0]) > 0:
        circles = np.uint16(np.around(circles))  # inteiros p/ a máscara
        final_image = apply_circular_mask(bgr, circles)
    else:
        # print("⚠️ Nenhum círculo detectado — ajuste min/maxRadius ou param2.")
        final_image = bgr  # evita crash; você pode levantar um erro aqui

    return final_image
