import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import api from '../services/api';

function StatCard({ label, value, sub, color }) {
  return (
    <div className="bg-aegis-surface rounded-xl border border-aegis-border p-5">
      <p className="text-aegis-text-muted text-sm">{label}</p>
      <p className={`text-3xl font-bold mt-1 ${color}`}>{value}</p>
      {sub && <p className="text-aegis-text-muted text-xs mt-1">{sub}</p>}
    </div>
  );
}

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [recent, setRecent] = useState([]);

  useEffect(() => {
    api.get('/stats/').then((r) => setStats(r.data));
    api.get('/history/?per_page=5').then((r) => setRecent(r.data.items));
  }, []);

  if (!stats) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-aegis-accent border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-aegis-text-muted text-sm mt-1">Resumen de actividad y amenazas</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Total Escaneos" value={stats.total_scans} color="text-white" />
        <StatCard label="Amenazas Bloqueadas" value={stats.threats_blocked} color="text-aegis-danger" />
        <StatCard label="Tasa de Aprobación" value={`${stats.approval_rate}%`} color="text-aegis-success" />
        <StatCard label="Escaneos Hoy" value={stats.scans_today} color="text-aegis-accent" />
      </div>

      {/* Chart */}
      <div className="bg-aegis-surface rounded-xl border border-aegis-border p-6">
        <h2 className="font-semibold mb-4">Actividad — Últimos 7 Días</h2>
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={stats.daily}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="date" stroke="#94a3b8" tick={{ fontSize: 12 }} />
            <YAxis stroke="#94a3b8" tick={{ fontSize: 12 }} />
            <Tooltip
              contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: 8 }}
              labelStyle={{ color: '#e2e8f0' }}
            />
            <Line type="monotone" dataKey="scans" name="Escaneos" stroke="#3b82f6" strokeWidth={2} dot={{ r: 4 }} />
            <Line type="monotone" dataKey="threats" name="Amenazas" stroke="#ef4444" strokeWidth={2} dot={{ r: 4 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Recent Scans */}
      <div className="bg-aegis-surface rounded-xl border border-aegis-border p-6">
        <h2 className="font-semibold mb-4">Escaneos Recientes</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-aegis-text-muted border-b border-aegis-border">
                <th className="pb-3 font-medium">Archivo</th>
                <th className="pb-3 font-medium">Estado</th>
                <th className="pb-3 font-medium">Riesgo</th>
                <th className="pb-3 font-medium">Fecha</th>
              </tr>
            </thead>
            <tbody>
              {recent.map((item) => (
                <tr key={item.id} className="border-b border-aegis-border/50 hover:bg-aegis-surface-hover transition">
                  <td className="py-3 font-medium">{item.filename}</td>
                  <td className="py-3">
                    <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${item.status === 'BLOQUEADO' ? 'bg-aegis-danger/15 text-aegis-danger' : 'bg-aegis-success/15 text-aegis-success'}`}>
                      {item.status}
                    </span>
                  </td>
                  <td className="py-3 capitalize text-aegis-text-muted">{item.risk_level}</td>
                  <td className="py-3 text-aegis-text-muted">{new Date(item.timestamp).toLocaleString()}</td>
                </tr>
              ))}
              {recent.length === 0 && (
                <tr><td colSpan={4} className="py-8 text-center text-aegis-text-muted">Sin escaneos aún</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
