'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams, ReadonlyURLSearchParams } from 'next/navigation';
import { getEmailById, type Email } from '@/lib/api';
import { isAuthenticated, handleAuthError } from '@/lib/auth';
import { EmailContent } from './email-content';
import { Toaster } from 'react-hot-toast';

interface EmailDetailProps {
    emailId: string;
}

export default function EmailDetail({ emailId }: EmailDetailProps) {
    const router = useRouter();
    const searchParams = useSearchParams();
    const [email, setEmail] = useState<Email | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Get any filter parameters that we need to preserve
    const backToEmailsUrl = constructBackUrl(searchParams);

    function constructBackUrl(params: URLSearchParams | ReadonlyURLSearchParams | null): string {
        // Start with base URL
        let url = '/emails';
        
        // Check if we have any params to add
        const category = params?.get('category') ?? null;
        const status = params?.get('status') ?? null;
        const label = params?.get('label') ?? null;
        
        const queryParams = [];
        if (category) queryParams.push(`category=${category}`);
        if (status) queryParams.push(`status=${status}`);
        if (label) queryParams.push(`label=${label}`);
        
        // If we're in a trash email detail but no category was specified in URL,
        // and the email has the TRASH label, add the trash category filter
        if (!category && email?.labels?.includes('TRASH')) {
            queryParams.push('category=trash');
        }
        
        // Add query params if any exist
        if (queryParams.length > 0) {
            url += `?${queryParams.join('&')}`;
        }
        
        return url;
    }

    useEffect(() => {
        const fetchEmail = async () => {
            try {
                if (!isAuthenticated()) {
                    console.log('User not authenticated, redirecting to authentication');
                    handleAuthError();
                    return;
                }

                setLoading(true);
                console.log('Fetching email details...');
                const data = await getEmailById(emailId);
                console.log('Email details fetched:', data);
                setEmail(data);
                setError(null);
            } catch (err) {
                console.error('Error in email detail page:', err);
                const errorMessage = err instanceof Error ? err.message : 'Failed to fetch email';
                
                // Check if this is an authentication error
                if (errorMessage.includes('Authentication failed') || 
                    errorMessage.includes('token') || 
                    errorMessage.includes('401')) {
                    handleAuthError();
                    return;
                }
                
                setError(errorMessage);
            } finally {
                setLoading(false);
            }
        };

        if (emailId) {
            fetchEmail();
        }
    }, [emailId, router]);

    // Handle label updates
    const handleLabelsUpdated = (updatedEmail: Email) => {
        setEmail(updatedEmail);
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-full">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-6 bg-white rounded-2xl shadow-lg border border-gray-300">
                <button 
                    className="text-blue-600 text-sm mb-4" 
                    onClick={() => router.push(backToEmailsUrl)}
                >
                    ← Back to Emails
                </button>
                <div className="text-center">
                    <h2 className="text-xl font-bold text-gray-900 mb-2">Error</h2>
                    <p className="text-gray-600">{error}</p>
                </div>
            </div>
        );
    }

    if (!email) {
        return (
            <div className="p-6 bg-white rounded-2xl shadow-lg border border-gray-300">
                <button 
                    className="text-blue-600 text-sm mb-4" 
                    onClick={() => router.push(backToEmailsUrl)}
                >
                    ← Back to Emails
                </button>
                <div className="text-center">
                    <h2 className="text-xl font-bold text-gray-900 mb-2">Email not found</h2>
                    <p className="text-gray-600">The requested email could not be found.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="p-6 bg-white rounded-2xl shadow-lg border border-gray-300">
            <Toaster position="top-right" toastOptions={{ duration: 6000 }} />
            <button 
                className="text-blue-600 text-sm mb-4" 
                onClick={() => router.push(backToEmailsUrl)}
            >
                ← Back to Emails
            </button>
            <EmailContent email={email} onLabelsUpdated={handleLabelsUpdated} />
        </div>
    );
} 