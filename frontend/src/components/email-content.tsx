'use client';

import React, { useEffect, useState, useMemo } from 'react';
import { type Email, updateEmailCategory, archiveEmail } from '@/lib/api';
import { toast } from 'react-hot-toast';
import { IframeEmailViewer } from '@/components/ui/iframe-email-viewer';
import { showSuccessToast, showErrorToast, showLoadingToast, dismissAllToasts } from '@/utils/toast-config';
import { mapLabelsToComponents } from '@/components/ui/email-label';

function decodeBase64Url(str: string): string {
  const base64 = str.replace(/-/g, '+').replace(/_/g, '/');
  try {
    return atob(base64);
  } catch (e) {
    console.error('Failed to decode Base64 string', e);
    return '';
  }
}

function normalizeCategory(cat: string | undefined): string {
    if (!cat) return 'primary';
    if (cat.toLowerCase() === 'promotional') return 'promotions';
    if (cat.toLowerCase() === 'important') return 'important';
    if (cat.toLowerCase() === 'archive') return 'archive';
    return cat.toLowerCase(); 
  }



function extractEmailBody(payload: any): string {
  if (payload.body && payload.body.data) {
    return decodeBase64Url(payload.body.data);
  }
  if (payload.parts && payload.parts.length > 0) {
    const htmlPart = payload.parts.find((part: any) => part.mimeType === 'text/html');
    if (htmlPart?.body?.data) {
      return decodeBase64Url(htmlPart.body.data);
    }
    const textPart = payload.parts.find((part: any) => part.mimeType === 'text/plain');
    if (textPart?.body?.data) {
      return decodeBase64Url(textPart.body.data);
    }
  }
  return '';
}

interface EmailContentProps {
  email: Email;
  onLabelsUpdated?: (updatedEmail: Email) => void;
}

export function EmailContent({ email, onLabelsUpdated }: EmailContentProps) {
  const [bodyContent, setBodyContent] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState(() => normalizeCategory(email.category));
  const [updating, setUpdating] = useState(false);

  const decodedContent = useMemo(() => {
    if (email?.raw_data?.payload) {
      return extractEmailBody(email.raw_data.payload);
    }
    return '';
  }, [email]);

  useEffect(() => {
    setBodyContent(decodedContent);
  }, [decodedContent]);

  useEffect(() => {
    setSelectedCategory(normalizeCategory(email.category));
  }, [email.category]);

  const categoryOptions = [
    'Primary',
    'Social',
    'Promotions',
    'Updates',
    'Forums',
    'Personal',
    'Important',
    'Archive',
    'Trash'
  ];

  const handleCategoryChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newCategory = e.target.value;
    setSelectedCategory(newCategory);
    
    try {
      setUpdating(true);
      // Show a toast with the loading state that can be dismissed
      const toastId = showLoadingToast('Updating category...');
      
      const response = await updateEmailCategory(email.id, newCategory);
      
      // Always dismiss the loading toast
      toast.dismiss(toastId);
      
      if (response.status === 'success') {
        showSuccessToast(response.message || 'Category updated successfully');
        
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
        // Handle error in successful response but with error status
        showErrorToast(response.message || 'Failed to update category');
      }
    } catch (error) {
      // Dismiss all loading toasts
      dismissAllToasts();
      
      // Show a meaningful error toast
      const errorMessage = error instanceof Error ? error.message : 'Error updating category';
      showErrorToast(errorMessage);
      console.error('Error updating category:', error);
    } finally {
      setUpdating(false);
    }
  };

  const handleArchive = async () => {
    try {
      // Show a toast with the loading state that can be dismissed
      const toastId = showLoadingToast('Archiving email...');
      
      const response = await archiveEmail(email.id);
      
      // Always dismiss the loading toast
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
        // Handle error in successful response but with error status
        showErrorToast(response.message || 'Failed to archive email');
      }
    } catch (error) {
      // Dismiss all loading toasts
      dismissAllToasts();
      
      // Show a meaningful error toast
      const errorMessage = error instanceof Error ? error.message : 'Error archiving email';
      showErrorToast(errorMessage);
      console.error('Error archiving email:', error);
    }
  };

  // Filter out inconsistent labels - don't show INBOX if email is in TRASH
  const filteredLabels = useMemo(() => {
    if (!email.labels) return [];
    
    // If this email has TRASH label, don't display INBOX label
    if (email.labels.includes('TRASH')) {
      return email.labels.filter(label => label !== 'INBOX');
    }
    
    return email.labels;
  }, [email.labels]);

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h1 className="text-xl font-bold mb-2">{email.subject}</h1>
      <p className="mb-2 text-gray-700">From: {email.from_email}</p>

      {email.labels.includes('TRASH') && (
        <div className="my-3 px-4 py-3 bg-red-50 border-l-4 border-red-500 text-red-700">
          <span className="font-semibold">⚠️ This email is in Trash</span>
        </div>
      )}

      <div className="mb-4">
        <p className="font-medium text-sm mb-1">Labels:</p>
        <div className="flex flex-wrap gap-2">
          {filteredLabels.length > 0 ? (
            mapLabelsToComponents(filteredLabels)
          ) : (
            <span className="text-gray-500">None</span>
          )}
        </div>
      </div>

      <div className="flex items-center justify-between mb-4">
        <div className="flex space-x-2">
          <button
            onClick={handleArchive}
            className="px-3 py-1 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-md flex items-center text-sm"
            disabled={updating}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8" />
            </svg>
            Archive
          </button>
        </div>
        
        <div className="mb-4">
          <span className="font-semibold mr-2">Category:</span>
          <select
            value={selectedCategory}
            onChange={handleCategoryChange}
            disabled={updating}
            className="bg-gray-100 text-gray-800 rounded px-3 py-1 text-xs font-semibold"
          >
            {categoryOptions.map((option, index) => (
              <option key={index} value={option.toLowerCase()}>
                {option}
              </option>
            ))}
          </select>
          {updating && <span className="ml-2 text-gray-500 text-xs">Updating...</span>}
        </div>
      </div>

      {/* Instead of directly rendering the HTML, use the IframeEmailViewer */}
      <div className="border border-gray-200 rounded">
        <IframeEmailViewer htmlContent={bodyContent} />
      </div>
    </div>
  );
}
