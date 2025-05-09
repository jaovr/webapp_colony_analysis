export default function Controls({
  nomeArquivo,
  imagemOriginal,
  carregando,
  handleUpload,
  converterImagem
}) {
  return (
    <div className="controls">
      <input id="fileInput" type="file" accept="image/*" onChange={handleUpload} />
      <label htmlFor="fileInput" className="upload-button">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" stroke="currentColor">
          <polyline points="17 8 12 3 7 8" />
          <line x1="12" y1="3" x2="12" y2="15" />
        </svg>
        <span>{nomeArquivo ? nomeArquivo : 'Selecionar Imagem'}</span>
      </label>

      <button
        className="convert-button"
        onClick={converterImagem}
        disabled={!imagemOriginal || carregando}
      >
        {carregando ? (
          <>
            <div className="button-spinner"></div>
            <span>Processando</span>
          </>
        ) : (
          <>
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" stroke="currentColor">
              <polyline points="1 4 1 10 7 10" />
              <polyline points="23 20 23 14 17 14" />
              <path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15" />
            </svg>
            <span>Converter</span>
          </>
        )}
      </button>
    </div>
  );
}

