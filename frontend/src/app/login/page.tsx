'use client';

import { useEffect, useState } from 'react';
import { initiateGoogleLogin } from '@/lib/auth';

export default function LoginPage() {
  const [showAuthError, setShowAuthError] = useState(false);
  const [autoRedirect, setAutoRedirect] = useState(false);

  useEffect(() => {
    // Check if we were redirected here due to an auth error
    const urlParams = new URLSearchParams(window.location.search);
    const authError = urlParams.get('auth_error');
    
    if (authError) {
      console.log('Authentication error detected:', authError);
      setShowAuthError(true);
      
      // Set a timer to automatically redirect after 5 seconds
      const timer = setTimeout(() => {
        setAutoRedirect(true);
        initiateGoogleLogin();
      }, 5000);
      
      return () => clearTimeout(timer);
    }
  }, []);

  const handleLogin = () => {
    initiateGoogleLogin();
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      {showAuthError && (
        <div className="fixed top-0 left-0 right-0 bg-red-500 text-white p-4 text-center shadow-md">
          <p className="text-lg font-semibold">Your session has expired</p>
          <p>Please sign in again to continue using Email Agent {autoRedirect && '(Redirecting...)'}</p>
        </div>
      )}
      
      <div className="bg-white p-8 rounded-lg shadow-md w-[400px] mt-12">
        <h1 className="text-2xl font-bold mb-2">Email Agent</h1>
        
        {showAuthError && (
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-4">
            <p className="text-yellow-700 font-medium">Authentication Required</p>
            <p className="text-sm text-yellow-600">
              Your session has expired or you need to log in. {autoRedirect ? 'Redirecting to Google login...' : 'Please click the button below to sign in.'}
            </p>
          </div>
        )}
        
        <p className="text-gray-600 mb-6">
          Sign in with your Google account to access your emails
        </p>
        <p className="text-sm text-gray-500 mb-4">
          This application requires access to your Gmail account to manage emails and labels.
        </p>
        <button 
          onClick={handleLogin} 
          className={`w-full ${showAuthError 
            ? 'bg-blue-600 hover:bg-blue-700 animate-pulse text-white font-bold py-3 px-4 rounded-md shadow-lg' 
            : 'bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded'}`}
        >
          Sign in with Google
        </button>
      </div>
    </div>
  );
} 