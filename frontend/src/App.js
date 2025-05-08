import { useState } from 'react';
import './App.css';

function App() {
  const [imagemOriginal, setImagemOriginal] = useState(null);
  const [imagemConvertida, setImagemConvertida] = useState(null);
  const [nomeArquivo, setNomeArquivo] = useState('');
  const [carregando, setCarregando] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  function handleUpload(event) {
    const file = event.target.files[0];
    if (file) {
      setNomeArquivo(file.name);
      const imageUrl = URL.createObjectURL(file);
      setImagemOriginal(imageUrl);
      setImagemConvertida(null);
    }
  }

  function converterImagem() {
    if (!imagemOriginal) return;
    
    setCarregando(true);
    
    setTimeout(() => {
      setImagemConvertida(imagemOriginal);
      setCarregando(false);
    }, 1000);
  }

  function toggleSidebar() {
    setSidebarOpen(!sidebarOpen);
  }

  return (
    <div className="app">
      {/* Header */}
      <header>
        <div className="logo">
          <button className="menu-button" onClick={toggleSidebar}>
            <span></span>
            <span></span>
            <span></span>
          </button>
          <h1>Conversor</h1>
        </div>
        <div className="actions">
          <button className="action-button">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="16" x2="12" y2="12"></line>
              <line x1="12" y1="8" x2="12.01" y2="8"></line>
            </svg>
          </button>
        </div>
      </header>

      <div className="layout">
        {/* Sidebar */}
        <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
          <nav>
            <div className="nav-group">
              <h3>Ferramentas</h3>
              <ul>
                <li className="active">Detector de Bordas</li>
                <li>Filtros</li>
                <li>Ajustes</li>
              </ul>
            </div>
            <div className="nav-group">
              <h3>Recentes</h3>
              <ul>
                <li>Projeto 1</li>
                <li>Projeto 2</li>
              </ul>
            </div>
          </nav>
          <div className="sidebar-footer">
            <button className="settings-button">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="3"></circle>
                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
              </svg>
              <span>Configurações</span>
            </button>
          </div>
        </aside>

        {/* Main Content */}
        <main>
          <div className="workspace">
            <div className="image-container">
              <div className="image-panel">
                <div className="panel-header">
                  <h2>Original</h2>
                </div>
                <div className="panel-content">
                  {imagemOriginal ? (
                    <img src={imagemOriginal} alt="Original" />
                  ) : (
                    <div className="empty-state">
                      <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round">
                        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                        <circle cx="8.5" cy="8.5" r="1.5"></circle>
                        <polyline points="21 15 16 10 5 21"></polyline>
                      </svg>
                      <p>Sem imagem</p>
                    </div>
                  )}
                </div>
              </div>
              
              <div className="image-panel">
                <div className="panel-header">
                  <h2>Resultado</h2>
                </div>
                <div className="panel-content">
                  {carregando ? (
                    <div className="loading-state">
                      <div className="spinner"></div>
                      <p>Processando...</p>
                    </div>
                  ) : imagemConvertida ? (
                    <img src={imagemConvertida} alt="Convertida" />
                  ) : (
                    <div className="empty-state">
                      <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                        <line x1="12" y1="9" x2="12" y2="13"></line>
                        <line x1="12" y1="17" x2="12.01" y2="17"></line>
                      </svg>
                      <p>Aguardando conversão</p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="controls">
              <input 
                id="fileInput" 
                type="file" 
                accept="image/*" 
                onChange={handleUpload} 
              />
              <label htmlFor="fileInput" className="upload-button">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                  <polyline points="17 8 12 3 7 8"></polyline>
                  <line x1="12" y1="3" x2="12" y2="15"></line>
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
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="1 4 1 10 7 10"></polyline>
                      <polyline points="23 20 23 14 17 14"></polyline>
                      <path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15"></path>
                    </svg>
                    <span>Converter</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </main>
      </div>

      {/* Footer */}
      <footer>
        <div className="footer-content">
          <p>Conversor de Imagem • <span className="version">v1.0</span></p>
        </div>
      </footer>
    </div>
  );
}

export default App;