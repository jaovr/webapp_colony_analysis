import cv2, os, uuid
import numpy as np
import matplotlib.pyplot as plt
from core.io import to_bgr, to_gray
from core.denoise import median_filter
from core.mask import apply_circular_mask
from core.contrast import equalize
from numpy.ma.core import bitwise_or


def _save(path, img):
    """Salva imagem de debug."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cv2.imwrite(path, img)


# Função de circularidade movida para o escopo global
def circularity(cnt):
    area = cv2.contourArea(cnt)
    perimeter = cv2.arcLength(cnt, True)
    if perimeter == 0:
        return 0
    return 4 * np.pi * area / (perimeter * perimeter)


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

    # 2) Filtro e equalização de contraste (Apenas para detecção do CÍRCULO)
    gray_blurred_hough = median_filter(gray, 25)
    clahe_hough = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray_eq_hough = clahe_hough.apply(gray_blurred_hough)

    if ddir:
        _save(f"{ddir}/20_median.png", gray_blurred_hough)
        _save(f"{ddir}/30_clahe.png", gray_eq_hough)

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
        image=gray_eq_hough,
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

    # 7) Converter para análise
    gray_2 = to_gray(masked)

    # --- Contagem de colônias com refinamento (PLANO AE) ---

    # 1. Aplicar a máscara menor
    mask = np.zeros_like(gray_2)
    cv2.circle(mask, (x, y), int(r * 0.9), 255, -1)
    masked_inner_gray = cv2.bitwise_and(gray_2, gray_2, mask=mask)

    # 2. Aplicar MedianBlur para remover ruído ANTES do CLAHE
    blurred = cv2.medianBlur(masked_inner_gray, 5)

    # 3. Aplicar CLAHE para aumentar contraste localmente
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    clahe_img = clahe.apply(blurred)

    # 4. Re-aplicar a máscara
    clahe_img = cv2.bitwise_and(clahe_img, clahe_img, mask=mask)

    if ddir:
        _save(f"{ddir}/55_masked_inner.png", clahe_img)

    # 5. Binarização (AdaptiveThreshold C=7)
    #    Isto cria anéis + texto (sem ruído)
    binary_raw = cv2.adaptiveThreshold(
        clahe_img,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        blockSize=71,
        C=7
    )
    binary_raw = cv2.bitwise_and(binary_raw, binary_raw, mask=mask)

    if ddir:
        _save(f"{ddir}/60_binary_raw.png", binary_raw)

    # --- MUDANÇA CRÍTICA: Filtragem e Preenchimento de Contornos ---

    # 1. Encontrar TODOS os contornos (anéis e texto) da imagem raw
    contours_raw, _ = cv2.findContours(binary_raw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 2. Criar uma nova imagem preta para desenhar os blobs FINAIS
    binary_final = np.zeros_like(binary_raw)

    # 3. Filtrar os contornos por CIRCULARIDADE e ÁREA (para remover texto/ruído)
    MIN_RING_CIRCULARITY = 0.3 # Texto é linear (< 0.3), Anéis são curvados (> 0.3)
    MIN_RING_AREA = 100        # Filtra poeira

    contours_to_fill = []
    for c in contours_raw:
        area = cv2.contourArea(c)
        circ = circularity(c)
        if circ > MIN_RING_CIRCULARITY and area > MIN_RING_AREA:
            contours_to_fill.append(c)

    # 4. Desenhar os contornos filtrados (anéis) como blobs sólidos
    cv2.drawContours(binary_final, contours_to_fill, -1, 255, cv2.FILLED)

    # 5. Encontrar os contornos FINAIS (agora são blobs sólidos)
    contours, _ = cv2.findContours(binary_final, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # --- Análise de áreas detectadas (debug) ---
    areas = [cv2.contourArea(c) for c in contours if cv2.contourArea(c) > 0]
    if len(areas) > 0:
        print(f"Total de contornos detectados (final): {len(areas)}")
        print(f"Área mínima: {np.min(areas):.2f}, máxima: {np.max(areas):.2f}")
        plt.figure(figsize=(6, 4))
        max_plot_area = min(np.max(areas) + 100, 10000)
        plt.hist(areas, bins=100, color='gray', edgecolor='black', range=(0, max_plot_area))
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
        print("Nenhum contorno detectado (final) para análise de área.")

    # --- Filtros Finais ---
    # Agora estamos filtrando os BLOBS PREENCHIDOS

    MIN_COLONY_AREA = 1000 # Filtra blobs pequenos (ex-anéis quebrados)
    MAX_COLONY_AREA = 10000

    print(f"[Filtro] Usando Área > {MIN_COLONY_AREA}")

    # --- Filtrar colônias ---
    colonies = []
    for c in contours: # Loop nos contornos JÁ PREENCHIDOS
        area = cv2.contourArea(c)

        if area > MIN_COLONY_AREA and area < MAX_COLONY_AREA:
            (cx, cy), _ = cv2.minEnclosingCircle(c)
            if (x - 0.9 * r) < cx < (x + 0.9 * r) and (y - 0.9 * r) < cy < (y + 0.9 * r):
                colonies.append(c)

    # 8) Visualizar resultado final
    result_img_base = masked.copy()
    cv2.drawContours(result_img_base, colonies, -1, (0, 255, 0), 2)
    cv2.putText(result_img_base, f"Colonias: {len(colonies)}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    if ddir:
        # Esta é a imagem binária FINAL (com blobs)
        _save(f"{ddir}/60_binary_final.png", binary_final)
        _save(f"{ddir}/70_result.jpg", result_img_base)

    # 9) Retornar imagem e metadados
    return result_img_base, {
        "circle": [x, y, r],
        "colonies_count": len(colonies),
        "debug_dir": ddir
    }