import React from 'react';

interface EmailLabelProps {
  label: string;
  className?: string;
}

/**
 * Converts raw Gmail labels to user-friendly display labels
 */
export function getDisplayLabel(label: string): string {
  const labelMap: Record<string, string> = {
    'INBOX': 'Inbox',
    'UNREAD': 'Unread',
    'TRASH': 'Trash',
    'IMPORTANT': 'Important',
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
      return 'bg-blue-100 text-blue-700';
    case 'UNREAD':
      return 'bg-yellow-100 text-yellow-700';
    case 'TRASH':
      return 'bg-red-100 text-red-700';
    case 'IMPORTANT':
      return 'bg-amber-100 text-amber-700';
    case 'ARCHIVE':
      return 'bg-gray-100 text-gray-700';
    case 'CATEGORY_UPDATES':
    case 'UPDATES':
      return 'bg-purple-100 text-purple-700';
    case 'CATEGORY_SOCIAL':
    case 'SOCIAL':
      return 'bg-green-100 text-green-700';
    case 'CATEGORY_PROMOTIONS':
    case 'PROMOTIONS':
      return 'bg-orange-100 text-orange-700';
    case 'CATEGORY_PERSONAL':
    case 'PERSONAL':
      return 'bg-indigo-100 text-indigo-700';
    case 'CATEGORY_FORUMS':
    case 'FORUMS':
      return 'bg-teal-100 text-teal-700';
    default:
      return 'bg-gray-100 text-gray-700';
  }
}

/**
 * Email label component that displays a user-friendly label with appropriate styling
 */
export function EmailLabel({ label, className = '' }: EmailLabelProps) {
  const displayLabel = getDisplayLabel(label);
  const style = getLabelStyle(label);
  
  return (
    <span className={`px-2 py-0.5 rounded-md text-xs ${style} ${className}`}>
      {displayLabel}
    </span>
  );
}

/**
 * Filters and maps raw Gmail labels to display-friendly EmailLabel components
 */
export function mapLabelsToComponents(labels: string[], showSystem = false): React.ReactNode[] {
  if (!labels || labels.length === 0) return [];
  
  // System labels that shouldn't be displayed by default
  const systemLabels = ['EA_NEEDS_LABEL_UPDATE', 'SENT', 'DRAFT'];
  
  return labels
    .filter(label => showSystem || !systemLabels.includes(label))
    .map(label => (
      <EmailLabel key={label} label={label} />
    ));
} 