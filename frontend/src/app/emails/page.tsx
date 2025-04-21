'use client';

import { useEffect, useState, useRef, useCallback } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { getEmails, type Email, type EmailsParams } from '@/lib/api';
import { isAuthenticated, handleAuthError } from '@/lib/auth';
import { SearchInput } from '@/components/ui/search-input';
import { EmailCard } from '@/components/ui/email-card';
import { EMAIL_SYNC_COMPLETED_EVENT } from '@/components/layout/main-layout';
import { toast, Toaster } from 'react-hot-toast';
import { SyncStatusBar } from '@/components/ui/sync-status-bar';

// Add the API function to fix trash consistency
const fixTrashConsistency = async () => {
    try {
        // Get the authentication token from localStorage
        const token = localStorage.getItem('token');
        if (!token) {
            console.error('Authentication token not found');
            throw new Error('Authentication token not found');
        }
        
        // Get the API URL from environment variables
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        console.log(`Making API request to ${apiUrl}/emails/fix-trash-consistency`);
        
        // Make the request to fix trash consistency
        const response = await fetch(`${apiUrl}/emails/fix-trash-consistency`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
        });
        
        // Check if the response is ok
        if (!response.ok) {
            // Try to get error details from response
            const errorData = await response.json().catch(() => null);
            const errorMessage = errorData?.detail || `API error: ${response.status} ${response.statusText}`;
            console.error('Error response:', errorMessage);
            throw new Error(errorMessage);
        }
        
        // Parse the response
        const data = await response.json();
        console.log('Fix trash consistency response:', data);
        return data;
    } catch (error) {
        console.error('Error fixing trash consistency:', error);
        throw error;
    }
};

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
    const [scrollRestored, setScrollRestored] = useState(false);
    const [isFixingTrash, setIsFixingTrash] = useState(false);
    const [showTrashNotification, setShowTrashNotification] = useState(true);
    const [mounted, setMounted] = useState(false);
    const [syncStatus, setSyncStatus] = useState<'idle' | 'syncing' | 'success' | 'error'>('idle');
    const [lastSync, setLastSync] = useState<Date | null>(null);
    const [syncError, setSyncError] = useState<string | null>(null);
    
    // Get category from URL parameters
    const categoryParam = searchParams?.get('category') ?? null;
    // Get status from URL parameters
    const statusParam = searchParams?.get('status') ?? null;
    // Get label from URL parameters
    const labelParam = searchParams?.get('label') ?? null;
    // Get view from URL parameters (for inbox view)
    const viewParam = searchParams?.get('view') ?? null;
    
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
            
            // If no specific filters are applied and not in inbox view, show all emails EXCEPT trash
            const isAllEmailsView = !categoryParam && !statusParam && !labelParam && !viewParam;
            
            // Handle inbox view - exclude archived and trash emails
            if (viewParam === 'inbox') {
                // Add INBOX label filter to only show emails in the inbox
                params.label = 'INBOX';
                console.log('Inbox view: Showing only emails with INBOX label');
            }
            
            if (isAllEmailsView) {
                // Instead of setting showAll=true which includes trash,
                // we don't set any parameter which will use the backend's default
                // behavior of excluding trash emails
            }
            
            if (categoryParam) {
                params.category = categoryParam;
                
                // Set showAll to true for trash view and also when we SPECIFICALLY
                // need to get emails with the trash category
                if (categoryParam.toLowerCase() === 'trash') {
                    params.showAll = true;
                    
                    // We also need to add a parameter to ensure we're getting emails
                    // with either the trash category OR the TRASH label
                    params.label = 'TRASH';
                }
            }

            if (statusParam) {
                if (statusParam === 'read' || statusParam === 'unread') {
                    // Convert status string to boolean read_status
                    params.read_status = statusParam === 'read';
                }
            }
            
            if (labelParam && categoryParam !== 'trash') {
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
    }, [categoryParam, statusParam, labelParam, router, viewParam]);

    // Initial data load
    useEffect(() => {
        setPage(1);
        setEmails([]);
        setHasMore(true);
        setInitialLoadComplete(false);
        fetchEmails(1, true);
    }, [fetchEmails, categoryParam, statusParam, labelParam, viewParam]);

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
            (labelParam && !updatedEmail.labels.includes(labelParam)) ||
            // If we're not viewing trash but the email has been moved to trash
            (categoryParam !== 'trash' && updatedEmail.labels.includes('TRASH'))
        );

        // Special case: If the email has been moved to trash and we're not in trash view,
        // remove it from the current view
        if (updatedEmail.labels.includes('TRASH') && categoryParam !== 'trash') {
            setEmails(prevEmails => prevEmails.filter(email => email.id !== updatedEmail.id));
            setTotalEmails(prev => Math.max(0, prev - 1));
            return;
        }

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

    // Save scroll position when navigating away
    const saveScrollPosition = useCallback(() => {
        const scrollY = window.scrollY;
        sessionStorage.setItem('emailListScrollPosition', scrollY.toString());
        console.log('Saved scroll position:', scrollY);
    }, []);
    
    // Restore scroll position
    const restoreScrollPosition = useCallback(() => {
        const savedPosition = sessionStorage.getItem('emailListScrollPosition');
        if (savedPosition && !scrollRestored) {
            const position = parseInt(savedPosition, 10);
            console.log('Restoring scroll position to:', position);
            window.scrollTo(0, position);
            setScrollRestored(true);
        }
    }, [scrollRestored]);

    // Effect to restore scroll position when returning to this page
    useEffect(() => {
        if (initialLoadComplete && !scrollRestored) {
            restoreScrollPosition();
        }
    }, [initialLoadComplete, restoreScrollPosition, scrollRestored]);
    
    // Set up event handlers for saving scroll position on navigation
    useEffect(() => {
        // Add click event listener to email cards to save position
        const handleEmailCardClick = () => {
            saveScrollPosition();
        };
        
        // Find all email card links and attach event listeners
        const emailCards = document.querySelectorAll('[data-email-card]');
        emailCards.forEach(card => {
            card.addEventListener('click', handleEmailCardClick);
        });
        
        return () => {
            // Clean up event listeners
            emailCards.forEach(card => {
                card.removeEventListener('click', handleEmailCardClick);
            });
        };
    }, [emails, saveScrollPosition]);

    // Handle the trash consistency fix
    const handleFixTrashConsistency = async () => {
        if (isFixingTrash) return;
        
        try {
            setIsFixingTrash(true);
            const toastId = toast.loading('Fixing trash inconsistencies...');
            
            const result = await fixTrashConsistency();
            
            toast.dismiss(toastId);
            
            if (result.fixed_count > 0) {
                toast.success(`Fixed ${result.fixed_count} emails with trash inconsistencies. Refreshing...`);
                
                // Reset pagination and reload emails
                setPage(1);
                setEmails([]);
                setHasMore(true);
                setInitialLoadComplete(false);
                fetchEmails(1, true);
            } else {
                toast.success('No inconsistencies found. All emails are correctly labeled.');
            }
        } catch (error) {
            toast.error(`Error fixing trash inconsistencies: ${error instanceof Error ? error.message : 'Unknown error'}`);
            console.error('Failed to fix trash inconsistencies:', error);
        } finally {
            setIsFixingTrash(false);
        }
    };

    // Effect to show notification in trash view
    useEffect(() => {
        if (categoryParam?.toLowerCase() === 'trash') {
            setShowTrashNotification(true);
        } else {
            setShowTrashNotification(false);
        }
    }, [categoryParam]);

    // New: Sync handler
    const handleSyncNow = async () => {
        setSyncStatus('syncing');
        setSyncError(null);
        try {
            // Get the authentication token from localStorage
            const token = localStorage.getItem('token');
            if (!token) throw new Error('Authentication token not found');
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const response = await fetch(`${apiUrl}/emails/sync`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
            });
            if (!response.ok) {
                const errorData = await response.json().catch(() => null);
                const errorMessage = errorData?.detail || `API error: ${response.status} ${response.statusText}`;
                setSyncStatus('error');
                setSyncError(errorMessage);
                return;
            }
            setSyncStatus('success');
            setLastSync(new Date());
            setSyncError(null);
            // Optionally, refresh emails after sync
            setPage(1);
            setEmails([]);
            setHasMore(true);
            setInitialLoadComplete(false);
            fetchEmails(1, true);
        } catch (error) {
            setSyncStatus('error');
            setSyncError(error instanceof Error ? error.message : 'Unknown error');
        }
    };

    useEffect(() => { setMounted(true); }, []);
    if (!mounted) return null;

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

    // Determine the title based on category, status, or view parameters
    let pageTitle = 'All Emails';
    if (viewParam === 'inbox') {
        pageTitle = 'Inbox';
    } else if (categoryParam) {
        pageTitle = `${categoryParam.charAt(0).toUpperCase() + categoryParam.slice(1)} Emails`;
    } else if (statusParam) {
        pageTitle = `${statusParam.charAt(0).toUpperCase() + statusParam.slice(1)} Emails`;
    }

    return (
        <div className="px-4 py-8">
            <Toaster position="top-right" toastOptions={{ duration: 6000 }} />
            <div className="w-full max-w-3xl mx-auto sm:px-2 md:px-4">
                {/* Show prominent notification in trash view */}
                {categoryParam?.toLowerCase() === 'trash' && showTrashNotification && (
                    <div className="mb-4 p-4 bg-orange-50 border border-orange-200 rounded-lg">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center">
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-orange-500 mr-2" viewBox="0 0 20 20" fill="currentColor">
                                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                                </svg>
                                <div>
                                    <p className="text-sm text-orange-800 font-medium">
                                        Some emails may not appear in this Trash view due to inconsistent labeling.
                                    </p>
                                </div>
                            </div>
                            <div className="flex space-x-2">
                                <button
                                    onClick={handleFixTrashConsistency}
                                    disabled={isFixingTrash}
                                    className="px-3 py-1 bg-orange-500 text-white text-sm font-medium rounded hover:bg-orange-600 transition-colors"
                                >
                                    {isFixingTrash ? 'Fixing...' : 'Fix Now'}
                                </button>
                                <button
                                    onClick={() => setShowTrashNotification(false)}
                                    className="text-orange-500 hover:text-orange-700"
                                >
                                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                        <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                                    </svg>
                                </button>
                            </div>
                        </div>
                    </div>
                )}
                
                <div className="flex flex-col mb-6">
                    <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center mb-4">
                        <h1 className="text-2xl font-bold text-gray-900 mb-4 lg:mb-0 flex-shrink-0">
                            {pageTitle}
                            {totalEmails > 0 && <span className="text-gray-500 text-lg ml-2">({totalEmails})</span>}
                        </h1>
                        
                        {/* Add trash fix button prominently next to the title if in trash view */}
                        {categoryParam?.toLowerCase() === 'trash' && (
                            <button
                                onClick={handleFixTrashConsistency}
                                disabled={isFixingTrash}
                                className={`px-4 py-2 text-sm bg-orange-500 text-white rounded-md hover:bg-orange-600 transition-colors ${isFixingTrash ? 'opacity-50 cursor-not-allowed' : ''}`}
                            >
                                {isFixingTrash ? 'Fixing...' : 'Fix Trash Inconsistencies'}
                            </button>
                        )}
                    </div>
                    <div className="w-full">
                        <SearchInput 
                            value={searchTerm} 
                            onChange={setSearchTerm} 
                            placeholder="Search emails..." 
                            className="w-full"
                        />
                    </div>
                </div>
                
                <p className="mt-1 text-sm text-gray-600 mb-4">
                    {totalEmails} {totalEmails === 1 ? 'email' : 'emails'} found
                </p>

                {/* Email list */}
                <div>
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
                                    onClick={() => {
                                        saveScrollPosition();
                                        router.push(`/emails/${email.id}`);
                                    }}
                                    data-email-card
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