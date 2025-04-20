'use client';

import React, { useState, useEffect } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import Link from 'next/link';
import { 
  HomeIcon, 
  InboxIcon, 
  TagIcon, 
  ChartBarIcon, 
  ArrowPathIcon, 
  TrashIcon, 
  EnvelopeIcon, 
  EnvelopeOpenIcon,
  StarIcon,
  UserGroupIcon,
  BellAlertIcon,
  MegaphoneIcon,
  NewspaperIcon,
  ChatBubbleLeftRightIcon,
  ArrowRightOnRectangleIcon,
  Cog6ToothIcon
} from '@heroicons/react/24/outline';
import { isAuthenticated, handleAuthError, logout, initiateGoogleLogin } from '@/lib/auth';
import { triggerEmailSync, Category } from '@/lib/api';
import { useCategoryContext } from '@/lib/category-context';
import { toast } from 'react-hot-toast';

// Define types for navigation items
type NavItem = {
  name: string;
  href?: string;
  icon?: React.ComponentType<React.SVGProps<SVGSVGElement>>;
  type?: 'link' | 'divider' | 'category';
  section?: string;
};

// Fixed navigation items that aren't categories
const baseNavigation: NavItem[] = [
  // Main Views
  { name: 'Dashboard', href: '/', icon: HomeIcon, type: 'link', section: 'main' },
  { name: 'Inbox', href: '/emails?view=inbox', icon: InboxIcon, type: 'link', section: 'main' },
  { name: 'All Mail', href: '/emails', icon: EnvelopeIcon, type: 'link', section: 'main' },
  
  // Email Status
  { name: 'Unread', href: '/emails?status=unread', icon: EnvelopeIcon, type: 'link', section: 'filters' },
  { name: 'Read', href: '/emails?status=read', icon: EnvelopeOpenIcon, type: 'link', section: 'filters' },
  
  // Tools & Settings
  { name: 'Analytics', href: '/analytics', icon: ChartBarIcon, type: 'link', section: 'tools' },
  { name: 'Categories', href: '/categories/improved', icon: Cog6ToothIcon, type: 'link', section: 'tools' },
];

// Custom event name for email sync completion
export const EMAIL_SYNC_COMPLETED_EVENT = 'emailSyncCompleted';

// Add this new client component at the top level of the file, before the MainLayout function
function SyncButton({ handleSync, isSyncing }: { handleSync: () => Promise<void>, isSyncing: boolean }) {
  const [mounted, setMounted] = useState(false);
  
  useEffect(() => {
    setMounted(true);
  }, []);
  
  if (!mounted) return null;
  
  return (
    <button
      onClick={handleSync}
      disabled={isSyncing}
      className={`inline-flex items-center px-4 py-2 rounded-md text-sm font-medium shadow-sm ${
        isSyncing 
          ? 'bg-blue-400 text-white cursor-not-allowed' 
          : 'bg-blue-600 text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500'
      }`}
      type="button"
    >
      <svg 
        className={`-ml-1 mr-2 h-5 w-5 ${isSyncing ? 'animate-spin' : ''}`}
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        strokeWidth="1.5"
        stroke="currentColor"
        aria-hidden="true"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99"
        />
      </svg>
      {isSyncing ? 'Syncing...' : 'Sync Emails'}
    </button>
  );
}

function GoogleLoginButton() {
  const [mounted, setMounted] = useState(false);
  
  useEffect(() => {
    setMounted(true);
  }, []);
  
  if (!mounted) return null;
  
  return (
    <button
      onClick={initiateGoogleLogin}
      type="button"
      className="inline-flex items-center px-4 py-2 rounded-md text-sm font-medium shadow-sm bg-white text-gray-800 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 border border-gray-300"
    >
      <svg 
        className="-ml-1 mr-2 h-5 w-5" 
        xmlns="http://www.w3.org/2000/svg" 
        viewBox="0 0 48 48"
        aria-hidden="true"
      >
        <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
        <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
        <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
        <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
      </svg>
      Sign in with Google
    </button>
  );
}

