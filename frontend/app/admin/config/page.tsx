'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store/auth';
import AdminLayout from '@/components/admin/AdminLayout';
import api from '@/lib/api';
import toast from 'react-hot-toast';
import { FiSave, FiRefreshCw } from 'react-icons/fi';

export default function AdminConfigPage() {
  const router = useRouter();
  const { isAuthenticated, user } = useAuthStore();
  const [config, setConfig] = useState({
    rate_limit_per_minute: 60,
    rate_limit_per_hour: 1000,
    footer_text: 'Built by Nikhil Dodda',
    max_memory_items: 10000,
  });
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (!isAuthenticated || user?.username !== 'admin') {
      router.push('/');
    } else {
      fetchConfig();
    }
  }, [isAuthenticated, user, router]);

  const fetchConfig = async () => {
    setIsLoading(true);
    try {
      const response = await api.get('/api/admin/config');
      setConfig(response.data.config);
    } catch (error) {
      toast.error('Failed to load configuration');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await api.put('/api/admin/config', config);
      toast.success('Configuration saved successfully');
    } catch (error) {
      toast.error('Failed to save configuration');
    } finally {
      setIsSaving(false);
    }
  };

  const handleInputChange = (field: string, value: any) => {
    setConfig(prev => ({ ...prev, [field]: value }));
  };

  if (!isAuthenticated || user?.username !== 'admin') {
    return null;
  }

  return (
    <AdminLayout>
      <div className="max-w-4xl">
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">Configuration</h1>
          <p className="text-gray-400">Manage system settings and limits</p>
        </div>

        {isLoading ? (
          <div className="bg-gray-800 rounded-lg p-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Rate Limiting */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Rate Limiting</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Requests per Minute
                  </label>
                  <input
                    type="number"
                    value={config.rate_limit_per_minute}
                    onChange={(e) => handleInputChange('rate_limit_per_minute', parseInt(e.target.value))}
                    className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <p className="text-xs text-gray-400 mt-1">
                    Maximum API requests allowed per minute per IP
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Requests per Hour
                  </label>
                  <input
                    type="number"
                    value={config.rate_limit_per_hour}
                    onChange={(e) => handleInputChange('rate_limit_per_hour', parseInt(e.target.value))}
                    className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <p className="text-xs text-gray-400 mt-1">
                    Maximum API requests allowed per hour per IP
                  </p>
                </div>
              </div>
            </div>

            {/* Memory Settings */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Memory Settings</h2>
              <div>
                <label className="block text-sm font-medium mb-2">
                  Maximum Memory Items
                </label>
                <input
                  type="number"
                  value={config.max_memory_items}
                  onChange={(e) => handleInputChange('max_memory_items', parseInt(e.target.value))}
                  className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p className="text-xs text-gray-400 mt-1">
                  Maximum number of nodes allowed in the memory graph
                </p>
              </div>
            </div>

            {/* Attribution Settings */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Attribution</h2>
              <div>
                <label className="block text-sm font-medium mb-2">
                  Footer Text
                </label>
                <input
                  type="text"
                  value={config.footer_text}
                  onChange={(e) => handleInputChange('footer_text', e.target.value)}
                  className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p className="text-xs text-gray-400 mt-1">
                  Attribution text displayed in the application footer
                </p>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex justify-end space-x-4">
              <button
                onClick={fetchConfig}
                disabled={isLoading}
                className="px-6 py-2 bg-gray-700 hover:bg-gray-600 rounded-md transition flex items-center space-x-2"
              >
                <FiRefreshCw />
                <span>Reset</span>
              </button>
              <button
                onClick={handleSave}
                disabled={isSaving}
                className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 rounded-md transition flex items-center space-x-2"
              >
                <FiSave />
                <span>{isSaving ? 'Saving...' : 'Save Changes'}</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </AdminLayout>
  );
}