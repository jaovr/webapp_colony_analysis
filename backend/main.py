# Make sure to run: pip install fastapi python-multipart uvicorn
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import cv2
import numpy as np
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/cinza/")
async def converter_para_cinza(imagem: UploadFile = File(...)):
    # Lê os bytes da imagem
    conteudo = await imagem.read()

    # Converte os bytes para array NumPy
    np_array = np.frombuffer(conteudo, np.uint8)

    # Decodifica como imagem
    img_colorida = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

    # Converte para escala de cinza
    img_cinza = cv2.cvtColor(img_colorida, cv2.COLOR_BGR2GRAY)

    # Codifica de volta para JPG
    sucesso, buffer = cv2.imencode('.jpg', img_cinza)
    if not sucesso:
        return {"erro": "Erro ao converter a imagem."}

    # Retorna como imagem
    retorno = io.BytesIO(buffer)
    return StreamingResponse(retorno, media_type="image/jpeg")
