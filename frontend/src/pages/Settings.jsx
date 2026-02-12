import { useAuth } from '../context/AuthContext';

export default function Settings() {
  const { user } = useAuth();

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold">Configuración</h1>
        <p className="text-aegis-text-muted text-sm mt-1">Perfil de usuario y preferencias</p>
      </div>

      {/* Profile Card */}
      <div className="bg-aegis-surface rounded-xl border border-aegis-border p-6">
        <h2 className="font-semibold mb-6">Perfil</h2>
        <div className="flex items-start gap-6">
          <div className="w-20 h-20 rounded-2xl bg-aegis-accent/20 flex items-center justify-center text-aegis-accent text-3xl font-bold shrink-0">
            {user?.email?.[0]?.toUpperCase() || 'U'}
          </div>
          <div className="space-y-4 flex-1">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs text-aegis-text-muted mb-1">Email</label>
                <p className="text-sm font-medium">{user?.email}</p>
              </div>
              <div>
                <label className="block text-xs text-aegis-text-muted mb-1">Nombre</label>
                <p className="text-sm font-medium">{user?.full_name || '—'}</p>
              </div>
              <div>
                <label className="block text-xs text-aegis-text-muted mb-1">Rol</label>
                <span className={`inline-block px-2.5 py-1 rounded-full text-xs font-semibold capitalize ${
                  user?.role === 'admin' ? 'bg-aegis-accent/15 text-aegis-accent' : 'bg-aegis-text-muted/15 text-aegis-text-muted'
                }`}>
                  {user?.role}
                </span>
              </div>
              <div>
                <label className="block text-xs text-aegis-text-muted mb-1">Estado</label>
                <p className="text-sm">{user?.is_active ? '🟢 Activo' : '🔴 Inactivo'}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* System Info */}
      <div className="bg-aegis-surface rounded-xl border border-aegis-border p-6">
        <h2 className="font-semibold mb-4">Sistema</h2>
        <div className="space-y-3 text-sm">
          <div className="flex justify-between">
            <span className="text-aegis-text-muted">Versión</span>
            <span>AegisShare v2.0.0</span>
          </div>
          <div className="flex justify-between">
            <span className="text-aegis-text-muted">Motor DLP</span>
            <span>Microsoft Presidio + spaCy</span>
          </div>
          <div className="flex justify-between">
            <span className="text-aegis-text-muted">Backend</span>
            <span>FastAPI + SQLAlchemy</span>
          </div>
        </div>
      </div>
    </div>
  );
}
