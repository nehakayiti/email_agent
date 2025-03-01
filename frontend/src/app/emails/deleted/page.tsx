'use client';

import { useEffect, useState, useRef, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { getDeletedEmails, type Email, type EmailsParams } from '@/lib/api';
import { isAuthenticated } from '@/lib/auth';
import { SearchInput } from '@/components/ui/search-input';
import { EmailCard } from '@/components/ui/email-card';
import { Toaster } from 'react-hot-toast';

export default function DeletedEmailsPage() {
    const router = useRouter();
    const [emails, setEmails] = useState<Email[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [hasMore, setHasMore] = useState(true);
    const [page, setPage] = useState(1);
    const [totalEmails, setTotalEmails] = useState(0);
    const [initialLoadComplete, setInitialLoadComplete] = useState(false);
    const [loadingMore, setLoadingMore] = useState(false);
    
    // Create a ref for the observer target element
    const observerTarget = useRef<HTMLDivElement>(null);

    // Function to fetch deleted emails with pagination
    const fetchDeletedEmails = useCallback(async (pageNum: number, isInitialLoad: boolean = false) => {
        try {
            if (!isAuthenticated()) {
                console.log('User not authenticated, redirecting to login');
                router.push('/');
                return;
            }

            if (isInitialLoad) {
                setLoading(true);
            } else {
                setLoadingMore(true);
            }
            
            console.log(`Fetching deleted emails for page ${pageNum}...`);
            
            const params: EmailsParams = {
                page: pageNum,
                limit: 20,
            };
            
            const response = await getDeletedEmails(params);
            console.log('Deleted emails fetched successfully:', response.emails.length, 'emails');
            
            if (isInitialLoad) {
                setEmails(response.emails);
            } else {
                setEmails(prev => [...prev, ...response.emails]);
            }
            
            setTotalEmails(response.pagination.total);
            setHasMore(response.pagination.has_next);
            setError(null);
            
            if (isInitialLoad) {
                setInitialLoadComplete(true);
            }
        } catch (err) {
            console.error('Error in deleted emails page:', err);
            const errorMessage = err instanceof Error ? err.message : 'Failed to fetch deleted emails';
            setError(errorMessage);
        } finally {
            if (isInitialLoad) {
                setLoading(false);
            } else {
                setLoadingMore(false);
            }
        }
    }, [router]);

    // Initial data load
    useEffect(() => {
        setPage(1);
        setEmails([]);
        setHasMore(true);
        setInitialLoadComplete(false);
        fetchDeletedEmails(1, true);
    }, [fetchDeletedEmails]);

    // Set up intersection observer for infinite scrolling
    useEffect(() => {
        if (!initialLoadComplete || !hasMore || loadingMore) return;
        
        const observer = new IntersectionObserver(
            entries => {
                if (entries[0].isIntersecting && hasMore && !loadingMore) {
                    const nextPage = page + 1;
                    setPage(nextPage);
                    fetchDeletedEmails(nextPage);
                }
            },
            { threshold: 0.5 }
        );
        
        if (observerTarget.current) {
            observer.observe(observerTarget.current);
        }
        
        return () => {
            if (observerTarget.current) {
                observer.unobserve(observerTarget.current);
            }
        };
    }, [initialLoadComplete, hasMore, loadingMore, page, fetchDeletedEmails]);

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
                        <h2 className="text-xl font-bold text-gray-900 mb-2">Error Loading Deleted Emails</h2>
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
    
    const filteredEmails = emails.filter(email => {
        const matchesSearch = !searchTerm || 
            email.subject?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            email.from_email.toLowerCase().includes(searchTerm.toLowerCase()) ||
            email.snippet.toLowerCase().includes(searchTerm.toLowerCase());
        return matchesSearch;
    });

    return (
        <div className="container mx-auto px-4 py-8">
            <Toaster position="top-right" />
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 mb-2">
                        Deleted Emails
                        {totalEmails > 0 && <span className="text-gray-500 text-lg ml-2">({totalEmails})</span>}
                    </h1>
                    <p className="text-sm text-gray-600 mb-4 md:mb-0">
                        Emails that have been deleted in Gmail but are preserved locally
                    </p>
                </div>
                <div className="flex flex-col sm:flex-row gap-2 w-full md:w-auto">
                    <SearchInput 
                        value={searchTerm} 
                        onChange={setSearchTerm} 
                        placeholder="Search deleted emails..." 
                        className="w-full sm:w-64"
                    />
                    <button
                        onClick={() => router.push('/emails')}
                        className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
                    >
                        Back to Inbox
                    </button>
                </div>
            </div>
            
            <div className="w-full max-w-2xl">
                <p className="mt-1 text-sm text-gray-600">
                    {totalEmails} {totalEmails === 1 ? 'deleted email' : 'deleted emails'} found
                </p>

                {/* Email list */}
                <div className="space-y-4">
                    {filteredEmails.length === 0 ? (
                        <div className="bg-white rounded-2xl shadow-md p-8 text-center">
                            <h3 className="text-lg font-medium text-gray-900">No deleted emails found</h3>
                            <p className="mt-2 text-sm text-gray-500">
                                When emails are deleted in Gmail, they will appear here
                            </p>
                        </div>
                    ) : (
                        filteredEmails.map(email => (
                            <EmailCard 
                                key={email.id} 
                                email={email} 
                                onClick={() => router.push(`/emails/${email.id}`)}
                                isDeleted={true}
                            />
                        ))
                    )}
                    
                    {/* Loading indicator and observer target */}
                    {hasMore && (
                        <div 
                            ref={observerTarget} 
                            className="py-4 flex justify-center"
                        >
                            {loadingMore && (
                                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
} 