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

export const isAuthenticated = (): boolean => {
    return !!getToken();
}; 