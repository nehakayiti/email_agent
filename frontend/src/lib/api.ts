import { getToken, handleAuthError } from './auth';

interface Email {
    id: string;
    subject: string;
    from_email: string;
    received_at: string;
    snippet: string;
    is_read: boolean;
    importance_score: number;
    category: string;
}

interface EmailsResponse {
    emails: Email[];
}

const API_URL = process.env.NEXT_PUBLIC_API_URL;

if (!API_URL) {
    throw new Error('NEXT_PUBLIC_API_URL environment variable is not set');
}

function isEmailArray(data: unknown): data is Email[] {
    return Array.isArray(data) && data.every(item => 
        typeof item === 'object' && 
        item !== null && 
        'id' in item && 
        'subject' in item &&
        'from_email' in item &&
        'received_at' in item
    );
}

function isEmailsResponse(data: unknown): data is EmailsResponse {
    return (
        typeof data === 'object' &&
        data !== null &&
        'emails' in data &&
        isEmailArray((data as EmailsResponse).emails)
    );
}

async function fetchWithAuth(endpoint: string, options: RequestInit = {}) {
    const token = getToken();
    if (!token) {
        handleAuthError();
        throw new Error('No authentication token found');
    }

    try {
        console.log(`Making API request to ${API_URL}${endpoint}`);
        const response = await fetch(`${API_URL}${endpoint}`, {
            ...options,
            headers: {
                ...options.headers,
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            if (response.status === 401) {
                handleAuthError();
                throw new Error('Authentication failed: Invalid or expired token');
            }

            const errorData = await response.json().catch(() => null);
            throw new Error(
                errorData?.detail || 
                `API error: ${response.status} ${response.statusText}`
            );
        }

        const data = await response.json();
        console.log(`API response from ${endpoint}:`, data);
        return data;
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

export async function getEmails(): Promise<Email[]> {
    const data = await fetchWithAuth('/emails');
    if (!isEmailsResponse(data)) {
        console.error('Invalid email data received:', data);
        throw new Error('Invalid response format: Expected an object with emails array');
    }
    return data.emails;
}

export async function getEmailById(id: string): Promise<Email> {
    const data = await fetchWithAuth(`/emails/${id}`);
    if (!data || typeof data !== 'object' || !('id' in data)) {
        console.error('Invalid email data received:', data);
        throw new Error('Invalid response format: Expected an email object');
    }
    return data as Email;
}

export type { Email }; 