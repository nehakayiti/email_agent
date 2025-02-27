'use client';

import { useMemo, useState } from 'react';
import { type Email, updateEmailLabels } from '@/lib/api';
import { toast } from 'react-hot-toast';

interface EmailContentProps {
    email: Email;
    onLabelsUpdated?: (email: Email) => void;
}

export function EmailContent({ email, onLabelsUpdated }: EmailContentProps) {
    const [isUpdatingLabels, setIsUpdatingLabels] = useState(false);
    
    const gmailUrl = useMemo(() => {
        return `https://mail.google.com/mail/u/0/#inbox/${email.gmail_id}`;
    }, [email.gmail_id]);

    const content = useMemo(() => {
        const payload = email.raw_data?.payload;
        if (!payload) return null;

        // Helper function to decode base64 content
        const decodeBase64 = (data: string) => {
            try {
                return atob(data.replace(/-/g, '+').replace(/_/g, '/'));
            } catch (error) {
                console.error('Error decoding base64:', error);
                return '';
            }
        };

        // Helper function to get content from parts or body
        const getContent = (part: { mimeType: string; body: { data?: string } }) => {
            if (!part.body.data) return null;
            
            const decoded = decodeBase64(part.body.data);
            
            if (part.mimeType === 'text/plain') {
                return <pre className="whitespace-pre-wrap font-sans text-sm">{decoded}</pre>;
            }
            
            if (part.mimeType === 'text/html') {
                return (
                    <div 
                        className="prose prose-sm max-w-none"
                        dangerouslySetInnerHTML={{ __html: decoded }} 
                    />
                );
            }
            
            return null;
        };

        // Check for multipart content
        if (payload.parts) {
            const htmlPart = payload.parts.find(part => part.mimeType === 'text/html');
            if (htmlPart) {
                return getContent(htmlPart);
            }

            const textPart = payload.parts.find(part => part.mimeType === 'text/plain');
            if (textPart) {
                return getContent(textPart);
            }
        }

        // Check for single part content
        if (payload.body?.data) {
            return getContent({
                mimeType: payload.headers.find(h => h.name.toLowerCase() === 'content-type')?.value || 'text/plain',
                body: payload.body
            });
        }

        return <p className="text-gray-500 italic">No content available</p>;
    }, [email.raw_data]);

    // Get the category label from the email
    const categoryLabel = useMemo(() => {
        return email.category || 'primary';
    }, [email.category]);

    // Get the read status
    const readStatus = useMemo(() => {
        return email.is_read ? 'Read' : 'Unread';
    }, [email.is_read]);

    // Handle label change
    const handleLabelChange = async (newCategory: string) => {
        if (isUpdatingLabels || email.is_deleted_in_gmail) return;
        
        try {
            setIsUpdatingLabels(true);
            
            // Map frontend category to Gmail label
            const categoryToLabelMap: Record<string, string> = {
                'primary': 'CATEGORY_PERSONAL',
                'social': 'CATEGORY_SOCIAL',
                'promotional': 'CATEGORY_PROMOTIONS',
                'updates': 'CATEGORY_UPDATES',
                'forums': 'CATEGORY_FORUMS'
            };
            
            // Get current category label
            const currentLabel = categoryToLabelMap[email.category] || 'CATEGORY_PERSONAL';
            
            // Get new category label
            const newLabel = categoryToLabelMap[newCategory] || 'CATEGORY_PERSONAL';
            
            // Update labels in Gmail
            const result = await updateEmailLabels(
                email.id,
                [newLabel],
                [currentLabel]
            );
            
            // Update local state
            if (onLabelsUpdated) {
                onLabelsUpdated({
                    ...email,
                    category: newCategory,
                    labels: result.labels
                });
            }
            
            toast.success(`Changed category to ${newCategory}`);
        } catch (error) {
            console.error('Error updating label:', error);
            toast.error('Failed to update label');
        } finally {
            setIsUpdatingLabels(false);
        }
    };

    // Handle read status change
    const handleReadStatusChange = async (isRead: boolean) => {
        if (isUpdatingLabels || email.is_deleted_in_gmail) return;
        
        try {
            setIsUpdatingLabels(true);
            
            // Update labels in Gmail
            const result = await updateEmailLabels(
                email.id,
                isRead ? [] : ['UNREAD'],
                isRead ? ['UNREAD'] : []
            );
            
            // Update local state
            if (onLabelsUpdated) {
                onLabelsUpdated({
                    ...email,
                    is_read: isRead,
                    labels: result.labels
                });
            }
            
            toast.success(`Marked as ${isRead ? 'read' : 'unread'}`);
        } catch (error) {
            console.error('Error updating read status:', error);
            toast.error('Failed to update read status');
        } finally {
            setIsUpdatingLabels(false);
        }
    };

    return (
        <div className="space-y-4">
            {/* Email metadata */}
            <div className="space-y-2 border-b border-gray-200 pb-4">
                <h1 className="text-xl font-semibold text-gray-900">
                    {email.subject || '(No subject)'}
                </h1>
                <div className="flex items-center justify-between text-sm text-gray-600">
                    <div>
                        From: <span className="font-medium">{email.from_email}</span>
                    </div>
                    <div>
                        {new Date(email.received_at).toLocaleString()}
                    </div>
                </div>
                
                {/* Labels and actions */}
                <div className="flex flex-wrap items-center gap-2 mt-2">
                    {/* Category label */}
                    <div className="flex items-center">
                        <span className="text-sm text-gray-500 mr-1">Category:</span>
                        <select 
                            className="text-sm bg-gray-100 border border-gray-300 rounded px-2 py-1"
                            value={categoryLabel}
                            onChange={(e) => handleLabelChange(e.target.value)}
                            disabled={isUpdatingLabels || email.is_deleted_in_gmail}
                        >
                            <option value="primary">Primary</option>
                            <option value="social">Social</option>
                            <option value="promotional">Promotional</option>
                            <option value="updates">Updates</option>
                            <option value="forums">Forums</option>
                        </select>
                    </div>
                    
                    {/* Read status */}
                    <div className="flex items-center">
                        <span className="text-sm text-gray-500 mr-1">Status:</span>
                        <select 
                            className="text-sm bg-gray-100 border border-gray-300 rounded px-2 py-1"
                            value={readStatus}
                            onChange={(e) => handleReadStatusChange(e.target.value === 'Read')}
                            disabled={isUpdatingLabels || email.is_deleted_in_gmail}
                        >
                            <option value="Read">Read</option>
                            <option value="Unread">Unread</option>
                        </select>
                    </div>
                    
                    {/* Deleted status */}
                    {email.is_deleted_in_gmail && (
                        <div className="bg-red-100 text-red-800 text-xs font-medium px-2.5 py-0.5 rounded">
                            Deleted in Gmail
                        </div>
                    )}
                    
                    {/* Gmail link */}
                    <a
                        href={gmailUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center text-sm text-blue-600 hover:text-blue-800 ml-auto"
                    >
                        <svg className="h-4 w-4 mr-1" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm0 22c-5.523 0-10-4.477-10-10S6.477 2 12 2s10 4.477 10 10-4.477 10-10 10zm-1-11v6h2v-6h3l-4-4-4 4h3z"/>
                        </svg>
                        Open in Gmail
                    </a>
                </div>
            </div>

            {/* Email content */}
            <div className="bg-white rounded-lg overflow-hidden">
                {content}
            </div>
        </div>
    );
} 