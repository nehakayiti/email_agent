'use client';

import React, { useEffect, useState, useMemo } from 'react';
import { type Email } from '@/lib/api';
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
  onCategoryUpdated?: (updatedCategory: string) => void;
}

export function EmailContent({ email, onCategoryUpdated }: EmailContentProps) {
  const [bodyContent, setBodyContent] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState(email.category || '');

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
    setSelectedCategory(email.category || '');
  }, [email.category]);

  const categoryOptions = [
    'Primary',
    'Social',
    'Promotions',
    'Updates',
    'Forums',
    'Personal'
  ];

  const handleCategoryChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newCategory = e.target.value;
    setSelectedCategory(newCategory);
    if (onCategoryUpdated) {
      onCategoryUpdated(newCategory);
    }
    toast('Category updated locally');
  };

  return (
    <div>
      <h1 className="text-xl font-bold mb-2">{email.subject}</h1>
      <p className="mb-2 text-gray-700">From: {email.from_email}</p>

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
          className="bg-gray-100 text-gray-800 rounded px-3 py-1 text-xs font-semibold"
        >
          {categoryOptions.map((option, index) => (
            <option key={index} value={option.toLowerCase()}>
              {option}
            </option>
          ))}
        </select>
      </div>

      {/* Instead of directly rendering the HTML, use the IframeEmailViewer */}
      <div className="border border-gray-200 rounded">
        <IframeEmailViewer htmlContent={bodyContent} />
      </div>
    </div>
  );
}
