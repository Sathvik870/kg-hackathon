import React, { useState } from 'react';
import { Database, Server, User, Key, Globe } from 'lucide-react';
import { connectToDb } from '../api';

export default function ConnectionForm({ onConnect }: { onConnect: () => void }) {
  const [formData, setFormData] = useState({
    host: 'localhost',
    port: '5432',
    user: 'postgres',
    password: '',
    database: 'postgres',
    ssl: false
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await connectToDb(formData);
      onConnect();
    } catch (err: any) {
      setError(err.message || 'Connection failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen items-center justify-center bg-[#1e1e1e] text-white">
      <div className="w-96 rounded-lg border border-[#333] bg-[#252526] p-6 shadow-xl">
        <div className="mb-6 flex items-center gap-2 text-blue-400">
          <Database className="h-6 w-6" />
          <h1 className="text-xl font-semibold">Postgres Connect</h1>
        </div>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="group relative">
            <Server className="absolute left-3 top-2.5 h-4 w-4 text-gray-500" />
            <input
              type="text"
              placeholder="Host"
              className="w-full rounded bg-[#3c3c3c] py-2 pl-9 pr-3 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
              value={formData.host}
              onChange={e => setFormData({...formData, host: e.target.value})}
            />
          </div>

          <div className="flex gap-4">
             <div className="group relative flex-1">
              <Globe className="absolute left-3 top-2.5 h-4 w-4 text-gray-500" />
              <input
                type="text"
                placeholder="Port"
                className="w-full rounded bg-[#3c3c3c] py-2 pl-9 pr-3 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                value={formData.port}
                onChange={e => setFormData({...formData, port: e.target.value})}
              />
            </div>
            <div className="group relative flex-1">
              <Database className="absolute left-3 top-2.5 h-4 w-4 text-gray-500" />
              <input
                type="text"
                placeholder="Database"
                className="w-full rounded bg-[#3c3c3c] py-2 pl-9 pr-3 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                value={formData.database}
                onChange={e => setFormData({...formData, database: e.target.value})}
              />
            </div>
          </div>

          <div className="group relative">
            <User className="absolute left-3 top-2.5 h-4 w-4 text-gray-500" />
            <input
              type="text"
              placeholder="Username"
              className="w-full rounded bg-[#3c3c3c] py-2 pl-9 pr-3 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
              value={formData.user}
              onChange={e => setFormData({...formData, user: e.target.value})}
            />
          </div>

          <div className="group relative">
            <Key className="absolute left-3 top-2.5 h-4 w-4 text-gray-500" />
            <input
              type="password"
              placeholder="Password"
              className="w-full rounded bg-[#3c3c3c] py-2 pl-9 pr-3 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
              value={formData.password}
              onChange={e => setFormData({...formData, password: e.target.value})}
            />
          </div>

          <div className="flex items-center gap-2 text-sm text-gray-400">
            <input 
              type="checkbox" 
              checked={formData.ssl}
              onChange={e => setFormData({...formData, ssl: e.target.checked})}
            />
            <label>Enable SSL</label>
          </div>

          {error && <div className="text-xs text-red-500">{error}</div>}

          <button
            disabled={loading}
            className="w-full rounded bg-blue-600 py-2 text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Connecting...' : 'Connect'}
          </button>
        </form>
      </div>
    </div>
  );
}