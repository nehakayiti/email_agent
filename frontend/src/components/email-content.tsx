'use client';

import React, { useEffect, useState, useMemo } from 'react';
import { type Email, updateEmailCategory } from '@/lib/api';
import { toast } from 'react-hot-toast';
import { IframeEmailViewer } from '@/components/ui/iframe-email-viewer';  // Updated import path

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
    'Trash'
  ];

  const handleCategoryChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newCategory = e.target.value;
    setSelectedCategory(newCategory);
    
    try {
      setUpdating(true);
      // Show a toast with the loading state that can be dismissed
      const toastId = toast.loading('Updating category...');
      
      const response = await updateEmailCategory(email.id, newCategory);
      
      // Always dismiss the loading toast
      toast.dismiss(toastId);
      
      if (response.status === 'success') {
        toast.success(response.message || 'Category updated successfully');
        
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
        toast.error(response.message || 'Failed to update category');
      }
    } catch (error) {
      // Dismiss all loading toasts
      toast.dismiss();
      
      // Show a meaningful error toast
      const errorMessage = error instanceof Error ? error.message : 'Error updating category';
      toast.error(errorMessage);
      console.error('Error updating category:', error);
    } finally {
      setUpdating(false);
    }
  };

  return (
    <div>
      <h1 className="text-xl font-bold mb-2">{email.subject}</h1>
      <p className="mb-2 text-gray-700">From: {email.from_email}</p>

      {email.labels.includes('TRASH') && (
        <div className="my-2 px-3 py-2 bg-red-50 border-l-4 border-red-500 text-red-700">
          <span className="font-semibold">⚠️ This email is in Trash</span>
        </div>
      )}

      <div className="mb-4">
        <span className="font-semibold mr-2">Labels:</span>
        {email.labels && email.labels.length > 0 ? (
          email.labels.map((label, index) => (
            <span
              key={index}
              className="inline-block bg-blue-100 text-blue-800 rounded-full px-3 py-1 text-xs font-semibold mr-2 mb-2"
            >
              {label}
            </span>
          ))
        ) : (
          <span className="text-gray-500">None</span>
        )}
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

      {/* Instead of directly rendering the HTML, use the IframeEmailViewer */}
      <div className="border border-gray-200 rounded">
        <IframeEmailViewer htmlContent={bodyContent} />
      </div>
    </div>
  );
}
