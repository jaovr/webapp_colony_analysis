import {Image} from 'lucide-react';
export default function ImagePanel({ titulo, imagem, carregando, vazioMsg }) {
  return (
    <div className="image-panel">
      <div className="panel-header">
        <h2>{titulo}</h2>
      </div>
      <div className="panel-content">
        {carregando ? (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Processando...</p>
          </div>
        ) : imagem ? (
          <img src={imagem} alt={titulo} />
        ) : (
          <div className="empty-state">
            <Image size={40} className="text-gray-400" strokeWidth={1.2} />
            <p>{vazioMsg}</p>
          </div>
        )}
      </div>
    </div>
  );
}