function LogoutButton({ handleLogout, isLoggingOut }: { handleLogout: () => Promise<void>, isLoggingOut: boolean }) {
  const [mounted, setMounted] = useState(false);
  
  useEffect(() => {
    setMounted(true);
  }, []);
  
  if (!mounted) return null;
  
  return (
    <button
      onClick={handleLogout}
      disabled={isLoggingOut}
      type="button"
      className={`inline-flex items-center px-4 py-2 rounded-md text-sm font-medium shadow-sm ${
        isLoggingOut 
          ? 'bg-gray-400 cursor-not-allowed' 
          : 'bg-red-600 hover:bg-red-700'
      } text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500`}
    >
      {isLoggingOut ? (
        <>
          <svg 
            className="animate-spin -ml-1 mr-2 h-5 w-5" 
            xmlns="http://www.w3.org/2000/svg" 
            fill="none" 
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <circle 
              className="opacity-25" 
              cx="12" 
              cy="12" 
              r="10" 
              stroke="currentColor" 
              strokeWidth="4"
            />
            <path 
              className="opacity-75" 
              fill="currentColor" 
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          Logging out...
        </>
      ) : (
        <>
          <svg
            className="-ml-1 mr-2 h-5 w-5"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth="1.5"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15m3 0l3-3m0 0l-3-3m3 3H9"
            />
          </svg>
          Logout
        </>
      )}
    </button>
  );
}

