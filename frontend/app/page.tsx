
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store/auth';
import api from '@/lib/api';
import { endpoints } from '@/lib/config';
import toast from 'react-hot-toast';
import { FiLogOut, FiDatabase, FiSearch, FiUpload } from 'react-icons/fi';

export default function HomePage() {
  const router = useRouter();
  const { isAuthenticated, checkAuth, logout, user } = useAuthStore();
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [stats, setStats] = useState<any>(null);
  const [queryText, setQueryText] = useState('');
  const [queryResults, setQueryResults] = useState<any>(null);

  useEffect(() => {
    checkAuth().then(() => {
      if (!isAuthenticated) {
        router.push('/login');
      } else {
        fetchStats();
      }
    });
  }, [isAuthenticated, checkAuth, router]);

  const fetchStats = async () => {
    try {
      const response = await api.get('/api/memory/stats');
      setStats(response.data.stats);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const handleInsertMemory = async () => {
    if (!inputText.trim()) {
      toast.error('Please enter some text');
      return;
    }

    setIsLoading(true);
    try {
      const response = await api.post(endpoints.memory.insert, {
        text: inputText,
        extract_triples: true,
      });

      toast.success(
        `Memory inserted! Extracted ${response.data.triples_extracted} triples.`
      );
      setInputText('');
      fetchStats(); // Refresh stats
    } catch (error) {
      toast.error('Failed to insert memory');
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuery = async () => {
    if (!queryText.trim()) {
      toast.error('Please enter a query');
      return;
    }

    setIsLoading(true);
    try {
      const response = await api.post(endpoints.memory.query, {
        query: queryText,
        top_k: 10,
      });

      setQueryResults(response.data);
    } catch (error) {
      toast.error('Failed to query memory');
    } finally {
      setIsLoading(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-900">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">ContextCache</h1>
            <p className="text-sm text-gray-400">AI Memory Engine</p>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-gray-400">Welcome, {user?.username}</span>
            <button
              onClick={logout}
              className="flex items-center space-x-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-md transition"
            >
              <FiLogOut />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Insert Memory Section */}
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center">
              <FiUpload className="mr-2" />
              Insert Memory
            </h2>
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Enter text to extract knowledge from..."
              className="w-full h-32 px-4 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={handleInsertMemory}
              disabled={isLoading}
              className="mt-4 w-full py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-md transition"
            >
              {isLoading ? 'Processing...' : 'Extract & Store Triples'}
            </button>
          </div>

          {/* Query Memory Section */}
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center">
              <FiSearch className="mr-2" />
              Query Memory
            </h2>
            <input
              type="text"
              value={queryText}
              onChange={(e) => setQueryText(e.target.value)}
              placeholder="Search the knowledge graph..."
              className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={handleQuery}
              disabled={isLoading}
              className="mt-4 w-full py-2 bg-green-600 hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-md transition"
            >
              {isLoading ? 'Searching...' : 'Search'}
            </button>

            {queryResults && (
              <div className="mt-4 p-4 bg-gray-700 rounded-md">
                <h3 className="font-semibold mb-2">Results:</h3>
                <pre className="text-sm overflow-auto max-h-64">
                  {JSON.stringify(queryResults, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </div>

        {/* Stats Section */}
        {stats && (
          <div className="mt-8 bg-gray-800 rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center">
              <FiDatabase className="mr-2" />
              Memory Statistics
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-gray-700 p-4 rounded-md">
                <p className="text-gray-400 text-sm">Total Nodes</p>
                <p className="text-2xl font-bold">{stats.total_nodes}</p>
              </div>
              <div className="bg-gray-700 p-4 rounded-md">
                <p className="text-gray-400 text-sm">Total Edges</p>
                <p className="text-2xl font-bold">{stats.total_edges}</p>
              </div>
              <div className="bg-gray-700 p-4 rounded-md">
                <p className="text-gray-400 text-sm">Immediate Memory</p>
                <p className="text-2xl font-bold">{stats.memory_layers?.immediate || 0}</p>
              </div>
              <div className="bg-gray-700 p-4 rounded-md">
                <p className="text-gray-400 text-sm">Long-term Memory</p>
                <p className="text-2xl font-bold">{stats.memory_layers?.long_term || 0}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}