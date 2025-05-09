export default function Header({ toggleSidebar }) {
  return (
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
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="16" x2="12" y2="12" />
            <line x1="12" y1="8" x2="12.01" y2="8" />
          </svg>
        </button>
      </div>
    </header>
  );
}