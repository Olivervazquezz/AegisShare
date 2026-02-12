import { useState, useEffect } from 'react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function Policies() {
  const { user } = useAuth();
  const isAdmin = user?.role === 'admin';
  const [policies, setPolicies] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({ entity_type: '', display_name: '', action: 'block', min_confidence: 0.4, is_active: true });

  const fetchPolicies = async () => {
    const res = await api.get('/policies/');
    setPolicies(res.data);
  };

  useEffect(() => { fetchPolicies(); }, []);

  const resetForm = () => {
    setForm({ entity_type: '', display_name: '', action: 'block', min_confidence: 0.4, is_active: true });
    setEditing(null);
    setShowForm(false);
  };

  const handleSave = async (e) => {
    e.preventDefault();
    if (editing) {
      await api.put(`/policies/${editing}`, form);
    } else {
      await api.post('/policies/', form);
    }
    resetForm();
    fetchPolicies();
  };

  const handleEdit = (p) => {
    setForm({ entity_type: p.entity_type, display_name: p.display_name, action: p.action, min_confidence: p.min_confidence, is_active: p.is_active });
    setEditing(p.id);
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!confirm('¿Eliminar esta política?')) return;
    await api.delete(`/policies/${id}`);
    fetchPolicies();
  };

  const actionColors = {
    block: 'bg-aegis-danger/15 text-aegis-danger',
    warn: 'bg-aegis-warning/15 text-aegis-warning',
    ignore: 'bg-aegis-text-muted/15 text-aegis-text-muted',
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold">Políticas DLP</h1>
          <p className="text-aegis-text-muted text-sm mt-1">Reglas de detección de datos sensibles</p>
        </div>
        {isAdmin && (
          <button
            onClick={() => { resetForm(); setShowForm(true); }}
            className="px-4 py-2 bg-aegis-accent hover:bg-aegis-accent-hover text-white rounded-lg text-sm font-medium transition"
          >
            + Nueva Política
          </button>
        )}
      </div>

      {/* Form Modal */}
      {showForm && (
        <div className="bg-aegis-surface rounded-xl border border-aegis-border p-6">
          <h2 className="font-semibold mb-4">{editing ? 'Editar Política' : 'Crear Política'}</h2>
          <form onSubmit={handleSave} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-aegis-text-muted mb-1">Tipo de Entidad</label>
              <input
                value={form.entity_type}
                onChange={(e) => setForm({ ...form, entity_type: e.target.value })}
                placeholder="e.g. PHONE_NUMBER"
                disabled={!!editing}
                required
                className="w-full px-3 py-2 bg-aegis-bg border border-aegis-border rounded-lg text-sm focus:outline-none focus:border-aegis-accent disabled:opacity-50"
              />
            </div>
            <div>
              <label className="block text-sm text-aegis-text-muted mb-1">Nombre</label>
              <input
                value={form.display_name}
                onChange={(e) => setForm({ ...form, display_name: e.target.value })}
                placeholder="e.g. Teléfono"
                required
                className="w-full px-3 py-2 bg-aegis-bg border border-aegis-border rounded-lg text-sm focus:outline-none focus:border-aegis-accent"
              />
            </div>
            <div>
              <label className="block text-sm text-aegis-text-muted mb-1">Acción</label>
              <select
                value={form.action}
                onChange={(e) => setForm({ ...form, action: e.target.value })}
                className="w-full px-3 py-2 bg-aegis-bg border border-aegis-border rounded-lg text-sm focus:outline-none focus:border-aegis-accent"
              >
                <option value="block">Bloquear</option>
                <option value="warn">Advertir</option>
                <option value="ignore">Ignorar</option>
              </select>
            </div>
            <div>
              <label className="block text-sm text-aegis-text-muted mb-1">
                Confianza Mínima: {(form.min_confidence * 100).toFixed(0)}%
              </label>
              <input
                type="range"
                min="0" max="1" step="0.05"
                value={form.min_confidence}
                onChange={(e) => setForm({ ...form, min_confidence: parseFloat(e.target.value) })}
                className="w-full accent-aegis-accent"
              />
            </div>
            <div className="md:col-span-2 flex items-center gap-4">
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={form.is_active}
                  onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
                  className="accent-aegis-accent"
                />
                Activa
              </label>
              <div className="ml-auto flex gap-2">
                <button type="button" onClick={resetForm} className="px-4 py-2 border border-aegis-border rounded-lg text-sm hover:bg-aegis-surface-hover transition">
                  Cancelar
                </button>
                <button type="submit" className="px-4 py-2 bg-aegis-accent hover:bg-aegis-accent-hover text-white rounded-lg text-sm font-medium transition">
                  {editing ? 'Guardar Cambios' : 'Crear Política'}
                </button>
              </div>
            </div>
          </form>
        </div>
      )}

      {/* Policies Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {policies.map((p) => (
          <div key={p.id} className={`bg-aegis-surface rounded-xl border border-aegis-border p-5 transition ${!p.is_active ? 'opacity-50' : ''}`}>
            <div className="flex items-start justify-between mb-3">
              <div>
                <h3 className="font-semibold">{p.display_name}</h3>
                <p className="text-aegis-text-muted text-xs font-mono mt-0.5">{p.entity_type}</p>
              </div>
              <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${actionColors[p.action]}`}>
                {p.action.toUpperCase()}
              </span>
            </div>
            <p className="text-sm text-aegis-text-muted">
              Confianza mínima: <span className="text-white font-medium">{(p.min_confidence * 100).toFixed(0)}%</span>
            </p>
            <p className="text-sm text-aegis-text-muted mt-1">
              Estado: {p.is_active ? '🟢 Activa' : '⚫ Inactiva'}
            </p>
            {isAdmin && (
              <div className="flex gap-2 mt-4 pt-3 border-t border-aegis-border/50">
                <button onClick={() => handleEdit(p)} className="text-xs text-aegis-accent hover:underline">Editar</button>
                <button onClick={() => handleDelete(p.id)} className="text-xs text-aegis-danger hover:underline">Eliminar</button>
              </div>
            )}
          </div>
        ))}
        {policies.length === 0 && (
          <div className="md:col-span-3 py-12 text-center text-aegis-text-muted">
            No hay políticas configuradas. {isAdmin && 'Crea una para empezar.'}
          </div>
        )}
      </div>
    </div>
  );
}
