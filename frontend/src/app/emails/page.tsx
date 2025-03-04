'use client';

import { useEffect, useState, useRef, useCallback } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { getEmails, type Email, type EmailsParams } from '@/lib/api';
import { isAuthenticated, handleAuthError } from '@/lib/auth';
import { SearchInput } from '@/components/ui/search-input';
import { EmailCard } from '@/components/ui/email-card';
import { EMAIL_SYNC_COMPLETED_EVENT } from '@/components/layout/main-layout';
import { toast, Toaster } from 'react-hot-toast';

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
    // Get status from URL parameters
    const statusParam = searchParams.get('status');
    // Get label from URL parameters
    const labelParam = searchParams.get('label');
    
    // Create a ref for the observer target element
    const observerTarget = useRef<HTMLDivElement>(null);

    // Function to fetch emails with pagination
    const fetchEmails = useCallback(async (pageNum: number, isInitialLoad: boolean = false) => {
        try {
            if (!isAuthenticated()) {
                console.log('User not authenticated, redirecting to authentication');
                handleAuthError();
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
            
            // If no specific filters are applied, show all emails EXCEPT trash
            const isAllEmailsView = !categoryParam && !statusParam && !labelParam;
            
            if (isAllEmailsView) {
                // Instead of setting showAll=true which includes trash,
                // we don't set any parameter which will use the backend's default
                // behavior of excluding trash emails
            }
            
            if (categoryParam) {
                params.category = categoryParam;
            }

            if (statusParam) {
                if (statusParam === 'read' || statusParam === 'unread') {
                    // Convert status string to boolean read_status
                    params.read_status = statusParam === 'read';
                }
            }
            
            if (labelParam) {
                params.label = labelParam;
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
        } catch (error) {
            console.error('Error fetching emails:', error);
            
            // Check if it's an authentication error
            const errorMessage = error instanceof Error ? error.message : 'Error fetching emails';
            if (errorMessage.includes('Authentication failed') || 
                errorMessage.includes('token') || 
                errorMessage.includes('401')) {
                handleAuthError();
                return;
            }
            
            setError(errorMessage);
        } finally {
            setLoading(false);
            setLoadingMore(false);
        }
    }, [categoryParam, statusParam, labelParam, router]);

    // Initial data load
    useEffect(() => {
        setPage(1);
        setEmails([]);
        setHasMore(true);
        setInitialLoadComplete(false);
        fetchEmails(1, true);
    }, [fetchEmails, categoryParam, statusParam, labelParam]);

    // Listen for email sync completion event
    useEffect(() => {
        const handleSyncCompleted = () => {
            console.log('Email sync completed, refreshing email list');
            // Reset pagination and reload emails
            setPage(1);
            setEmails([]);
            setHasMore(true);
            setInitialLoadComplete(false);
            fetchEmails(1, true);
        };

        // Add event listener
        window.addEventListener(EMAIL_SYNC_COMPLETED_EVENT, handleSyncCompleted);

        // Clean up
        return () => {
            window.removeEventListener(EMAIL_SYNC_COMPLETED_EVENT, handleSyncCompleted);
        };
    }, [fetchEmails]);

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

    // Add a handler for labels updated
    const handleLabelsUpdated = (updatedEmail: Email) => {
        // Check if the email should be removed from the current view based on category/status filter
        const shouldRemoveFromCurrentView = (
            // If we're viewing a specific category and the email category has changed
            (categoryParam && updatedEmail.category !== categoryParam) ||
            // If we're viewing archived emails and the email is no longer archived
            (categoryParam === 'archive' && updatedEmail.labels.includes('INBOX')) ||
            // If we're viewing by label and the email no longer has that label
            (labelParam && !updatedEmail.labels.includes(labelParam))
        );

        if (shouldRemoveFromCurrentView) {
            // Remove the email from the current view
            setEmails(prevEmails => prevEmails.filter(email => email.id !== updatedEmail.id));
            // Update total count
            setTotalEmails(prev => Math.max(0, prev - 1));
        } else {
            // Update the email in the list
            setEmails(prevEmails => 
                prevEmails.map(email => 
                    email.id === updatedEmail.id ? updatedEmail : email
                )
            );
        }
    };

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

    // Determine the title based on category or status parameters
    let pageTitle = 'All Emails';
    if (categoryParam) {
        pageTitle = `${categoryParam.charAt(0).toUpperCase() + categoryParam.slice(1)} Emails`;
    } else if (statusParam) {
        pageTitle = `${statusParam.charAt(0).toUpperCase() + statusParam.slice(1)} Emails`;
    }

    return (
        <div className="px-4 py-8">
            <Toaster position="top-right" toastOptions={{ duration: 6000 }} />
            <div className="w-full max-w-3xl mx-auto sm:px-2 md:px-4">
                <div className="flex flex-col mb-6">
                    <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center mb-4">
                        <h1 className="text-2xl font-bold text-gray-900 mb-4 lg:mb-0 flex-shrink-0">
                            {pageTitle}
                            {totalEmails > 0 && <span className="text-gray-500 text-lg ml-2">({totalEmails})</span>}
                        </h1>
                    </div>
                    <SearchInput 
                        value={searchTerm} 
                        onChange={setSearchTerm} 
                        placeholder="Search emails..." 
                        className="w-full"
                    />
                </div>
                
                <p className="mt-1 text-sm text-gray-600 mb-4">
                    {totalEmails} {totalEmails === 1 ? 'email' : 'emails'} found
                </p>

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
                                    onLabelsUpdated={handleLabelsUpdated}
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