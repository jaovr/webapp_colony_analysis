import { useState } from 'react';
import Header from './components/Header.jsx';
import Sidebar from './components/Sidebar.jsx';
import ImagePanel from './components/ImagePanel.jsx';
import Controls from './components/Controls.jsx';
import Footer from './components/Footer.jsx';
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

  async function converterImagem() {
    if (!imagemOriginal) return;

    setCarregando(true);

    try {
      const input = document.getElementById("fileInput");
      const file = input.files[0];
      const formData = new FormData();
      formData.append("imagem", file);

      const resposta = await fetch("http://localhost:8000/cinza/", {
        method: "POST",
        body: formData,
      });

      const blob = await resposta.blob();
      const urlImagemCinza = URL.createObjectURL(blob);
      setImagemConvertida(urlImagemCinza);
    } catch (erro) {
      console.error("Erro ao converter imagem:", erro);
    } finally {
      setCarregando(false);
    }
  }

  return (
    <div className="app">
      <Header toggleSidebar={() => setSidebarOpen(!sidebarOpen)} />
      <div className="layout">
        <Sidebar sidebarOpen={sidebarOpen} />
        <main>
          <div className="workspace">
            <div className="image-container">
              <ImagePanel titulo="Original" imagem={imagemOriginal} carregando={false} vazioMsg="Sem imagem" />
              <ImagePanel titulo="Resultado" imagem={imagemConvertida} carregando={carregando} vazioMsg="Aguardando conversão" />
            </div>
            <Controls
              nomeArquivo={nomeArquivo}
              imagemOriginal={imagemOriginal}
              carregando={carregando}
              handleUpload={handleUpload}
              converterImagem={converterImagem}
            />
          </div>
        </main>
      </div>
      <Footer />
    </div>
  );
}

export default App;
