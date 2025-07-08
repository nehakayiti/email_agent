'use client';

import { useState } from 'react';
import { ActionRule } from '@/lib/api';

interface ActionRuleDisplayProps {
  rules: ActionRule[];
  categoryId: number;
  categoryName: string;
  onEdit: (rule: ActionRule) => void;
  onPreview: (rule: ActionRule) => void;
  onToggle: (rule: ActionRule, enabled: boolean) => void;
  onAddRule: () => void;
  onDeleteRule: (rule: ActionRule) => void;
}

export function ActionRuleDisplay({
  rules,
  categoryId,
  categoryName,
  onEdit,
  onPreview,
  onToggle,
  onAddRule,
  onDeleteRule,
}: ActionRuleDisplayProps) {
  const [expanded, setExpanded] = useState(false);

  const getActionIcon = (action: string) => {
    switch (action) {
      case 'ARCHIVE':
        return '📤';
      case 'TRASH':
        return '🗑️';
      default:
        return '⚙️';
    }
  };

  const getActionColor = (action: string) => {
    switch (action) {
      case 'ARCHIVE':
        return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'TRASH':
        return 'text-red-600 bg-red-50 border-red-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getStatusColor = (enabled: boolean) => {
    return enabled ? 'text-green-600' : 'text-gray-400';
  };

  if (rules.length === 0) {
    return (
      <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-lg">🎯</span>
            <span className="font-medium text-gray-700">Action Rules</span>
          </div>
          <button
            onClick={onAddRule}
            className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-indigo-600 bg-indigo-50 border border-indigo-200 rounded-md hover:bg-indigo-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
          >
            <span className="mr-1">➕</span>
            Add Action Rules
          </button>
        </div>
        <p className="mt-2 text-sm text-gray-500">
          No action rules configured for this category yet.
        </p>
      </div>
    );
  }

  return (
    <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <span className="text-lg">🎯</span>
          <span className="font-medium text-gray-700">Action Rules</span>
          <span className="text-sm text-gray-500">({rules.length})</span>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-sm text-gray-500 hover:text-gray-700 focus:outline-none"
          >
            {expanded ? 'Show Less' : 'Show Details'}
          </button>
          <button
            onClick={onAddRule}
            className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-indigo-600 bg-indigo-50 border border-indigo-200 rounded-md hover:bg-indigo-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
          >
            <span className="mr-1">➕</span>
            Add Another Rule
          </button>
        </div>
      </div>

      <div className="mt-3 space-y-3">
        {rules.map((rule, index) => (
          <div
            key={`${rule.category_id}-${index}`}
            className={`p-3 rounded-lg border ${getActionColor(rule.action || '')} transition-all duration-200`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <span className="text-lg">{getActionIcon(rule.action || '')}</span>
                <div>
                  <div className="font-medium">
                    {rule.action === 'ARCHIVE' ? 'Archive' : 'Trash'} after {rule.delay_days} days
                  </div>
                  <div className="text-sm opacity-75">
                    Status: <span className={getStatusColor(rule.enabled)}>
                      {rule.enabled ? 'Active' : 'Disabled'}
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="flex items-center space-x-1">
                <button
                  onClick={() => onPreview(rule)}
                  className="px-2 py-1 text-xs font-medium text-gray-600 bg-white border border-gray-300 rounded hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-gray-500 transition-colors"
                >
                  Preview
                </button>
                <button
                  onClick={() => onEdit(rule)}
                  className="px-2 py-1 text-xs font-medium text-blue-600 bg-white border border-blue-300 rounded hover:bg-blue-50 focus:outline-none focus:ring-1 focus:ring-blue-500 transition-colors"
                >
                  Edit
                </button>
                <button
                  onClick={() => onToggle(rule, !rule.enabled)}
                  className={`px-2 py-1 text-xs font-medium rounded border transition-colors focus:outline-none focus:ring-1 ${
                    rule.enabled
                      ? 'text-red-600 bg-white border-red-300 hover:bg-red-50 focus:ring-red-500'
                      : 'text-green-600 bg-white border-green-300 hover:bg-green-50 focus:ring-green-500'
                  }`}
                >
                  {rule.enabled ? 'Disable' : 'Enable'}
                </button>
                <button
                  onClick={() => onDeleteRule(rule)}
                  className="px-2 py-1 text-xs font-medium text-red-600 bg-white border border-red-300 rounded hover:bg-red-50 focus:outline-none focus:ring-1 focus:ring-red-500 transition-colors"
                >
                  Delete
                </button>
              </div>
            </div>

            {expanded && (
              <div className="mt-3 pt-3 border-t border-current border-opacity-20">
                <div className="text-sm">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <span className="font-medium">Action Type:</span>
                      <span className="ml-1">{rule.action}</span>
                    </div>
                    <div>
                      <span className="font-medium">Delay:</span>
                      <span className="ml-1">{rule.delay_days} days</span>
                    </div>
                    <div>
                      <span className="font-medium">Status:</span>
                      <span className={`ml-1 ${getStatusColor(rule.enabled)}`}>
                        {rule.enabled ? 'Active' : 'Disabled'}
                      </span>
                    </div>
                    <div>
                      <span className="font-medium">Category:</span>
                      <span className="ml-1">{rule.category_name}</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
} 