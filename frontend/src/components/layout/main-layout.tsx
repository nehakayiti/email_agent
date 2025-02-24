'use client';

import { useState, useEffect } from 'react';
import { HomeIcon, InboxIcon, TagIcon, ChartBarIcon } from '@heroicons/react/24/outline';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { getEmails, type Email } from '@/lib/api';

const baseNavigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'All Emails', href: '/emails', icon: InboxIcon },
  { name: 'Analytics', href: '/analytics', icon: ChartBarIcon },
];

export default function MainLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [categories, setCategories] = useState<string[]>([]);
  const [greeting] = useState(() => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  });

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const emails = await getEmails();
        const uniqueCategories = [...new Set(emails.map(email => email.category).filter(Boolean))];
        setCategories(uniqueCategories.sort()); // Sort categories alphabetically
      } catch (error) {
        console.error('Error fetching categories:', error);
      }
    };

    fetchCategories();
  }, []);

  // Create navigation items with base items and categories
  const navigation = [
    ...baseNavigation,
    // Add a divider for categories if there are any
    ...(categories.length > 0 ? [{ type: 'divider', name: 'Categories' }] : []),
    // Add the categories
    ...categories.map(category => ({
      name: category.charAt(0).toUpperCase() + category.slice(1),
      href: `/emails?category=${category.toLowerCase()}`,
      icon: TagIcon,
      type: 'category'
    }))
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
        <nav className="mt-6 px-3">
          {navigation.map((item) => {
            if ('type' in item && item.type === 'divider') {
              return (
                <div key={item.name} className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  {item.name}
                </div>
              );
            }

            if (!('href' in item)) return null;

            const isActive = pathname === item.href || 
              (pathname.startsWith('/emails') && item.href.startsWith('/emails') && 
               new URLSearchParams(item.href.split('?')[1]).get('category') === 
               new URLSearchParams(pathname.split('?')[1]).get('category'));
            
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`group flex items-center px-3 py-2 my-1 text-sm font-medium rounded-lg ${
                  isActive
                    ? 'bg-indigo-50 text-indigo-600'
                    : 'text-gray-700 hover:bg-gray-50'
                }`}
              >
                <item.icon
                  className={`mr-3 h-6 w-6 flex-shrink-0 ${
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