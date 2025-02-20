'use client';

import { useRouter } from 'next/navigation';
import { ReactNode, useEffect, useState } from 'react';
import { isAuthenticated, removeToken } from '@/lib/auth';

interface AppLayoutProps {
  children: ReactNode;
  userName?: string;
}

export default function AppLayout({ children, userName = 'User' }: AppLayoutProps) {
  const router = useRouter();
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/');
    }
  }, [router]);

  const handleLogout = () => {
    removeToken();
    router.push('/');
  };

  return (
    <div className="h-screen flex">
      {/* Sidebar */}
      <div className={`bg-gray-900 text-white w-64 flex-shrink-0 ${isSidebarOpen ? '' : 'hidden'}`}>
        <div className="h-16 flex items-center justify-between px-4 border-b border-gray-800">
          <h1 className="text-xl font-semibold">Email Agent</h1>
          <button
            onClick={() => setIsSidebarOpen(false)}
            className="text-gray-400 hover:text-white"
          >
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <nav className="mt-4">
          <div className="px-4 mb-4">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center">
                {userName[0].toUpperCase()}
              </div>
              <span className="text-sm font-medium">{userName}</span>
            </div>
          </div>
          
          <div className="space-y-1 px-2">
            <button
              onClick={() => router.push('/emails')}
              className="flex items-center space-x-2 w-full px-2 py-2 text-sm rounded-md hover:bg-gray-800"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              <span>All Emails</span>
            </button>
            
            <button
              onClick={handleLogout}
              className="flex items-center space-x-2 w-full px-2 py-2 text-sm rounded-md hover:bg-gray-800 text-red-400 hover:text-red-300"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              <span>Sign Out</span>
            </button>
          </div>
        </nav>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="h-16 bg-white border-b border-gray-200 flex items-center px-4">
          {!isSidebarOpen && (
            <button
              onClick={() => setIsSidebarOpen(true)}
              className="mr-4 text-gray-600 hover:text-gray-900"
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          )}
          <h2 className="text-xl font-semibold text-gray-900">Your Emails</h2>
        </header>
        
        <main className="flex-1 overflow-auto bg-gray-50">
          {children}
        </main>
      </div>
    </div>
  );
} 