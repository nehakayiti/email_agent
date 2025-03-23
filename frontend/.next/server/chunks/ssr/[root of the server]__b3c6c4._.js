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
    window.location.href = `${"TURBOPACK compile-time value", "http://localhost:8000"}/auth/login`;
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
        const response = await fetch(`${("TURBOPACK compile-time value", "http://localhost:8000")}/auth/logout`, {
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
    "createCategory": (()=>createCategory),
    "deleteCategory": (()=>deleteCategory),
    "deleteEmail": (()=>deleteEmail),
    "fetchWithAuth": (()=>fetchWithAuth),
    "getCategoriesApi": (()=>getCategoriesApi),
    "getCategoryKeywords": (()=>getCategoryKeywords),
    "getCategorySenderRules": (()=>getCategorySenderRules),
    "getDbInsights": (()=>getDbInsights),
    "getDeletedEmails": (()=>getDeletedEmails),
    "getEmailById": (()=>getEmailById),
    "getEmails": (()=>getEmails),
    "getResponseTimeAnalytics": (()=>getResponseTimeAnalytics),
    "getSentimentAnalytics": (()=>getSentimentAnalytics),
    "getTopContacts": (()=>getTopContacts),
    "getTrashedEmails": (()=>getTrashedEmails),
    "getVolumeAnalytics": (()=>getVolumeAnalytics),
    "initializeCategories": (()=>initializeCategories),
    "reprocessAllEmails": (()=>reprocessAllEmails),
    "triggerEmailSync": (()=>triggerEmailSync),
    "updateEmailCategory": (()=>updateEmailCategory),
    "updateEmailLabels": (()=>updateEmailLabels)
});
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$auth$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/src/lib/auth.ts [app-ssr] (ecmascript)");
;
const API_URL = ("TURBOPACK compile-time value", "http://localhost:8000") || 'http://localhost:8000';
if ("TURBOPACK compile-time falsy", 0) {
    "TURBOPACK unreachable";
}
function isEmailArray(data) {
    return Array.isArray(data) && data.every((item)=>typeof item === 'object' && item !== null && 'id' in item && 'subject' in item && 'from_email' in item && 'received_at' in item);
}
function isEmailsResponse(data) {
    return typeof data === 'object' && data !== null && 'emails' in data && isEmailArray(data.emails) && 'pagination' in data && typeof data.pagination === 'object';
}
async function fetchWithAuth(endpoint, options = {}) {
    const token = (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$auth$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["getToken"])();
    if (!token) {
        console.log('No authentication token found');
        (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$auth$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["handleAuthError"])();
        throw new Error('No authentication token found');
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
                throw new Error('Authentication failed. Token expired. Redirecting to login...');
            }
            const errorData = await response.json().catch(()=>null);
            throw new Error(errorData?.detail || `API error: ${response.status} ${response.statusText}`);
        }
        const data = await response.json();
        console.log(`API response from ${endpoint}:`, data);
        return data;
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
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
    try {
        const timestamp = new Date().getTime();
        const response = await fetchWithAuth(`/emails/sync?t=${timestamp}&use_current_date=true`, {
            method: 'POST'
        });
        return response;
    } catch (error) {
        console.error('Error triggering email sync:', error);
        throw error;
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
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/next/dist/client/app-dir/link.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/next/navigation.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/src/lib/api.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$auth$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/src/lib/auth.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$HomeIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__HomeIcon$3e$__ = __turbopack_import__("[project]/node_modules/@heroicons/react/24/outline/esm/HomeIcon.js [app-ssr] (ecmascript) <export default as HomeIcon>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$InboxIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__InboxIcon$3e$__ = __turbopack_import__("[project]/node_modules/@heroicons/react/24/outline/esm/InboxIcon.js [app-ssr] (ecmascript) <export default as InboxIcon>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$ChartBarIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ChartBarIcon$3e$__ = __turbopack_import__("[project]/node_modules/@heroicons/react/24/outline/esm/ChartBarIcon.js [app-ssr] (ecmascript) <export default as ChartBarIcon>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$EnvelopeIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__EnvelopeIcon$3e$__ = __turbopack_import__("[project]/node_modules/@heroicons/react/24/outline/esm/EnvelopeIcon.js [app-ssr] (ecmascript) <export default as EnvelopeIcon>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$EnvelopeOpenIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__EnvelopeOpenIcon$3e$__ = __turbopack_import__("[project]/node_modules/@heroicons/react/24/outline/esm/EnvelopeOpenIcon.js [app-ssr] (ecmascript) <export default as EnvelopeOpenIcon>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$TagIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__TagIcon$3e$__ = __turbopack_import__("[project]/node_modules/@heroicons/react/24/outline/esm/TagIcon.js [app-ssr] (ecmascript) <export default as TagIcon>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$StarIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__StarIcon$3e$__ = __turbopack_import__("[project]/node_modules/@heroicons/react/24/outline/esm/StarIcon.js [app-ssr] (ecmascript) <export default as StarIcon>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$UserGroupIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__UserGroupIcon$3e$__ = __turbopack_import__("[project]/node_modules/@heroicons/react/24/outline/esm/UserGroupIcon.js [app-ssr] (ecmascript) <export default as UserGroupIcon>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$MegaphoneIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__MegaphoneIcon$3e$__ = __turbopack_import__("[project]/node_modules/@heroicons/react/24/outline/esm/MegaphoneIcon.js [app-ssr] (ecmascript) <export default as MegaphoneIcon>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$BellAlertIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__BellAlertIcon$3e$__ = __turbopack_import__("[project]/node_modules/@heroicons/react/24/outline/esm/BellAlertIcon.js [app-ssr] (ecmascript) <export default as BellAlertIcon>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$NewspaperIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__NewspaperIcon$3e$__ = __turbopack_import__("[project]/node_modules/@heroicons/react/24/outline/esm/NewspaperIcon.js [app-ssr] (ecmascript) <export default as NewspaperIcon>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$ChatBubbleLeftRightIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ChatBubbleLeftRightIcon$3e$__ = __turbopack_import__("[project]/node_modules/@heroicons/react/24/outline/esm/ChatBubbleLeftRightIcon.js [app-ssr] (ecmascript) <export default as ChatBubbleLeftRightIcon>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$ArrowPathIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ArrowPathIcon$3e$__ = __turbopack_import__("[project]/node_modules/@heroicons/react/24/outline/esm/ArrowPathIcon.js [app-ssr] (ecmascript) <export default as ArrowPathIcon>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$TrashIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__TrashIcon$3e$__ = __turbopack_import__("[project]/node_modules/@heroicons/react/24/outline/esm/TrashIcon.js [app-ssr] (ecmascript) <export default as TrashIcon>");
'use client';
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
        type: 'link'
    },
    {
        name: 'All Emails',
        href: '/emails',
        icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$InboxIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__InboxIcon$3e$__["InboxIcon"],
        type: 'link'
    },
    {
        name: 'Analytics',
        href: '/analytics',
        icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$ChartBarIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ChartBarIcon$3e$__["ChartBarIcon"],
        type: 'link'
    },
    // Email Status
    {
        type: 'divider',
        name: 'Status'
    },
    {
        name: 'Unread',
        href: '/emails?status=unread',
        icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$EnvelopeIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__EnvelopeIcon$3e$__["EnvelopeIcon"],
        type: 'link'
    },
    {
        name: 'Read',
        href: '/emails?status=read',
        icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$EnvelopeOpenIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__EnvelopeOpenIcon$3e$__["EnvelopeOpenIcon"],
        type: 'link'
    },
    // Category Management Link
    {
        type: 'divider',
        name: 'CATEGORIES'
    },
    {
        name: 'Manage Categories',
        href: '/categories',
        icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$TagIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__TagIcon$3e$__["TagIcon"],
        type: 'link'
    }
];
const EMAIL_SYNC_COMPLETED_EVENT = 'emailSyncCompleted';
function MainLayout({ children }) {
    const pathname = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["usePathname"])();
    const router = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useRouter"])();
    const [isSyncing, setIsSyncing] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(false);
    const [categories, setCategories] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])([]);
    const [syncStatus, setSyncStatus] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(null);
    const [syncMessage, setSyncMessage] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])('');
    const [isAuthError, setIsAuthError] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(false);
    const [lastSyncTime, setLastSyncTime] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(null);
    const [categoriesRefreshTrigger, setCategoriesRefreshTrigger] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(0);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        if (!(0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$auth$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["isAuthenticated"])()) {
            (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$auth$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["handleAuthError"])();
            return;
        }
        // Fetch categories directly from the API
        async function fetchCategories() {
            try {
                const response = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["getCategoriesApi"])();
                // Sort categories by priority (lower number = higher priority)
                const sortedCategories = response.data.sort((a, b)=>a.priority - b.priority);
                setCategories(sortedCategories);
            } catch (error) {
                console.error('Error fetching categories:', error);
            }
        }
        fetchCategories();
    }, [
        categoriesRefreshTrigger
    ]);
    // Listen for email sync completion event to refresh categories
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        const handleSyncCompleted = ()=>{
            // Refresh categories when emails are synced
            setCategoriesRefreshTrigger((prev)=>prev + 1);
        };
        // Add event listener
        window.addEventListener(EMAIL_SYNC_COMPLETED_EVENT, handleSyncCompleted);
        // Clean up
        return ()=>{
            window.removeEventListener(EMAIL_SYNC_COMPLETED_EVENT, handleSyncCompleted);
        };
    }, []);
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
    // Create navigation items with base items and categories from database
    const navigation = [
        ...baseNavigation,
        // Add all regular categories (sorted by priority)
        ...regularCategories.map((category)=>({
                name: category.display_name,
                href: `/emails?category=${category.name.toLowerCase()}`,
                icon: getCategoryIcon(category.name),
                type: 'category'
            })),
        // Add Storage divider if we have storage categories
        ...storageCategories.length > 0 ? [
            {
                type: 'divider',
                name: 'Storage'
            }
        ] : [],
        // Add storage categories
        ...storageCategories.map((category)=>({
                name: category.display_name,
                href: category.name.toLowerCase() === 'trash' ? '/emails/deleted' : `/emails?category=${category.name.toLowerCase()}`,
                icon: getCategoryIcon(category.name),
                type: 'category'
            }))
    ];
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "min-h-screen bg-gray-50",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "flex h-16 items-center px-6",
                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"], {
                            href: "/",
                            className: "flex items-center space-x-2",
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    className: "text-2xl font-bold text-indigo-600",
                                    children: "EA"
                                }, void 0, false, {
                                    fileName: "[project]/src/components/layout/main-layout.tsx",
                                    lineNumber: 228,
                                    columnNumber: 13
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                    className: "text-lg font-semibold text-gray-900",
                                    children: "EmailAgent"
                                }, void 0, false, {
                                    fileName: "[project]/src/components/layout/main-layout.tsx",
                                    lineNumber: 229,
                                    columnNumber: 13
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/src/components/layout/main-layout.tsx",
                            lineNumber: 227,
                            columnNumber: 11
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/src/components/layout/main-layout.tsx",
                        lineNumber: 226,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("nav", {
                        className: "mt-5 px-3",
                        children: navigation.map((item)=>{
                            if (item.type === 'divider') {
                                return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    className: "px-2 py-1.5 text-xs font-semibold text-gray-500 uppercase tracking-wider",
                                    children: item.name
                                }, item.name, false, {
                                    fileName: "[project]/src/components/layout/main-layout.tsx",
                                    lineNumber: 236,
                                    columnNumber: 17
                                }, this);
                            }
                            if (!item.href || !item.icon) return null;
                            const isActive = pathname === item.href || pathname && item.href && pathname.startsWith('/emails') && item.href.startsWith('/emails') && new URLSearchParams(item.href.split('?')[1]).get('category') === new URLSearchParams(pathname.split('?')[1]).get('category');
                            return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"], {
                                href: item.href,
                                className: `group flex items-center px-2.5 py-2 my-0.5 text-sm font-medium rounded-lg ${isActive ? 'bg-indigo-50 text-indigo-600' : 'text-gray-700 hover:bg-gray-50'}`,
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(item.icon, {
                                        className: `mr-2.5 h-5 w-5 flex-shrink-0 ${isActive ? 'text-indigo-600' : 'text-gray-400 group-hover:text-gray-500'}`,
                                        "aria-hidden": "true"
                                    }, void 0, false, {
                                        fileName: "[project]/src/components/layout/main-layout.tsx",
                                        lineNumber: 259,
                                        columnNumber: 17
                                    }, this),
                                    item.name
                                ]
                            }, item.name, true, {
                                fileName: "[project]/src/components/layout/main-layout.tsx",
                                lineNumber: 250,
                                columnNumber: 15
                            }, this);
                        })
                    }, void 0, false, {
                        fileName: "[project]/src/components/layout/main-layout.tsx",
                        lineNumber: 232,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/src/components/layout/main-layout.tsx",
                lineNumber: 225,
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
                                    lineNumber: 277,
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
                                            lineNumber: 283,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                            onClick: handleSync,
                                            disabled: isSyncing,
                                            className: `inline-flex items-center px-4 py-2 rounded-md text-sm font-medium shadow-sm ${isSyncing ? 'bg-blue-400 text-white cursor-not-allowed' : 'bg-blue-600 text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500'}`,
                                            "aria-label": "Sync emails",
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$heroicons$2f$react$2f$24$2f$outline$2f$esm$2f$ArrowPathIcon$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ArrowPathIcon$3e$__["ArrowPathIcon"], {
                                                    className: `-ml-1 mr-2 h-5 w-5 ${isSyncing ? 'animate-spin' : ''}`,
                                                    "aria-hidden": "true"
                                                }, void 0, false, {
                                                    fileName: "[project]/src/components/layout/main-layout.tsx",
                                                    lineNumber: 303,
                                                    columnNumber: 17
                                                }, this),
                                                isSyncing ? 'Syncing...' : 'Sync Emails'
                                            ]
                                        }, void 0, true, {
                                            fileName: "[project]/src/components/layout/main-layout.tsx",
                                            lineNumber: 293,
                                            columnNumber: 15
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/src/components/layout/main-layout.tsx",
                                    lineNumber: 281,
                                    columnNumber: 13
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/src/components/layout/main-layout.tsx",
                            lineNumber: 276,
                            columnNumber: 11
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/src/components/layout/main-layout.tsx",
                        lineNumber: 275,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("main", {
                        className: "py-6 px-6",
                        children: children
                    }, void 0, false, {
                        fileName: "[project]/src/components/layout/main-layout.tsx",
                        lineNumber: 314,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/src/components/layout/main-layout.tsx",
                lineNumber: 273,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/src/components/layout/main-layout.tsx",
        lineNumber: 223,
        columnNumber: 5
    }, this);
}
}}),
"[project]/src/app/layout.tsx [app-rsc] (ecmascript, Next.js server component, client modules ssr)": ((__turbopack_context__) => {

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, t: __turbopack_require_real__ } = __turbopack_context__;
{
}}),

};

//# sourceMappingURL=%5Broot%20of%20the%20server%5D__b3c6c4._.js.map