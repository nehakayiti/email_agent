export const initiateGoogleLogin = () => {
    window.location.href = `${process.env.NEXT_PUBLIC_API_URL}/auth/login`;
};

export const getToken = (): string | null => {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('auth_token');
};

export const setToken = (token: string) => {
    if (typeof window === 'undefined') return;
    localStorage.setItem('auth_token', token);
};

export const removeToken = () => {
    if (typeof window === 'undefined') return;
    localStorage.removeItem('auth_token');
};

export const handleAuthError = () => {
    removeToken();
    
    // Prevent redirect loops by checking if we're already on the home page
    // or in the authentication flow
    if (typeof window !== 'undefined' && 
        !window.location.pathname.includes('/auth') && 
        window.location.pathname !== '/') {
        
        // Use a flag in sessionStorage to prevent multiple redirects
        if (!sessionStorage.getItem('auth_redirect_in_progress')) {
            sessionStorage.setItem('auth_redirect_in_progress', 'true');
            
            // Clear the flag after navigation completes
            window.addEventListener('load', () => {
                sessionStorage.removeItem('auth_redirect_in_progress');
            }, { once: true });
            
            window.location.href = '/';
        }
    }
};

export const isAuthenticated = (): boolean => {
    const token = getToken();
    return !!token;
}; 