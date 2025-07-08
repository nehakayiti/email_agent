import { getToken, handleAuthError, initiateGoogleLogin } from './auth';
import { toast } from 'react-hot-toast';

export interface Email {
    id: string;
    gmail_id: string;
    thread_id: string;
    subject: string;
    from_email: string;
    received_at: string;
    snippet: string;
    labels: string[];
    is_read: boolean;
    is_processed: boolean;
    importance_score: number;
    category: string;
    raw_data?: any;
    created_at: string;
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

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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

// Helper function to handle auth errors gracefully
const handleApiError = (error: any) => {
    if (error.message === 'No authentication token found' || error.message.includes('Authentication failed')) {
        // Handle auth errors by redirecting to login
        handleAuthError();
        // Return null to indicate auth error
        return null;
    }
    // For other errors, show toast and throw
    toast.error(error.message || 'An error occurred');
    throw error;
};

// Update the checkAuthToken function to be more graceful
const checkAuthToken = () => {
    const token = localStorage.getItem('auth_token');
    if (!token) {
        console.log('No authentication token found');
        handleAuthError();
        return null;
    }
    return token;
};

export async function fetchWithAuth<T>(endpoint: string, options: RequestInit = {}): Promise<T | null> {
    const token = getToken();
    
    if (!token) {
        console.log('No authentication token found');
        handleAuthError();
        return null;
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
                console.log('Authentication failed: Invalid or expired token');
                handleAuthError();
                return null;
            }

            const errorData = await response.json().catch(() => null);
            if (errorData?.detail) {
                if (typeof errorData.detail === 'object') {
                    // Attach the detail object to the error for downstream handling
                    const err = new Error(errorData.detail.message || 'API error');
                    (err as any).response = { detail: errorData.detail };
                    throw err;
                } else {
                    throw new Error(errorData.detail);
                }
            }
            throw new Error(`API error: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        console.log(`API response from ${endpoint}:`, data);
        return data as T;
    } catch (error) {
        console.error('API request failed:', error);
        return handleApiError(error);
    }
}

export interface EmailsParams {
    category?: string;
    importance_threshold?: number;
    limit?: number;
    page?: number;
    status?: 'read' | 'unread';
    label?: string;
    showAll?: boolean;
    read_status?: boolean;
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
    
    if (params.status) {
        queryParams.append('status', params.status);
    }
    
    if (params.read_status !== undefined) {
        queryParams.append('read_status', params.read_status.toString());
    }
    
    if (params.label) {
        queryParams.append('label', params.label);
    }
    
    if (params.showAll) {
        queryParams.append('show_all', 'true');
    }
    
    const queryString = queryParams.toString();
    const endpoint = `/emails${queryString ? `?${queryString}` : ''}`;
    
    const data = await fetchWithAuth<EmailsResponse>(endpoint);
    
    if (!data) {
        return {
            emails: [],
            pagination: {
                total: 0,
                limit: params.limit || 20,
                current_page: params.page || 1,
                total_pages: 0,
                has_next: false,
                has_previous: false,
                next_page: null,
                previous_page: null
            }
        };
    }
    
    if ('error' in data && 'status' in data) {
        console.error('Error fetching emails:', data.error);
        return {
            emails: [],
            pagination: {
                total: 0,
                limit: params.limit || 20,
                current_page: params.page || 1,
                total_pages: 0,
                has_next: false,
                has_previous: false,
                next_page: null,
                previous_page: null
            }
        };
    }
    
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
    if (!response) {
      throw new Error('Failed to fetch DB insights');
    }
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

export async function triggerEmailSync() {
    const token = checkAuthToken();
    if (!token) return null;

    try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/emails/sync`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Failed to sync emails');
        }

        return await response.json();
    } catch (error) {
        return handleApiError(error);
    }
}

export async function getTrashedEmails(params: EmailsParams = {}): Promise<EmailsResponse> {
  try {
    const queryParams = new URLSearchParams();
    
    if (params.limit) queryParams.set('limit', params.limit.toString());
    if (params.page) queryParams.set('page', params.page.toString());
    
    const queryString = queryParams.toString();
    const url = `/emails/deleted${queryString ? `?${queryString}` : ''}`;
    
    const response = await fetchWithAuth<EmailsResponse>(url);
    if (!response) {
      throw new Error('Failed to fetch trashed emails');
    }
    return response;
  } catch (error) {
    console.error('Error fetching trashed emails:', error);
    throw error;
  }
}

