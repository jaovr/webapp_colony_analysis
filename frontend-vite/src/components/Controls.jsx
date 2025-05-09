import { ImageUp, RefreshCcw } from 'lucide-react';
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
        <ImageUp size={18} className="text-gray-700" />
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
            <RefreshCcw size={18} className="text-white" />
            <span>Converter</span>
          </>
        )}
      </button>
    </div>
  );
}

