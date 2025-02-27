'use client';

import { useEffect } from 'react';
import { initiateGoogleLogin } from '@/lib/auth';

export default function LoginPage() {
  useEffect(() => {
    // Check if we were redirected here due to an auth error
    const urlParams = new URLSearchParams(window.location.search);
    const authError = urlParams.get('auth_error');
    
    if (authError) {
      console.log('Authentication error detected:', authError);
    }
  }, []);

  const handleLogin = () => {
    initiateGoogleLogin();
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md w-[350px]">
        <h1 className="text-2xl font-bold mb-2">Email Agent</h1>
        <p className="text-gray-600 mb-6">
          Sign in with your Google account to access your emails
        </p>
        <p className="text-sm text-gray-500 mb-4">
          This application requires access to your Gmail account to manage emails and labels.
        </p>
        <button 
          onClick={handleLogin} 
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          Sign in with Google
        </button>
      </div>
    </div>
  );
} 