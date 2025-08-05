'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store/auth';
import AdminLayout from '@/components/admin/AdminLayout';
import api from '@/lib/api';
import toast from 'react-hot-toast';
import { FiDatabase, FiTrash2, FiDownload, FiAlertTriangle } from 'react-icons/fi';

export default function AdminDatabasePage() {
  const router = useRouter();
  const { isAuthenticated, user } = useAuthStore();
  const [stats, setStats] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [confirmText, setConfirmText] = useState('');

  useEffect(() => {
    if (!isAuthenticated || user?.username !== 'admin') {
      router.push('/');
    } else {
      fetchStats();
    }
  }, [isAuthenticated, user, router]);

  const fetchStats = async () => {
    setIsLoading(true);
    try {
      const response = await api.get('/api/memory/stats');
      setStats(response.data.stats);
    } catch (error) {
      toast.error('Failed to load database stats');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearDatabase = async () => {
    if (confirmText !== 'DELETE ALL DATA') {
      toast.error('Please type the confirmation text exactly');
      return;
    }

    try {
      await api.delete('/api/memory/clear');
      toast.success('Database cleared successfully');
      setShowConfirmDialog(false);
      setConfirmText('');
      fetchStats();
    } catch (error) {
      toast.error('Failed to clear database');
    }
  };

  const handleExport = async () => {
    try {
      const response = await api.get('/api/memory/export');
      const data = JSON.stringify(response.data.export, null, 2);
      const blob = new Blob([data], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `contextcache-export-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      toast.success('Export completed');
    } catch (error) {
      toast.error('Failed to export data');
    }
  };

  if (!isAuthenticated || user?.username !== 'admin') {
    return null;
  }

  return (
    <AdminLayout>
      <div className="max-w-4xl">
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">Database Management</h1>
          <p className="text-gray-400">Monitor and manage the knowledge graph database</p>
        </div>

        {/* Database Stats */}
        <div className="bg-gray-800 rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <FiDatabase className="mr-2" />
            Database Statistics
          </h2>
          {stats ? (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-gray-700 p-4 rounded-md">
                <p className="text-sm text-gray-400">Total Nodes</p>
                <p className="text-2xl font-bold">{stats.total_nodes}</p>
              </div>
              <div className="bg-gray-700 p-4 rounded-md">
                <p className="text-sm text-gray-400">Total Edges</p>
                <p className="text-2xl font-bold">{stats.total_edges}</p>
              </div>
              <div className="bg-gray-700 p-4 rounded-md">
                <p className="text-sm text-gray-400">Database Size</p>
                <p className="text-2xl font-bold">
                  {((stats.total_nodes + stats.total_edges) * 0.5).toFixed(1)} KB
                </p>
              </div>
              <div className="bg-gray-700 p-4 rounded-md">
                <p className="text-sm text-gray-400">Collections</p>
                <p className="text-2xl font-bold">4</p>
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Export Data */}
          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-3">Export Data</h3>
            <p className="text-gray-400 text-sm mb-4">
              Download a complete backup of all nodes and edges in JSON format.
            </p>
            <button
              onClick={handleExport}
              className="w-full px-4 py-2 bg-green-600 hover:bg-green-700 rounded-md transition flex items-center justify-center space-x-2"
            >
              <FiDownload />
              <span>Export Database</span>
            </button>
          </div>

          {/* Clear Database */}
          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-3 text-red-400">Danger Zone</h3>
            <p className="text-gray-400 text-sm mb-4">
              Permanently delete all data from the database. This action cannot be undone.
            </p>
            <button
              onClick={() => setShowConfirmDialog(true)}
              className="w-full px-4 py-2 bg-red-600 hover:bg-red-700 rounded-md transition flex items-center justify-center space-x-2"
            >
              <FiTrash2 />
              <span>Clear Database</span>
            </button>
          </div>
        </div>

        {/* Confirm Dialog */}
        {showConfirmDialog && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
              <div className="flex items-center mb-4 text-red-400">
                <FiAlertTriangle className="text-2xl mr-3" />
                <h3 className="text-xl font-semibold">Confirm Database Deletion</h3>
              </div>
              <p className="text-gray-300 mb-4">
                This will permanently delete all nodes, edges, and sessions from the database.
                This action cannot be undone.
              </p>
              <p className="text-gray-300 mb-4">
                Type <span className="font-mono bg-gray-700 px-2 py-1 rounded">DELETE ALL DATA</span> to confirm:
              </p>
              <input
                type="text"
                value={confirmText}
                onChange={(e) => setConfirmText(e.target.value)}
                className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-md text-white mb-4 focus:outline-none focus:ring-2 focus:ring-red-500"
                placeholder="Type confirmation text here"
              />
              <div className="flex space-x-4">
                <button
                  onClick={() => {
                    setShowConfirmDialog(false);
                    setConfirmText('');
                  }}
                  className="flex-1 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-md transition"
                >
                  Cancel
                </button>
                <button
                  onClick={handleClearDatabase}
                  disabled={confirmText !== 'DELETE ALL DATA'}
                  className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-md transition"
                >
                  Delete Everything
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </AdminLayout>
  );
}