// Keep for backward compatibility
export async function getDeletedEmails(params: EmailsParams = {}): Promise<EmailsResponse> {
  return getTrashedEmails(params);
}

export interface UpdateLabelsResponse {
  status: string;
  message: string;
  email_id: string;
  labels: string[];
  is_read: boolean;
}

export async function updateEmailLabels(
  emailId: string,
  addLabels?: string[],
  removeLabels?: string[]
): Promise<UpdateLabelsResponse> {
  try {
    const body: Record<string, any> = {};
    
    if (addLabels && addLabels.length > 0) {
      body.add_labels = addLabels;
    }
    
    if (removeLabels && removeLabels.length > 0) {
      body.remove_labels = removeLabels;
    }
    
    const response = await fetchWithAuth<UpdateLabelsResponse>(`/emails/${emailId}/update-labels`, {
      method: 'POST',
      body: JSON.stringify(body),
    });
    
    if (!response) {
      throw new Error('Failed to update email labels');
    }
    
    return response;
  } catch (error) {
    console.error('Error updating email labels:', error);
    throw error;
  }
}

export interface UpdateCategoryResponse {
  status: string;
  message: string;
  email_id: string;
  category: string;
  labels: string[];
  confidence_score: number | null;
  decision_factors: Record<string, any> | null;
}

export async function updateEmailCategory(
  emailId: string,
  category: string
): Promise<UpdateCategoryResponse> {
  try {
    const response = await fetchWithAuth<UpdateCategoryResponse>(`/emails/${emailId}/update-category`, {
      method: 'POST',
      body: JSON.stringify({ category }),
    });
    
    if (!response) {
      throw new Error('Failed to update email category');
    }
    
    return response;
  } catch (error) {
    console.error('Error updating email category:', error);
    throw error;
  }
}

export async function archiveEmail(emailId: string): Promise<{ 
  status: string; 
  message: string;
  labels?: string[];
  category?: string;
}> {
  try {
    const response = await fetchWithAuth<{ 
      status: string; 
      message: string;
      labels?: string[];
      category?: string;
    }>(`/emails/${emailId}/archive`, {
      method: 'POST',
    });
    
    if (!response) {
      throw new Error('Failed to archive email');
    }
    
    return response;
  } catch (error) {
    console.error('Error archiving email:', error);
    throw error;
  }
}

export async function deleteEmail(emailId: string): Promise<{ 
  status: string; 
  message: string;
}> {
  try {
    const response = await fetchWithAuth<{ 
      status: string; 
      message: string;
    }>(`/emails/${emailId}`, {
      method: 'DELETE',
    });
    
    if (!response) {
      throw new Error('Failed to delete email');
    }
    
    return response;
  } catch (error) {
    console.error('Error deleting email:', error);
    throw error;
  }
}

// Category management API functions
export interface Category {
  id: number;
  name: string;
  display_name: string;
  description: string | null;
  priority: number;
  is_system: boolean;
  keyword_count: number;
  sender_rule_count: number;
}

export interface CategoryKeyword {
  id: number;
  keyword: string;
  is_regex: boolean;
  weight: number;
  user_id: string | null;
}

export interface SenderRule {
  id: number;
  pattern: string;
  is_domain: boolean;
  weight: number;
  user_id: string | null;
}

export interface ClassifierStatus {
  is_model_available: boolean;
  training_data_count: number;
  last_trained: string | null;
}

// New model metrics interface
export interface ModelMetrics {
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  confusion_matrix: {
    true_positives: number;
    false_positives: number;
    true_negatives: number;
    false_negatives: number;
  };
  top_features: Array<{
    feature: string;
    importance: number;
    class: string;
  }>;
  training_size: number;
  test_size: number;
  training_time: string;
}

interface CategoriesResponse {
  data: Category[];
}

export async function getCategoriesApi(): Promise<CategoriesResponse> {
  const data = await fetchWithAuth<Category[]>('/email-management/categories');
  if (!data) {
    return { data: [] };
  }
  return { data };
}

export async function initializeCategories(): Promise<any> {
  return fetchWithAuth('/email-management/initialize-categories', {
    method: 'POST'
  });
}

