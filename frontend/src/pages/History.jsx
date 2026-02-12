import { useState, useEffect } from 'react';
import api from '../services/api';

export default function History() {
  const [data, setData] = useState({ items: [], total: 0, page: 1, pages: 1 });
  const [page, setPage] = useState(1);
  const [status, setStatus] = useState('');
  const [search, setSearch] = useState('');

  const fetchHistory = async () => {
    const params = { page, per_page: 10 };
    if (status) params.status = status;
    if (search) params.search = search;
    const res = await api.get('/history/', { params });
    setData(res.data);
  };

  useEffect(() => { fetchHistory(); }, [page, status]);

  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1);
    fetchHistory();
  };

  const exportCSV = () => {
    window.open('/api/history/export', '_blank');
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold">Historial de Escaneos</h1>
          <p className="text-aegis-text-muted text-sm mt-1">{data.total} registro(s) encontrado(s)</p>
        </div>
        <button
          onClick={exportCSV}
          className="px-4 py-2 bg-aegis-surface border border-aegis-border rounded-lg text-sm hover:bg-aegis-surface-hover transition"
        >
          📥 Exportar CSV
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-3 flex-wrap">
        <form onSubmit={handleSearch} className="flex-1 min-w-[200px]">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Buscar por nombre de archivo…"
            className="w-full px-4 py-2.5 bg-aegis-surface border border-aegis-border rounded-lg text-sm focus:outline-none focus:border-aegis-accent transition"
          />
        </form>
        <select
          value={status}
          onChange={(e) => { setStatus(e.target.value); setPage(1); }}
          className="px-4 py-2.5 bg-aegis-surface border border-aegis-border rounded-lg text-sm focus:outline-none focus:border-aegis-accent"
        >
          <option value="">Todos los estados</option>
          <option value="APROBADO">Aprobado</option>
          <option value="BLOQUEADO">Bloqueado</option>
        </select>
      </div>

      {/* Table */}
      <div className="bg-aegis-surface rounded-xl border border-aegis-border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-aegis-text-muted bg-aegis-bg/50">
                <th className="px-5 py-3 font-medium">Archivo</th>
                <th className="px-5 py-3 font-medium">Estado</th>
                <th className="px-5 py-3 font-medium">Riesgo</th>
                <th className="px-5 py-3 font-medium">Entidades</th>
                <th className="px-5 py-3 font-medium">Usuario</th>
                <th className="px-5 py-3 font-medium">Fecha</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((item) => (
                <tr key={item.id} className="border-t border-aegis-border/50 hover:bg-aegis-surface-hover transition">
                  <td className="px-5 py-3 font-medium">{item.filename}</td>
                  <td className="px-5 py-3">
                    <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
                      item.status === 'BLOQUEADO'
                        ? 'bg-aegis-danger/15 text-aegis-danger'
                        : 'bg-aegis-success/15 text-aegis-success'
                    }`}>
                      {item.status}
                    </span>
                  </td>
                  <td className="px-5 py-3 capitalize text-aegis-text-muted">{item.risk_level}</td>
                  <td className="px-5 py-3 text-aegis-text-muted">{item.entities_found}</td>
                  <td className="px-5 py-3 text-aegis-text-muted">{item.user_email}</td>
                  <td className="px-5 py-3 text-aegis-text-muted text-xs">{new Date(item.timestamp).toLocaleString()}</td>
                </tr>
              ))}
              {data.items.length === 0 && (
                <tr><td colSpan={6} className="px-5 py-12 text-center text-aegis-text-muted">Sin resultados</td></tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {data.pages > 1 && (
          <div className="flex items-center justify-between px-5 py-3 border-t border-aegis-border">
            <p className="text-aegis-text-muted text-xs">
              Página {data.page} de {data.pages}
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-3 py-1.5 rounded-lg border border-aegis-border text-xs hover:bg-aegis-surface-hover disabled:opacity-40 disabled:cursor-not-allowed transition"
              >
                ← Anterior
              </button>
              <button
                onClick={() => setPage((p) => Math.min(data.pages, p + 1))}
                disabled={page === data.pages}
                className="px-3 py-1.5 rounded-lg border border-aegis-border text-xs hover:bg-aegis-surface-hover disabled:opacity-40 disabled:cursor-not-allowed transition"
              >
                Siguiente →
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
