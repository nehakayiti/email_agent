'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { getEmails, type Email } from '@/lib/api';
import { isAuthenticated } from '@/lib/auth';
import { SearchInput } from '@/components/ui/search-input';
import { EmailCard } from '@/components/ui/email-card';

export default function EmailsPage() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const [emails, setEmails] = useState<Email[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [searchTerm, setSearchTerm] = useState('');

    // Get category from URL parameters
    const categoryParam = searchParams.get('category');

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
            <div className="flex items-center justify-center h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="bg-white rounded-2xl shadow-lg p-8 max-w-md w-full mx-4">
                    <div className="text-center">
                        <h2 className="text-xl font-bold text-gray-900 mb-2">Error Loading Emails</h2>
                        <p className="text-gray-600">{error}</p>
                        <button
                            onClick={() => window.location.reload()}
                            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-500"
                        >
                            Try Again
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    const emailList = Array.isArray(emails) ? emails : [];
    
    const filteredEmails = emailList.filter(email => {
        const matchesCategory = !categoryParam || email.category?.toLowerCase() === categoryParam.toLowerCase();
        const matchesSearch = !searchTerm || 
            email.subject?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            email.from_email.toLowerCase().includes(searchTerm.toLowerCase()) ||
            email.snippet.toLowerCase().includes(searchTerm.toLowerCase());
        return matchesCategory && matchesSearch;
    });

    const categoryTitle = categoryParam 
        ? categoryParam.charAt(0).toUpperCase() + categoryParam.slice(1) + ' Emails'
        : 'All Emails';

    return (
        <div className="flex flex-col items-center p-6 bg-gray-100 min-h-screen">
            <div className="w-full max-w-2xl">
                <h1 className="text-2xl font-semibold text-gray-800 mb-4">{categoryTitle}</h1>
                <p className="mt-1 text-sm text-gray-600">
                    {filteredEmails.length} {filteredEmails.length === 1 ? 'email' : 'emails'} found
                </p>

                {/* Search */}
                <div className="mb-8 mt-4">
                    <SearchInput
                        value={searchTerm}
                        onChange={setSearchTerm}
                        placeholder="Search in emails..."
                    />
                </div>

                {/* Email list */}
                <div className="space-y-4">
                    {filteredEmails.length === 0 ? (
                        <div className="bg-white rounded-2xl shadow-md p-8 text-center">
                            <h3 className="text-lg font-medium text-gray-900">No emails found</h3>
                            <p className="mt-2 text-sm text-gray-500">
                                Try adjusting your search or filter to find what you're looking for.
                            </p>
                        </div>
                    ) : (
                        filteredEmails.map((email) => (
                            <EmailCard
                                key={email.id}
                                email={email}
                                onClick={() => router.push(`/emails/${email.id}`)}
                            />
                        ))
                    )}
                </div>
            </div>
        </div>
    );
} 