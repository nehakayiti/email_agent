import React from 'react';
import Link from 'next/link';
import { Email, archiveEmail, deleteEmail } from '@/lib/api';
import { formatRelativeTime } from '@/utils/date-utils';
import { EmailLabel, mapLabelsToComponents } from '@/components/ui/email-label';
import { toast } from 'react-hot-toast';
import { showSuccessToast, showErrorToast, showLoadingToast, dismissAllToasts } from '@/utils/toast-config';

// Filter out system labels and get the primary category label for display
function getPrimaryDisplayLabel(labels: string[]): string | null {
  if (!labels || labels.length === 0) return null;
  
  // Priority order for display
  const categoryLabels = [
    'CATEGORY_PERSONAL',
    'CATEGORY_UPDATES',
    'CATEGORY_SOCIAL',
    'CATEGORY_PROMOTIONS',
    'CATEGORY_FORUMS',
    'IMPORTANT',
    'ARCHIVE',
    'TRASH'
  ];
  
  // Find the first matching category label
  for (const categoryLabel of categoryLabels) {
    if (labels.includes(categoryLabel)) {
      return categoryLabel;
    }
  }
  
  // If no category labels, show Inbox if present
  if (labels.includes('INBOX')) {
    return 'INBOX';
  }
  
  return null;
}

interface EmailCardProps {
  email: Email;
  onClick?: () => void;
  isDeleted?: boolean;
  onLabelsUpdated?: (updatedEmail: Email) => void;
}

export function EmailCard({ email, onClick, isDeleted = false, onLabelsUpdated }: EmailCardProps) {
  // Filter out system labels
  const filteredLabels = React.useMemo(() => {
    if (!email.labels || email.labels.length === 0) return [];
    
    // Filter out system labels
    const systemLabels = ['EA_NEEDS_LABEL_UPDATE', 'SENT', 'DRAFT'];
    const visibleLabels = email.labels.filter(label => !systemLabels.includes(label));
    
    // If this email has TRASH label, don't display INBOX label
    if (visibleLabels.includes('TRASH')) {
      return visibleLabels.filter(label => label !== 'INBOX');
    }
    
    return visibleLabels;
  }, [email.labels]);

  // Handle archive action
  const handleArchive = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    try {
      const toastId = showLoadingToast('Archiving email...');
      
      const response = await archiveEmail(email.id);
      
      toast.dismiss(toastId);
      
      if (response.status === 'success') {
        showSuccessToast(response.message || 'Email archived successfully');
        
        // Update the email object with new labels
        const updatedEmail = {
          ...email,
          labels: response.labels || email.labels,
          // Update the category if returned from the API
          category: response.category || email.category
        };
        
        // Call onLabelsUpdated to update the parent component
        if (onLabelsUpdated) {
          onLabelsUpdated(updatedEmail);
        }
      } else {
        showErrorToast(response.message || 'Failed to archive email');
      }
    } catch (error) {
      dismissAllToasts();
      const errorMessage = error instanceof Error ? error.message : 'Error archiving email';
      showErrorToast(errorMessage);
      console.error('Error archiving email:', error);
    }
  };
  
  // Handle trash action
  const handleTrash = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    try {
      const toastId = showLoadingToast('Moving to trash...');
      
      const response = await deleteEmail(email.id);
      
      toast.dismiss(toastId);
      
      if (response.status === 'success') {
        showSuccessToast(response.message || 'Email moved to trash');
        
        // Update the email object with new category and labels
        const updatedEmail = {
          ...email,
          category: 'trash',
          labels: [...(email.labels || []).filter(label => label !== 'INBOX'), 'TRASH'],
        };
        
        // Call onLabelsUpdated to update the parent component
        if (onLabelsUpdated) {
          onLabelsUpdated(updatedEmail);
        }
      } else {
        showErrorToast(response.message || 'Failed to move email to trash');
      }
    } catch (error) {
      dismissAllToasts();
      const errorMessage = error instanceof Error ? error.message : 'Error moving email to trash';
      showErrorToast(errorMessage);
      console.error('Error moving email to trash:', error);
    }
  };

  // Create the container div element
  const containerClasses = `border-b border-gray-200 p-4 hover:bg-gray-50 ${
    !email.is_read ? 'bg-blue-50' : ''
  } ${isDeleted ? 'border-red-200 bg-red-50' : ''}`;
  
  const emailContent = (
    <div 
      className={containerClasses}
      onClick={onClick}
    >
      <div className="flex justify-between items-start mb-2">
        <div className="font-medium text-gray-900 truncate mr-2" style={{ maxWidth: 'calc(100% - 100px)' }}>
          {email.subject || '(No Subject)'}
        </div>
        <div className="text-sm text-gray-500 whitespace-nowrap">
          {formatRelativeTime(new Date(email.received_at))}
        </div>
      </div>
      
      <div className="flex justify-between items-center mb-2">
        <div className="text-sm text-gray-600 truncate mr-2" style={{ maxWidth: 'calc(100% - 140px)' }}>
          {email.from_email}
        </div>
        
        <div className="flex space-x-2">
          <button
            onClick={handleArchive}
            className="p-1 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded"
            title="Archive"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8" />
            </svg>
          </button>
          
          <button
            onClick={handleTrash}
            className="p-1 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded"
            title="Move to trash"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>
      
      {/* Display all labels */}
      <div className="flex flex-wrap gap-1 mb-2">
        {filteredLabels.length > 0 ? (
          mapLabelsToComponents(filteredLabels)
        ) : null}
      </div>
      
      <div className="text-sm text-gray-500 line-clamp-2">
        {email.snippet}
      </div>
    </div>
  );
  
  // If there's a click handler, don't wrap with Link
  if (onClick) {
    return emailContent;
  }
  
  // Otherwise, wrap with Link for navigation
  return (
    <Link href={`/emails/${email.id}`} className="block">
      {emailContent}
    </Link>
  );
} 