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
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkAuth = () => {
      if (!isAuthenticated()) {
        removeToken();
        router.push('/');
      }
      setIsLoading(false);
    };

    checkAuth();
  }, [router]);

  const handleLogout = () => {
    console.log('Logout clicked');
    removeToken();
    router.push('/');
  };

  const handleLogoClick = () => {
    console.log('Logo clicked');
    router.push('/');
  };

  if (isLoading) {
    return (
      <div className="h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      {/* Simple Header */}
      <header className="fixed top-0 left-0 right-0 h-16 bg-red-200 flex items-center justify-between px-6 z-50">
        <button 
          onClick={handleLogoClick}
          className="text-xl font-bold text-black p-2 bg-white rounded hover:bg-gray-100"
        >
          Email Agent
        </button>
        
        <button
          onClick={handleLogout}
          className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Logout
        </button>
      </header>

      {/* Content */}
      <div className="pt-16">
        <main className="bg-gray-50 min-h-screen">
          {children}
        </main>
      </div>
    </div>
  );
} 