'use client';

import { useState, useEffect } from 'react';
import { getDbInsights, type DbInsightsResponse } from '@/lib/api';
import { ClipboardIcon, CheckIcon } from '@heroicons/react/24/outline';

export default function DbInsightsCard() {
  const [insights, setInsights] = useState<DbInsightsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copiedToken, setCopiedToken] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await getDbInsights();
        setInsights(response);
      } catch (err) {
        setError('Failed to load database insights');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text).then(
      () => {
        setCopiedToken(true);
        setTimeout(() => setCopiedToken(false), 2000);
      },
      () => {
        console.error('Failed to copy token');
      }
    );
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-red-500" />
      </div>
    );
  }

  if (error || !insights) {
    return (
      <div className="flex items-center justify-center h-full text-red-500">
        {error || 'No data available'}
      </div>
    );
  }

  return (
    <div className="overflow-y-auto h-full space-y-4">
      {/* Summary Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-gray-500">Users</h3>
          <p className="text-2xl font-semibold">{insights.user_count}</p>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-gray-500">Emails</h3>
          <p className="text-2xl font-semibold">{insights.email_count}</p>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-gray-500">Last Sync</h3>
          <p className="text-sm font-semibold">
            {insights.last_sync 
              ? new Date(insights.last_sync).toLocaleString() 
              : 'Never'}
          </p>
        </div>
      </div>

      {/* API Token */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <div className="flex justify-between items-center">
          <h3 className="text-sm font-medium text-gray-500">Sample Token</h3>
          <button 
            onClick={() => copyToClipboard(insights.sample_token)}
            className="text-gray-500 hover:text-gray-700"
          >
            {copiedToken ? (
              <CheckIcon className="h-5 w-5 text-green-500" />
            ) : (
              <ClipboardIcon className="h-5 w-5" />
            )}
          </button>
        </div>
        <p className="text-sm font-mono mt-1 bg-gray-100 p-2 rounded overflow-x-auto">
          {insights.sample_token}
        </p>
      </div>

      {/* Table Sizes */}
      <div>
        <h3 className="text-sm font-medium text-gray-500 mb-2">Table Sizes</h3>
        <div className="bg-white overflow-hidden shadow-sm sm:rounded-lg">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Table
                </th>
                <th scope="col" className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Size
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {insights.table_sizes.map((table, index) => (
                <tr key={`${table.table_name}-${index}`}>
                  <td className="px-3 py-2 whitespace-nowrap text-xs text-gray-900">
                    {table.table_name}
                  </td>
                  <td className="px-3 py-2 whitespace-nowrap text-xs text-gray-500">
                    {table.size}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* User Syncs */}
      {insights.user_syncs.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-gray-500 mb-2">Recent Syncs</h3>
          <div className="bg-white overflow-hidden shadow-sm sm:rounded-lg">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    User
                  </th>
                  <th scope="col" className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Last Sync
                  </th>
                  <th scope="col" className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Cadence (min)
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {insights.user_syncs.map((sync, index) => (
                  <tr key={`${sync.email}-${index}`}>
                    <td className="px-3 py-2 whitespace-nowrap text-xs text-gray-900">
                      {sync.email}
                    </td>
                    <td className="px-3 py-2 whitespace-nowrap text-xs text-gray-500">
                      {new Date(sync.last_fetched_at).toLocaleString()}
                    </td>
                    <td className="px-3 py-2 whitespace-nowrap text-xs text-gray-500">
                      {sync.sync_cadence_minutes}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
} 