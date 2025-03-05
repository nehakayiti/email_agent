import React from 'react';

interface EmailLabelProps {
  label: string;
  className?: string;
  variant?: 'default' | 'compact';
}

/**
 * Converts raw Gmail labels to user-friendly display labels
 */
export function getDisplayLabel(label: string): string {
  const labelMap: Record<string, string> = {
    'INBOX': 'Inbox',
    'UNREAD': 'Unread',
    'TRASH': 'Trash',
    'IMPORTANT': '★',
    'ARCHIVE': 'Archive',
    'CATEGORY_UPDATES': 'Updates',
    'CATEGORY_SOCIAL': 'Social',
    'CATEGORY_PROMOTIONS': 'Promotions',
    'CATEGORY_PERSONAL': 'Personal',
    'CATEGORY_FORUMS': 'Forums',
  };
  
  return labelMap[label] || label;
}

/**
 * Gets the appropriate styling for different label types
 */
export function getLabelStyle(label: string): string {
  // Define different background and text colors for different labels
  switch (label.toUpperCase()) {
    case 'INBOX':
      return 'bg-blue-100 text-blue-800 border border-blue-200';
    case 'UNREAD':
      return 'bg-yellow-100 text-yellow-800 border border-yellow-200';
    case 'TRASH':
      return 'bg-red-100 text-red-800 border border-red-200';
    case 'IMPORTANT':
      return 'bg-amber-100 text-amber-800 border border-amber-200';
    case 'ARCHIVE':
      return 'bg-gray-100 text-gray-800 border border-gray-200';
    case 'CATEGORY_UPDATES':
      return 'bg-purple-100 text-purple-800 border border-purple-200';
    case 'CATEGORY_SOCIAL':
      return 'bg-green-100 text-green-800 border border-green-200';
    case 'CATEGORY_PROMOTIONS':
      return 'bg-orange-100 text-orange-800 border border-orange-200';
    case 'CATEGORY_PERSONAL':
      return 'bg-indigo-100 text-indigo-800 border border-indigo-200';
    case 'CATEGORY_FORUMS':
      return 'bg-teal-100 text-teal-800 border border-teal-200';
    case 'PRIMARY':
      return 'bg-blue-100 text-blue-800 border border-blue-200';
    default:
      return 'bg-gray-100 text-gray-800 border border-gray-200';
  }
}

/**
 * Email label component that displays a user-friendly label with appropriate styling
 */
export function EmailLabel({ label, className = '', variant = 'default' }: EmailLabelProps) {
  const displayLabel = getDisplayLabel(label);
  const style = getLabelStyle(label);
  const isImportant = label.toUpperCase() === 'IMPORTANT';
  
  // For important label, show just the star
  if (isImportant) {
    return (
      <span className={`inline-flex items-center text-amber-500 ${className}`} title="Important">
        {displayLabel}
      </span>
    );
  }
  
  // For compact variant, use smaller padding
  const baseClasses = variant === 'compact' 
    ? 'px-2 py-0.5 text-xs font-medium rounded-full'
    : 'px-2.5 py-0.5 text-xs font-medium rounded-full';
  
  return (
    <span className={`${baseClasses} ${style} ${className}`}>
      {displayLabel}
    </span>
  );
}

/**
 * Filters and maps raw Gmail labels to display-friendly EmailLabel components
 */
export function mapLabelsToComponents(
  labels: string[], 
  options: { 
    showSystem?: boolean;
    variant?: 'default' | 'compact';
  } = {}
): React.ReactNode[] {
  const { showSystem = false, variant = 'default' } = options;
  
  if (!labels || labels.length === 0) return [];
  
  // System labels that shouldn't be displayed
  const systemLabels = ['EA_NEEDS_LABEL_UPDATE', 'SENT', 'DRAFT'];
  
  // Important label should always be first if present
  const sortedLabels = [...labels].sort((a, b) => {
    if (a === 'IMPORTANT') return -1;
    if (b === 'IMPORTANT') return 1;
    return 0;
  });
  
  return sortedLabels
    .filter(label => {
      if (!showSystem && systemLabels.includes(label)) return false;
      // Don't show category labels here since they're handled separately
      if (label.startsWith('CATEGORY_') || label === 'PRIMARY') return false;
      return true;
    })
    .map(label => (
      <EmailLabel key={label} label={label} variant={variant} />
    ));
} 