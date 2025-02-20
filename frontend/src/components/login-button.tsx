'use client';

import { initiateGoogleLogin } from '@/lib/auth';
import { useState } from 'react';

export default function LoginButton() {
    const [isHovered, setIsHovered] = useState(false);

    return (
        <button
            onClick={initiateGoogleLogin}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
            className="group relative inline-flex items-center justify-center overflow-hidden rounded-lg bg-gradient-to-br from-blue-600 to-indigo-600 p-0.5 text-sm font-medium text-gray-900 hover:text-white focus:outline-none focus:ring-4 focus:ring-blue-300"
        >
            <span className={`relative flex items-center gap-2 rounded-md bg-white px-5 py-2.5 transition-all duration-300 ease-in-out group-hover:bg-opacity-0 ${isHovered ? 'text-white' : 'text-gray-900'}`}>
                <svg
                    className={`h-5 w-5 transition-transform duration-300 ${isHovered ? 'scale-110' : ''}`}
                    viewBox="0 0 24 24"
                    fill="currentColor"
                >
                    <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                    <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                    <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                    <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                </svg>
                Sign in with Google
                <svg
                    className={`h-4 w-4 transition-transform duration-300 ${isHovered ? 'translate-x-1' : ''}`}
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                >
                    <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M13 7l5 5m0 0l-5 5m5-5H6"
                    />
                </svg>
            </span>
        </button>
    );
} 