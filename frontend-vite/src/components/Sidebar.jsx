export default function Sidebar({ sidebarOpen }) {
  return (
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
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="3" />
            <path d="M19.4 15a1.65 1.65..." />
          </svg>
          <span>Configurações</span>
        </button>
      </div>
    </aside>
  );
}
