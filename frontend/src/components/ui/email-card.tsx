import React from 'react';
import Link from 'next/link';
import { Email, archiveEmail, deleteEmail, updateEmailLabels } from '@/lib/api';
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

  // Handle mark as read action
  const handleMarkAsRead = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    // Skip if already read
    if (email.is_read) {
      return;
    }
    
    try {
      const toastId = showLoadingToast('Marking as read...');
      
      const response = await updateEmailLabels(email.id, [], ['UNREAD']);
      
      toast.dismiss(toastId);
      
      if (response.status === 'success') {
        showSuccessToast('Email marked as read');
        
        // Update the email object with new read status
        const updatedEmail = {
          ...email,
          is_read: true,
          labels: response.labels || email.labels,
        };
        
        // Call onLabelsUpdated to update the parent component
        if (onLabelsUpdated) {
          onLabelsUpdated(updatedEmail);
        }
      } else {
        showErrorToast(response.message || 'Failed to mark email as read');
      }
    } catch (error) {
      dismissAllToasts();
      const errorMessage = error instanceof Error ? error.message : 'Error marking email as read';
      showErrorToast(errorMessage);
      console.error('Error marking email as read:', error);
    }
  };

  // Handle mark as unread action
  const handleMarkAsUnread = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    // Skip if already unread
    if (!email.is_read) {
      return;
    }
    
    try {
      const toastId = showLoadingToast('Marking as unread...');
      
      const response = await updateEmailLabels(email.id, ['UNREAD'], []);
      
      toast.dismiss(toastId);
      
      if (response.status === 'success') {
        showSuccessToast('Email marked as unread');
        
        // Update the email object with new read status
        const updatedEmail = {
          ...email,
          is_read: false,
          labels: response.labels || email.labels,
        };
        
        // Call onLabelsUpdated to update the parent component
        if (onLabelsUpdated) {
          onLabelsUpdated(updatedEmail);
        }
      } else {
        showErrorToast(response.message || 'Failed to mark email as unread');
      }
    } catch (error) {
      dismissAllToasts();
      const errorMessage = error instanceof Error ? error.message : 'Error marking email as unread';
      showErrorToast(errorMessage);
      console.error('Error marking email as unread:', error);
    }
  };

  // Create the container div element
  const containerClasses = `
    ${!email.is_read 
      ? 'border-l-4 border-l-indigo-500 bg-white font-medium' 
      : 'border-l-4 border-l-transparent bg-gray-50 font-normal'}
    border border-gray-200 rounded-md mb-2 p-4 
    hover:shadow-md hover:border-indigo-200 transition-all duration-150
    ${isDeleted ? 'border-red-200 bg-red-50' : ''}
  `;
  
  const emailContent = (
    <div 
      className={containerClasses}
      onClick={onClick}
    >
      <div className="flex justify-between items-start mb-2">
        <div className={`text-gray-900 truncate mr-2 ${!email.is_read ? 'font-semibold' : ''}`} style={{ maxWidth: 'calc(100% - 100px)' }}>
          {email.subject || '(No Subject)'}
        </div>
        <div className="text-sm text-gray-500 whitespace-nowrap">
          {formatRelativeTime(new Date(email.received_at))}
        </div>
      </div>
      
      <div className="flex justify-between items-center mb-2">
        <div className={`text-sm truncate mr-2 ${!email.is_read ? 'text-gray-700' : 'text-gray-600'}`} style={{ maxWidth: 'calc(100% - 140px)' }}>
          {email.from_email}
        </div>
        
        <div className="flex space-x-2">
          {/* Mark as Read/Unread button */}
          {email.is_read ? (
            <button
              onClick={handleMarkAsUnread}
              className="p-1.5 text-gray-500 hover:text-indigo-600 hover:bg-indigo-50 rounded transition-colors"
              title="Mark as unread"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </button>
          ) : (
            <button
              onClick={handleMarkAsRead}
              className="p-1.5 text-gray-500 hover:text-green-600 hover:bg-green-50 rounded transition-colors"
              title="Mark as read"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 19h18M3 14h18M3 9h18M3 4h18" />
              </svg>
            </button>
          )}
          
          <button
            onClick={handleArchive}
            className="p-1.5 text-gray-500 hover:text-indigo-600 hover:bg-indigo-50 rounded transition-colors"
            title="Archive"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8" />
            </svg>
          </button>
          
          <button
            onClick={handleTrash}
            className="p-1.5 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
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
      
      <div className={`text-sm line-clamp-2 ${!email.is_read ? 'text-gray-700' : 'text-gray-500'}`}>
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