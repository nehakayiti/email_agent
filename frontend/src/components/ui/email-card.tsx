import React, { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import { Email, archiveEmail, deleteEmail, updateEmailLabels, updateEmailCategory } from '@/lib/api';
import { formatRelativeTime } from '@/utils/date-utils';
import { EmailLabel, mapLabelsToComponents } from '@/components/ui/email-label';
import { toast } from 'react-hot-toast';
import { showSuccessToast, showErrorToast, showLoadingToast, dismissAllToasts } from '@/utils/toast-config';
import { useCategoryContext } from '@/lib/category-context';

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

// Get category display info
function getCategoryDisplayInfo(category: string): { display_name: string; color: string; description: string | null } | null {
  // This function should be used with the CategoryContext's getCategoryInfo
  // It remains here for compatibility with existing code, but will delegate to the context
  
  // Default category information if needed - we'll use the same format as CategoryContext
  const defaultCategoryMap: Record<string, { display_name: string; color: string; description: string | null }> = {
    'CATEGORY_PERSONAL': { display_name: 'Personal', color: 'bg-indigo-100 text-indigo-800 border border-indigo-200', description: null },
    'CATEGORY_UPDATES': { display_name: 'Updates', color: 'bg-purple-100 text-purple-800 border border-purple-200', description: null },
    'CATEGORY_SOCIAL': { display_name: 'Social', color: 'bg-green-100 text-green-800 border border-green-200', description: null },
    'CATEGORY_PROMOTIONS': { display_name: 'Promotions', color: 'bg-orange-100 text-orange-800 border border-orange-200', description: null },
    'CATEGORY_FORUMS': { display_name: 'Forums', color: 'bg-teal-100 text-teal-800 border border-teal-200', description: null },
    'PRIMARY': { display_name: 'Primary', color: 'bg-blue-100 text-blue-800 border border-blue-200', description: null },
  };

  return defaultCategoryMap[category] || null;
}

// Separate labels into categories and regular labels
function separateLabels(labels: string[]): { categories: string[]; regularLabels: string[] } {
  const categories = labels.filter(label => label.startsWith('CATEGORY_') || label === 'PRIMARY');
  const regularLabels = labels.filter(label => 
    !label.startsWith('CATEGORY_') && 
    !label.startsWith('EA_') && 
    label !== 'PRIMARY' &&
    !['SENT', 'DRAFT'].includes(label)
  );
  
  return { categories, regularLabels };
}

interface EmailCardProps {
  email: Email;
  onClick?: () => void;
  isDeleted?: boolean;
  onLabelsUpdated?: (updatedEmail: Email) => void;
}

export function EmailCard({ email, onClick, isDeleted = false, onLabelsUpdated }: EmailCardProps) {
  // Use the category context
  const { getCategoryInfo, categories } = useCategoryContext();
  const [updating, setUpdating] = useState(false);
  const [showCategoryDropdown, setShowCategoryDropdown] = useState(false);
  const categoryBadgeRef = useRef<HTMLDivElement>(null);
  const [dropdownPosition, setDropdownPosition] = useState({ top: 0, left: 0 });
  const [showArrowAnimation, setShowArrowAnimation] = useState(true);
  
  // Disable arrow animation after a short delay
  useEffect(() => {
    const timer = setTimeout(() => {
      setShowArrowAnimation(false);
    }, 2000);
    
    return () => clearTimeout(timer);
  }, []);
  
  // Update dropdown position when it's shown
  useEffect(() => {
    if (showCategoryDropdown && categoryBadgeRef.current) {
      const rect = categoryBadgeRef.current.getBoundingClientRect();
      setDropdownPosition({
        top: rect.bottom + window.scrollY,
        left: rect.left + window.scrollX
      });
    }
  }, [showCategoryDropdown]);
  
  // Filter out system labels
  const filteredLabels = React.useMemo(() => {
    if (!email.labels || email.labels.length === 0) return [];
    
    // Filter out system labels and category labels (we'll show categories separately)
    const systemLabels = ['EA_NEEDS_LABEL_UPDATE', 'SENT', 'DRAFT'];
    const visibleLabels = email.labels.filter(label => 
      !systemLabels.includes(label) && 
      !label.startsWith('CATEGORY_')
    );
    
    // If this email has TRASH label, don't display INBOX label
    if (visibleLabels.includes('TRASH')) {
      return visibleLabels.filter(label => label !== 'INBOX');
    }
    
    return visibleLabels;
  }, [email.labels]);

  // Get category display info
  const categoryInfo = React.useMemo(() => {
    // First check if the email has the TRASH label, and if so, prioritize it
    if (email.labels && email.labels.includes('TRASH')) {
      return getCategoryInfo('TRASH') || { display_name: 'Trash', color: 'bg-red-50 text-red-700', description: null };
    }
    
    // If we have a category value from the email, use that
    if (email.category) {
      const info = getCategoryInfo(email.category);
      if (info) return info;
    }
    
    // If no category is found or the lookup failed, check if the email has a category label
    if (email.labels) {
      const categoryLabel = email.labels.find(label => label.startsWith('CATEGORY_') || label === 'PRIMARY');
      if (categoryLabel) {
        const info = getCategoryInfo(categoryLabel);
        if (info) return info;
      }
    }
    
    // Default fallback
    return getCategoryInfo('primary') || { display_name: 'Primary', color: 'bg-blue-50 text-blue-700', description: null };
  }, [email.category, email.labels, getCategoryInfo]);

  // Create a derived property to determine if the email is unread
  const isUnread = React.useMemo(() => {
    // An email is unread if is_read is false OR it has the UNREAD label
    return !email.is_read || email.labels.includes('UNREAD');
  }, [email.is_read, email.labels]);

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
    if (email.is_read && !email.labels.includes('UNREAD')) {
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
    if (!email.is_read || email.labels.includes('UNREAD')) {
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

  // Handle category change
  const handleCategoryChange = async (e: React.MouseEvent<HTMLElement>, newCategory: string) => {
    e.preventDefault();
    e.stopPropagation();
    
    // Skip if already in this category
    if (email.category?.toLowerCase() === newCategory.toLowerCase()) {
      return;
    }
    
    try {
      setUpdating(true);
      const toastId = showLoadingToast('Updating category...');
      
      const response = await updateEmailCategory(email.id, newCategory.toLowerCase());
      
      toast.dismiss(toastId);
      
      if (response.status === 'success') {
        showSuccessToast('Category updated');
        
        // Update the email object with new category and labels
        const updatedEmail = {
          ...email,
          category: response.category,
          labels: response.labels,
        };
        
        // Call onLabelsUpdated to update the parent component
        if (onLabelsUpdated) {
          onLabelsUpdated(updatedEmail);
        }
      } else {
        showErrorToast(response.message || 'Failed to update category');
      }
    } catch (error) {
      dismissAllToasts();
      const errorMessage = error instanceof Error ? error.message : 'Error updating category';
      showErrorToast(errorMessage);
      console.error('Error updating category:', error);
    } finally {
      setUpdating(false);
    }
  };

  // Create the email card content
  const emailContent = (
    <div 
      className={`p-4 border-b border-gray-200 hover:bg-gray-50 cursor-pointer transition-all ${isUnread ? 'bg-slate-50' : ''}`}
      onClick={onClick}
    >
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 mt-0.5">
          {isUnread && (
            <div className="h-2 w-2 rounded-full bg-blue-600" title="Unread"></div>
          )}
        </div>
        
        <div className="min-w-0 flex-1">
          <div className="flex items-center justify-between mb-1">
            <div className="truncate font-medium text-sm">
              {email.from_email}
            </div>
            <div className="text-xs text-gray-500 whitespace-nowrap ml-2">
              {formatRelativeTime(new Date(email.received_at))}
            </div>
          </div>
          
          <div className="flex justify-between items-start">
            <div className="truncate font-medium text-base mb-1">
              {email.subject || '(No subject)'}
            </div>
          </div>
          
          <div className="text-sm text-gray-500 line-clamp-1 mb-2">
            {email.snippet}
          </div>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {/* Category badge */}
              <div className="relative">
                <div 
                  ref={categoryBadgeRef}
                  className={`text-xs px-2 py-1 rounded-md bg-white shadow-sm cursor-pointer flex items-center gap-1 hover:shadow transition-all border border-gray-300 hover:border-gray-400 ${showCategoryDropdown ? 'ring-2 ring-blue-300 border-blue-300' : ''}`}
                  onClick={(e) => {
                    e.stopPropagation();
                    setShowCategoryDropdown(!showCategoryDropdown);
                  }}
                  title="Click to change category"
                >
                  <span className="font-medium mr-1 text-gray-500">Category:</span>
                  <span className={`mr-1 px-1.5 py-0.5 rounded ${categoryInfo.color}`}>{categoryInfo.display_name}</span>
                  <span className="border-l border-gray-300 pl-1 flex items-center text-gray-500 bg-gray-50 -mr-2 -my-1 py-1 px-1 rounded-r-md">
                    <span className="text-xs mr-1 font-medium">Select</span>
                    <svg 
                      xmlns="http://www.w3.org/2000/svg" 
                      className={`h-4 w-4 transition-transform ${showCategoryDropdown ? 'rotate-180' : ''} ${
                        showArrowAnimation ? 'animate-bounce' : ''
                      }`} 
                      viewBox="0 0 24 24" 
                      fill="none" 
                      stroke="currentColor" 
                      strokeWidth="2" 
                      strokeLinecap="round" 
                      strokeLinejoin="round"
                    >
                      <polyline points="6 9 12 15 18 9"></polyline>
                    </svg>
                  </span>
                </div>
                
                {/* Dropdown menu */}
                {showCategoryDropdown && (
                  <div 
                    className="fixed inset-0 z-10"
                    onClick={(e) => {
                      e.stopPropagation();
                      setShowCategoryDropdown(false);
                    }}
                  >
                    <div 
                      style={{
                        position: 'absolute',
                        top: `${dropdownPosition.top}px`,
                        left: `${dropdownPosition.left}px`,
                      }}
                      className="mt-1 w-48 bg-white rounded-md shadow-lg z-20 border border-gray-200 overflow-hidden"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <div className="py-1 max-h-60 overflow-y-auto">
                        <div className="px-4 py-2 text-xs font-medium text-gray-500 border-b border-gray-100 bg-gray-50">
                          Change category
                        </div>
                        {updating && (
                          <div className="px-4 py-2 text-xs text-gray-500 flex items-center justify-center">
                            <svg className="animate-spin h-3 w-3 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            Updating...
                          </div>
                        )}
                        {categories
                          .slice() // Create a copy to avoid mutating the original array
                          .sort((a, b) => a.priority - b.priority) // Sort by priority
                          .map((category) => {
                          const isSelected = email.category?.toLowerCase() === category.name.toLowerCase();
                          return (
                            <button
                              key={category.name}
                              className={`w-full text-left px-4 py-2 text-sm hover:bg-gray-50 flex items-center justify-between ${
                                isSelected ? 'bg-gray-50 font-medium' : ''
                              }`}
                              onClick={(e) => {
                                handleCategoryChange(e, category.name.toLowerCase());
                                setShowCategoryDropdown(false);
                              }}
                              disabled={updating}
                            >
                              <span>{category.display_name}</span>
                              {isSelected && (
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                </svg>
                              )}
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  </div>
                )}
              </div>
              
              {/* Regular labels */}
              <div className="flex flex-wrap gap-1">
                {mapLabelsToComponents(filteredLabels, { variant: 'compact', showPrefix: false })}
              </div>
            </div>
            
            {/* Email actions */}
            <div className="ml-auto flex gap-1">
              {!isDeleted && !email.labels.includes('TRASH') && (
                <>
                  {!isUnread ? (
                    <button
                      onClick={handleMarkAsUnread}
                      className="p-1 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded"
                      title="Mark as unread"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                    </button>
                  ) : (
                    <button
                      onClick={handleMarkAsRead}
                      className="p-1 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded"
                      title="Mark as read"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 19v-8.93a2 2 0 01.89-1.664l7-4.666a2 2 0 012.22 0l7 4.666A2 2 0 0121 10.07V19M3 19a2 2 0 002 2h14a2 2 0 002-2M3 19l6.75-4.5M21 19l-6.75-4.5M3 10l6.75 4.5M21 10l-6.75 4.5m0 0l-1.14.76a2 2 0 01-2.22 0l-1.14-.76" />
                      </svg>
                    </button>
                  )}
                
                  <button
                    onClick={handleArchive}
                    className="p-1 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded"
                    title="Archive"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8" />
                    </svg>
                  </button>
                  
                  <button
                    onClick={handleTrash}
                    className="p-1 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded"
                    title="Move to trash"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
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