import cv2
import os

caminho_imagem = os.path.join("images", "AGAR_demo", "AGAR_representative", "higher-resolution", "bright", "349.jpg")
imagem = cv2.imread(caminho_imagem)

if imagem is None:
    print("Erro ao carregar imagem.")
    exit()

imagem_cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
_, img_threshold = cv2.threshold(imagem_cinza, 150, 255, cv2.THRESH_BINARY)

img_menor = cv2.resize(img_threshold, (800, 800))

cv2.imshow("Imagem Limiarizada", img_menor)
cv2.waitKey(0)
cv2.destroyAllWindows()
