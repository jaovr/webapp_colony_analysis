import cv2
import os

caminho_imagem = os.path.join("images", "image_test1.png")

imagem = cv2.imread(caminho_imagem)

if imagem is None:
    print("Erro ao carregar imagem. Verifique o caminho ou nome.")
    exit()


imagem_cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)

tamanho_padrao = (500, 500)

imagem_redimensionada = cv2.resize(imagem, tamanho_padrao)
imagem_cinza_redimensionada = cv2.resize(imagem_cinza, tamanho_padrao)

cv2.imshow("imagem", imagem_redimensionada)
cv2.imshow("imagem_cinza", imagem_cinza_redimensionada)

cv2.waitKey(0)
cv2.destroyAllWindows()




