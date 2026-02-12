import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch {
      setError('Credenciales inválidas. Intenta de nuevo.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-aegis-bg p-4">
      <div className="w-full max-w-md">
        {/* Card */}
        <div className="bg-aegis-surface rounded-2xl border border-aegis-border shadow-2xl p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-aegis-accent/15 mb-4">
              <span className="text-3xl">🛡️</span>
            </div>
            <h1 className="text-2xl font-bold text-white">AegisShare</h1>
            <p className="text-aegis-text-muted text-sm mt-1">AI-Powered Data Loss Prevention</p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-aegis-text-muted mb-1.5">
                Email
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="usuario@empresa.com"
                required
                className="w-full px-4 py-3 bg-aegis-bg border border-aegis-border rounded-lg text-white placeholder-aegis-text-muted/50 focus:outline-none focus:border-aegis-accent focus:ring-1 focus:ring-aegis-accent transition"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-aegis-text-muted mb-1.5">
                Contraseña
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                className="w-full px-4 py-3 bg-aegis-bg border border-aegis-border rounded-lg text-white placeholder-aegis-text-muted/50 focus:outline-none focus:border-aegis-accent focus:ring-1 focus:ring-aegis-accent transition"
              />
            </div>

            {error && (
              <div className="p-3 bg-aegis-danger/10 border border-aegis-danger/30 rounded-lg text-aegis-danger text-sm text-center">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-aegis-accent hover:bg-aegis-accent-hover text-white font-semibold rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Verificando…' : 'Iniciar Sesión'}
            </button>
          </form>
        </div>

        <p className="text-center text-aegis-text-muted/50 text-xs mt-6">
          AegisShare v2.0 — Plataforma de Prevención de Pérdida de Datos
        </p>
      </div>
    </div>
  );
}