export async function getCategoryKeywords(categoryName: string): Promise<CategoryKeyword[]> {
  const response = await fetchWithAuth<CategoryKeyword[]>(`/email-management/categories/${categoryName}/keywords`);
  if (!response) {
    return [];
  }
  return response;
}

export async function getCategorySenderRules(categoryName: string): Promise<SenderRule[]> {
  const response = await fetchWithAuth<SenderRule[]>(`/email-management/categories/${categoryName}/sender-rules`);
  if (!response) {
    return [];
  }
  return response;
}

export async function addKeyword(categoryName: string, keyword: string): Promise<any> {
  return fetchWithAuth('/email-management/keywords', {
    method: 'POST',
    body: JSON.stringify({
      category_name: categoryName,
      keyword
    })
  });
}

export async function addSenderRule(categoryName: string, pattern: string, isDomain: boolean = true, weight: number = 1): Promise<any> {
  return fetchWithAuth('/email-management/sender-rules', {
    method: 'POST',
    body: JSON.stringify({
      category_name: categoryName,
      pattern,
      is_domain: isDomain,
      weight
    })
  });
}

export async function reprocessAllEmails(): Promise<any> {
  return fetchWithAuth('/email-management/reprocess', {
    method: 'POST',
    body: JSON.stringify({
      force_reprocess: true,
      include_reprocessed: true
    })
  });
}

export async function trainTrashClassifier(testSize: number = 0.2): Promise<any> {
  return fetchWithAuth('/email-management/classifier/train', {
    method: 'POST',
    body: JSON.stringify({
      test_size: testSize
    })
  });
}

export async function getTrashClassifierStatus(): Promise<ClassifierStatus> {
  const response = await fetchWithAuth<ClassifierStatus>('/email-management/classifier/status');
  if (!response) {
    throw new Error('Failed to get classifier status');
  }
  return response;
}

// New function to evaluate the model with test data
export async function evaluateTrashClassifier(): Promise<ModelMetrics> {
  const response = await fetchWithAuth<ModelMetrics>('/email-management/classifier/evaluate');
  if (!response) {
    throw new Error('Failed to evaluate classifier');
  }
  return response;
}

// New function to get model metrics
export async function getClassifierMetrics(): Promise<ModelMetrics> {
  const response = await fetchWithAuth<ModelMetrics>('/email-management/classifier/metrics');
  if (!response) {
    throw new Error('Failed to get classifier metrics');
  }
  return response;
}

export async function deleteCategory(categoryName: string): Promise<any> {
  return fetchWithAuth(`/email-management/categories/${categoryName}`, {
    method: 'DELETE'
  });
}

export interface CreateCategoryRequest {
  name: string;
  display_name: string;
  description?: string;
  priority?: number;
}

export async function createCategory(data: CreateCategoryRequest): Promise<Category> {
  const response = await fetchWithAuth<Category>('/email-management/categories', {
    method: 'POST',
    body: JSON.stringify(data)
  });
  if (!response) {
    throw new Error('Failed to create category');
  }
  return response;
}

export async function bootstrapTrashClassifier(testSize: number = 0.2): Promise<any> {
  return fetchWithAuth('/email-management/classifier/bootstrap', {
    method: 'POST',
    body: JSON.stringify({
      test_size: testSize
    })
  });
}

export async function emptyTrash() {
    const token = checkAuthToken();
    if (!token) {
        throw new Error('No authentication token found');
    }

    try {
        const response = await fetch(`${API_URL}/emails/empty-trash`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => null);
            const errorMessage = errorData?.detail || `API error: ${response.status} ${response.statusText}`;
            console.error('Error emptying trash:', errorMessage);
            throw new Error(errorMessage);
        }

        return await response.json();
    } catch (error) {
        console.error('Error emptying trash:', error);
        throw error;
    }
}

export async function updateSenderRuleWeight(ruleId: number, weight: number): Promise<SenderRule> {
  const response = await fetchWithAuth<SenderRule>(`/email-management/sender-rules/${ruleId}`, {
    method: 'PATCH',
    body: JSON.stringify({
      weight
    })
  });
  if (!response) {
    throw new Error('Failed to update sender rule weight');
  }
  return response;
}

export async function deleteSenderRule(ruleId: number): Promise<any> {
  return fetchWithAuth(`/email-management/sender-rules/${ruleId}`, {
    method: 'DELETE'
  });
}

