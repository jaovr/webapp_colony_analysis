import cv2
import numpy as np
import os

# Caminho da imagem
caminho_imagem = os.path.join("images", "image_test1.png")
imagem = cv2.imread(caminho_imagem)

if imagem is None:
    print("Erro ao carregar imagem.")
    exit()

imagem_cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
# Obter altura e largura da imagem
altura, largura = imagem.shape[:2]

# Criar uma imagem preta do mesmo tamanho (a máscara)
mascara = np.zeros((altura, largura), dtype="uint8")

centro = (largura // 2, altura // 2)

raio = min(centro) - 100

cv2.circle(mascara, centro, raio, (255, 255, 255), -1)


# Aplicar a máscara na imagem original
imagem_mascarada = cv2.bitwise_and(imagem, imagem, mask=mascara)

mascara_redimensionada = cv2.resize(mascara, (800, 800))
imagem_final = cv2.resize(imagem_mascarada,(800, 800))


cv2.imshow("Mascara", mascara_redimensionada)
cv2.imshow("imagem_mascarada", imagem_final)

cv2.waitKey(0)
cv2.destroyAllWindows()




