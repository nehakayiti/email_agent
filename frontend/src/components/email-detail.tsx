'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { getEmailById, type Email } from '@/lib/api';
import { isAuthenticated } from '@/lib/auth';

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
            <div className="flex items-center justify-center h-full">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-6 bg-white rounded-2xl shadow-lg border border-gray-300">
                <button className="text-blue-600 text-sm mb-4" onClick={() => router.back()}>← Back to Emails</button>
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
                <button className="text-blue-600 text-sm mb-4" onClick={() => router.back()}>← Back to Emails</button>
                <div className="text-center">
                    <h2 className="text-xl font-bold text-gray-900 mb-2">Email not found</h2>
                    <p className="text-gray-600">The requested email could not be found.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="p-6 bg-white rounded-2xl shadow-lg border border-gray-300">
            <button className="text-blue-600 text-sm mb-4" onClick={() => router.back()}>← Back to Emails</button>
            <p className="text-sm text-gray-600">From: <span className="font-medium">{email.from_email}</span></p>
            <p className="text-xs text-gray-500">{new Date(email.received_at).toLocaleString()}</p>
            <h2 className="text-xl font-semibold text-gray-800 mt-2">{email.subject || '(No subject)'}</h2>
            <p className="text-sm text-gray-700 mt-2">{email.snippet}</p>
            <div className="flex space-x-2 mt-4">
                {email.category && (
                    <span className="px-3 py-1 text-sm bg-green-100 text-green-600 rounded-full">{email.category}</span>
                )}
                <span className="px-3 py-1 text-sm bg-green-100 text-green-600 rounded-full">
                    {email.is_read ? 'Read' : 'Unread'}
                </span>
            </div>
        </div>
    );
} 