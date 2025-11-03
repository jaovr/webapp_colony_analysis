# pipeline.py
import cv2, os, uuid
import numpy as np
import matplotlib.pyplot as plt  # <-- adicionado para análise
from core.io import to_bgr, to_gray
from core.denoise import median_filter
from core.mask import apply_circular_mask
from core.contrast import equalize
from numpy.ma.core import bitwise_or


def _save(path, img):
    """Salva imagem de debug."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cv2.imwrite(path, img)


def run_pipeline(file_bytes: bytes, debug_dir: str | None = None):
    """Detecta o círculo da placa e realiza a contagem das colônias."""
    run_id = (str(uuid.uuid4())[:8])
    ddir = None if debug_dir is None else os.path.join(debug_dir, run_id)

    # 1) Carregar imagem e converter
    bgr = to_bgr(file_bytes)
    gray = to_gray(bgr)

    if ddir:
        _save(f"{ddir}/00_input.jpg", bgr)
        _save(f"{ddir}/10_gray.png", gray)

    # 2) Filtro e equalização de contraste
    gray_blurred = median_filter(gray, 25)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray_eq = clahe.apply(gray_blurred)

    if ddir:
        _save(f"{ddir}/20_median.png", gray_blurred)
        _save(f"{ddir}/30_clahe.png", gray_eq)

    # 3) Configurações do detector de círculo (Hough)
    h, w = gray.shape[:2]
    s = min(h, w)
    dp = 1.2
    minDist = int(s * 0.70)
    minRadius = int(s * 0.25)
    maxRadius = int(s * 0.65)
    param1 = 120
    param2 = 60
    print(f"[Hough] h×w={h}×{w}  s={s}  dp={dp}  minDist={minDist}  "
          f"r∈[{minRadius},{maxRadius}]  p1={param1} p2={param2}")

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

    # 5) Verificar e visualizar círculo
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

    # 6) Aplicar máscara circular principal
    masked = apply_circular_mask(bgr, circles)
    if ddir:
        _save(f"{ddir}/50_masked.jpg", masked)

    # 7) Converter e equalizar para análise
    gray_2 = to_gray(masked)
    equalize_img = equalize(gray_2)

    # --- Contagem de colônias com refinamento ---

    # Máscara menor (evita bordas da placa)
    mask = np.zeros_like(equalize_img)
    cv2.circle(mask, (x, y), int(r * 0.9), 255, -1)
    masked_inner = cv2.bitwise_and(equalize_img, equalize_img, mask=mask)

    # Binarização e limpeza morfológica
    blurred = cv2.medianBlur(masked_inner, 5)
    binary = cv2.adaptiveThreshold(blurred, 255,
                                   cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV,
                                   11, 2)
    kernel = np.ones((3, 3), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=1)

    # Encontrar contornos
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # --- Análise de áreas detectadas (debug) ---
    areas = [cv2.contourArea(c) for c in contours if cv2.contourArea(c) > 0]
    if len(areas) > 0:
        print(f"Total de contornos detectados: {len(areas)}")
        print(f"Área mínima: {np.min(areas):.2f}, máxima: {np.max(areas):.2f}")
        plt.figure(figsize=(6, 4))
        plt.hist(areas, bins=50, color='gray', edgecolor='black')
        plt.title("Distribuição das Áreas dos Contornos Detectados")
        plt.xlabel("Área (pixels)")
        plt.ylabel("Frequência")
        plt.grid(alpha=0.3)
        plt.tight_layout()
        if ddir:
            plt.savefig(f"{ddir}/areas_histogram.png")
            print(f"Histograma salvo em {ddir}/areas_histogram.png")
        plt.close()

    else:
        print("Nenhum contorno detectado para análise de área.")

    # Função de circularidade
    def circularity(cnt):
        area = cv2.contourArea(cnt)
        perimeter = cv2.arcLength(cnt, True)
        if perimeter == 0:
            return 0
        return 4 * np.pi * area / (perimeter * perimeter)

    # Filtrar colônias
    colonies = []
    for c in contours:
        area = cv2.contourArea(c)
        circ = circularity(c)
        (cx, cy), _ = cv2.minEnclosingCircle(c)
        if 400 < area < 6000 and circ > 0.65:

            if (x - 0.9 * r) < cx < (x + 0.9 * r) and (y - 0.9 * r) < cy < (y + 0.9 * r):
                colonies.append(c)

    # 8) Visualizar resultado final
    result = cv2.cvtColor(equalize_img, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(result, colonies, -1, (0, 255, 0), 1)
    cv2.putText(result, f"Colonias: {len(colonies)}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    if ddir:
        _save(f"{ddir}/60_binary.png", binary)
        _save(f"{ddir}/70_result.jpg", result)

    # 9) Retornar imagem e metadados
    return result, {
        "circle": [x, y, r],
        "colonies_count": len(colonies),
        "debug_dir": ddir
    }
