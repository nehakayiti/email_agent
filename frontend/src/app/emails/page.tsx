'use client';

import { useEffect, useState, useRef, useCallback } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { getEmails, type Email, type EmailsParams } from '@/lib/api';
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
    const [hasMore, setHasMore] = useState(true);
    const [page, setPage] = useState(1);
    const [totalEmails, setTotalEmails] = useState(0);
    const [initialLoadComplete, setInitialLoadComplete] = useState(false);
    const [loadingMore, setLoadingMore] = useState(false);
    
    // Get category from URL parameters
    const categoryParam = searchParams.get('category');
    
    // Create a ref for the observer target element
    const observerTarget = useRef<HTMLDivElement>(null);

    // Function to fetch emails with pagination
    const fetchEmails = useCallback(async (pageNum: number, isInitialLoad: boolean = false) => {
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
            
            console.log(`Fetching emails for page ${pageNum}...`);
            
            const params: EmailsParams = {
                page: pageNum,
                limit: 20,
            };
            
            if (categoryParam) {
                params.category = categoryParam;
            }
            
            const response = await getEmails(params);
            console.log('Emails fetched successfully:', response.emails.length, 'emails');
            
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
            console.error('Error in emails page:', err);
            const errorMessage = err instanceof Error ? err.message : 'Failed to fetch emails';
            setError(errorMessage);
        } finally {
            if (isInitialLoad) {
                setLoading(false);
            } else {
                setLoadingMore(false);
            }
        }
    }, [router, categoryParam]);

    // Initial data load
    useEffect(() => {
        setPage(1);
        setEmails([]);
        setHasMore(true);
        setInitialLoadComplete(false);
        fetchEmails(1, true);
    }, [fetchEmails, categoryParam]);

    // Set up intersection observer for infinite scrolling
    useEffect(() => {
        if (!initialLoadComplete || !hasMore || loadingMore) return;
        
        const observer = new IntersectionObserver(
            entries => {
                if (entries[0].isIntersecting && hasMore && !loadingMore) {
                    const nextPage = page + 1;
                    setPage(nextPage);
                    fetchEmails(nextPage);
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
    }, [initialLoadComplete, hasMore, loadingMore, page, fetchEmails]);

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
    
    const filteredEmails = emails.filter(email => {
        const matchesSearch = !searchTerm || 
            email.subject?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            email.from_email.toLowerCase().includes(searchTerm.toLowerCase()) ||
            email.snippet.toLowerCase().includes(searchTerm.toLowerCase());
        return matchesSearch;
    });

    const categoryTitle = categoryParam 
        ? categoryParam.charAt(0).toUpperCase() + categoryParam.slice(1) + ' Emails'
        : 'All Emails';

    return (
        <div className="flex flex-col items-center p-6 bg-gray-100 min-h-screen">
            <div className="w-full max-w-2xl">
                <h1 className="text-2xl font-semibold text-gray-800 mb-4">{categoryTitle}</h1>
                <p className="mt-1 text-sm text-gray-600">
                    {totalEmails} {totalEmails === 1 ? 'email' : 'emails'} found
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
                        <>
                            {filteredEmails.map((email) => (
                                <EmailCard
                                    key={email.id}
                                    email={email}
                                    onClick={() => router.push(`/emails/${email.id}`)}
                                />
                            ))}
                            
                            {/* Loading indicator for more emails */}
                            {loadingMore && (
                                <div className="flex justify-center py-4">
                                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                                </div>
                            )}
                            
                            {/* Observer target element */}
                            <div 
                                ref={observerTarget} 
                                className="h-10 w-full"
                                aria-hidden="true"
                            />
                            
                            {/* End of list message */}
                            {!hasMore && emails.length > 0 && (
                                <div className="text-center py-8 text-gray-500 text-sm">
                                    You've reached the end of the list
                                </div>
                            )}
                        </>
                    )}
                </div>
            </div>
        </div>
    );
} 