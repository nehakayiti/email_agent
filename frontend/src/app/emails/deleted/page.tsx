'use client';

import { useEffect, useState, useRef, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { getTrashedEmails, emptyTrash, type Email, type EmailsParams } from '@/lib/api';
import { isAuthenticated, handleAuthError } from '@/lib/auth';
import { SearchInput } from '@/components/ui/search-input';
import { EmailCard } from '@/components/ui/email-card';
import { Toaster } from 'react-hot-toast';
import { toast } from 'react-hot-toast';

export default function TrashPage() {
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
    const [isEmptyingTrash, setIsEmptyingTrash] = useState(false);
    
    // Create a ref for the observer target element
    const observerTarget = useRef<HTMLDivElement>(null);

    // Function to fetch trashed emails with pagination
    const fetchTrashedEmails = useCallback(async (pageNum: number, isInitialLoad: boolean = false) => {
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
            
            console.log(`Fetching trashed emails for page ${pageNum}...`);
            
            const params: EmailsParams = {
                page: pageNum,
                limit: 20,
            };
            
            const response = await getTrashedEmails(params);
            console.log('Trashed emails fetched successfully:', response.emails.length, 'emails');
            
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
            console.error('Error fetching trashed emails:', error);
            
            // Check if it's an authentication error
            const errorMessage = error instanceof Error ? error.message : 'Error fetching trashed emails';
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
    }, [router]);

    // Initial data load
    useEffect(() => {
        setPage(1);
        setEmails([]);
        setHasMore(true);
        setInitialLoadComplete(false);
        fetchTrashedEmails(1, true);
    }, [fetchTrashedEmails]);

    // Set up intersection observer for infinite scrolling
    useEffect(() => {
        if (!initialLoadComplete || !hasMore || loadingMore) return;
        
        const observer = new IntersectionObserver(
            entries => {
                if (entries[0].isIntersecting && hasMore && !loadingMore) {
                    const nextPage = page + 1;
                    setPage(nextPage);
                    fetchTrashedEmails(nextPage);
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
    }, [initialLoadComplete, hasMore, loadingMore, page, fetchTrashedEmails]);

    // Add a handler for labels updated
    const handleLabelsUpdated = (updatedEmail: Email) => {
        // Remove the email from Trash if it is no longer in Trash (category or label)
        if (updatedEmail.category !== 'trash' && !updatedEmail.labels.includes('TRASH')) {
            setEmails(prevEmails => prevEmails.filter(email => email.id !== updatedEmail.id));
        } else {
            // Otherwise, update the email in the list
            setEmails(prevEmails => 
                prevEmails.map(email => 
                    email.id === updatedEmail.id ? updatedEmail : email
                )
            );
        }
    };

    // Function to handle emptying the trash
    const handleEmptyTrash = async () => {
        if (isEmptyingTrash) return;
        
        if (confirm('Are you sure you want to permanently delete all items in Trash? This action cannot be undone.')) {
            try {
                setIsEmptyingTrash(true);
                const result = await emptyTrash();
                
                if (result.success) {
                    toast.success(result.message || 'Trash emptied successfully');
                    setEmails([]);
                    setTotalEmails(0);
                } else {
                    toast.error(result.message || 'Failed to empty trash');
                }
            } catch (error) {
                console.error('Error emptying trash:', error);
                toast.error('Failed to empty trash. Please try again.');
            } finally {
                setIsEmptyingTrash(false);
            }
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
                        <h2 className="text-xl font-bold text-gray-900 mb-2">Error Loading Trashed Emails</h2>
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
        <div className="container mx-auto max-w-6xl">
            <Toaster position="top-right" toastOptions={{ duration: 6000 }} />
            
            {/* Trash notification banner */}
            <div className="bg-gray-100 border-b border-gray-200 py-3 px-4 mb-4 flex items-center justify-between">
                <div className="text-gray-700">
                    Messages that have been in Trash more than 30 days will be automatically deleted.
                </div>
                <button 
                    onClick={handleEmptyTrash}
                    disabled={isEmptyingTrash || emails.length === 0}
                    className={`text-blue-600 hover:text-blue-800 font-medium ${
                        isEmptyingTrash || emails.length === 0 ? 'opacity-50 cursor-not-allowed' : ''
                    }`}
                >
                    {isEmptyingTrash ? (
                        <span className="flex items-center">
                            <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            Emptying...
                        </span>
                    ) : 'Empty Trash now'}
                </button>
            </div>
            
            <div className="bg-white rounded-lg shadow-sm overflow-hidden">
                <div className="p-4 border-b border-gray-200">
                    <div className="flex justify-between items-center mb-4">
                        <h1 className="text-xl font-semibold text-gray-900">
                            Trash
                            {totalEmails > 0 && <span className="text-gray-500 text-lg ml-2">({totalEmails})</span>}
                        </h1>
                        <div className="w-64">
                            <SearchInput 
                                value={searchTerm} 
                                onChange={setSearchTerm} 
                                placeholder="Search in trash..." 
                            />
                        </div>
                    </div>
                    <div className="flex justify-end">
                        <button
                            onClick={() => router.push('/emails?view=inbox')}
                            className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 flex-shrink-0"
                        >
                            Back to Inbox
                        </button>
                    </div>
                </div>
                
                <p className="mt-1 text-sm text-gray-600 mb-4">
                    {totalEmails} {totalEmails === 1 ? 'trashed email' : 'trashed emails'} found
                </p>

                {/* Email list */}
                <div className="space-y-4">
                    {filteredEmails.length === 0 ? (
                        <div className="bg-white rounded-2xl shadow-md p-8 text-center">
                            <h3 className="text-lg font-medium text-gray-900">No trashed emails found</h3>
                            <p className="mt-2 text-sm text-gray-500">
                                When emails are trashed in Gmail, they will appear here
                            </p>
                        </div>
                    ) : (
                        filteredEmails.map((email) => (
                            <EmailCard 
                                key={email.id} 
                                email={email} 
                                isDeleted={true}
                                onLabelsUpdated={handleLabelsUpdated}
                                onClick={() => router.push(`/emails/${email.id}`)}
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