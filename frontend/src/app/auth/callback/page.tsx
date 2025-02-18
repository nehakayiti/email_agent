'use client';

import { useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { setToken } from '@/lib/auth';

export default function AuthCallback() {
    const router = useRouter();
    const searchParams = useSearchParams();

    useEffect(() => {
        const token = searchParams.get('token');
        if (token) {
            setToken(token);
            router.push('/emails');
        } else {
            router.push('/');
        }
    }, [searchParams, router]);

    return (
        <div className="min-h-screen flex items-center justify-center">
            <div className="animate-pulse">
                <div className="h-8 w-8 bg-blue-600 rounded-full"></div>
            </div>
        </div>
    );
} 