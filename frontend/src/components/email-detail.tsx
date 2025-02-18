'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { getEmailById, type Email } from '@/lib/api';
import { isAuthenticated, removeToken } from '@/lib/auth';

interface EmailDetailProps {
    emailId: string;
}

export default function EmailDetail({ emailId }: EmailDetailProps) {
    const router = useRouter();
    const [email, setEmail] = useState<Email | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchEmail = async () => {
            try {
                if (!isAuthenticated()) {
                    console.log('User not authenticated, redirecting to login');
                    router.push('/');
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
                setError(errorMessage);

                if (errorMessage.includes('404')) {
                    setError('Email not found');
                } else if (errorMessage.includes('authentication') || errorMessage.includes('401')) {
                    console.log('Authentication error detected, redirecting to login');
                    removeToken();
                    router.push('/');
                }
            } finally {
                setLoading(false);
            }
        };

        if (emailId) {
            fetchEmail();
        }
    }, [emailId, router]);

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="animate-pulse">
                    <div className="h-8 w-8 bg-blue-600 rounded-full"></div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-red-600 max-w-md p-4 text-center">
                    <h2 className="text-xl font-bold mb-2">Error</h2>
                    <p className="mb-4">{error}</p>
                    <button
                        onClick={() => router.back()}
                        className="text-blue-600 hover:text-blue-700 underline"
                    >
                        Go Back
                    </button>
                </div>
            </div>
        );
    }

    if (!email) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-gray-600">
                    <p>Email not found</p>
                </div>
            </div>
        );
    }

    return (
        <div className="container mx-auto px-4 py-8">
            <button
                onClick={() => router.back()}
                className="mb-6 text-blue-600 hover:text-blue-700 flex items-center gap-2"
            >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
                Back to list
            </button>

            <div className="bg-white p-6 rounded-lg shadow">
                <div className="mb-6">
                    <h1 className="text-2xl font-bold mb-4">{email.subject || '(No subject)'}</h1>
                    <div className="text-gray-600 mb-2">From: {email.from_email}</div>
                    <div className="text-gray-500 text-sm">
                        {new Date(email.received_at).toLocaleString()}
                    </div>
                </div>

                <div className="mb-6">
                    <p className="text-gray-800 whitespace-pre-wrap">{email.snippet}</p>
                </div>

                <div className="flex gap-3">
                    {email.category && (
                        <span className="px-3 py-1 bg-gray-100 rounded-full text-sm">
                            {email.category}
                        </span>
                    )}
                    <span className="px-3 py-1 bg-blue-100 rounded-full text-sm">
                        Importance: {email.importance_score}
                    </span>
                    <span className={`px-3 py-1 rounded-full text-sm ${
                        email.is_read ? 'bg-green-100' : 'bg-yellow-100'
                    }`}>
                        {email.is_read ? 'Read' : 'Unread'}
                    </span>
                </div>
            </div>
        </div>
    );
} 