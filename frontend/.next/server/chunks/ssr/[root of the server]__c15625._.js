module.exports = {

"[externals]/next/dist/compiled/next-server/app-page.runtime.dev.js [external] (next/dist/compiled/next-server/app-page.runtime.dev.js, cjs)": (function(__turbopack_context__) {

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, x: __turbopack_external_require__, y: __turbopack_external_import__, m: module, e: exports, t: __turbopack_require_real__ } = __turbopack_context__;
{
const mod = __turbopack_external_require__("next/dist/compiled/next-server/app-page.runtime.dev.js", () => require("next/dist/compiled/next-server/app-page.runtime.dev.js"));

module.exports = mod;
}}),
"[externals]/next/dist/server/app-render/action-async-storage.external.js [external] (next/dist/server/app-render/action-async-storage.external.js, cjs)": (function(__turbopack_context__) {

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, x: __turbopack_external_require__, y: __turbopack_external_import__, m: module, e: exports, t: __turbopack_require_real__ } = __turbopack_context__;
{
const mod = __turbopack_external_require__("next/dist/server/app-render/action-async-storage.external.js", () => require("next/dist/server/app-render/action-async-storage.external.js"));

module.exports = mod;
}}),
"[externals]/next/dist/server/app-render/work-unit-async-storage.external.js [external] (next/dist/server/app-render/work-unit-async-storage.external.js, cjs)": (function(__turbopack_context__) {

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, x: __turbopack_external_require__, y: __turbopack_external_import__, m: module, e: exports, t: __turbopack_require_real__ } = __turbopack_context__;
{
const mod = __turbopack_external_require__("next/dist/server/app-render/work-unit-async-storage.external.js", () => require("next/dist/server/app-render/work-unit-async-storage.external.js"));

module.exports = mod;
}}),
"[externals]/next/dist/server/app-render/work-async-storage.external.js [external] (next/dist/server/app-render/work-async-storage.external.js, cjs)": (function(__turbopack_context__) {

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, x: __turbopack_external_require__, y: __turbopack_external_import__, m: module, e: exports, t: __turbopack_require_real__ } = __turbopack_context__;
{
const mod = __turbopack_external_require__("next/dist/server/app-render/work-async-storage.external.js", () => require("next/dist/server/app-render/work-async-storage.external.js"));

module.exports = mod;
}}),
"[project]/src/lib/auth.ts [app-ssr] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, x: __turbopack_external_require__, y: __turbopack_external_import__, z: __turbopack_require_stub__ } = __turbopack_context__;
{
__turbopack_esm__({
    "getToken": (()=>getToken),
    "handleAuthError": (()=>handleAuthError),
    "initiateGoogleLogin": (()=>initiateGoogleLogin),
    "isAuthenticated": (()=>isAuthenticated),
    "logout": (()=>logout),
    "removeToken": (()=>removeToken),
    "setToken": (()=>setToken)
});
const initiateGoogleLogin = ()=>{
    window.location.href = `${process.env.NEXT_PUBLIC_API_URL}/auth/login`;
};
const getToken = ()=>{
    if ("TURBOPACK compile-time truthy", 1) return null;
    "TURBOPACK unreachable";
};
const setToken = (token)=>{
    if ("TURBOPACK compile-time truthy", 1) return;
    "TURBOPACK unreachable";
};
const removeToken = ()=>{
    if ("TURBOPACK compile-time truthy", 1) return;
    "TURBOPACK unreachable";
};
const handleAuthError = ()=>{
    removeToken();
    // Prevent redirect loops by checking if we're already on the login page
    // or in the authentication flow
    if ("undefined" !== 'undefined' && !window.location.pathname.includes('/auth') && !window.location.pathname.includes('/login')) {
        "TURBOPACK unreachable";
    }
};
const isAuthenticated = ()=>{
    const token = getToken();
    return !!token;
};
const logout = async ()=>{
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
    } finally{
        // Always remove the token from local storage
        removeToken();
        // Redirect to login page
        if ("TURBOPACK compile-time falsy", 0) {
            "TURBOPACK unreachable";
        }
    }
};
}}),
"[project]/src/lib/api.ts [app-ssr] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, x: __turbopack_external_require__, y: __turbopack_external_import__, z: __turbopack_require_stub__ } = __turbopack_context__;
{
__turbopack_esm__({
    "addKeyword": (()=>addKeyword),
    "addSenderRule": (()=>addSenderRule),
    "archiveEmail": (()=>archiveEmail),
    "bootstrapTrashClassifier": (()=>bootstrapTrashClassifier),
    "createCategory": (()=>createCategory),
    "deleteCategory": (()=>deleteCategory),
    "deleteEmail": (()=>deleteEmail),
    "emptyTrash": (()=>emptyTrash),
    "evaluateTrashClassifier": (()=>evaluateTrashClassifier),
    "fetchWithAuth": (()=>fetchWithAuth),
    "getCategoriesApi": (()=>getCategoriesApi),
    "getCategoryKeywords": (()=>getCategoryKeywords),
    "getCategorySenderRules": (()=>getCategorySenderRules),
    "getClassifierMetrics": (()=>getClassifierMetrics),
    "getDbInsights": (()=>getDbInsights),
    "getDeletedEmails": (()=>getDeletedEmails),
    "getEmailById": (()=>getEmailById),
    "getEmails": (()=>getEmails),
    "getResponseTimeAnalytics": (()=>getResponseTimeAnalytics),
    "getSentimentAnalytics": (()=>getSentimentAnalytics),
    "getTopContacts": (()=>getTopContacts),
    "getTrashClassifierStatus": (()=>getTrashClassifierStatus),
    "getTrashedEmails": (()=>getTrashedEmails),
    "getVolumeAnalytics": (()=>getVolumeAnalytics),
    "initializeCategories": (()=>initializeCategories),
    "reprocessAllEmails": (()=>reprocessAllEmails),
    "trainTrashClassifier": (()=>trainTrashClassifier),
    "triggerEmailSync": (()=>triggerEmailSync),
    "updateEmailCategory": (()=>updateEmailCategory),
    "updateEmailLabels": (()=>updateEmailLabels)
});
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$auth$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/src/lib/auth.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$hot$2d$toast$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/react-hot-toast/dist/index.mjs [app-ssr] (ecmascript)");
;
;
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
if ("TURBOPACK compile-time falsy", 0) {
    "TURBOPACK unreachable";
}
function isEmailArray(data) {
    return Array.isArray(data) && data.every((item)=>typeof item === 'object' && item !== null && 'id' in item && 'subject' in item && 'from_email' in item && 'received_at' in item);
}
function isEmailsResponse(data) {
    return typeof data === 'object' && data !== null && 'emails' in data && isEmailArray(data.emails) && 'pagination' in data && typeof data.pagination === 'object';
}
// Helper function to handle auth errors gracefully
const handleApiError = (error)=>{
    if (error.message === 'No authentication token found' || error.message.includes('Authentication failed')) {
        // Handle auth errors by redirecting to login
        (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$auth$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["handleAuthError"])();
        // Return null to indicate auth error
        return null;
    }
    // For other errors, show toast and throw
    __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$hot$2d$toast$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["toast"].error(error.message || 'An error occurred');
    throw error;
};
// Update the checkAuthToken function to be more graceful
const checkAuthToken = ()=>{
    const token = localStorage.getItem('auth_token');
    if (!token) {
        console.log('No authentication token found');
        (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$auth$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["handleAuthError"])();
        return null;
    }
    return token;
};
async function fetchWithAuth(endpoint, options = {}) {
    const token = (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$auth$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["getToken"])();
    if (!token) {
        console.log('No authentication token found');
        (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$auth$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["handleAuthError"])();
        return null;
    }
    try {
        console.log(`Making API request to ${API_URL}${endpoint}`);
        const response = await fetch(`${API_URL}${endpoint}`, {
            ...options,
            headers: {
                ...options.headers,
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        if (!response.ok) {
            if (response.status === 401) {
                console.log('Authentication failed: Invalid or expired token');
                (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$auth$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["handleAuthError"])();
                return null;
            }
            const errorData = await response.json().catch(()=>null);
            throw new Error(errorData?.detail || `API error: ${response.status} ${response.statusText}`);
        }
        const data = await response.json();
        console.log(`API response from ${endpoint}:`, data);
        return data;
    } catch (error) {
        console.error('API request failed:', error);
        return handleApiError(error);
    }
}
async function getEmails(params = {}) {
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
    const data = await fetchWithAuth(endpoint);
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
async function getEmailById(id) {
    const data = await fetchWithAuth(`/emails/${id}`);
    if (!data || typeof data !== 'object' || !('id' in data)) {
        console.error('Invalid email data received:', data);
        throw new Error('Invalid response format: Expected an email object');
    }
    return data;
}
async function getSentimentAnalytics(days = 30) {
    const response = await fetchWithAuth(`/analytics/sentiment?days=${days}`);
    console.log('Sentiment Analytics Response:', response);
    if (!response?.sentiment_trend || !Array.isArray(response.sentiment_trend)) {
        throw new Error('Invalid sentiment analytics response format');
    }
    return {
        dates: response.sentiment_trend.map((item)=>item.date),
        scores: response.sentiment_trend.map((item)=>item.sentiment)
    };
}
async function getResponseTimeAnalytics(periods = 90) {
    const response = await fetchWithAuth(`/analytics/response-time?periods=${periods}`);
    console.log('Response Time Analytics Response:', response);
    if (!response?.periods || typeof response.periods !== 'object') {
        throw new Error('Invalid response time analytics response format');
    }
    const periodNames = Object.keys(response.periods);
    const periodValues = Object.values(response.periods);
    return {
        periods: periodNames.map((name)=>name.replace('_days', ' Days')),
        averages: periodValues
    };
}
async function getVolumeAnalytics(days = 30) {
    const response = await fetchWithAuth(`/analytics/volume?days=${days}`);
    console.log('Volume Analytics Response:', response);
    if (!response?.daily_volume || !Array.isArray(response.daily_volume)) {
        throw new Error('Invalid volume analytics response format');
    }
    return {
        dates: response.daily_volume.map((item)=>item.date),
        counts: response.daily_volume.map((item)=>item.count)
    };
}
async function getTopContacts(limit = 10, days = 30) {
    const response = await fetchWithAuth(`/analytics/top-contacts?limit=${limit}&days=${days}`);
    console.log('Top Contacts Response:', response);
    if (!response?.top_contacts || !Array.isArray(response.top_contacts)) {
        throw new Error('Invalid top contacts response format');
    }
    return {
        contacts: response.top_contacts.map((item)=>item.email),
        counts: response.top_contacts.map((item)=>item.count)
    };
}
async function getDbInsights() {
    try {
        const response = await fetchWithAuth(`/analytics/db-insights`);
        return response;
    } catch (error) {
        console.error('Error fetching DB insights:', error);
        throw error;
    }
}
async function triggerEmailSync() {
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
async function getTrashedEmails(params = {}) {
    try {
        const queryParams = new URLSearchParams();
        if (params.limit) queryParams.set('limit', params.limit.toString());
        if (params.page) queryParams.set('page', params.page.toString());
        const queryString = queryParams.toString();
        const url = `/emails/deleted${queryString ? `?${queryString}` : ''}`;
        const response = await fetchWithAuth(url);
        return response;
    } catch (error) {
        console.error('Error fetching trashed emails:', error);
        throw error;
    }
}
async function getDeletedEmails(params = {}) {
    return getTrashedEmails(params);
}
async function updateEmailLabels(emailId, addLabels, removeLabels) {
    try {
        const body = {};
        if (addLabels && addLabels.length > 0) {
            body.add_labels = addLabels;
        }
        if (removeLabels && removeLabels.length > 0) {
            body.remove_labels = removeLabels;
        }
        const response = await fetchWithAuth(`/emails/${emailId}/update-labels`, {
            method: 'POST',
            body: JSON.stringify(body)
        });
        return response;
    } catch (error) {
        console.error('Error updating email labels:', error);
        throw error;
    }
}
async function updateEmailCategory(emailId, category) {
    try {
        const response = await fetchWithAuth(`/emails/${emailId}/update-category`, {
            method: 'POST',
            body: JSON.stringify({
                category
            })
        });
        return response;
    } catch (error) {
        console.error('Error updating email category:', error);
        throw error;
    }
}
async function archiveEmail(emailId) {
    try {
        const response = await fetchWithAuth(`/emails/${emailId}/archive`, {
            method: 'POST'
        });
        return response;
    } catch (error) {
        console.error('Error archiving email:', error);
        throw error;
    }
}
async function deleteEmail(emailId) {
    try {
        const response = await fetchWithAuth(`/emails/${emailId}`, {
            method: 'DELETE'
        });
        return response;
    } catch (error) {
        console.error('Error deleting email:', error);
        throw error;
    }
}
async function getCategoriesApi() {
    const data = await fetchWithAuth('/email-management/categories');
    return {
        data
    };
}
async function initializeCategories() {
    return fetchWithAuth('/email-management/initialize-categories', {
        method: 'POST'
    });
}
async function getCategoryKeywords(categoryName) {
    return fetchWithAuth(`/email-management/categories/${categoryName}/keywords`);
}
async function getCategorySenderRules(categoryName) {
    return fetchWithAuth(`/email-management/categories/${categoryName}/sender-rules`);
}
async function addKeyword(categoryName, keyword) {
    return fetchWithAuth('/email-management/keywords', {
        method: 'POST',
        body: JSON.stringify({
            category_name: categoryName,
            keyword
        })
    });
}
async function addSenderRule(categoryName, pattern, isDomain = true) {
    return fetchWithAuth('/email-management/sender-rules', {
        method: 'POST',
        body: JSON.stringify({
            category_name: categoryName,
            pattern,
            is_domain: isDomain
        })
    });
}
async function reprocessAllEmails() {
    return fetchWithAuth('/email-management/reprocess', {
        method: 'POST',
        body: JSON.stringify({})
    });
}
async function trainTrashClassifier(testSize = 0.2) {
    return fetchWithAuth('/email-management/classifier/train', {
        method: 'POST',
        body: JSON.stringify({
            test_size: testSize
        })
    });
}
async function getTrashClassifierStatus() {
    return fetchWithAuth('/email-management/classifier/status');
}
async function evaluateTrashClassifier() {
    return fetchWithAuth('/email-management/classifier/evaluate');
}
async function getClassifierMetrics() {
    return fetchWithAuth('/email-management/classifier/metrics');
}
async function deleteCategory(categoryName) {
    return fetchWithAuth(`/email-management/categories/${categoryName}`, {
        method: 'DELETE'
    });
}
async function createCategory(data) {
    return fetchWithAuth('/email-management/categories', {
        method: 'POST',
        body: JSON.stringify(data)
    });
}
async function bootstrapTrashClassifier(testSize = 0.2) {
    return fetchWithAuth('/email-management/classifier/bootstrap', {
        method: 'POST',
        body: JSON.stringify({
            test_size: testSize
        })
    });
}
async function emptyTrash() {
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
            const errorData = await response.json().catch(()=>null);
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
}}),
"[project]/src/lib/category-context.tsx [app-ssr] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, x: __turbopack_external_require__, y: __turbopack_external_import__, z: __turbopack_require_stub__ } = __turbopack_context__;
{
__turbopack_esm__({
    "CategoryProvider": (()=>CategoryProvider),
    "useCategoryContext": (()=>useCategoryContext)
});
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/src/lib/api.ts [app-ssr] (ecmascript)");
'use client';
;
;
;
const defaultCategoryContext = {
    categories: [],
    loading: true,
    error: null,
    refreshCategories: ()=>{},
    getCategoryInfo: ()=>null
};
const CategoryContext = /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["createContext"])(defaultCategoryContext);
function useCategoryContext() {
    return (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useContext"])(CategoryContext);
}
function CategoryProvider({ children }) {
    const [categories, setCategories] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])([]);
    const [loading, setLoading] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(true);
    const [error, setError] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(null);
    const [refreshKey, setRefreshKey] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(0);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        async function fetchCategories() {
            try {
                setLoading(true);
                const response = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["getCategoriesApi"])();
                // Sort categories by priority (lower number = higher priority)
                const sortedCategories = response.data.sort((a, b)=>a.priority - b.priority);
                setCategories(sortedCategories);
                setError(null);
            } catch (error) {
                console.error('Error fetching categories:', error);
                setError('Failed to load categories');
            } finally{
                setLoading(false);
            }
        }
        fetchCategories();
    }, [
        refreshKey
    ]);
    // Helper function to get category display information
    const getCategoryInfo = (categoryName)=>{
        if (!categoryName) return null;
        // Normalize category name for consistent lookup
        const normalizedCategoryName = categoryName.toLowerCase();
        // Find the category in our list by case-insensitive name matching
        const category = categories.find((c)=>c.name.toLowerCase() === normalizedCategoryName);
        if (category) {
            // Map category name to tailwind classes for styling
            const colorMap = {
                'personal': 'bg-indigo-100 text-indigo-800 border border-indigo-200',
                'updates': 'bg-purple-100 text-purple-800 border border-purple-200',
                'social': 'bg-green-100 text-green-800 border border-green-200',
                'promotional': 'bg-orange-100 text-orange-800 border border-orange-200',
                'promotions': 'bg-orange-100 text-orange-800 border border-orange-200',
                'forums': 'bg-teal-100 text-teal-800 border border-teal-200',
                'primary': 'bg-blue-100 text-blue-800 border border-blue-200',
                'important': 'bg-yellow-100 text-yellow-800 border border-yellow-200',
                'trash': 'bg-red-100 text-red-800 border border-red-200',
                'archive': 'bg-gray-100 text-gray-800 border border-gray-200',
                // Defaults for other categories
                'default': 'bg-gray-100 text-gray-800 border border-gray-200'
            };
            return {
                display_name: category.display_name,
                color: colorMap[category.name.toLowerCase()] || colorMap.default,
                description: category.description
            };
        }
        // Default styles if category not found
        const defaultStyles = {
            'primary': {
                display_name: 'Primary',
                color: 'bg-blue-100 text-blue-800 border border-blue-200',
                description: null
            },
            'important': {
                display_name: 'Important',
                color: 'bg-yellow-100 text-yellow-800 border border-yellow-200',
                description: null
            },
            'trash': {
                display_name: 'Trash',
                color: 'bg-red-100 text-red-800 border border-red-200',
                description: null
            },
            'archive': {
                display_name: 'Archive',
                color: 'bg-gray-100 text-gray-800 border border-gray-200',
                description: null
            }
        };
        return defaultStyles[normalizedCategoryName] || null;
    };
    const refreshCategories = ()=>{
        setRefreshKey((prev)=>prev + 1);
    };
    const value = {
        categories,
        loading,
        error,
        refreshCategories,
        getCategoryInfo
    };
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(CategoryContext.Provider, {
        value: value,
        children: children
    }, void 0, false, {
        fileName: "[project]/src/lib/category-context.tsx",
        lineNumber: 134,
        columnNumber: 5
    }, this);
}
}}),
"[project]/src/components/layout/main-layout.tsx [app-ssr] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, x: __turbopack_external_require__, y: __turbopack_external_import__, z: __turbopack_require_stub__ } = __turbopack_context__;
{
__turbopack_esm__({
    "EMAIL_SYNC_COMPLETED_EVENT": (()=>EMAIL_SYNC_COMPLETED_EVENT),
    "default": (()=>MainLayout)
});
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/next/navigation.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/next/dist/client/app-dir/link.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$auth$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/src/lib/auth.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/src/lib/api.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$category$2d$context$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/src/lib/category-context.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$hot$2d$toast$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/react-hot-toast/dist/index.mjs [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$InboxIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__InboxIcon$3e$__ = __turbopack_import__("[project]/node_modules/@heroicons/react/24/outline/esm/InboxIcon.js [app-ssr] (ecmascript) <export default as InboxIcon>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$StarIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__StarIcon$3e$__ = __turbopack_import__("[project]/node_modules/@heroicons/react/24/outline/esm/StarIcon.js [app-ssr] (ecmascript) <export default as StarIcon>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$UserGroupIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__UserGroupIcon$3e$__ = __turbopack_import__("[project]/node_modules/@heroicons/react/24/outline/esm/UserGroupIcon.js [app-ssr] (ecmascript) <export default as UserGroupIcon>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$MegaphoneIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__MegaphoneIcon$3e$__ = __turbopack_import__("[project]/node_modules/@heroicons/react/24/outline/esm/MegaphoneIcon.js [app-ssr] (ecmascript) <export default as MegaphoneIcon>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$BellAlertIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__BellAlertIcon$3e$__ = __turbopack_import__("[project]/node_modules/@heroicons/react/24/outline/esm/BellAlertIcon.js [app-ssr] (ecmascript) <export default as BellAlertIcon>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$TagIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__TagIcon$3e$__ = __turbopack_import__("[project]/node_modules/@heroicons/react/24/outline/esm/TagIcon.js [app-ssr] (ecmascript) <export default as TagIcon>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$NewspaperIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__NewspaperIcon$3e$__ = __turbopack_import__("[project]/node_modules/@heroicons/react/24/outline/esm/NewspaperIcon.js [app-ssr] (ecmascript) <export default as NewspaperIcon>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$ChatBubbleLeftRightIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ChatBubbleLeftRightIcon$3e$__ = __turbopack_import__("[project]/node_modules/@heroicons/react/24/outline/esm/ChatBubbleLeftRightIcon.js [app-ssr] (ecmascript) <export default as ChatBubbleLeftRightIcon>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$ArrowPathIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ArrowPathIcon$3e$__ = __turbopack_import__("[project]/node_modules/@heroicons/react/24/outline/esm/ArrowPathIcon.js [app-ssr] (ecmascript) <export default as ArrowPathIcon>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$TrashIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__TrashIcon$3e$__ = __turbopack_import__("[project]/node_modules/@heroicons/react/24/outline/esm/TrashIcon.js [app-ssr] (ecmascript) <export default as TrashIcon>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$HomeIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__HomeIcon$3e$__ = __turbopack_import__("[project]/node_modules/@heroicons/react/24/outline/esm/HomeIcon.js [app-ssr] (ecmascript) <export default as HomeIcon>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$EnvelopeIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__EnvelopeIcon$3e$__ = __turbopack_import__("[project]/node_modules/@heroicons/react/24/outline/esm/EnvelopeIcon.js [app-ssr] (ecmascript) <export default as EnvelopeIcon>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$EnvelopeOpenIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__EnvelopeOpenIcon$3e$__ = __turbopack_import__("[project]/node_modules/@heroicons/react/24/outline/esm/EnvelopeOpenIcon.js [app-ssr] (ecmascript) <export default as EnvelopeOpenIcon>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$ChartBarIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ChartBarIcon$3e$__ = __turbopack_import__("[project]/node_modules/@heroicons/react/24/outline/esm/ChartBarIcon.js [app-ssr] (ecmascript) <export default as ChartBarIcon>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$Cog6ToothIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Cog6ToothIcon$3e$__ = __turbopack_import__("[project]/node_modules/@heroicons/react/24/outline/esm/Cog6ToothIcon.js [app-ssr] (ecmascript) <export default as Cog6ToothIcon>");
'use client';
;
;
;
;
;
;
;
;
;
// Fixed navigation items that aren't categories
const baseNavigation = [
    // Main Views
    {
        name: 'Dashboard',
        href: '/',
        icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$HomeIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__HomeIcon$3e$__["HomeIcon"],
        type: 'link',
        section: 'main'
    },
    {
        name: 'Inbox',
        href: '/emails?view=inbox',
        icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$InboxIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__InboxIcon$3e$__["InboxIcon"],
        type: 'link',
        section: 'main'
    },
    {
        name: 'All Mail',
        href: '/emails',
        icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$EnvelopeIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__EnvelopeIcon$3e$__["EnvelopeIcon"],
        type: 'link',
        section: 'main'
    },
    // Email Status
    {
        name: 'Unread',
        href: '/emails?status=unread',
        icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$EnvelopeIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__EnvelopeIcon$3e$__["EnvelopeIcon"],
        type: 'link',
        section: 'filters'
    },
    {
        name: 'Read',
        href: '/emails?status=read',
        icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$EnvelopeOpenIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__EnvelopeOpenIcon$3e$__["EnvelopeOpenIcon"],
        type: 'link',
        section: 'filters'
    },
    // Tools & Settings
    {
        name: 'Analytics',
        href: '/analytics',
        icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$ChartBarIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ChartBarIcon$3e$__["ChartBarIcon"],
        type: 'link',
        section: 'tools'
    },
    {
        name: 'Manage Categories',
        href: '/categories',
        icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$Cog6ToothIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Cog6ToothIcon$3e$__["Cog6ToothIcon"],
        type: 'link',
        section: 'tools'
    }
];
const EMAIL_SYNC_COMPLETED_EVENT = 'emailSyncCompleted';
// Add this new client component at the top level of the file, before the MainLayout function
function SyncButton({ handleSync, isSyncing }) {
    const [mounted, setMounted] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(false);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        setMounted(true);
    }, []);
    if (!mounted) return null;
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
        onClick: handleSync,
        disabled: isSyncing,
        className: `inline-flex items-center px-4 py-2 rounded-md text-sm font-medium shadow-sm ${isSyncing ? 'bg-blue-400 text-white cursor-not-allowed' : 'bg-blue-600 text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500'}`,
        type: "button",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("svg", {
                className: `-ml-1 mr-2 h-5 w-5 ${isSyncing ? 'animate-spin' : ''}`,
                xmlns: "http://www.w3.org/2000/svg",
                fill: "none",
                viewBox: "0 0 24 24",
                strokeWidth: "1.5",
                stroke: "currentColor",
                "aria-hidden": "true",
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("path", {
                    strokeLinecap: "round",
                    strokeLinejoin: "round",
                    d: "M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99"
                }, void 0, false, {
                    fileName: "[project]/src/components/layout/main-layout.tsx",
                    lineNumber: 87,
                    columnNumber: 9
                }, this)
            }, void 0, false, {
                fileName: "[project]/src/components/layout/main-layout.tsx",
                lineNumber: 78,
                columnNumber: 7
            }, this),
            isSyncing ? 'Syncing...' : 'Sync Emails'
        ]
    }, void 0, true, {
        fileName: "[project]/src/components/layout/main-layout.tsx",
        lineNumber: 68,
        columnNumber: 5
    }, this);
}
function GoogleLoginButton() {
    const [mounted, setMounted] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(false);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        setMounted(true);
    }, []);
    if (!mounted) return null;
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
        onClick: __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$auth$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["initiateGoogleLogin"],
        type: "button",
        className: "inline-flex items-center px-4 py-2 rounded-md text-sm font-medium shadow-sm bg-white text-gray-800 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 border border-gray-300",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("svg", {
                className: "-ml-1 mr-2 h-5 w-5",
                xmlns: "http://www.w3.org/2000/svg",
                viewBox: "0 0 48 48",
                "aria-hidden": "true",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("path", {
                        fill: "#EA4335",
                        d: "M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"
                    }, void 0, false, {
                        fileName: "[project]/src/components/layout/main-layout.tsx",
                        lineNumber: 119,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("path", {
                        fill: "#4285F4",
                        d: "M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"
                    }, void 0, false, {
                        fileName: "[project]/src/components/layout/main-layout.tsx",
                        lineNumber: 120,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("path", {
                        fill: "#FBBC05",
                        d: "M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"
                    }, void 0, false, {
                        fileName: "[project]/src/components/layout/main-layout.tsx",
                        lineNumber: 121,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("path", {
                        fill: "#34A853",
                        d: "M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"
                    }, void 0, false, {
                        fileName: "[project]/src/components/layout/main-layout.tsx",
                        lineNumber: 122,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/src/components/layout/main-layout.tsx",
                lineNumber: 113,
                columnNumber: 7
            }, this),
            "Sign in with Google"
        ]
    }, void 0, true, {
        fileName: "[project]/src/components/layout/main-layout.tsx",
        lineNumber: 108,
        columnNumber: 5
    }, this);
}
function LogoutButton({ handleLogout, isLoggingOut }) {
    const [mounted, setMounted] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(false);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        setMounted(true);
    }, []);
    if (!mounted) return null;
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
        onClick: handleLogout,
        disabled: isLoggingOut,
        type: "button",
        className: `inline-flex items-center px-4 py-2 rounded-md text-sm font-medium shadow-sm ${isLoggingOut ? 'bg-gray-400 cursor-not-allowed' : 'bg-red-600 hover:bg-red-700'} text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500`,
        children: isLoggingOut ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Fragment"], {
            children: [
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("svg", {
                    className: "animate-spin -ml-1 mr-2 h-5 w-5",
                    xmlns: "http://www.w3.org/2000/svg",
                    fill: "none",
                    viewBox: "0 0 24 24",
                    "aria-hidden": "true",
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("circle", {
                            className: "opacity-25",
                            cx: "12",
                            cy: "12",
                            r: "10",
                            stroke: "currentColor",
                            strokeWidth: "4"
                        }, void 0, false, {
                            fileName: "[project]/src/components/layout/main-layout.tsx",
                            lineNumber: 158,
                            columnNumber: 13
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("path", {
                            className: "opacity-75",
                            fill: "currentColor",
                            d: "M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                        }, void 0, false, {
                            fileName: "[project]/src/components/layout/main-layout.tsx",
                            lineNumber: 166,
                            columnNumber: 13
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/src/components/layout/main-layout.tsx",
                    lineNumber: 151,
                    columnNumber: 11
                }, this),
                "Logging out..."
            ]
        }, void 0, true) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Fragment"], {
            children: [
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("svg", {
                    className: "-ml-1 mr-2 h-5 w-5",
                    xmlns: "http://www.w3.org/2000/svg",
                    fill: "none",
                    viewBox: "0 0 24 24",
                    strokeWidth: "1.5",
                    stroke: "currentColor",
                    "aria-hidden": "true",
                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("path", {
                        strokeLinecap: "round",
                        strokeLinejoin: "round",
                        d: "M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15m3 0l3-3m0 0l-3-3m3 3H9"
                    }, void 0, false, {
                        fileName: "[project]/src/components/layout/main-layout.tsx",
                        lineNumber: 185,
                        columnNumber: 13
                    }, this)
                }, void 0, false, {
                    fileName: "[project]/src/components/layout/main-layout.tsx",
                    lineNumber: 176,
                    columnNumber: 11
                }, this),
                "Logout"
            ]
        }, void 0, true)
    }, void 0, false, {
        fileName: "[project]/src/components/layout/main-layout.tsx",
        lineNumber: 139,
        columnNumber: 5
    }, this);
}
function MainLayout({ children }) {
    const pathname = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["usePathname"])();
    const router = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useRouter"])();
    const [isSyncing, setIsSyncing] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(false);
    const [isLoggingOut, setIsLoggingOut] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(false);
    const [syncStatus, setSyncStatus] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(null);
    const [syncMessage, setSyncMessage] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])('');
    const [isAuthError, setIsAuthError] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(false);
    const [lastSyncTime, setLastSyncTime] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(null);
    // Use the CategoryContext instead of fetching categories directly
    const { categories, refreshCategories } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$category$2d$context$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useCategoryContext"])();
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        if (!(0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$auth$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["isAuthenticated"])()) {
            (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$auth$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["handleAuthError"])();
            return;
        }
    }, []);
    // Listen for email sync completion event to refresh categories
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        const handleSyncCompleted = ()=>{
            // Refresh categories when emails are synced
            refreshCategories();
        };
        // Add event listener
        window.addEventListener(EMAIL_SYNC_COMPLETED_EVENT, handleSyncCompleted);
        // Clean up
        return ()=>{
            window.removeEventListener(EMAIL_SYNC_COMPLETED_EVENT, handleSyncCompleted);
        };
    }, [
        refreshCategories
    ]);
    const handleSync = async ()=>{
        if (isSyncing || !(0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$auth$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["isAuthenticated"])()) return;
        try {
            setIsSyncing(true);
            setSyncMessage('Syncing emails...');
            setSyncStatus(null);
            const response = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["triggerEmailSync"])();
            // Check for success based on the response structure
            if (response.success || response.status === 'success') {
                setSyncStatus('success');
                // Handle the case when no new emails are found
                if (response.sync_count === 0) {
                    setSyncMessage('No new emails to sync.');
                } else {
                    // Extract only the count of new emails, not including checkpoint emails
                    const newEmailCount = response.new_email_count || response.sync_count || 0;
                    setSyncMessage(response.message || `Sync completed! ${newEmailCount} new emails processed.`);
                }
                // Dispatch a custom event to notify components that sync is complete
                window.dispatchEvent(new CustomEvent(EMAIL_SYNC_COMPLETED_EVENT, {
                    detail: {
                        syncCount: response.sync_count || 0
                    }
                }));
                // Clear the success message after 3 seconds
                setTimeout(()=>{
                    setSyncMessage('');
                    setSyncStatus(null);
                }, 3000);
            } else if (response.status === 'warning' && response.message?.includes('No changes detected')) {
                // Handle the "No changes detected" case with a more user-friendly message
                setSyncStatus('success');
                setSyncMessage('Your inbox is up to date! No new changes found.');
                // Clear the message after 3 seconds
                setTimeout(()=>{
                    setSyncMessage('');
                    setSyncStatus(null);
                }, 3000);
            } else {
                setSyncStatus('error');
                setSyncMessage(`Sync failed: ${response.message}`);
                // Clear the error message after 5 seconds
                setTimeout(()=>{
                    setSyncMessage('');
                    setSyncStatus(null);
                }, 5000);
            }
        } catch (error) {
            console.error('Error syncing emails:', error);
            setSyncStatus('error');
            // Check if it's an auth error
            if (error instanceof Error && (error.message.includes('No authentication token found') || error.message.includes('Authentication failed'))) {
                setIsAuthError(true);
                (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$auth$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["handleAuthError"])();
                setSyncMessage('Authentication failed. Please log in again.');
            } else {
                setSyncMessage('Failed to sync emails. Please try again.');
            }
            // Clear the error message after 5 seconds
            setTimeout(()=>{
                setSyncMessage('');
                setSyncStatus(null);
            }, 5000);
        } finally{
            setIsSyncing(false);
        }
    };
    const handleLogout = async ()=>{
        try {
            setIsLoggingOut(true);
            await (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$auth$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["logout"])();
            // Show success message
            __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$hot$2d$toast$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["toast"].success('Successfully logged out');
            // Redirect to login page with a clean URL
            router.push('/');
        } catch (error) {
            console.error('Logout error:', error);
            __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$hot$2d$toast$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["toast"].error('Failed to logout. Please try again.');
        } finally{
            setIsLoggingOut(false);
        }
    };
    // Create mapping of icons that can be used for categories
    const getCategoryIcon = (categoryName)=>{
        const iconMap = {
            'primary': __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$InboxIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__InboxIcon$3e$__["InboxIcon"],
            'important': __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$StarIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__StarIcon$3e$__["StarIcon"],
            'social': __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$UserGroupIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__UserGroupIcon$3e$__["UserGroupIcon"],
            'promotional': __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$MegaphoneIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__MegaphoneIcon$3e$__["MegaphoneIcon"],
            'updates': __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$BellAlertIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__BellAlertIcon$3e$__["BellAlertIcon"],
            'personal': __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$TagIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__TagIcon$3e$__["TagIcon"],
            'newsletters': __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$NewspaperIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__NewspaperIcon$3e$__["NewspaperIcon"],
            'forums': __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$ChatBubbleLeftRightIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ChatBubbleLeftRightIcon$3e$__["ChatBubbleLeftRightIcon"],
            'archive': __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$ArrowPathIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ArrowPathIcon$3e$__["ArrowPathIcon"],
            'trash': __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$TrashIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__TrashIcon$3e$__["TrashIcon"]
        };
        return iconMap[categoryName.toLowerCase()] || __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$TagIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__TagIcon$3e$__["TagIcon"]; // Default to TagIcon
    };
    // Create storage section with Archive and Trash
    const storageCategories = categories.filter((cat)=>cat.name.toLowerCase() === 'archive' || cat.name.toLowerCase() === 'trash');
    // Create regular categories (excluding storage categories)
    const regularCategories = categories.filter((cat)=>cat.name.toLowerCase() !== 'archive' && cat.name.toLowerCase() !== 'trash');
    // Group navigation items by section
    const mainNavItems = baseNavigation.filter((item)=>item.section === 'main');
    const filterNavItems = baseNavigation.filter((item)=>item.section === 'filters');
    const toolNavItems = baseNavigation.filter((item)=>item.section === 'tools');
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "min-h-screen bg-gray-50",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg flex flex-col",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "flex h-16 items-center px-6 border-b border-gray-200",
                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"], {
                            href: "/",
                            className: "flex items-center space-x-2",
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    className: "text-2xl font-bold text-indigo-600",
                                    children: "EA"
                                }, void 0, false, {
                                    fileName: "[project]/src/components/layout/main-layout.tsx",
                                    lineNumber: 368,
                                    columnNumber: 13
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                    className: "text-lg font-semibold text-gray-900",
                                    children: "EmailAgent"
                                }, void 0, false, {
                                    fileName: "[project]/src/components/layout/main-layout.tsx",
                                    lineNumber: 369,
                                    columnNumber: 13
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/src/components/layout/main-layout.tsx",
                            lineNumber: 367,
                            columnNumber: 11
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/src/components/layout/main-layout.tsx",
                        lineNumber: 366,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("nav", {
                        className: "flex-1 overflow-y-auto py-4 px-3",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "mb-6",
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        className: "px-3 mb-2 text-xs font-semibold text-gray-500 uppercase tracking-wider",
                                        children: "Main"
                                    }, void 0, false, {
                                        fileName: "[project]/src/components/layout/main-layout.tsx",
                                        lineNumber: 377,
                                        columnNumber: 13
                                    }, this),
                                    mainNavItems.map((item)=>{
                                        if (!item.href || !item.icon) return null;
                                        const isActive = pathname === item.href || pathname && item.href && pathname.startsWith('/emails') && item.href.startsWith('/emails') && (// Match category parameter
                                        new URLSearchParams(item.href.split('?')[1]).get('category') === new URLSearchParams(pathname.split('?')[1]).get('category') || new URLSearchParams(item.href.split('?')[1]).get('view') === new URLSearchParams(pathname.split('?')[1]).get('view') || item.href === '/emails' && !pathname.includes('?') && !pathname.includes('/deleted'));
                                        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"], {
                                            href: item.href,
                                            className: `group flex items-center px-3 py-2 my-1 text-sm font-medium rounded-md ${isActive ? 'bg-indigo-50 text-indigo-600' : 'text-gray-700 hover:bg-gray-50'}`,
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(item.icon, {
                                                    className: `mr-3 h-5 w-5 flex-shrink-0 ${isActive ? 'text-indigo-600' : 'text-gray-400 group-hover:text-gray-500'}`,
                                                    "aria-hidden": "true"
                                                }, void 0, false, {
                                                    fileName: "[project]/src/components/layout/main-layout.tsx",
                                                    lineNumber: 408,
                                                    columnNumber: 19
                                                }, this),
                                                item.name
                                            ]
                                        }, item.name, true, {
                                            fileName: "[project]/src/components/layout/main-layout.tsx",
                                            lineNumber: 399,
                                            columnNumber: 17
                                        }, this);
                                    })
                                ]
                            }, void 0, true, {
                                fileName: "[project]/src/components/layout/main-layout.tsx",
                                lineNumber: 376,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "mb-6",
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        className: "px-3 mb-2 text-xs font-semibold text-gray-500 uppercase tracking-wider",
                                        children: "Filters"
                                    }, void 0, false, {
                                        fileName: "[project]/src/components/layout/main-layout.tsx",
                                        lineNumber: 422,
                                        columnNumber: 13
                                    }, this),
                                    filterNavItems.map((item)=>{
                                        if (!item.href || !item.icon) return null;
                                        const isActive = pathname === item.href || pathname && item.href && pathname.startsWith('/emails') && item.href.startsWith('/emails') && new URLSearchParams(item.href.split('?')[1]).get('status') === new URLSearchParams(pathname.split('?')[1]).get('status');
                                        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"], {
                                            href: item.href,
                                            className: `group flex items-center px-3 py-2 my-1 text-sm font-medium rounded-md ${isActive ? 'bg-indigo-50 text-indigo-600' : 'text-gray-700 hover:bg-gray-50'}`,
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(item.icon, {
                                                    className: `mr-3 h-5 w-5 flex-shrink-0 ${isActive ? 'text-indigo-600' : 'text-gray-400 group-hover:text-gray-500'}`,
                                                    "aria-hidden": "true"
                                                }, void 0, false, {
                                                    fileName: "[project]/src/components/layout/main-layout.tsx",
                                                    lineNumber: 443,
                                                    columnNumber: 19
                                                }, this),
                                                item.name
                                            ]
                                        }, item.name, true, {
                                            fileName: "[project]/src/components/layout/main-layout.tsx",
                                            lineNumber: 434,
                                            columnNumber: 17
                                        }, this);
                                    })
                                ]
                            }, void 0, true, {
                                fileName: "[project]/src/components/layout/main-layout.tsx",
                                lineNumber: 421,
                                columnNumber: 11
                            }, this),
                            regularCategories.length > 0 && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "mb-6",
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        className: "px-3 mb-2 text-xs font-semibold text-gray-500 uppercase tracking-wider",
                                        children: "Categories"
                                    }, void 0, false, {
                                        fileName: "[project]/src/components/layout/main-layout.tsx",
                                        lineNumber: 458,
                                        columnNumber: 15
                                    }, this),
                                    regularCategories.map((category)=>{
                                        const href = `/emails?category=${category.name.toLowerCase()}`;
                                        const Icon = getCategoryIcon(category.name);
                                        const isActive = pathname && pathname.startsWith('/emails') && new URLSearchParams(pathname.split('?')[1]).get('category') === category.name.toLowerCase();
                                        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"], {
                                            href: href,
                                            className: `group flex items-center px-3 py-2 my-1 text-sm font-medium rounded-md ${isActive ? 'bg-indigo-50 text-indigo-600' : 'text-gray-700 hover:bg-gray-50'}`,
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(Icon, {
                                                    className: `mr-3 h-5 w-5 flex-shrink-0 ${isActive ? 'text-indigo-600' : 'text-gray-400 group-hover:text-gray-500'}`,
                                                    "aria-hidden": "true"
                                                }, void 0, false, {
                                                    fileName: "[project]/src/components/layout/main-layout.tsx",
                                                    lineNumber: 477,
                                                    columnNumber: 21
                                                }, this),
                                                category.display_name
                                            ]
                                        }, category.name, true, {
                                            fileName: "[project]/src/components/layout/main-layout.tsx",
                                            lineNumber: 468,
                                            columnNumber: 19
                                        }, this);
                                    })
                                ]
                            }, void 0, true, {
                                fileName: "[project]/src/components/layout/main-layout.tsx",
                                lineNumber: 457,
                                columnNumber: 13
                            }, this),
                            storageCategories.length > 0 && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "mb-6",
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        className: "px-3 mb-2 text-xs font-semibold text-gray-500 uppercase tracking-wider",
                                        children: "Storage"
                                    }, void 0, false, {
                                        fileName: "[project]/src/components/layout/main-layout.tsx",
                                        lineNumber: 493,
                                        columnNumber: 15
                                    }, this),
                                    storageCategories.map((category)=>{
                                        const href = category.name.toLowerCase() === 'trash' ? '/emails/deleted' : `/emails?category=${category.name.toLowerCase()}`;
                                        const Icon = getCategoryIcon(category.name);
                                        const isActive = category.name.toLowerCase() === 'trash' && pathname === '/emails/deleted' || pathname && pathname.startsWith('/emails') && new URLSearchParams(pathname.split('?')[1]).get('category') === category.name.toLowerCase();
                                        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"], {
                                            href: href,
                                            className: `group flex items-center px-3 py-2 my-1 text-sm font-medium rounded-md ${isActive ? 'bg-indigo-50 text-indigo-600' : 'text-gray-700 hover:bg-gray-50'}`,
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(Icon, {
                                                    className: `mr-3 h-5 w-5 flex-shrink-0 ${isActive ? 'text-indigo-600' : 'text-gray-400 group-hover:text-gray-500'}`,
                                                    "aria-hidden": "true"
                                                }, void 0, false, {
                                                    fileName: "[project]/src/components/layout/main-layout.tsx",
                                                    lineNumber: 515,
                                                    columnNumber: 21
                                                }, this),
                                                category.display_name
                                            ]
                                        }, category.name, true, {
                                            fileName: "[project]/src/components/layout/main-layout.tsx",
                                            lineNumber: 506,
                                            columnNumber: 19
                                        }, this);
                                    })
                                ]
                            }, void 0, true, {
                                fileName: "[project]/src/components/layout/main-layout.tsx",
                                lineNumber: 492,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "mb-6",
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        className: "px-3 mb-2 text-xs font-semibold text-gray-500 uppercase tracking-wider",
                                        children: "Tools"
                                    }, void 0, false, {
                                        fileName: "[project]/src/components/layout/main-layout.tsx",
                                        lineNumber: 530,
                                        columnNumber: 13
                                    }, this),
                                    toolNavItems.map((item)=>{
                                        if (!item.href || !item.icon) return null;
                                        const isActive = pathname === item.href;
                                        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"], {
                                            href: item.href,
                                            className: `group flex items-center px-3 py-2 my-1 text-sm font-medium rounded-md ${isActive ? 'bg-indigo-50 text-indigo-600' : 'text-gray-700 hover:bg-gray-50'}`,
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(item.icon, {
                                                    className: `mr-3 h-5 w-5 flex-shrink-0 ${isActive ? 'text-indigo-600' : 'text-gray-400 group-hover:text-gray-500'}`,
                                                    "aria-hidden": "true"
                                                }, void 0, false, {
                                                    fileName: "[project]/src/components/layout/main-layout.tsx",
                                                    lineNumber: 548,
                                                    columnNumber: 19
                                                }, this),
                                                item.name
                                            ]
                                        }, item.name, true, {
                                            fileName: "[project]/src/components/layout/main-layout.tsx",
                                            lineNumber: 539,
                                            columnNumber: 17
                                        }, this);
                                    })
                                ]
                            }, void 0, true, {
                                fileName: "[project]/src/components/layout/main-layout.tsx",
                                lineNumber: 529,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/src/components/layout/main-layout.tsx",
                        lineNumber: 374,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/src/components/layout/main-layout.tsx",
                lineNumber: 365,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "pl-64",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("header", {
                        className: "bg-white shadow-sm",
                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "flex h-16 items-center justify-between px-6",
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("h2", {
                                    className: "text-lg font-medium text-gray-900"
                                }, void 0, false, {
                                    fileName: "[project]/src/components/layout/main-layout.tsx",
                                    lineNumber: 567,
                                    columnNumber: 13
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    className: "flex items-center space-x-3",
                                    children: [
                                        syncMessage && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                            className: `text-sm font-medium px-3 py-1 rounded-md ${syncStatus === 'error' ? 'text-red-800 bg-red-100' : syncStatus === 'success' ? 'text-green-800 bg-green-100' : 'text-gray-800 bg-gray-100'}`,
                                            children: syncMessage
                                        }, void 0, false, {
                                            fileName: "[project]/src/components/layout/main-layout.tsx",
                                            lineNumber: 573,
                                            columnNumber: 17
                                        }, this),
                                        (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$auth$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["isAuthenticated"])() && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(SyncButton, {
                                            handleSync: handleSync,
                                            isSyncing: isSyncing
                                        }, void 0, false, {
                                            fileName: "[project]/src/components/layout/main-layout.tsx",
                                            lineNumber: 585,
                                            columnNumber: 17
                                        }, this),
                                        (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$auth$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["isAuthenticated"])() ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(LogoutButton, {
                                            handleLogout: handleLogout,
                                            isLoggingOut: isLoggingOut
                                        }, void 0, false, {
                                            fileName: "[project]/src/components/layout/main-layout.tsx",
                                            lineNumber: 589,
                                            columnNumber: 17
                                        }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(GoogleLoginButton, {}, void 0, false, {
                                            fileName: "[project]/src/components/layout/main-layout.tsx",
                                            lineNumber: 591,
                                            columnNumber: 17
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/src/components/layout/main-layout.tsx",
                                    lineNumber: 571,
                                    columnNumber: 13
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/src/components/layout/main-layout.tsx",
                            lineNumber: 566,
                            columnNumber: 11
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/src/components/layout/main-layout.tsx",
                        lineNumber: 565,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("main", {
                        className: "py-6 px-6",
                        children: children
                    }, void 0, false, {
                        fileName: "[project]/src/components/layout/main-layout.tsx",
                        lineNumber: 598,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/src/components/layout/main-layout.tsx",
                lineNumber: 563,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/src/components/layout/main-layout.tsx",
        lineNumber: 363,
        columnNumber: 5
    }, this);
}
}}),
"[project]/src/app/layout.tsx [app-rsc] (ecmascript, Next.js server component, client modules ssr)": ((__turbopack_context__) => {

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, t: __turbopack_require_real__ } = __turbopack_context__;
{
}}),

};

//# sourceMappingURL=%5Broot%20of%20the%20server%5D__c15625._.js.map