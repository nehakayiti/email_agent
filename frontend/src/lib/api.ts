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
    raw_data: {
        payload: {
            headers: Array<{ name: string; value: string }>;
            parts?: Array<{
                mimeType: string;
                body: {
                    data?: string;
                    size?: number;
                };
            }>;
            body?: {
                data?: string;
                size?: number;
            };
        };
    };
    gmail_id: string;
    thread_id: string;
}

interface PaginationMetadata {
    total: number;
    limit: number;
    current_page: number;
    total_pages: number;
    has_next: boolean;
    has_previous: boolean;
    next_page: number | null;
    previous_page: number | null;
}

interface EmailsResponse {
    emails: Email[];
    pagination: PaginationMetadata;
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
        isEmailArray((data as EmailsResponse).emails) &&
        'pagination' in data &&
        typeof (data as EmailsResponse).pagination === 'object'
    );
}

async function fetchWithAuth<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = getToken();
    if (!token) {
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
        return data as T;
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

export interface EmailsParams {
    category?: string;
    importance_threshold?: number;
    limit?: number;
    page?: number;
}

export async function getEmails(params: EmailsParams = {}): Promise<EmailsResponse> {
    const queryParams = new URLSearchParams();
    
    if (params.category) {
        queryParams.append('category', params.category);
    }
    
    if (params.importance_threshold !== undefined) {
        queryParams.append('importance_threshold', params.importance_threshold.toString());
    }
    
    if (params.limit) {
        queryParams.append('limit', params.limit.toString());
    }
    
    if (params.page) {
        queryParams.append('page', params.page.toString());
    }
    
    const queryString = queryParams.toString();
    const endpoint = `/emails${queryString ? `?${queryString}` : ''}`;
    
    const data = await fetchWithAuth<EmailsResponse>(endpoint);
    
    if (!isEmailsResponse(data)) {
        console.error('Invalid email data received:', data);
        throw new Error('Invalid response format: Expected an object with emails array and pagination metadata');
    }
    
    return data;
}

export async function getEmailById(id: string): Promise<Email> {
    const data = await fetchWithAuth<Email>(`/emails/${id}`);
    if (!data || typeof data !== 'object' || !('id' in data)) {
        console.error('Invalid email data received:', data);
        throw new Error('Invalid response format: Expected an email object');
    }
    return data as Email;
}

export type { Email };

// Analytics Response Types
interface SentimentTrendItem {
  date: string;
  sentiment: number;
}

interface SentimentAnalyticsResponse {
  total_emails: number;
  period_days: number;
  average_sentiment: number;
  sentiment_distribution: {
    positive: number;
    neutral: number;
    negative: number;
  };
  sentiment_trend: SentimentTrendItem[];
}

interface ResponseTimeAnalyticsResponse {
  periods: Record<string, number>;
  unit: string;
}

interface VolumeDataItem {
  date: string;
  count: number;
}

interface VolumeAnalyticsResponse {
  daily_volume: VolumeDataItem[];
  total_days: number;
  total_emails: number;
}

interface TopContactItem {
  email: string;
  count: number;
}

interface TopContactsResponse {
  top_contacts: TopContactItem[];
  period_days: number;
  total_contacts: number;
}

// Analytics Types
interface SentimentAnalytics {
  dates: string[];
  scores: number[];
}

interface ResponseTimeAnalytics {
  periods: string[];
  averages: number[];
}

interface VolumeAnalytics {
  dates: string[];
  counts: number[];
}

interface TopContactsAnalytics {
  contacts: string[];
  counts: number[];
}

// Analytics API endpoints
export async function getSentimentAnalytics(days: number = 30): Promise<SentimentAnalytics> {
  const response = await fetchWithAuth<SentimentAnalyticsResponse>(`/analytics/sentiment?days=${days}`);
  console.log('Sentiment Analytics Response:', response);
  
  if (!response?.sentiment_trend || !Array.isArray(response.sentiment_trend)) {
    throw new Error('Invalid sentiment analytics response format');
  }

  return {
    dates: response.sentiment_trend.map((item: SentimentTrendItem) => item.date),
    scores: response.sentiment_trend.map((item: SentimentTrendItem) => item.sentiment)
  };
}

export async function getResponseTimeAnalytics(periods: number = 90): Promise<ResponseTimeAnalytics> {
  const response = await fetchWithAuth<ResponseTimeAnalyticsResponse>(`/analytics/response-time?periods=${periods}`);
  console.log('Response Time Analytics Response:', response);
  
  if (!response?.periods || typeof response.periods !== 'object') {
    throw new Error('Invalid response time analytics response format');
  }

  const periodNames = Object.keys(response.periods);
  const periodValues = Object.values(response.periods) as number[];

  return {
    periods: periodNames.map(name => name.replace('_days', ' Days')),
    averages: periodValues
  };
}

export async function getVolumeAnalytics(days: number = 30): Promise<VolumeAnalytics> {
  const response = await fetchWithAuth<VolumeAnalyticsResponse>(`/analytics/volume?days=${days}`);
  console.log('Volume Analytics Response:', response);
  
  if (!response?.daily_volume || !Array.isArray(response.daily_volume)) {
    throw new Error('Invalid volume analytics response format');
  }

  return {
    dates: response.daily_volume.map((item: VolumeDataItem) => item.date),
    counts: response.daily_volume.map((item: VolumeDataItem) => item.count)
  };
}

export async function getTopContacts(limit: number = 10, days: number = 30): Promise<TopContactsAnalytics> {
  const response = await fetchWithAuth<TopContactsResponse>(`/analytics/top-contacts?limit=${limit}&days=${days}`);
  console.log('Top Contacts Response:', response);
  
  if (!response?.top_contacts || !Array.isArray(response.top_contacts)) {
    throw new Error('Invalid top contacts response format');
  }

  return {
    contacts: response.top_contacts.map((item: TopContactItem) => item.email),
    counts: response.top_contacts.map((item: TopContactItem) => item.count)
  };
}

export type { 
  SentimentAnalytics, 
  ResponseTimeAnalytics, 
  VolumeAnalytics, 
  TopContactsAnalytics 
};

export interface DbInsightsResponse {
  user_count: number;
  email_count: number;
  last_sync: string | null;
  user_syncs: Array<{
    email: string;
    last_fetched_at: string;
    sync_cadence_minutes: number;
  }>;
  table_sizes: Array<{
    table_name: string;
    size: string;
    raw_size: number;
  }>;
  sample_token: string;
}

export async function getDbInsights(): Promise<DbInsightsResponse> {
  try {
    const response = await fetchWithAuth<DbInsightsResponse>(`/analytics/db-insights`);
    return response;
  } catch (error) {
    console.error('Error fetching DB insights:', error);
    throw error;
  }
}

export interface SyncResponse {
  success?: boolean;
  status?: string;
  message: string;
  sync_started_at?: string;
  user_id?: string;
  sync_count?: number;
  new_email_count?: number;
}

export async function triggerEmailSync(): Promise<SyncResponse> {
  try {
    const timestamp = new Date().getTime();
    const response = await fetchWithAuth<SyncResponse>(`/emails/sync?t=${timestamp}&use_current_date=true`, {
      method: 'POST',
    });
    return response;
  } catch (error) {
    console.error('Error triggering email sync:', error);
    throw error;
  }
} 