export default function MainLayout({ children }: { children: React.ReactNode }) {
  const [mounted, setMounted] = useState(false);
  const pathname = usePathname();
  const router = useRouter();
  const [isSyncing, setIsSyncing] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const [syncStatus, setSyncStatus] = useState<'success' | 'error' | null>(null);
  const [syncMessage, setSyncMessage] = useState('');
  const [isAuthError, setIsAuthError] = useState(false);
  const [lastSyncTime, setLastSyncTime] = useState<Date | null>(null);
  
  // Use the CategoryContext instead of fetching categories directly
  const { categories, refreshCategories } = useCategoryContext();

  useEffect(() => {
    if (!isAuthenticated()) {
      handleAuthError();
      return;
    }
  }, []);

  // Listen for email sync completion event to refresh categories
  useEffect(() => {
    const handleSyncCompleted = () => {
      // Refresh categories when emails are synced
      refreshCategories();
    };

    // Add event listener
    window.addEventListener(EMAIL_SYNC_COMPLETED_EVENT, handleSyncCompleted);

    // Clean up
    return () => {
      window.removeEventListener(EMAIL_SYNC_COMPLETED_EVENT, handleSyncCompleted);
    };
  }, [refreshCategories]);

  const handleSync = async () => {
    if (isSyncing || !isAuthenticated()) return;
    
    try {
      setIsSyncing(true);
      setSyncMessage('Syncing emails...');
      setSyncStatus(null);
      
      const response = await triggerEmailSync();
      
      // Check for success based on the response structure
      if (response.success || response.status === 'success') {
        setSyncStatus('success');
        
        // Handle the case when no new emails are found
        if (response.sync_count === 0) {
          setSyncMessage('No new emails to sync.');
        } else {
          // Extract only the count of new emails, not including checkpoint emails
          const newEmailCount = response.new_email_count || response.sync_count || 0;
          setSyncMessage(response.message || `Sync completed! ${newEmailCount} new emails processed.`);
        }
        
        // Dispatch a custom event to notify components that sync is complete
        window.dispatchEvent(new CustomEvent(EMAIL_SYNC_COMPLETED_EVENT, { 
          detail: { syncCount: response.sync_count || 0 } 
        }));
        
        // Clear the success message after 3 seconds
        setTimeout(() => {
          setSyncMessage('');
          setSyncStatus(null);
        }, 3000);
      } else if (response.status === 'warning' && response.message?.includes('No changes detected')) {
        // Handle the "No changes detected" case with a more user-friendly message
        setSyncStatus('success');
        setSyncMessage('Your inbox is up to date! No new changes found.');
        
        // Clear the message after 3 seconds
        setTimeout(() => {
          setSyncMessage('');
          setSyncStatus(null);
        }, 3000);
      } else {
        setSyncStatus('error');
        setSyncMessage(`Sync failed: ${response.message}`);
        // Clear the error message after 5 seconds
        setTimeout(() => {
          setSyncMessage('');
          setSyncStatus(null);
        }, 5000);
      }
    } catch (error) {
      console.error('Error syncing emails:', error);
      setSyncStatus('error');
      
      // Check if it's an auth error
      if (error instanceof Error && 
          (error.message.includes('No authentication token found') || 
           error.message.includes('Authentication failed'))) {
        setIsAuthError(true);
        handleAuthError();
        setSyncMessage('Authentication failed. Please log in again.');
      } else {
        setSyncMessage('Failed to sync emails. Please try again.');
      }
      
      // Clear the error message after 5 seconds
      setTimeout(() => {
        setSyncMessage('');
        setSyncStatus(null);
      }, 5000);
    } finally {
      setIsSyncing(false);
    }
  };

  const handleLogout = async () => {
    try {
      setIsLoggingOut(true);
      await logout();
      
      // Show success message
      toast.success('Successfully logged out');
      
      // Redirect to login page with a clean URL
      router.push('/');
    } catch (error) {
      console.error('Logout error:', error);
      toast.error('Failed to logout. Please try again.');
    } finally {
      setIsLoggingOut(false);
    }
  };

  // Create mapping of icons that can be used for categories
  const getCategoryIcon = (categoryName: string) => {
    const iconMap: Record<string, React.ComponentType<React.SVGProps<SVGSVGElement>>> = {
      'primary': InboxIcon,
      'important': StarIcon,
      'social': UserGroupIcon,
      'promotional': MegaphoneIcon,
      'updates': BellAlertIcon,
      'personal': TagIcon,
      'newsletters': NewspaperIcon,
      'forums': ChatBubbleLeftRightIcon,
      'archive': ArrowPathIcon,
      'trash': TrashIcon
    };

    return iconMap[categoryName.toLowerCase()] || TagIcon; // Default to TagIcon
  };

  // Create storage section with Archive and Trash
  const storageCategories = categories.filter(cat => 
    cat.name.toLowerCase() === 'archive' || cat.name.toLowerCase() === 'trash'
  );

  // Create regular categories (excluding storage categories)
  const regularCategories = categories.filter(cat => 
    cat.name.toLowerCase() !== 'archive' && cat.name.toLowerCase() !== 'trash'
  );

  // Group navigation items by section
  const mainNavItems = baseNavigation.filter(item => item.section === 'main');
  const filterNavItems = baseNavigation.filter(item => item.section === 'filters');
  const toolNavItems = baseNavigation.filter(item => item.section === 'tools');

  useEffect(() => { setMounted(true); }, []);
  if (!mounted) return null;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Left Navigation */}
      <div className="fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg flex flex-col">
        <div className="flex h-16 items-center px-6 border-b border-gray-200">
          <Link href="/" className="flex items-center space-x-2">
            <div className="text-2xl font-bold text-indigo-600">EA</div>
            <span className="text-lg font-semibold text-gray-900">EmailAgent</span>
          </Link>
        </div>
        
        {/* Scrollable navigation */}
        <nav className="flex-1 overflow-y-auto py-4 px-3">
          {/* Main section */}
          <div className="mb-6">
            <div className="px-3 mb-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Main
            </div>
            {mainNavItems.map((item) => {
              if (!item.href || !item.icon) return null;

              const isActive = pathname === item.href || 
                (pathname && item.href && pathname.startsWith('/emails') && item.href.startsWith('/emails') && 
                  (
                    // Match category parameter
                    (new URLSearchParams(item.href.split('?')[1]).get('category') === 
                     new URLSearchParams(pathname.split('?')[1]).get('category')) ||
                    // Match view parameter (for inbox)
                    (new URLSearchParams(item.href.split('?')[1]).get('view') === 
                     new URLSearchParams(pathname.split('?')[1]).get('view')) ||
                    // Special case for /emails with no parameters (All Emails)
                    (item.href === '/emails' && 
                     !pathname.includes('?') && 
                     !pathname.includes('/deleted'))
                  ));
              
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`group flex items-center px-3 py-2 my-1 text-sm font-medium rounded-md ${
                    isActive
                      ? 'bg-indigo-50 text-indigo-600'
                      : 'text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <item.icon
                    className={`mr-3 h-5 w-5 flex-shrink-0 ${
                      isActive ? 'text-indigo-600' : 'text-gray-400 group-hover:text-gray-500'
                    }`}
                    aria-hidden="true"
                  />
                  {item.name}
                </Link>
              );
            })}
          </div>
          
          {/* Filters section */}
          <div className="mb-6">
            <div className="px-3 mb-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Filters
            </div>
            {filterNavItems.map((item) => {
              if (!item.href || !item.icon) return null;

              const isActive = pathname === item.href || 
                (pathname && item.href && pathname.startsWith('/emails') && item.href.startsWith('/emails') && 
                  (new URLSearchParams(item.href.split('?')[1]).get('status') === 
                   new URLSearchParams(pathname.split('?')[1]).get('status')));
              
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`group flex items-center px-3 py-2 my-1 text-sm font-medium rounded-md ${
                    isActive
                      ? 'bg-indigo-50 text-indigo-600'
                      : 'text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <item.icon
                    className={`mr-3 h-5 w-5 flex-shrink-0 ${
                      isActive ? 'text-indigo-600' : 'text-gray-400 group-hover:text-gray-500'
                    }`}
                    aria-hidden="true"
                  />
                  {item.name}
                </Link>
              );
            })}
          </div>
          
          {/* Categories section */}
          {regularCategories.length > 0 && (
            <div className="mb-6">
              <div className="px-3 mb-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                Categories
              </div>
              {regularCategories.map((category) => {
                const href = `/emails?category=${category.name.toLowerCase()}`;
                const Icon = getCategoryIcon(category.name);
                const isActive = pathname && pathname.startsWith('/emails') && 
                  new URLSearchParams(pathname.split('?')[1]).get('category') === category.name.toLowerCase();
                
                return (
                  <Link
                    key={category.name}
                    href={href}
                    className={`group flex items-center px-3 py-2 my-1 text-sm font-medium rounded-md ${
                      isActive
                        ? 'bg-indigo-50 text-indigo-600'
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <Icon
                      className={`mr-3 h-5 w-5 flex-shrink-0 ${
                        isActive ? 'text-indigo-600' : 'text-gray-400 group-hover:text-gray-500'
                      }`}
                      aria-hidden="true"
                    />
                    {category.display_name}
                  </Link>
                );
              })}
            </div>
          )}
          
          {/* Storage section */}
          {storageCategories.length > 0 && (
            <div className="mb-6">
              <div className="px-3 mb-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                Storage
              </div>
              {storageCategories.map((category) => {
                const href = category.name.toLowerCase() === 'trash' 
                  ? '/emails/deleted' 
                  : `/emails?category=${category.name.toLowerCase()}`;
                const Icon = getCategoryIcon(category.name);
                const isActive = (category.name.toLowerCase() === 'trash' && pathname === '/emails/deleted') ||
                  (pathname && pathname.startsWith('/emails') && 
                   new URLSearchParams(pathname.split('?')[1]).get('category') === category.name.toLowerCase());
                
                return (
                  <Link
                    key={category.name}
                    href={href}
                    className={`group flex items-center px-3 py-2 my-1 text-sm font-medium rounded-md ${
                      isActive
                        ? 'bg-indigo-50 text-indigo-600'
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <Icon
                      className={`mr-3 h-5 w-5 flex-shrink-0 ${
                        isActive ? 'text-indigo-600' : 'text-gray-400 group-hover:text-gray-500'
                      }`}
                      aria-hidden="true"
                    />
                    {category.display_name}
                  </Link>
                );
              })}
            </div>
          )}
          
          {/* Tools section */}
          <div className="mb-6">
            <div className="px-3 mb-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Tools
            </div>
            {toolNavItems.map((item) => {
              if (!item.href || !item.icon) return null;

              const isActive = pathname === item.href;
              
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`group flex items-center px-3 py-2 my-1 text-sm font-medium rounded-md ${
                    isActive
                      ? 'bg-indigo-50 text-indigo-600'
                      : 'text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <item.icon
                    className={`mr-3 h-5 w-5 flex-shrink-0 ${
                      isActive ? 'text-indigo-600' : 'text-gray-400 group-hover:text-gray-500'
                    }`}
                    aria-hidden="true"
                  />
                  {item.name}
                </Link>
              );
            })}
          </div>
        </nav>
      </div>

      {/* Main Content */}
      <div className="pl-64">
        {/* Header */}
        <header className="bg-white shadow-sm">
          <div className="flex h-16 items-center justify-between px-6">
            <h2 className="text-lg font-medium text-gray-900">
              {/* greeting }, Sunny! */}
            </h2>
            
            <div className="flex items-center space-x-3">
              {syncMessage && (
                <span className={`text-sm font-medium px-3 py-1 rounded-md ${
                  syncStatus === 'error' 
                    ? 'text-red-800 bg-red-100' 
                    : syncStatus === 'success'
                      ? 'text-green-800 bg-green-100'
                      : 'text-gray-800 bg-gray-100'
                }`}>
                  {syncMessage}
                </span>
              )}
              
              {isAuthenticated() && (
                <SyncButton handleSync={handleSync} isSyncing={isSyncing} />
              )}

              {isAuthenticated() ? (
                <LogoutButton handleLogout={handleLogout} isLoggingOut={isLoggingOut} />
              ) : (
                <GoogleLoginButton />
              )}
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="py-6 px-6">
          {children}
        </main>
      </div>
    </div>
  );
} 