'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { getEmails, type Email } from '@/lib/api';
import { isAuthenticated } from '@/lib/auth';
import AppLayout from '@/components/app-layout';

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
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [router]);

    if (loading) {
        return (
            <AppLayout>
                <div className="flex items-center justify-center h-full">
                    <div className="flex flex-col items-center gap-4">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
                        <p className="text-gray-600">Loading your emails...</p>
                    </div>
                </div>
            </AppLayout>
        );
    }

    if (error) {
        return (
            <AppLayout>
                <div className="flex items-center justify-center h-full">
                    <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full">
                        <div className="text-center">
                            <svg className="mx-auto h-12 w-12 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                            </svg>
                            <h2 className="mt-4 text-xl font-bold text-gray-900">Error Loading Emails</h2>
                            <p className="mt-2 text-gray-600">{error}</p>
                        </div>
                    </div>
                </div>
            </AppLayout>
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
        <AppLayout>
            <div className="p-6">
                {/* Search and filters */}
                <div className="mb-6 flex flex-col sm:flex-row gap-4">
                    <div className="flex-1">
                        <input
                            type="text"
                            placeholder="Search emails..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                        />
                    </div>
                    <div className="sm:w-48">
                        <select
                            value={selectedCategory || ''}
                            onChange={(e) => setSelectedCategory(e.target.value || null)}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                        >
                            <option value="">All Categories</option>
                            {categories.map(category => (
                                <option key={category} value={category}>{category}</option>
                            ))}
                        </select>
                    </div>
                </div>

                {/* Email list */}
                <div className="bg-white rounded-lg shadow">
                    {filteredEmails.length === 0 ? (
                        <div className="p-8 text-center text-gray-500">
                            No emails found
                        </div>
                    ) : (
                        <ul className="divide-y divide-gray-200">
                            {filteredEmails.map((email) => (
                                <li
                                    key={email.id}
                                    className="hover:bg-gray-50 cursor-pointer transition-colors duration-150"
                                    onClick={() => router.push(`/emails/${email.id}`)}
                                >
                                    <div className="px-6 py-4">
                                        <div className="flex items-center justify-between">
                                            <h3 className="text-sm font-medium text-gray-900">
                                                {email.from_email}
                                            </h3>
                                            <span className="text-xs text-gray-500">
                                                {new Date(email.received_at).toLocaleDateString()}
                                            </span>
                                        </div>
                                        <p className="mt-1 text-sm font-medium text-gray-900 truncate">
                                            {email.subject}
                                        </p>
                                        <p className="mt-1 text-sm text-gray-500 truncate">
                                            {email.snippet}
                                        </p>
                                        <div className="mt-2 flex items-center gap-2">
                                            {email.category && (
                                                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-indigo-100 text-indigo-800">
                                                    {email.category}
                                                </span>
                                            )}
                                            <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                                                email.is_read 
                                                    ? 'bg-green-100 text-green-800'
                                                    : 'bg-yellow-100 text-yellow-800'
                                            }`}>
                                                {email.is_read ? 'Read' : 'Unread'}
                                            </span>
                                        </div>
                                    </div>
                                </li>
                            ))}
                        </ul>
                    )}
                </div>
            </div>
        </AppLayout>
    );
} 