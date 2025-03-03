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
    
    // Prevent redirect loops by checking if we're already on the login page
    // or in the authentication flow
    if (typeof window !== 'undefined' && 
        !window.location.pathname.includes('/auth') &&
        !window.location.pathname.includes('/login')) {
        
        // Use a flag in sessionStorage to prevent multiple redirects
        if (!sessionStorage.getItem('auth_redirect_in_progress')) {
            sessionStorage.setItem('auth_redirect_in_progress', 'true');
            
            // Clear the flag after navigation completes
            window.addEventListener('load', () => {
                sessionStorage.removeItem('auth_redirect_in_progress');
            }, { once: true });
            
            // Redirect to login page with auth_error parameter
            window.location.href = '/login?auth_error=session_expired';
        }
    }
};

export const isAuthenticated = (): boolean => {
    const token = getToken();
    return !!token;
};

export const logout = async () => {
    try {
        // Call the backend logout endpoint
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/logout`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${getToken()}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            console.error('Logout failed:', response.statusText);
        } else {
            console.log('Logged out successfully');
        }
    } catch (error) {
        console.error('Logout error:', error);
    } finally {
        // Always remove the token from local storage
        removeToken();
        
        // Redirect to login page
        if (typeof window !== 'undefined') {
            window.location.href = '/login';
        }
    }
}; 