export async function deleteKeyword(keywordId: number): Promise<any> {
  return fetchWithAuth(`/email-management/keywords/${keywordId}`, {
    method: 'DELETE'
  });
}

export async function updateKeywordWeight(keywordId: number, weight: number): Promise<CategoryKeyword> {
  const response = await fetchWithAuth<CategoryKeyword>(`/email-management/keywords/${keywordId}`, {
    method: 'PATCH',
    body: JSON.stringify({
      weight
    })
  });
  if (!response) {
    throw new Error('Failed to update keyword weight');
  }
  return response;
}

export async function updateSenderRulePattern(ruleId: number, pattern: string, isDomain: boolean): Promise<SenderRule> {
  const response = await fetchWithAuth<SenderRule>(`/email-management/sender-rules/${ruleId}/pattern`, {
    method: 'PATCH',
    body: JSON.stringify({
      pattern,
      is_domain: isDomain
    })
  });
  if (!response) {
    throw new Error('Failed to update sender rule pattern');
  }
  return response;
}

export async function getLatestSyncDetails(): Promise<any | null> {
    return fetchWithAuth('/sync/details/latest');
}

export async function getSyncHistory(limit: number = 3): Promise<any[] | null> {
    return fetchWithAuth(`/sync/details/?limit=${limit}`);
}

export async function updateSyncCadence(cadence: number): Promise<{ sync_cadence: number } | null> {
    return await fetchWithAuth<{ sync_cadence: number }>(
        '/emails/sync-cadence',
        {
            method: 'PATCH',
            body: JSON.stringify({ cadence }),
        }
    );
} 

// Action Engine Types and Interfaces
export interface ActionRule {
  category_id: number;
  category_name: string;
  action: 'ARCHIVE' | 'TRASH' | null;
  delay_days: number | null;
  enabled: boolean;
}

export interface ActionRuleRequest {
  action: 'ARCHIVE' | 'TRASH';
  delay_days: number;
  enabled: boolean;
}

export interface ActionPreview {
  category_id: number;
  affected_email_count: number;
  affected_emails: Array<{
    id: string;
    subject: string;
    from_email: string;
    received_at: string;
    age_days: number;
  }>;
}

export interface ProposedActionItem {
  id: string;
  email_id: string;
  email_subject: string;
  email_sender: string;
  email_date: string | null;
  category_id: number;
  category_name: string;
  action_type: 'ARCHIVE' | 'TRASH';
  reason: string;
  email_age_days: number;
  created_at: string;
  status: 'pending' | 'approved' | 'rejected' | 'expired';
}

export interface ProposedActionList {
  items: ProposedActionItem[];
  total_count: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ActionProcessResponse {
  success: boolean;
  mode: string;
  proposals_created?: number;
  operations_created?: number;
  emails_processed: number;
  message: string;
}

// Action Rule Management API Functions
export async function getActionRules(categoryId?: number): Promise<ActionRule[]> {
  if (categoryId) {
    const rule = await fetchWithAuth<ActionRule>(`/action-management/categories/${categoryId}/action-rule`);
    return rule ? [rule] : [];
  } else {
    const rules = await fetchWithAuth<ActionRule[]>('/action-management/action-rules');
    return rules || [];
  }
}

export async function createActionRule(categoryId: number, rule: ActionRuleRequest): Promise<ActionRule> {
  const response = await fetchWithAuth<ActionRule>(
    `/action-management/categories/${categoryId}/action-rule`,
    {
      method: 'POST',
      body: JSON.stringify(rule),
    }
  );
  if (!response) throw new Error('Failed to create action rule');
  return response;
}

export async function updateActionRule(categoryId: number, rule: ActionRuleRequest): Promise<ActionRule> {
  const response = await fetchWithAuth<ActionRule>(
    `/action-management/categories/${categoryId}/action-rule`,
    {
      method: 'POST',
      body: JSON.stringify(rule),
    }
  );
  if (!response) throw new Error('Failed to update action rule');
  return response;
}

export async function deleteActionRule(categoryId: number): Promise<void> {
  const response = await fetchWithAuth(
    `/action-management/categories/${categoryId}/action-rule`,
    {
      method: 'DELETE',
    }
  );
  if (response === null) throw new Error('Failed to delete action rule');
}

export async function toggleActionRule(categoryId: number, enabled: boolean): Promise<ActionRule> {
  const currentRule = await getActionRules(categoryId);
  if (!currentRule.length) {
    throw new Error('No action rule found for this category');
  }
  
  const rule = currentRule[0];
  return updateActionRule(categoryId, {
    action: rule.action || 'ARCHIVE',
    delay_days: rule.delay_days || 7,
    enabled,
  });
}

// Action Preview API Functions
export async function getActionPreview(categoryId: number): Promise<ActionPreview> {
  const response = await fetchWithAuth<ActionPreview>(`/action-management/categories/${categoryId}/action-preview`);
  if (!response) throw new Error('Failed to get action preview');
  return response;
}

// Proposed Actions API Functions
export async function getProposedActions(params: {
  status_filter?: string;
  action_type?: string;
  category_id?: number;
  page?: number;
  page_size?: number;
} = {}): Promise<ProposedActionList> {
  const queryParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined) {
      queryParams.append(key, value.toString());
    }
  });
  
  const queryString = queryParams.toString();
  const endpoint = `/proposed-actions${queryString ? `?${queryString}` : ''}`;
  
  const response = await fetchWithAuth<ProposedActionList>(endpoint);
  if (!response) throw new Error('Failed to get proposed actions');
  return response;
}

