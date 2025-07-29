import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import './LogViewer.css';

interface Props {
  refreshInterval: number;
}

const LogViewer: React.FC<Props> = ({ refreshInterval }) => {
  const [logs, setLogs] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [autoScroll, setAutoScroll] = useState(true);

  const loadLogs = async () => {
    try {
      const response = await api.get('/logs?limit=200');
      setLogs(response.data.logs || []);
    } catch (err) {
      console.error('Error loading logs:', err);
      setLogs(['Error loading logs']);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLogs();
    const interval = setInterval(loadLogs, refreshInterval);
    return () => clearInterval(interval);
  }, [refreshInterval]);

  useEffect(() => {
    if (autoScroll) {
      const element = document.getElementById('log-bottom');
      element?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, autoScroll]);

  return (
    <div className="log-viewer">
      <div className="log-header">
        <h2>System Logs</h2>
        <label>
          <input
            type="checkbox"
            checked={autoScroll}
            onChange={(e) => setAutoScroll(e.target.checked)}
          />
          Auto-scroll
        </label>
      </div>
      
      <div className="log-content">
        {loading ? (
          <div className="loading">Loading logs...</div>
        ) : logs.length === 0 ? (
          <div className="no-logs">No logs available</div>
        ) : (
          <>
            {logs.map((log, index) => (
              <div key={index} className="log-line">
                {log}
              </div>
            ))}
            <div id="log-bottom" />
          </>
        )}
      </div>
    </div>
  );
};

export default LogViewer;