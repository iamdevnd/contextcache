'use client';

import { useState } from 'react';
import { FiSearch, FiSettings, FiZap } from 'react-icons/fi';
import api from '@/lib/api';
import toast from 'react-hot-toast';

interface AdvancedSearchProps {
  onResults: (results: any) => void;
}

export default function AdvancedSearch({ onResults }: AdvancedSearchProps) {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [options, setOptions] = useState({
    useSemantic: true,
    usePagerank: true,
    useTimeDecay: true,
    limit: 10,
  });

  const handleSearch = async () => {
    if (!query.trim()) {
      toast.error('Please enter a search query');
      return;
    }

    setIsLoading(true);
    try {
      const response = await api.post('/api/memory/query/advanced', {
        query,
        top_k: options.limit,
        use_semantic: options.useSemantic,
        use_pagerank: options.usePagerank,
        use_time_decay: options.useTimeDecay,
      });

      onResults(response.data);
      
      if (response.data.results?.results?.length === 0) {
        toast('No results found', { icon: '🔍' });
      } else {
        toast.success(`Found ${response.data.results.results.length} results`);
      }
    } catch (error) {
      toast.error('Search failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold flex items-center">
          <FiZap className="mr-2 text-yellow-500" />
          Advanced Search
        </h2>
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="text-gray-400 hover:text-white transition"
        >
          <FiSettings />
        </button>
      </div>

      <div className="space-y-4">
        <div className="flex space-x-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="Search with AI-powered ranking..."
            className="flex-1 px-4 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={handleSearch}
            disabled={isLoading}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-md transition flex items-center"
          >
            <FiSearch className="mr-2" />
            {isLoading ? 'Searching...' : 'Search'}
          </button>
        </div>

        {showAdvanced && (
          <div className="bg-gray-700 rounded-md p-4 space-y-3">
            <h3 className="text-sm font-semibold text-gray-300 mb-2">Ranking Options</h3>
            
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={options.useSemantic}
                onChange={(e) => setOptions({ ...options, useSemantic: e.target.checked })}
                className="rounded bg-gray-600 border-gray-500"
              />
              <span className="text-sm">Semantic Similarity (AI)</span>
            </label>

            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={options.usePagerank}
                onChange={(e) => setOptions({ ...options, usePagerank: e.target.checked })}
                className="rounded bg-gray-600 border-gray-500"
              />
              <span className="text-sm">PageRank (Importance)</span>
            </label>

            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={options.useTimeDecay}
                onChange={(e) => setOptions({ ...options, useTimeDecay: e.target.checked })}
                className="rounded bg-gray-600 border-gray-500"
              />
              <span className="text-sm">Time Decay (Recency)</span>
            </label>

            <div>
              <label className="text-sm text-gray-300">Results Limit</label>
              <input
                type="number"
                min="1"
                max="50"
                value={options.limit}
                onChange={(e) => setOptions({ ...options, limit: parseInt(e.target.value) || 10 })}
                className="w-full mt-1 px-3 py-1 bg-gray-600 border border-gray-500 rounded text-sm"
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
