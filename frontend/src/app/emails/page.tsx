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
    const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        const fetchData = async () => {
            try {
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
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="flex flex-col items-center gap-4">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
                    <p className="text-gray-600">Loading your emails...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full">
                    <div className="text-center">
                        <svg className="mx-auto h-12 w-12 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                        <h2 className="mt-4 text-xl font-bold text-gray-900">Error Loading Emails</h2>
                        <p className="mt-2 text-gray-600">{error}</p>
                        <button
                            onClick={() => router.push('/')}
                            className="mt-4 text-indigo-600 hover:text-indigo-700 font-medium"
                        >
                            Return to Login
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    const emailList = Array.isArray(emails) ? emails : [];
    const categories = [...new Set(emailList.map(email => email.category).filter(Boolean))];
    
    const filteredEmails = emailList.filter(email => {
        const matchesCategory = !selectedCategory || email.category === selectedCategory;
        const matchesSearch = !searchTerm || 
            email.subject?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            email.from_email.toLowerCase().includes(searchTerm.toLowerCase()) ||
            email.snippet.toLowerCase().includes(searchTerm.toLowerCase());
        return matchesCategory && matchesSearch;
    });

    return (
        <div className="min-h-screen bg-gray-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Header */}
                <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
                    <div className="flex justify-between items-center">
                        <h1 className="text-2xl font-bold text-gray-900">Your Emails</h1>
                        <button
                            onClick={() => {
                                removeToken();
                                router.push('/');
                            }}
                            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                        >
                            <svg className="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                            </svg>
                            Sign Out
                        </button>
                    </div>
                    
                    {/* Filters */}
                    <div className="mt-6 flex flex-col sm:flex-row gap-4">
                        <div className="flex-1">
                            <input
                                type="text"
                                placeholder="Search emails..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                            />
                        </div>
                        <select
                            value={selectedCategory || ''}
                            onChange={(e) => setSelectedCategory(e.target.value || null)}
                            className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                        >
                            <option value="">All Categories</option>
                            {categories.map((category) => (
                                <option key={category} value={category}>
                                    {category}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>

                {/* Email List */}
                {filteredEmails.length === 0 ? (
                    <div className="bg-white rounded-lg shadow-sm p-8 text-center">
                        <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                        </svg>
                        <p className="mt-4 text-gray-600">No emails found</p>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {filteredEmails.map((email) => (
                            <div
                                key={email.id}
                                onClick={() => router.push(`/emails/${email.id}`)}
                                className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200 cursor-pointer overflow-hidden"
                            >
                                <div className="p-6">
                                    <div className="flex items-center justify-between mb-4">
                                        <h2 className="text-lg font-semibold text-gray-900 line-clamp-1">
                                            {email.subject || '(No subject)'}
                                        </h2>
                                        <span className="text-sm text-gray-500">
                                            {new Date(email.received_at).toLocaleDateString()}
                                        </span>
                                    </div>
                                    <div className="flex items-center text-sm text-gray-600 mb-3">
                                        <svg className="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                                        </svg>
                                        {email.from_email}
                                    </div>
                                    <p className="text-gray-700 line-clamp-2">{email.snippet}</p>
                                    <div className="mt-4 flex items-center gap-2">
                                        {email.category && (
                                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                                                {email.category}
                                            </span>
                                        )}
                                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                                            Score: {email.importance_score}
                                        </span>
                                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                            email.is_read 
                                                ? 'bg-green-100 text-green-800'
                                                : 'bg-yellow-100 text-yellow-800'
                                        }`}>
                                            {email.is_read ? 'Read' : 'Unread'}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
} 