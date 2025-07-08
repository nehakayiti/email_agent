'use client';

import { ActionRuleRequest } from '@/lib/api';

interface ActionRuleSuggestion {
  id: string;
  title: string;
  description: string;
  rule: ActionRuleRequest;
  icon: string;
  color: string;
}

interface ActionRuleSuggestionsProps {
  categoryName: string;
  onSelectSuggestion: (suggestion: ActionRuleRequest) => void;
}

export function ActionRuleSuggestions({
  categoryName,
  onSelectSuggestion,
}: ActionRuleSuggestionsProps) {
  const getSuggestionsForCategory = (categoryName: string): ActionRuleSuggestion[] => {
    const categoryLower = categoryName.toLowerCase();
    
    if (categoryLower.includes('promotion') || categoryLower.includes('marketing') || categoryLower.includes('newsletter')) {
      return [
        {
          id: 'promo-trash',
          title: 'Trash after 3 days',
          description: 'Quick cleanup for promotional emails',
          rule: { action: 'TRASH', delay_days: 3, enabled: true },
          icon: '🗑️',
          color: 'bg-red-50 border-red-200 text-red-700',
        },
        {
          id: 'promo-archive',
          title: 'Archive after 1 day (if not opened)',
          description: 'Archive unopened promotions quickly',
          rule: { action: 'ARCHIVE', delay_days: 1, enabled: true },
          icon: '📤',
          color: 'bg-blue-50 border-blue-200 text-blue-700',
        },
      ];
    }
    
    if (categoryLower.includes('social') || categoryLower.includes('notification')) {
      return [
        {
          id: 'social-archive',
          title: 'Archive after 7 days',
          description: 'Keep social notifications for a week',
          rule: { action: 'ARCHIVE', delay_days: 7, enabled: true },
          icon: '📤',
          color: 'bg-blue-50 border-blue-200 text-blue-700',
        },
      ];
    }
    
    if (categoryLower.includes('update') || categoryLower.includes('alert')) {
      return [
        {
          id: 'update-archive',
          title: 'Archive after 14 days',
          description: 'Keep updates for two weeks',
          rule: { action: 'ARCHIVE', delay_days: 14, enabled: true },
          icon: '📤',
          color: 'bg-blue-50 border-blue-200 text-blue-700',
        },
      ];
    }
    
    if (categoryLower.includes('primary') || categoryLower.includes('important')) {
      return [
        {
          id: 'primary-archive',
          title: 'Archive after 30 days',
          description: 'Keep important emails for a month',
          rule: { action: 'ARCHIVE', delay_days: 30, enabled: true },
          icon: '📤',
          color: 'bg-blue-50 border-blue-200 text-blue-700',
        },
      ];
    }
    
    // Default suggestions for any category
    return [
      {
        id: 'default-archive',
        title: 'Archive after 7 days',
        description: 'Standard archiving rule',
        rule: { action: 'ARCHIVE', delay_days: 7, enabled: true },
        icon: '📤',
        color: 'bg-blue-50 border-blue-200 text-blue-700',
      },
      {
        id: 'default-trash',
        title: 'Trash after 14 days',
        description: 'Remove old emails',
        rule: { action: 'TRASH', delay_days: 14, enabled: true },
        icon: '🗑️',
        color: 'bg-red-50 border-red-200 text-red-700',
      },
    ];
  };

  const suggestions = getSuggestionsForCategory(categoryName);

  return (
    <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
      <div className="flex items-center space-x-2 mb-3">
        <span className="text-lg">💡</span>
        <span className="font-medium text-gray-700">Suggested Rules</span>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {suggestions.map((suggestion) => (
          <button
            key={suggestion.id}
            onClick={() => onSelectSuggestion(suggestion.rule)}
            className={`p-3 rounded-lg border ${suggestion.color} hover:shadow-md transition-all duration-200 text-left focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500`}
          >
            <div className="flex items-start space-x-3">
              <span className="text-xl">{suggestion.icon}</span>
              <div className="flex-1">
                <div className="font-medium">{suggestion.title}</div>
                <div className="text-sm opacity-75 mt-1">{suggestion.description}</div>
              </div>
            </div>
          </button>
        ))}
      </div>
      
      <div className="mt-3 text-sm text-gray-500">
        <p>💡 These suggestions are based on the category type. You can customize them after adding.</p>
      </div>
    </div>
  );
} 