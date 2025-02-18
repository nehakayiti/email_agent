'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { getEmails, type Email } from '@/lib/api';
import { isAuthenticated, removeToken } from '@/lib/auth';

export default function EmailsPage() {
    const router = useRouter();
    const [emails, setEmails] = useState<Email[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                // Check authentication first
                if (!isAuthenticated()) {
                    console.log('User not authenticated, redirecting to login');
                    router.push('/');
                    return;
                }

                setLoading(true);
                console.log('Fetching emails...');
                const data = await getEmails();
                console.log('Emails fetched successfully:', data.length, 'emails');
                setEmails(data);
                setError(null);
            } catch (err) {
                console.error('Error in emails page:', err);
                const errorMessage = err instanceof Error ? err.message : 'Failed to fetch emails';
                setError(errorMessage);
                
                // If we get an authentication error, clear the token and redirect
                if (errorMessage.includes('authentication') || errorMessage.includes('401')) {
                    console.log('Authentication error detected, redirecting to login');
                    removeToken();
                    router.push('/');
                }
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [router]);

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
                    <h2 className="text-xl font-bold mb-2">Error Loading Emails</h2>
                    <p className="mb-4">{error}</p>
                    <button
                        onClick={() => router.push('/')}
                        className="text-blue-600 hover:text-blue-700 underline"
                    >
                        Return to Login
                    </button>
                </div>
            </div>
        );
    }

    // Ensure emails is always an array
    const emailList = Array.isArray(emails) ? emails : [];

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold">Your Emails</h1>
                <button
                    onClick={() => {
                        removeToken();
                        router.push('/');
                    }}
                    className="text-red-600 hover:text-red-700"
                >
                    Sign Out
                </button>
            </div>
            {emailList.length === 0 ? (
                <div className="text-center py-8">
                    <p className="text-gray-600">No emails found</p>
                </div>
            ) : (
                <div className="grid gap-4">
                    {emailList.map((email) => (
                        <div
                            key={email.id}
                            className="bg-white p-4 rounded-lg shadow hover:shadow-md transition-shadow cursor-pointer"
                            onClick={() => router.push(`/emails/${email.id}`)}
                        >
                            <div className="flex items-center justify-between mb-2">
                                <h2 className="font-semibold">{email.subject || '(No subject)'}</h2>
                                <span className="text-sm text-gray-500">
                                    {new Date(email.received_at).toLocaleDateString()}
                                </span>
                            </div>
                            <p className="text-sm text-gray-600 mb-2">From: {email.from_email}</p>
                            <p className="text-sm text-gray-700">{email.snippet}</p>
                            <div className="mt-2 flex gap-2">
                                {email.category && (
                                    <span className="text-xs px-2 py-1 bg-gray-100 rounded">
                                        {email.category}
                                    </span>
                                )}
                                <span className="text-xs px-2 py-1 bg-blue-100 rounded">
                                    Score: {email.importance_score}
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
} 