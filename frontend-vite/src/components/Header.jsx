import {Menu, Info} from 'lucide-react';
export default function Header({ toggleSidebar }) {
  return (
    <header>
      <div className="logo">
        <button className="menu-button" onClick={toggleSidebar}>
            <Menu size={24} color="white"/>
        </button>
        <h1>Processamento de Imagem</h1>
      </div>
      <div className="actions">
        <button className="action-button">
          <Info size={20} strokeWidth={2} color="white"/>
        </button>
      </div>
    </header>
  );
}