export async function approveProposedAction(actionId: string): Promise<void> {
  const response = await fetchWithAuth(`/proposed-actions/${actionId}/approve`, {
    method: 'POST',
  });
  if (response === null) throw new Error('Failed to approve action');
}

export async function rejectProposedAction(actionId: string): Promise<void> {
  const response = await fetchWithAuth(`/proposed-actions/${actionId}/reject`, {
    method: 'POST',
  });
  if (response === null) throw new Error('Failed to reject action');
}

export async function bulkApproveActions(actionIds: string[]): Promise<{
  approved_count: number;
  failed_count: number;
  failed_actions: Array<{ action_id: string; error: string }>;
}> {
  const response = await fetchWithAuth<{
    approved_count: number;
    failed_count: number;
    failed_actions: Array<{ action_id: string; error: string }>;
  }>('/proposed-actions/bulk-approve', {
    method: 'POST',
    body: JSON.stringify({ action_ids: actionIds }),
  });
  if (!response) throw new Error('Failed to bulk approve actions');
  return response;
}

export async function bulkRejectActions(actionIds: string[]): Promise<{
  rejected_count: number;
  failed_count: number;
  failed_actions: Array<{ action_id: string; error: string }>;
}> {
  const response = await fetchWithAuth<{
    rejected_count: number;
    failed_count: number;
    failed_actions: Array<{ action_id: string; error: string }>;
  }>('/proposed-actions/bulk-reject', {
    method: 'POST',
    body: JSON.stringify({ action_ids: actionIds }),
  });
  if (!response) throw new Error('Failed to bulk reject actions');
  return response;
}

// Action Engine Processing API Functions
export async function processDryRun(categoryIds?: number[]): Promise<ActionProcessResponse> {
  const response = await fetchWithAuth<ActionProcessResponse>('/proposed-actions/process-dry-run', {
    method: 'POST',
    body: JSON.stringify({ category_ids: categoryIds, force: false }),
  });
  if (!response) throw new Error('Failed to process dry run');
  return response;
}

export async function processExecute(categoryIds?: number[]): Promise<ActionProcessResponse> {
  const response = await fetchWithAuth<ActionProcessResponse>('/proposed-actions/process-execute', {
    method: 'POST',
    body: JSON.stringify({ category_ids: categoryIds, force: false }),
  });
  if (!response) throw new Error('Failed to process execute');
  return response;
}

export async function cleanupExpiredProposals(): Promise<{ expired_proposals_removed: number }> {
  const response = await fetchWithAuth<{ expired_proposals_removed: number }>('/proposed-actions/cleanup-expired', {
    method: 'POST',
  });
  if (!response) throw new Error('Failed to cleanup expired proposals');
  return response;
}

export async function getProposedActionsStats(): Promise<{
  total_proposals: number;
  by_status: { pending: number; approved: number; rejected: number; expired: number };
  by_action_type: { archive: number; trash: number };
}> {
  const response = await fetchWithAuth<{
    total_proposals: number;
    by_status: { pending: number; approved: number; rejected: number; expired: number };
    by_action_type: { archive: number; trash: number };
  }>('/proposed-actions/stats');
  if (!response) throw new Error('Failed to get proposed actions stats');
  return response;
} 