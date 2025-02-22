'use client';

import { useMemo } from 'react';
import { type Email } from '@/lib/api';

interface EmailContentProps {
    email: Email;
}

export function EmailContent({ email }: EmailContentProps) {
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
                <a
                    href={gmailUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center text-sm text-blue-600 hover:text-blue-800"
                >
                    <svg className="h-4 w-4 mr-1" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm0 22c-5.523 0-10-4.477-10-10S6.477 2 12 2s10 4.477 10 10-4.477 10-10 10zm-1-11v6h2v-6h3l-4-4-4 4h3z"/>
                    </svg>
                    Open in Gmail
                </a>
            </div>

            {/* Email content */}
            <div className="bg-white rounded-lg overflow-hidden">
                {content}
            </div>
        </div>
    );
} 