'use client';

import { useState, useEffect, useCallback } from 'react';
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
  MegaphoneIcon
} from '@heroicons/react/24/outline';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { getEmails, type Email, triggerEmailSync } from '@/lib/api';
import { isAuthenticated, handleAuthError } from '@/lib/auth';

// Define types for navigation items
type NavItem = {
  name: string;
  href?: string;
  icon?: React.ComponentType<React.SVGProps<SVGSVGElement>>;
  type?: 'link' | 'divider' | 'category';
};

const baseNavigation: NavItem[] = [
  // Main Views
  { name: 'Dashboard', href: '/', icon: HomeIcon, type: 'link' },
  { name: 'All Emails', href: '/emails', icon: InboxIcon, type: 'link' },
  { name: 'Analytics', href: '/analytics', icon: ChartBarIcon, type: 'link' },
  
  // Email Status
  { type: 'divider', name: 'Status' },
  { name: 'Unread', href: '/emails?status=unread', icon: EnvelopeIcon, type: 'link' },
  { name: 'Read', href: '/emails?status=read', icon: EnvelopeOpenIcon, type: 'link' },
  
  // Email Categories
  { type: 'divider', name: 'CATEGORIES' },
  { name: 'Manage Categories', href: '/categories', icon: TagIcon, type: 'link' },
  { name: 'Primary', href: '/emails?category=primary', icon: InboxIcon, type: 'link' },
  { name: 'Important', href: '/emails?label=IMPORTANT', icon: StarIcon, type: 'link' },
  { name: 'Social', href: '/emails?category=social', icon: UserGroupIcon, type: 'link' },
  { name: 'Promotional', href: '/emails?category=promotional', icon: MegaphoneIcon, type: 'link' },
  { name: 'Newsletters', href: '/emails?category=newsletters', icon: EnvelopeIcon, type: 'link' },
  { name: 'Updates', href: '/emails?category=updates', icon: BellAlertIcon, type: 'link' },
  { name: 'Personal', href: '/emails?category=personal', icon: TagIcon, type: 'link' },
  
  // Storage Locations
  { type: 'divider', name: 'Storage' },
  { name: 'Archive', href: '/emails?category=archive', icon: ArrowPathIcon, type: 'link' },
  { name: 'Trash', href: '/emails/deleted', icon: TrashIcon, type: 'link' },
];

// Custom event name for email sync completion
export const EMAIL_SYNC_COMPLETED_EVENT = 'emailSyncCompleted';

export default function MainLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [categories, setCategories] = useState<string[]>([]);
  const [isSyncing, setIsSyncing] = useState(false);
  const [syncMessage, setSyncMessage] = useState('');
  const [syncStatus, setSyncStatus] = useState<'success' | 'error' | null>(null);
  const [isAuthError, setIsAuthError] = useState(false);
  const [greeting] = useState(() => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  });

  const fetchCategories = useCallback(async () => {
    // Skip API calls if we're not authenticated
    if (!isAuthenticated()) {
      setIsAuthError(true);
      return;
    }

    try {
      const response = await getEmails();
      const uniqueCategories = [...new Set(response.emails.map(email => email.category).filter(Boolean))];
      setCategories(uniqueCategories.sort()); // Sort categories alphabetically
    } catch (error) {
      console.error('Error fetching categories:', error);
      // Check if it's an auth error
      if (error instanceof Error && 
          (error.message.includes('No authentication token found') || 
           error.message.includes('Authentication failed'))) {
        setIsAuthError(true);
        handleAuthError();
      }
    }
  }, []);

  useEffect(() => {
    // Only fetch categories if we're on a protected route
    // and we haven't encountered an auth error yet
    if (!isAuthError && pathname && !pathname.includes('/auth')) {
      fetchCategories();
    }
  }, [fetchCategories, isAuthError, pathname]);

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

  // Create navigation items with base items and categories
  const navigation: NavItem[] = [
    ...baseNavigation,
    // We'll only add dynamic categories that aren't already in our predefined list
    ...(categories.length > 0 
      ? categories
          .filter(category => !['primary', 'important', 'social', 'promotional', 'updates', 'archive', 'trash', 'personal', 'newsletters'].includes(category.toLowerCase()))
          .map(category => ({
            name: category.charAt(0).toUpperCase() + category.slice(1),
            href: `/emails?category=${category.toLowerCase()}`,
            icon: TagIcon,
            type: 'category' as const
          }))
      : [])
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Left Navigation */}
      <div className="fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg">
        <div className="flex h-16 items-center px-6">
          <Link href="/" className="flex items-center space-x-2">
            <div className="text-2xl font-bold text-indigo-600">EA</div>
            <span className="text-lg font-semibold text-gray-900">EmailAgent</span>
          </Link>
        </div>
        <nav className="mt-5 px-3">
          {navigation.map((item) => {
            if (item.type === 'divider') {
              return (
                <div key={item.name} className="px-2 py-1.5 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  {item.name}
                </div>
              );
            }

            if (!item.href || !item.icon) return null;

            const isActive = pathname === item.href || 
              (pathname && item.href && pathname.startsWith('/emails') && item.href.startsWith('/emails') && 
                new URLSearchParams(item.href.split('?')[1]).get('category') === 
                new URLSearchParams(pathname.split('?')[1]).get('category'));
            
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`group flex items-center px-2.5 py-2 my-0.5 text-sm font-medium rounded-lg ${
                  isActive
                    ? 'bg-indigo-50 text-indigo-600'
                    : 'text-gray-700 hover:bg-gray-50'
                }`}
              >
                <item.icon
                  className={`mr-2.5 h-5 w-5 flex-shrink-0 ${
                    isActive ? 'text-indigo-600' : 'text-gray-400 group-hover:text-gray-500'
                  }`}
                  aria-hidden="true"
                />
                {item.name}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Main Content */}
      <div className="pl-64">
        {/* Header */}
        <header className="bg-white shadow-sm">
          <div className="flex h-16 items-center justify-between px-6">
            <h2 className="text-lg font-medium text-gray-900">
              {greeting}, Sunny!
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
              <button
                onClick={handleSync}
                disabled={isSyncing}
                className={`inline-flex items-center px-4 py-2 rounded-md text-sm font-medium shadow-sm ${
                  isSyncing 
                    ? 'bg-blue-400 text-white cursor-not-allowed' 
                    : 'bg-blue-600 text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500'
                }`}
                aria-label="Sync emails"
              >
                <ArrowPathIcon 
                  className={`-ml-1 mr-2 h-5 w-5 ${isSyncing ? 'animate-spin' : ''}`} 
                  aria-hidden="true" 
                />
                {isSyncing ? 'Syncing...' : 'Sync Emails'}
              </button>
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