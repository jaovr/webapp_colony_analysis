export default function ImagePanel({ selectedImage, processedImageUrl }) {
    const preview = selectedImage ? URL.createObjectURL(selectedImage) : null

    return (
        /* grid que preenche 100% da largura */
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full">
            {/* Painel Original */}
            <div className="bg-base-200 rounded-lg shadow-md p-4 w-full">
                <h2 className="text-base font-semibold mb-4">Original</h2>
                <div className="h-80 w-full bg-base-100 flex items-center justify-center rounded-md">
                    {preview ? (
                        <img
                            src={preview}
                            alt="Original"
                            className="max-h-full max-w-full object-contain"
                        />
                    ) : (
                        <span className="opacity-60 text-sm">Sem imagem</span>
                    )}
                </div>
            </div>

            {/* Painel Resultado */}
            <div className="bg-base-200 rounded-lg shadow-md p-4 w-full">
                <h2 className="text-base font-semibold mb-4">Resultado</h2>
                <div className="h-80 w-full bg-base-100 flex items-center justify-center rounded-md">
                    {processedImageUrl ? (
                        <img
                            src={processedImageUrl}
                            alt="Resultado"
                            className="max-h-full max-w-full object-contain"
                        />
                    ) : (
                        <span className="opacity-60 text-sm">Aguardando conversão</span>
                    )}
                </div>
            </div>
        </div>
    )
}
