import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const navItems = [
  { to: '/dashboard', icon: '📊', label: 'Dashboard' },
  { to: '/scan', icon: '🔍', label: 'Escanear' },
  { to: '/history', icon: '📋', label: 'Historial' },
  { to: '/policies', icon: '🛡️', label: 'Políticas' },
  { to: '/settings', icon: '⚙️', label: 'Configuración' },
];

export default function Sidebar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <aside className="w-64 min-h-screen bg-aegis-surface border-r border-aegis-border flex flex-col">
      {/* Brand */}
      <div className="p-6 border-b border-aegis-border">
        <h1 className="text-xl font-bold text-aegis-accent flex items-center gap-2">
          <span className="text-2xl">🛡️</span> AegisShare
        </h1>
        <p className="text-xs text-aegis-text-muted mt-1">Data Loss Prevention</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map(({ to, icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                isActive
                  ? 'bg-aegis-accent/15 text-aegis-accent'
                  : 'text-aegis-text-muted hover:bg-aegis-surface-hover hover:text-aegis-text'
              }`
            }
          >
            <span className="text-lg">{icon}</span>
            {label}
          </NavLink>
        ))}
      </nav>

      {/* User & Logout */}
      <div className="p-4 border-t border-aegis-border">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-9 h-9 rounded-full bg-aegis-accent/20 flex items-center justify-center text-aegis-accent font-bold text-sm">
            {user?.email?.[0]?.toUpperCase() || 'U'}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{user?.full_name || user?.email}</p>
            <p className="text-xs text-aegis-text-muted capitalize">{user?.role}</p>
          </div>
        </div>
        <button
          onClick={handleLogout}
          className="w-full text-left px-4 py-2 rounded-lg text-sm text-aegis-text-muted hover:bg-aegis-surface-hover hover:text-aegis-danger transition-colors"
        >
          Cerrar Sesión
        </button>
      </div>
    </aside>
  );
}
