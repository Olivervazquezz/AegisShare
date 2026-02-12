import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import api from '../services/api';

export default function Scan() {
  const [result, setResult] = useState(null);
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState('');

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return;
    const file = acceptedFiles[0];

    setResult(null);
    setError('');
    setScanning(true);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const { data } = await api.post('/scan/', formData);
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al analizar el archivo.');
    } finally {
      setScanning(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: false,
  });

  const isBlocked = result?.analisis_ia === 'BLOQUEADO';

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold">Escanear Archivo</h1>
        <p className="text-aegis-text-muted text-sm mt-1">Sube un archivo para analizarlo con el motor DLP</p>
      </div>

      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all duration-300 ${
          isDragActive
            ? 'border-aegis-accent bg-aegis-accent/5 scale-[1.02]'
            : 'border-aegis-border hover:border-aegis-accent/50 hover:bg-aegis-surface'
        }`}
      >
        <input {...getInputProps()} />
        <div className="text-5xl mb-4">{scanning ? '⏳' : isDragActive ? '📥' : '📄'}</div>
        {scanning ? (
          <>
            <p className="text-lg font-medium text-aegis-accent">Analizando con IA…</p>
            <div className="mt-4 mx-auto w-48 h-1.5 bg-aegis-border rounded-full overflow-hidden">
              <div className="h-full bg-aegis-accent rounded-full animate-[pulse_1.5s_ease-in-out_infinite] w-3/4" />
            </div>
          </>
        ) : (
          <>
            <p className="text-lg font-medium">
              {isDragActive ? 'Suelta el archivo aquí' : 'Arrastra un archivo o haz click para seleccionar'}
            </p>
            <p className="text-aegis-text-muted text-sm mt-2">Archivos de texto (UTF-8) — .txt, .csv, .json, .log, .md</p>
          </>
        )}
      </div>

      {/* Error */}
      {error && (
        <div className="p-4 bg-aegis-danger/10 border border-aegis-danger/30 rounded-xl text-aegis-danger">
          {error}
        </div>
      )}

      {/* Result */}
      {result && (
        <div className={`rounded-xl border p-6 transition-all ${
          isBlocked
            ? 'bg-aegis-danger/5 border-aegis-danger/30 shadow-[0_0_30px_rgba(239,68,68,0.1)]'
            : 'bg-aegis-success/5 border-aegis-success/30'
        }`}>
          <div className="flex items-center gap-3 mb-4">
            <span className="text-3xl">{isBlocked ? '🚫' : '✅'}</span>
            <div>
              <p className={`text-xl font-bold ${isBlocked ? 'text-aegis-danger' : 'text-aegis-success'}`}>
                {result.analisis_ia}
              </p>
              <p className="text-aegis-text-muted text-sm">
                {result.archivo} • Riesgo: <span className="capitalize">{result.risk_level}</span> • {result.entities_found} entidade(s) detectada(s)
              </p>
            </div>
          </div>

          {/* Details */}
          <div className="bg-aegis-bg rounded-lg p-4 mt-4">
            <h3 className="text-sm font-semibold text-aegis-text-muted mb-2">Detalles del Análisis</h3>
            {result.detalles.map((d, i) => (
              <div key={i} className="flex items-center gap-3 py-2 border-b border-aegis-border/30 last:border-0">
                {d.entity_type ? (
                  <>
                    <span className={`px-2 py-0.5 rounded text-xs font-semibold ${
                      d.action === 'block' ? 'bg-aegis-danger/15 text-aegis-danger' : 'bg-aegis-warning/15 text-aegis-warning'
                    }`}>
                      {d.action?.toUpperCase()}
                    </span>
                    <span className="font-medium text-sm">{d.policy_name || d.entity_type}</span>
                    <span className="text-aegis-text-muted text-xs ml-auto">Confianza: {(d.confidence * 100).toFixed(0)}%</span>
                  </>
                ) : (
                  <span className="text-aegis-success text-sm">{d.mensaje}</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
