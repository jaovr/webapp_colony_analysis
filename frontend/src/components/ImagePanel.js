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
            <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" fill="none" stroke="currentColor">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
              <circle cx="8.5" cy="8.5" r="1.5" />
              <polyline points="21 15 16 10 5 21" />
            </svg>
            <p>{vazioMsg}</p>
          </div>
        )}
      </div>
    </div>
  );
}
