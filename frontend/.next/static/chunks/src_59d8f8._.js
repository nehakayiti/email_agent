(globalThis.TURBOPACK = globalThis.TURBOPACK || []).push(["static/chunks/src_59d8f8._.js", {

"[project]/src/components/ui/search-input.tsx [app-client] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, k: __turbopack_refresh__, m: module, z: __turbopack_require_stub__ } = __turbopack_context__;
{
__turbopack_esm__({
    "SearchInput": (()=>SearchInput)
});
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
;
function SearchInput({ value, onChange, placeholder = 'Search...', className = '' }) {
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: `relative ${className}`,
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none",
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("svg", {
                    className: "h-5 w-5 text-gray-400",
                    xmlns: "http://www.w3.org/2000/svg",
                    viewBox: "0 0 20 20",
                    fill: "currentColor",
                    "aria-hidden": "true",
                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("path", {
                        fillRule: "evenodd",
                        d: "M9 3.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11zM2 9a7 7 0 1112.452 4.391l3.328 3.329a.75.75 0 11-1.06 1.06l-3.329-3.328A7 7 0 012 9z",
                        clipRule: "evenodd"
                    }, void 0, false, {
                        fileName: "[project]/src/components/ui/search-input.tsx",
                        lineNumber: 19,
                        columnNumber: 11
                    }, this)
                }, void 0, false, {
                    fileName: "[project]/src/components/ui/search-input.tsx",
                    lineNumber: 12,
                    columnNumber: 9
                }, this)
            }, void 0, false, {
                fileName: "[project]/src/components/ui/search-input.tsx",
                lineNumber: 11,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                type: "text",
                value: value,
                onChange: (e)=>onChange(e.target.value),
                className: "block w-full rounded-md border border-gray-300 bg-white pl-10 pr-3 py-2.5 text-sm shadow-sm placeholder:text-gray-500  focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 transition-colors duration-150",
                placeholder: placeholder
            }, void 0, false, {
                fileName: "[project]/src/components/ui/search-input.tsx",
                lineNumber: 26,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/src/components/ui/search-input.tsx",
        lineNumber: 10,
        columnNumber: 5
    }, this);
}
_c = SearchInput;
var _c;
__turbopack_refresh__.register(_c, "SearchInput");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_refresh__.registerExports(module, globalThis.$RefreshHelpers$);
}
}}),
"[project]/src/utils/date-utils.ts [app-client] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, k: __turbopack_refresh__, m: module, z: __turbopack_require_stub__ } = __turbopack_context__;
{
__turbopack_esm__({
    "formatRelativeTime": (()=>formatRelativeTime)
});
function formatRelativeTime(date) {
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);
    // Less than a minute
    if (diffInSeconds < 60) {
        return 'just now';
    }
    // Less than an hour
    const diffInMinutes = Math.floor(diffInSeconds / 60);
    if (diffInMinutes < 60) {
        return `${diffInMinutes}m ago`;
    }
    // Less than a day
    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) {
        return `${diffInHours}h ago`;
    }
    // Less than a week
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 7) {
        return `${diffInDays}d ago`;
    }
    // More than a week - format as date
    const options = {
        month: 'short',
        day: 'numeric'
    };
    // Add year if not current year
    if (date.getFullYear() !== now.getFullYear()) {
        options.year = 'numeric';
    }
    return date.toLocaleDateString('en-US', options);
}
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_refresh__.registerExports(module, globalThis.$RefreshHelpers$);
}
}}),
"[project]/src/components/ui/email-label.tsx [app-client] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, k: __turbopack_refresh__, m: module, z: __turbopack_require_stub__ } = __turbopack_context__;
{
__turbopack_esm__({
    "EmailLabel": (()=>EmailLabel),
    "getDisplayLabel": (()=>getDisplayLabel),
    "getLabelStyle": (()=>getLabelStyle),
    "mapLabelsToComponents": (()=>mapLabelsToComponents)
});
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$category$2d$context$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/src/lib/category-context.tsx [app-client] (ecmascript)");
;
var _s = __turbopack_refresh__.signature();
'use client';
;
function getDisplayLabel(label) {
    // First check if it's a category label (those should be handled by the category context)
    if (label.startsWith('CATEGORY_') || label === 'PRIMARY') {
        return ''; // This will be handled by getCategoryInfo in components
    }
    // For non-category labels, use this mapping
    const labelMap = {
        'INBOX': 'Inbox',
        'UNREAD': 'Unread',
        'TRASH': 'Trash',
        'IMPORTANT': '★',
        'ARCHIVE': 'Archive'
    };
    return labelMap[label] || label;
}
function getLabelStyle(label) {
    // If it's a category label, this will be handled by the category context elsewhere
    if (label.startsWith('CATEGORY_') || label === 'PRIMARY') {
        return '';
    }
    // Define different background and text colors for different labels
    switch(label.toUpperCase()){
        case 'INBOX':
            return 'bg-blue-100 text-blue-800 border border-blue-200';
        case 'UNREAD':
            return 'bg-yellow-100 text-yellow-800 border border-yellow-200';
        case 'TRASH':
            return 'bg-red-100 text-red-800 border border-red-200';
        case 'IMPORTANT':
            return 'bg-amber-100 text-amber-800 border border-amber-200';
        case 'ARCHIVE':
            return 'bg-gray-100 text-gray-800 border border-gray-200';
        default:
            return 'bg-gray-100 text-gray-800 border border-gray-200';
    }
}
function EmailLabel({ label, className = '', variant = 'default', showPrefix = true }) {
    _s();
    const { getCategoryInfo } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$category$2d$context$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCategoryContext"])();
    // For category labels, get info from the context
    const isCategoryLabel = label.startsWith('CATEGORY_') || label === 'PRIMARY';
    const categoryInfo = isCategoryLabel ? getCategoryInfo(label) : null;
    // If this is a category label and we have category info, use that
    if (isCategoryLabel && categoryInfo) {
        const baseClasses = variant === 'compact' ? 'px-2 py-0.5 text-xs font-medium rounded-full' : 'px-2.5 py-0.5 text-xs font-medium rounded-full';
        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
            className: `${baseClasses} ${categoryInfo.color} ${className}`,
            children: [
                showPrefix && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                    className: "mr-1 opacity-70",
                    children: "Category:"
                }, void 0, false, {
                    fileName: "[project]/src/components/ui/email-label.tsx",
                    lineNumber: 78,
                    columnNumber: 24
                }, this),
                categoryInfo.display_name
            ]
        }, void 0, true, {
            fileName: "[project]/src/components/ui/email-label.tsx",
            lineNumber: 77,
            columnNumber: 7
        }, this);
    }
    // For non-category labels, use the original logic
    const displayLabel = getDisplayLabel(label);
    const style = getLabelStyle(label);
    const isImportant = label.toUpperCase() === 'IMPORTANT';
    // For important label, show just the star
    if (isImportant) {
        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
            className: `inline-flex items-center text-amber-500 ${className}`,
            title: "Important",
            children: displayLabel
        }, void 0, false, {
            fileName: "[project]/src/components/ui/email-label.tsx",
            lineNumber: 92,
            columnNumber: 7
        }, this);
    }
    // For compact variant, use smaller padding
    const baseClasses = variant === 'compact' ? 'px-2 py-0.5 text-xs font-medium rounded-full' : 'px-2.5 py-0.5 text-xs font-medium rounded-full';
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
        className: `${baseClasses} ${style} ${className}`,
        children: [
            showPrefix && !isImportant && label !== 'INBOX' && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                className: "mr-1 opacity-70",
                children: "Label:"
            }, void 0, false, {
                fileName: "[project]/src/components/ui/email-label.tsx",
                lineNumber: 105,
                columnNumber: 59
            }, this),
            displayLabel
        ]
    }, void 0, true, {
        fileName: "[project]/src/components/ui/email-label.tsx",
        lineNumber: 104,
        columnNumber: 5
    }, this);
}
_s(EmailLabel, "C1GK9M7y3zkfMrMRisXtSJb/J/0=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$category$2d$context$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCategoryContext"]
    ];
});
_c = EmailLabel;
function mapLabelsToComponents(labels, options = {}) {
    const { showSystem = false, variant = 'default', includeCategoryLabels = false, showPrefix = true } = options;
    if (!labels || labels.length === 0) return [];
    // System labels that shouldn't be displayed
    const systemLabels = [
        'EA_NEEDS_LABEL_UPDATE',
        'SENT',
        'DRAFT'
    ];
    // Important label should always be first if present
    const sortedLabels = [
        ...labels
    ].sort((a, b)=>{
        if (a === 'IMPORTANT') return -1;
        if (b === 'IMPORTANT') return 1;
        return 0;
    });
    return sortedLabels.filter((label)=>{
        if (!showSystem && systemLabels.includes(label)) return false;
        // Don't show category labels here unless explicitly requested
        if (!includeCategoryLabels && (label.startsWith('CATEGORY_') || label === 'PRIMARY')) return false;
        return true;
    }).map((label)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(EmailLabel, {
            label: label,
            variant: variant,
            showPrefix: showPrefix
        }, label, false, {
            fileName: "[project]/src/components/ui/email-label.tsx",
            lineNumber: 145,
            columnNumber: 7
        }, this));
}
var _c;
__turbopack_refresh__.register(_c, "EmailLabel");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_refresh__.registerExports(module, globalThis.$RefreshHelpers$);
}
}}),
"[project]/src/utils/toast-config.ts [app-client] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, k: __turbopack_refresh__, m: module, z: __turbopack_require_stub__ } = __turbopack_context__;
{
// Toast configuration settings for consistent behavior across the application
__turbopack_esm__({
    "defaultToastOptions": (()=>defaultToastOptions),
    "dismissAllToasts": (()=>dismissAllToasts),
    "showErrorToast": (()=>showErrorToast),
    "showLoadingToast": (()=>showLoadingToast),
    "showSuccessToast": (()=>showSuccessToast)
});
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$hot$2d$toast$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/react-hot-toast/dist/index.mjs [app-client] (ecmascript)");
;
const defaultToastOptions = {
    duration: 6000,
    position: 'top-right'
};
const showSuccessToast = (message, options)=>{
    return __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$hot$2d$toast$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["toast"].success(message, {
        ...defaultToastOptions,
        ...options
    });
};
const showErrorToast = (message, options)=>{
    return __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$hot$2d$toast$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["toast"].error(message, {
        ...defaultToastOptions,
        ...options
    });
};
const showLoadingToast = (message, options)=>{
    return __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$hot$2d$toast$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["toast"].loading(message, {
        ...defaultToastOptions,
        ...options
    });
};
const dismissAllToasts = ()=>{
    __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$hot$2d$toast$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["toast"].dismiss();
};
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_refresh__.registerExports(module, globalThis.$RefreshHelpers$);
}
}}),
"[project]/src/components/ui/email-card.tsx [app-client] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, k: __turbopack_refresh__, m: module, z: __turbopack_require_stub__ } = __turbopack_context__;
{
__turbopack_esm__({
    "EmailCard": (()=>EmailCard)
});
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/next/dist/client/app-dir/link.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/src/lib/api.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$utils$2f$date$2d$utils$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/src/utils/date-utils.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$ui$2f$email$2d$label$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/src/components/ui/email-label.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$hot$2d$toast$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/react-hot-toast/dist/index.mjs [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$utils$2f$toast$2d$config$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/src/utils/toast-config.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$category$2d$context$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/src/lib/category-context.tsx [app-client] (ecmascript)");
;
var _s = __turbopack_refresh__.signature();
;
;
;
;
;
;
;
;
// Filter out system labels and get the primary category label for display
function getPrimaryDisplayLabel(labels) {
    if (!labels || labels.length === 0) return null;
    // Priority order for display
    const categoryLabels = [
        'CATEGORY_PERSONAL',
        'CATEGORY_UPDATES',
        'CATEGORY_SOCIAL',
        'CATEGORY_PROMOTIONS',
        'CATEGORY_FORUMS',
        'IMPORTANT',
        'ARCHIVE',
        'TRASH'
    ];
    // Find the first matching category label
    for (const categoryLabel of categoryLabels){
        if (labels.includes(categoryLabel)) {
            return categoryLabel;
        }
    }
    // If no category labels, show Inbox if present
    if (labels.includes('INBOX')) {
        return 'INBOX';
    }
    return null;
}
// Get category display info
function getCategoryDisplayInfo(category) {
    // This function should be used with the CategoryContext's getCategoryInfo
    // It remains here for compatibility with existing code, but will delegate to the context
    // Default category information if needed - we'll use the same format as CategoryContext
    const defaultCategoryMap = {
        'CATEGORY_PERSONAL': {
            display_name: 'Personal',
            color: 'bg-indigo-100 text-indigo-800 border border-indigo-200',
            description: null
        },
        'CATEGORY_UPDATES': {
            display_name: 'Updates',
            color: 'bg-purple-100 text-purple-800 border border-purple-200',
            description: null
        },
        'CATEGORY_SOCIAL': {
            display_name: 'Social',
            color: 'bg-green-100 text-green-800 border border-green-200',
            description: null
        },
        'CATEGORY_PROMOTIONS': {
            display_name: 'Promotions',
            color: 'bg-orange-100 text-orange-800 border border-orange-200',
            description: null
        },
        'CATEGORY_FORUMS': {
            display_name: 'Forums',
            color: 'bg-teal-100 text-teal-800 border border-teal-200',
            description: null
        },
        'PRIMARY': {
            display_name: 'Primary',
            color: 'bg-blue-100 text-blue-800 border border-blue-200',
            description: null
        }
    };
    return defaultCategoryMap[category] || null;
}
// Separate labels into categories and regular labels
function separateLabels(labels) {
    const categories = labels.filter((label)=>label.startsWith('CATEGORY_') || label === 'PRIMARY');
    const regularLabels = labels.filter((label)=>!label.startsWith('CATEGORY_') && !label.startsWith('EA_') && label !== 'PRIMARY' && ![
            'SENT',
            'DRAFT'
        ].includes(label));
    return {
        categories,
        regularLabels
    };
}
function EmailCard({ email, onClick, isDeleted = false, onLabelsUpdated }) {
    _s();
    // Use the category context
    const { getCategoryInfo, categories } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$category$2d$context$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCategoryContext"])();
    const [updating, setUpdating] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [showCategoryDropdown, setShowCategoryDropdown] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const categoryBadgeRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(null);
    const [dropdownPosition, setDropdownPosition] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])({
        top: 0,
        left: 0
    });
    const [showArrowAnimation, setShowArrowAnimation] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(true);
    // Disable arrow animation after a short delay
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "EmailCard.useEffect": ()=>{
            const timer = setTimeout({
                "EmailCard.useEffect.timer": ()=>{
                    setShowArrowAnimation(false);
                }
            }["EmailCard.useEffect.timer"], 2000);
            return ({
                "EmailCard.useEffect": ()=>clearTimeout(timer)
            })["EmailCard.useEffect"];
        }
    }["EmailCard.useEffect"], []);
    // Update dropdown position when it's shown
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "EmailCard.useEffect": ()=>{
            if (showCategoryDropdown && categoryBadgeRef.current) {
                const rect = categoryBadgeRef.current.getBoundingClientRect();
                setDropdownPosition({
                    top: rect.bottom + window.scrollY,
                    left: rect.left + window.scrollX
                });
            }
        }
    }["EmailCard.useEffect"], [
        showCategoryDropdown
    ]);
    // Filter out system labels
    const filteredLabels = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"].useMemo({
        "EmailCard.useMemo[filteredLabels]": ()=>{
            if (!email.labels || email.labels.length === 0) return [];
            // Filter out system labels and category labels (we'll show categories separately)
            const systemLabels = [
                'EA_NEEDS_LABEL_UPDATE',
                'SENT',
                'DRAFT'
            ];
            const visibleLabels = email.labels.filter({
                "EmailCard.useMemo[filteredLabels].visibleLabels": (label)=>!systemLabels.includes(label) && !label.startsWith('CATEGORY_')
            }["EmailCard.useMemo[filteredLabels].visibleLabels"]);
            // If this email has TRASH label, don't display INBOX label
            if (visibleLabels.includes('TRASH')) {
                return visibleLabels.filter({
                    "EmailCard.useMemo[filteredLabels]": (label)=>label !== 'INBOX'
                }["EmailCard.useMemo[filteredLabels]"]);
            }
            return visibleLabels;
        }
    }["EmailCard.useMemo[filteredLabels]"], [
        email.labels
    ]);
    // Get category display info
    const categoryInfo = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"].useMemo({
        "EmailCard.useMemo[categoryInfo]": ()=>{
            // First check if the email has the TRASH label, and if so, prioritize it
            if (email.labels && email.labels.includes('TRASH')) {
                return getCategoryInfo('TRASH') || {
                    display_name: 'Trash',
                    color: 'bg-red-50 text-red-700',
                    description: null
                };
            }
            // If we have a category value from the email, use that
            if (email.category) {
                const info = getCategoryInfo(email.category);
                if (info) return info;
            }
            // If no category is found or the lookup failed, check if the email has a category label
            if (email.labels) {
                const categoryLabel = email.labels.find({
                    "EmailCard.useMemo[categoryInfo].categoryLabel": (label)=>label.startsWith('CATEGORY_') || label === 'PRIMARY'
                }["EmailCard.useMemo[categoryInfo].categoryLabel"]);
                if (categoryLabel) {
                    const info = getCategoryInfo(categoryLabel);
                    if (info) return info;
                }
            }
            // Default fallback
            return getCategoryInfo('primary') || {
                display_name: 'Primary',
                color: 'bg-blue-50 text-blue-700',
                description: null
            };
        }
    }["EmailCard.useMemo[categoryInfo]"], [
        email.category,
        email.labels,
        getCategoryInfo
    ]);
    // Handle archive action
    const handleArchive = async (e)=>{
        e.preventDefault();
        e.stopPropagation();
        try {
            const toastId = (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$utils$2f$toast$2d$config$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["showLoadingToast"])('Archiving email...');
            const response = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["archiveEmail"])(email.id);
            __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$hot$2d$toast$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["toast"].dismiss(toastId);
            if (response.status === 'success') {
                (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$utils$2f$toast$2d$config$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["showSuccessToast"])(response.message || 'Email archived successfully');
                // Update the email object with new labels
                const updatedEmail = {
                    ...email,
                    labels: response.labels || email.labels,
                    // Update the category if returned from the API
                    category: response.category || email.category
                };
                // Call onLabelsUpdated to update the parent component
                if (onLabelsUpdated) {
                    onLabelsUpdated(updatedEmail);
                }
            } else {
                (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$utils$2f$toast$2d$config$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["showErrorToast"])(response.message || 'Failed to archive email');
            }
        } catch (error) {
            (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$utils$2f$toast$2d$config$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["dismissAllToasts"])();
            const errorMessage = error instanceof Error ? error.message : 'Error archiving email';
            (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$utils$2f$toast$2d$config$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["showErrorToast"])(errorMessage);
            console.error('Error archiving email:', error);
        }
    };
    // Handle trash action
    const handleTrash = async (e)=>{
        e.preventDefault();
        e.stopPropagation();
        try {
            const toastId = (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$utils$2f$toast$2d$config$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["showLoadingToast"])('Moving to trash...');
            const response = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["deleteEmail"])(email.id);
            __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$hot$2d$toast$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["toast"].dismiss(toastId);
            if (response.status === 'success') {
                (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$utils$2f$toast$2d$config$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["showSuccessToast"])(response.message || 'Email moved to trash');
                // Update the email object with new category and labels
                const updatedEmail = {
                    ...email,
                    category: 'trash',
                    labels: [
                        ...(email.labels || []).filter((label)=>label !== 'INBOX'),
                        'TRASH'
                    ]
                };
                // Call onLabelsUpdated to update the parent component
                if (onLabelsUpdated) {
                    onLabelsUpdated(updatedEmail);
                }
            } else {
                (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$utils$2f$toast$2d$config$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["showErrorToast"])(response.message || 'Failed to move email to trash');
            }
        } catch (error) {
            (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$utils$2f$toast$2d$config$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["dismissAllToasts"])();
            const errorMessage = error instanceof Error ? error.message : 'Error moving email to trash';
            (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$utils$2f$toast$2d$config$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["showErrorToast"])(errorMessage);
            console.error('Error moving email to trash:', error);
        }
    };
    // Handle mark as read action
    const handleMarkAsRead = async (e)=>{
        e.preventDefault();
        e.stopPropagation();
        // Skip if already read
        if (email.is_read) {
            return;
        }
        try {
            const toastId = (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$utils$2f$toast$2d$config$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["showLoadingToast"])('Marking as read...');
            const response = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["updateEmailLabels"])(email.id, [], [
                'UNREAD'
            ]);
            __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$hot$2d$toast$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["toast"].dismiss(toastId);
            if (response.status === 'success') {
                (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$utils$2f$toast$2d$config$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["showSuccessToast"])('Email marked as read');
                // Update the email object with new read status
                const updatedEmail = {
                    ...email,
                    is_read: true,
                    labels: response.labels || email.labels
                };
                // Call onLabelsUpdated to update the parent component
                if (onLabelsUpdated) {
                    onLabelsUpdated(updatedEmail);
                }
            } else {
                (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$utils$2f$toast$2d$config$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["showErrorToast"])(response.message || 'Failed to mark email as read');
            }
        } catch (error) {
            (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$utils$2f$toast$2d$config$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["dismissAllToasts"])();
            const errorMessage = error instanceof Error ? error.message : 'Error marking email as read';
            (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$utils$2f$toast$2d$config$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["showErrorToast"])(errorMessage);
            console.error('Error marking email as read:', error);
        }
    };
    // Handle mark as unread action
    const handleMarkAsUnread = async (e)=>{
        e.preventDefault();
        e.stopPropagation();
        // Skip if already unread
        if (!email.is_read) {
            return;
        }
        try {
            const toastId = (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$utils$2f$toast$2d$config$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["showLoadingToast"])('Marking as unread...');
            const response = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["updateEmailLabels"])(email.id, [
                'UNREAD'
            ], []);
            __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$hot$2d$toast$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["toast"].dismiss(toastId);
            if (response.status === 'success') {
                (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$utils$2f$toast$2d$config$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["showSuccessToast"])('Email marked as unread');
                // Update the email object with new read status
                const updatedEmail = {
                    ...email,
                    is_read: false,
                    labels: response.labels || email.labels
                };
                // Call onLabelsUpdated to update the parent component
                if (onLabelsUpdated) {
                    onLabelsUpdated(updatedEmail);
                }
            } else {
                (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$utils$2f$toast$2d$config$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["showErrorToast"])(response.message || 'Failed to mark email as unread');
            }
        } catch (error) {
            (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$utils$2f$toast$2d$config$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["dismissAllToasts"])();
            const errorMessage = error instanceof Error ? error.message : 'Error marking email as unread';
            (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$utils$2f$toast$2d$config$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["showErrorToast"])(errorMessage);
            console.error('Error marking email as unread:', error);
        }
    };
    // Handle category change
    const handleCategoryChange = async (e, newCategory)=>{
        e.preventDefault();
        e.stopPropagation();
        // Skip if already in this category
        if (email.category?.toLowerCase() === newCategory.toLowerCase()) {
            return;
        }
        try {
            setUpdating(true);
            const toastId = (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$utils$2f$toast$2d$config$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["showLoadingToast"])('Updating category...');
            const response = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["updateEmailCategory"])(email.id, newCategory.toLowerCase());
            __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$hot$2d$toast$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["toast"].dismiss(toastId);
            if (response.status === 'success') {
                (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$utils$2f$toast$2d$config$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["showSuccessToast"])('Category updated');
                // Update the email object with new category and labels
                const updatedEmail = {
                    ...email,
                    category: response.category,
                    labels: response.labels
                };
                // Call onLabelsUpdated to update the parent component
                if (onLabelsUpdated) {
                    onLabelsUpdated(updatedEmail);
                }
            } else {
                (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$utils$2f$toast$2d$config$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["showErrorToast"])(response.message || 'Failed to update category');
            }
        } catch (error) {
            (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$utils$2f$toast$2d$config$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["dismissAllToasts"])();
            const errorMessage = error instanceof Error ? error.message : 'Error updating category';
            (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$utils$2f$toast$2d$config$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["showErrorToast"])(errorMessage);
            console.error('Error updating category:', error);
        } finally{
            setUpdating(false);
        }
    };
    // Create the email card content
    const emailContent = /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: `p-4 border-b border-gray-200 hover:bg-gray-50 cursor-pointer transition-all ${!email.is_read ? 'bg-slate-50' : ''}`,
        onClick: onClick,
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            className: "flex items-start gap-3",
            children: [
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: "flex-shrink-0 mt-0.5",
                    children: !email.is_read && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "h-2 w-2 rounded-full bg-blue-600",
                        title: "Unread"
                    }, void 0, false, {
                        fileName: "[project]/src/components/ui/email-card.tsx",
                        lineNumber: 366,
                        columnNumber: 13
                    }, this)
                }, void 0, false, {
                    fileName: "[project]/src/components/ui/email-card.tsx",
                    lineNumber: 364,
                    columnNumber: 9
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: "min-w-0 flex-1",
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "flex items-center justify-between mb-1",
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    className: "truncate font-medium text-sm",
                                    children: email.from_email
                                }, void 0, false, {
                                    fileName: "[project]/src/components/ui/email-card.tsx",
                                    lineNumber: 372,
                                    columnNumber: 13
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    className: "text-xs text-gray-500 whitespace-nowrap ml-2",
                                    children: (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$utils$2f$date$2d$utils$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["formatRelativeTime"])(new Date(email.received_at))
                                }, void 0, false, {
                                    fileName: "[project]/src/components/ui/email-card.tsx",
                                    lineNumber: 375,
                                    columnNumber: 13
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/src/components/ui/email-card.tsx",
                            lineNumber: 371,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "flex justify-between items-start",
                            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "truncate font-medium text-base mb-1",
                                children: email.subject || '(No subject)'
                            }, void 0, false, {
                                fileName: "[project]/src/components/ui/email-card.tsx",
                                lineNumber: 381,
                                columnNumber: 13
                            }, this)
                        }, void 0, false, {
                            fileName: "[project]/src/components/ui/email-card.tsx",
                            lineNumber: 380,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "text-sm text-gray-500 line-clamp-1 mb-2",
                            children: email.snippet
                        }, void 0, false, {
                            fileName: "[project]/src/components/ui/email-card.tsx",
                            lineNumber: 386,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "flex items-center justify-between",
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    className: "flex items-center gap-2",
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            className: "relative",
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                    ref: categoryBadgeRef,
                                                    className: `text-xs px-2 py-1 rounded-md bg-white shadow-sm cursor-pointer flex items-center gap-1 hover:shadow transition-all border border-gray-300 hover:border-gray-400 ${showCategoryDropdown ? 'ring-2 ring-blue-300 border-blue-300' : ''}`,
                                                    onClick: (e)=>{
                                                        e.stopPropagation();
                                                        setShowCategoryDropdown(!showCategoryDropdown);
                                                    },
                                                    title: "Click to change category",
                                                    children: [
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                            className: "font-medium mr-1 text-gray-500",
                                                            children: "Category:"
                                                        }, void 0, false, {
                                                            fileName: "[project]/src/components/ui/email-card.tsx",
                                                            lineNumber: 403,
                                                            columnNumber: 19
                                                        }, this),
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                            className: `mr-1 px-1.5 py-0.5 rounded ${categoryInfo.color}`,
                                                            children: categoryInfo.display_name
                                                        }, void 0, false, {
                                                            fileName: "[project]/src/components/ui/email-card.tsx",
                                                            lineNumber: 404,
                                                            columnNumber: 19
                                                        }, this),
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                            className: "border-l border-gray-300 pl-1 flex items-center text-gray-500 bg-gray-50 -mr-2 -my-1 py-1 px-1 rounded-r-md",
                                                            children: [
                                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                                    className: "text-xs mr-1 font-medium",
                                                                    children: "Select"
                                                                }, void 0, false, {
                                                                    fileName: "[project]/src/components/ui/email-card.tsx",
                                                                    lineNumber: 406,
                                                                    columnNumber: 21
                                                                }, this),
                                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("svg", {
                                                                    xmlns: "http://www.w3.org/2000/svg",
                                                                    className: `h-4 w-4 transition-transform ${showCategoryDropdown ? 'rotate-180' : ''} ${showArrowAnimation ? 'animate-bounce' : ''}`,
                                                                    viewBox: "0 0 24 24",
                                                                    fill: "none",
                                                                    stroke: "currentColor",
                                                                    strokeWidth: "2",
                                                                    strokeLinecap: "round",
                                                                    strokeLinejoin: "round",
                                                                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("polyline", {
                                                                        points: "6 9 12 15 18 9"
                                                                    }, void 0, false, {
                                                                        fileName: "[project]/src/components/ui/email-card.tsx",
                                                                        lineNumber: 419,
                                                                        columnNumber: 23
                                                                    }, this)
                                                                }, void 0, false, {
                                                                    fileName: "[project]/src/components/ui/email-card.tsx",
                                                                    lineNumber: 407,
                                                                    columnNumber: 21
                                                                }, this)
                                                            ]
                                                        }, void 0, true, {
                                                            fileName: "[project]/src/components/ui/email-card.tsx",
                                                            lineNumber: 405,
                                                            columnNumber: 19
                                                        }, this)
                                                    ]
                                                }, void 0, true, {
                                                    fileName: "[project]/src/components/ui/email-card.tsx",
                                                    lineNumber: 394,
                                                    columnNumber: 17
                                                }, this),
                                                showCategoryDropdown && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                    className: "fixed inset-0 z-10",
                                                    onClick: (e)=>{
                                                        e.stopPropagation();
                                                        setShowCategoryDropdown(false);
                                                    },
                                                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                        style: {
                                                            position: 'absolute',
                                                            top: `${dropdownPosition.top}px`,
                                                            left: `${dropdownPosition.left}px`
                                                        },
                                                        className: "mt-1 w-48 bg-white rounded-md shadow-lg z-20 border border-gray-200 overflow-hidden",
                                                        onClick: (e)=>e.stopPropagation(),
                                                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                            className: "py-1 max-h-60 overflow-y-auto",
                                                            children: [
                                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                                    className: "px-4 py-2 text-xs font-medium text-gray-500 border-b border-gray-100 bg-gray-50",
                                                                    children: "Change category"
                                                                }, void 0, false, {
                                                                    fileName: "[project]/src/components/ui/email-card.tsx",
                                                                    lineNumber: 443,
                                                                    columnNumber: 25
                                                                }, this),
                                                                updating && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                                    className: "px-4 py-2 text-xs text-gray-500 flex items-center justify-center",
                                                                    children: [
                                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("svg", {
                                                                            className: "animate-spin h-3 w-3 mr-2",
                                                                            xmlns: "http://www.w3.org/2000/svg",
                                                                            fill: "none",
                                                                            viewBox: "0 0 24 24",
                                                                            children: [
                                                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("circle", {
                                                                                    className: "opacity-25",
                                                                                    cx: "12",
                                                                                    cy: "12",
                                                                                    r: "10",
                                                                                    stroke: "currentColor",
                                                                                    strokeWidth: "4"
                                                                                }, void 0, false, {
                                                                                    fileName: "[project]/src/components/ui/email-card.tsx",
                                                                                    lineNumber: 449,
                                                                                    columnNumber: 31
                                                                                }, this),
                                                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("path", {
                                                                                    className: "opacity-75",
                                                                                    fill: "currentColor",
                                                                                    d: "M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                                                                                }, void 0, false, {
                                                                                    fileName: "[project]/src/components/ui/email-card.tsx",
                                                                                    lineNumber: 450,
                                                                                    columnNumber: 31
                                                                                }, this)
                                                                            ]
                                                                        }, void 0, true, {
                                                                            fileName: "[project]/src/components/ui/email-card.tsx",
                                                                            lineNumber: 448,
                                                                            columnNumber: 29
                                                                        }, this),
                                                                        "Updating..."
                                                                    ]
                                                                }, void 0, true, {
                                                                    fileName: "[project]/src/components/ui/email-card.tsx",
                                                                    lineNumber: 447,
                                                                    columnNumber: 27
                                                                }, this),
                                                                categories.slice() // Create a copy to avoid mutating the original array
                                                                .sort((a, b)=>a.priority - b.priority) // Sort by priority
                                                                .map((category)=>{
                                                                    const isSelected = email.category?.toLowerCase() === category.name.toLowerCase();
                                                                    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                                        className: `w-full text-left px-4 py-2 text-sm hover:bg-gray-50 flex items-center justify-between ${isSelected ? 'bg-gray-50 font-medium' : ''}`,
                                                                        onClick: (e)=>{
                                                                            handleCategoryChange(e, category.name.toLowerCase());
                                                                            setShowCategoryDropdown(false);
                                                                        },
                                                                        disabled: updating,
                                                                        children: [
                                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                                                children: category.display_name
                                                                            }, void 0, false, {
                                                                                fileName: "[project]/src/components/ui/email-card.tsx",
                                                                                lineNumber: 472,
                                                                                columnNumber: 31
                                                                            }, this),
                                                                            isSelected && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("svg", {
                                                                                xmlns: "http://www.w3.org/2000/svg",
                                                                                className: "h-4 w-4 text-blue-600",
                                                                                fill: "none",
                                                                                viewBox: "0 0 24 24",
                                                                                stroke: "currentColor",
                                                                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("path", {
                                                                                    strokeLinecap: "round",
                                                                                    strokeLinejoin: "round",
                                                                                    strokeWidth: 2,
                                                                                    d: "M5 13l4 4L19 7"
                                                                                }, void 0, false, {
                                                                                    fileName: "[project]/src/components/ui/email-card.tsx",
                                                                                    lineNumber: 475,
                                                                                    columnNumber: 35
                                                                                }, this)
                                                                            }, void 0, false, {
                                                                                fileName: "[project]/src/components/ui/email-card.tsx",
                                                                                lineNumber: 474,
                                                                                columnNumber: 33
                                                                            }, this)
                                                                        ]
                                                                    }, category.name, true, {
                                                                        fileName: "[project]/src/components/ui/email-card.tsx",
                                                                        lineNumber: 461,
                                                                        columnNumber: 29
                                                                    }, this);
                                                                })
                                                            ]
                                                        }, void 0, true, {
                                                            fileName: "[project]/src/components/ui/email-card.tsx",
                                                            lineNumber: 442,
                                                            columnNumber: 23
                                                        }, this)
                                                    }, void 0, false, {
                                                        fileName: "[project]/src/components/ui/email-card.tsx",
                                                        lineNumber: 433,
                                                        columnNumber: 21
                                                    }, this)
                                                }, void 0, false, {
                                                    fileName: "[project]/src/components/ui/email-card.tsx",
                                                    lineNumber: 426,
                                                    columnNumber: 19
                                                }, this)
                                            ]
                                        }, void 0, true, {
                                            fileName: "[project]/src/components/ui/email-card.tsx",
                                            lineNumber: 393,
                                            columnNumber: 15
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            className: "flex flex-wrap gap-1",
                                            children: (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$ui$2f$email$2d$label$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["mapLabelsToComponents"])(filteredLabels, {
                                                variant: 'compact',
                                                showPrefix: false
                                            })
                                        }, void 0, false, {
                                            fileName: "[project]/src/components/ui/email-card.tsx",
                                            lineNumber: 488,
                                            columnNumber: 15
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/src/components/ui/email-card.tsx",
                                    lineNumber: 391,
                                    columnNumber: 13
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    className: "ml-auto flex gap-1",
                                    children: !isDeleted && !email.labels.includes('TRASH') && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Fragment"], {
                                        children: [
                                            email.is_read ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                onClick: handleMarkAsUnread,
                                                className: "p-1 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded",
                                                title: "Mark as unread",
                                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("svg", {
                                                    xmlns: "http://www.w3.org/2000/svg",
                                                    className: "h-4 w-4",
                                                    fill: "none",
                                                    viewBox: "0 0 24 24",
                                                    stroke: "currentColor",
                                                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("path", {
                                                        strokeLinecap: "round",
                                                        strokeLinejoin: "round",
                                                        strokeWidth: 2,
                                                        d: "M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                                                    }, void 0, false, {
                                                        fileName: "[project]/src/components/ui/email-card.tsx",
                                                        lineNumber: 504,
                                                        columnNumber: 25
                                                    }, this)
                                                }, void 0, false, {
                                                    fileName: "[project]/src/components/ui/email-card.tsx",
                                                    lineNumber: 503,
                                                    columnNumber: 23
                                                }, this)
                                            }, void 0, false, {
                                                fileName: "[project]/src/components/ui/email-card.tsx",
                                                lineNumber: 498,
                                                columnNumber: 21
                                            }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                onClick: handleMarkAsRead,
                                                className: "p-1 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded",
                                                title: "Mark as read",
                                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("svg", {
                                                    xmlns: "http://www.w3.org/2000/svg",
                                                    className: "h-4 w-4",
                                                    fill: "none",
                                                    viewBox: "0 0 24 24",
                                                    stroke: "currentColor",
                                                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("path", {
                                                        strokeLinecap: "round",
                                                        strokeLinejoin: "round",
                                                        strokeWidth: 2,
                                                        d: "M3 19v-8.93a2 2 0 01.89-1.664l7-4.666a2 2 0 012.22 0l7 4.666A2 2 0 0121 10.07V19M3 19a2 2 0 002 2h14a2 2 0 002-2M3 19l6.75-4.5M21 19l-6.75-4.5M3 10l6.75 4.5M21 10l-6.75 4.5m0 0l-1.14.76a2 2 0 01-2.22 0l-1.14-.76"
                                                    }, void 0, false, {
                                                        fileName: "[project]/src/components/ui/email-card.tsx",
                                                        lineNumber: 514,
                                                        columnNumber: 25
                                                    }, this)
                                                }, void 0, false, {
                                                    fileName: "[project]/src/components/ui/email-card.tsx",
                                                    lineNumber: 513,
                                                    columnNumber: 23
                                                }, this)
                                            }, void 0, false, {
                                                fileName: "[project]/src/components/ui/email-card.tsx",
                                                lineNumber: 508,
                                                columnNumber: 21
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                onClick: handleArchive,
                                                className: "p-1 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded",
                                                title: "Archive",
                                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("svg", {
                                                    xmlns: "http://www.w3.org/2000/svg",
                                                    className: "h-4 w-4",
                                                    fill: "none",
                                                    viewBox: "0 0 24 24",
                                                    stroke: "currentColor",
                                                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("path", {
                                                        strokeLinecap: "round",
                                                        strokeLinejoin: "round",
                                                        strokeWidth: 2,
                                                        d: "M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8"
                                                    }, void 0, false, {
                                                        fileName: "[project]/src/components/ui/email-card.tsx",
                                                        lineNumber: 525,
                                                        columnNumber: 23
                                                    }, this)
                                                }, void 0, false, {
                                                    fileName: "[project]/src/components/ui/email-card.tsx",
                                                    lineNumber: 524,
                                                    columnNumber: 21
                                                }, this)
                                            }, void 0, false, {
                                                fileName: "[project]/src/components/ui/email-card.tsx",
                                                lineNumber: 519,
                                                columnNumber: 19
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                onClick: handleTrash,
                                                className: "p-1 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded",
                                                title: "Move to trash",
                                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("svg", {
                                                    xmlns: "http://www.w3.org/2000/svg",
                                                    className: "h-4 w-4",
                                                    fill: "none",
                                                    viewBox: "0 0 24 24",
                                                    stroke: "currentColor",
                                                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("path", {
                                                        strokeLinecap: "round",
                                                        strokeLinejoin: "round",
                                                        strokeWidth: 2,
                                                        d: "M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                                                    }, void 0, false, {
                                                        fileName: "[project]/src/components/ui/email-card.tsx",
                                                        lineNumber: 535,
                                                        columnNumber: 23
                                                    }, this)
                                                }, void 0, false, {
                                                    fileName: "[project]/src/components/ui/email-card.tsx",
                                                    lineNumber: 534,
                                                    columnNumber: 21
                                                }, this)
                                            }, void 0, false, {
                                                fileName: "[project]/src/components/ui/email-card.tsx",
                                                lineNumber: 529,
                                                columnNumber: 19
                                            }, this)
                                        ]
                                    }, void 0, true)
                                }, void 0, false, {
                                    fileName: "[project]/src/components/ui/email-card.tsx",
                                    lineNumber: 494,
                                    columnNumber: 13
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/src/components/ui/email-card.tsx",
                            lineNumber: 390,
                            columnNumber: 11
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/src/components/ui/email-card.tsx",
                    lineNumber: 370,
                    columnNumber: 9
                }, this)
            ]
        }, void 0, true, {
            fileName: "[project]/src/components/ui/email-card.tsx",
            lineNumber: 363,
            columnNumber: 7
        }, this)
    }, void 0, false, {
        fileName: "[project]/src/components/ui/email-card.tsx",
        lineNumber: 359,
        columnNumber: 5
    }, this);
    // If there's a click handler, don't wrap with Link
    if (onClick) {
        return emailContent;
    }
    // Otherwise, wrap with Link for navigation
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"], {
        href: `/emails/${email.id}`,
        className: "block",
        children: emailContent
    }, void 0, false, {
        fileName: "[project]/src/components/ui/email-card.tsx",
        lineNumber: 554,
        columnNumber: 5
    }, this);
}
_s(EmailCard, "kAAKxL0DEpUEFt+UowNiaVDUujc=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$category$2d$context$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCategoryContext"]
    ];
});
_c = EmailCard;
var _c;
__turbopack_refresh__.register(_c, "EmailCard");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_refresh__.registerExports(module, globalThis.$RefreshHelpers$);
}
}}),
"[project]/src/app/emails/page.tsx [app-client] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, k: __turbopack_refresh__, m: module, z: __turbopack_require_stub__ } = __turbopack_context__;
{
__turbopack_esm__({
    "default": (()=>EmailsPage)
});
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/next/navigation.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/src/lib/api.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$auth$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/src/lib/auth.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$ui$2f$search$2d$input$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/src/components/ui/search-input.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$ui$2f$email$2d$card$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/src/components/ui/email-card.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$layout$2f$main$2d$layout$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/src/components/layout/main-layout.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$hot$2d$toast$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/react-hot-toast/dist/index.mjs [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$build$2f$polyfills$2f$process$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/next/dist/build/polyfills/process.js [app-client] (ecmascript)");
;
var _s = __turbopack_refresh__.signature();
'use client';
;
;
;
;
;
;
;
;
// Add the API function to fix trash consistency
const fixTrashConsistency = async ()=>{
    try {
        // Get the authentication token from localStorage
        const token = localStorage.getItem('token');
        if (!token) {
            console.error('Authentication token not found');
            throw new Error('Authentication token not found');
        }
        // Get the API URL from environment variables
        const apiUrl = ("TURBOPACK compile-time value", "http://localhost:8000") || 'http://localhost:8000';
        console.log(`Making API request to ${apiUrl}/emails/fix-trash-consistency`);
        // Make the request to fix trash consistency
        const response = await fetch(`${apiUrl}/emails/fix-trash-consistency`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        // Check if the response is ok
        if (!response.ok) {
            // Try to get error details from response
            const errorData = await response.json().catch(()=>null);
            const errorMessage = errorData?.detail || `API error: ${response.status} ${response.statusText}`;
            console.error('Error response:', errorMessage);
            throw new Error(errorMessage);
        }
        // Parse the response
        const data = await response.json();
        console.log('Fix trash consistency response:', data);
        return data;
    } catch (error) {
        console.error('Error fixing trash consistency:', error);
        throw error;
    }
};
function EmailsPage() {
    _s();
    const router = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRouter"])();
    const searchParams = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useSearchParams"])();
    const [emails, setEmails] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])([]);
    const [loading, setLoading] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(true);
    const [error, setError] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [searchTerm, setSearchTerm] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])('');
    const [hasMore, setHasMore] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(true);
    const [page, setPage] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(1);
    const [totalEmails, setTotalEmails] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(0);
    const [initialLoadComplete, setInitialLoadComplete] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [loadingMore, setLoadingMore] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [scrollRestored, setScrollRestored] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [isFixingTrash, setIsFixingTrash] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [showTrashNotification, setShowTrashNotification] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(true);
    // Get category from URL parameters
    const categoryParam = searchParams?.get('category') ?? null;
    // Get status from URL parameters
    const statusParam = searchParams?.get('status') ?? null;
    // Get label from URL parameters
    const labelParam = searchParams?.get('label') ?? null;
    // Get view from URL parameters (for inbox view)
    const viewParam = searchParams?.get('view') ?? null;
    // Create a ref for the observer target element
    const observerTarget = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(null);
    // Function to fetch emails with pagination
    const fetchEmails = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "EmailsPage.useCallback[fetchEmails]": async (pageNum, isInitialLoad = false)=>{
            try {
                if (!(0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$auth$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["isAuthenticated"])()) {
                    console.log('User not authenticated, redirecting to authentication');
                    (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$auth$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["handleAuthError"])();
                    return;
                }
                if (isInitialLoad) {
                    setLoading(true);
                } else {
                    setLoadingMore(true);
                }
                console.log(`Fetching emails for page ${pageNum}...`);
                const params = {
                    page: pageNum,
                    limit: 20
                };
                // If no specific filters are applied and not in inbox view, show all emails EXCEPT trash
                const isAllEmailsView = !categoryParam && !statusParam && !labelParam && !viewParam;
                // Handle inbox view - exclude archived and trash emails
                if (viewParam === 'inbox') {
                    // Add INBOX label filter to only show emails in the inbox
                    params.label = 'INBOX';
                    console.log('Inbox view: Showing only emails with INBOX label');
                }
                if (isAllEmailsView) {
                // Instead of setting showAll=true which includes trash,
                // we don't set any parameter which will use the backend's default
                // behavior of excluding trash emails
                }
                if (categoryParam) {
                    params.category = categoryParam;
                    // Set showAll to true for trash view and also when we SPECIFICALLY
                    // need to get emails with the trash category
                    if (categoryParam.toLowerCase() === 'trash') {
                        params.showAll = true;
                        // We also need to add a parameter to ensure we're getting emails
                        // with either the trash category OR the TRASH label
                        params.label = 'TRASH';
                    }
                }
                if (statusParam) {
                    if (statusParam === 'read' || statusParam === 'unread') {
                        // Convert status string to boolean read_status
                        params.read_status = statusParam === 'read';
                    }
                }
                if (labelParam && categoryParam !== 'trash') {
                    params.label = labelParam;
                }
                const response = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["getEmails"])(params);
                console.log('Emails fetched successfully:', response.emails.length, 'emails');
                if (isInitialLoad) {
                    setEmails(response.emails);
                } else {
                    setEmails({
                        "EmailsPage.useCallback[fetchEmails]": (prev)=>[
                                ...prev,
                                ...response.emails
                            ]
                    }["EmailsPage.useCallback[fetchEmails]"]);
                }
                setTotalEmails(response.pagination.total);
                setHasMore(response.pagination.has_next);
                setError(null);
                if (isInitialLoad) {
                    setInitialLoadComplete(true);
                }
            } catch (error) {
                console.error('Error fetching emails:', error);
                // Check if it's an authentication error
                const errorMessage = error instanceof Error ? error.message : 'Error fetching emails';
                if (errorMessage.includes('Authentication failed') || errorMessage.includes('token') || errorMessage.includes('401')) {
                    (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$auth$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["handleAuthError"])();
                    return;
                }
                setError(errorMessage);
            } finally{
                setLoading(false);
                setLoadingMore(false);
            }
        }
    }["EmailsPage.useCallback[fetchEmails]"], [
        categoryParam,
        statusParam,
        labelParam,
        router,
        viewParam
    ]);
    // Initial data load
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "EmailsPage.useEffect": ()=>{
            setPage(1);
            setEmails([]);
            setHasMore(true);
            setInitialLoadComplete(false);
            fetchEmails(1, true);
        }
    }["EmailsPage.useEffect"], [
        fetchEmails,
        categoryParam,
        statusParam,
        labelParam,
        viewParam
    ]);
    // Listen for email sync completion event
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "EmailsPage.useEffect": ()=>{
            const handleSyncCompleted = {
                "EmailsPage.useEffect.handleSyncCompleted": ()=>{
                    console.log('Email sync completed, refreshing email list');
                    // Reset pagination and reload emails
                    setPage(1);
                    setEmails([]);
                    setHasMore(true);
                    setInitialLoadComplete(false);
                    fetchEmails(1, true);
                }
            }["EmailsPage.useEffect.handleSyncCompleted"];
            // Add event listener
            window.addEventListener(__TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$layout$2f$main$2d$layout$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["EMAIL_SYNC_COMPLETED_EVENT"], handleSyncCompleted);
            // Clean up
            return ({
                "EmailsPage.useEffect": ()=>{
                    window.removeEventListener(__TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$layout$2f$main$2d$layout$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["EMAIL_SYNC_COMPLETED_EVENT"], handleSyncCompleted);
                }
            })["EmailsPage.useEffect"];
        }
    }["EmailsPage.useEffect"], [
        fetchEmails
    ]);
    // Set up intersection observer for infinite scrolling
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "EmailsPage.useEffect": ()=>{
            if (!initialLoadComplete || !hasMore || loadingMore) return;
            const observer = new IntersectionObserver({
                "EmailsPage.useEffect": (entries)=>{
                    if (entries[0].isIntersecting && hasMore && !loadingMore) {
                        const nextPage = page + 1;
                        setPage(nextPage);
                        fetchEmails(nextPage);
                    }
                }
            }["EmailsPage.useEffect"], {
                threshold: 0.5
            });
            if (observerTarget.current) {
                observer.observe(observerTarget.current);
            }
            return ({
                "EmailsPage.useEffect": ()=>{
                    if (observerTarget.current) {
                        observer.unobserve(observerTarget.current);
                    }
                }
            })["EmailsPage.useEffect"];
        }
    }["EmailsPage.useEffect"], [
        initialLoadComplete,
        hasMore,
        loadingMore,
        page,
        fetchEmails
    ]);
    // Add a handler for labels updated
    const handleLabelsUpdated = (updatedEmail)=>{
        // Check if the email should be removed from the current view based on category/status filter
        const shouldRemoveFromCurrentView = // If we're viewing a specific category and the email category has changed
        categoryParam && updatedEmail.category !== categoryParam || categoryParam === 'archive' && updatedEmail.labels.includes('INBOX') || labelParam && !updatedEmail.labels.includes(labelParam) || categoryParam !== 'trash' && updatedEmail.labels.includes('TRASH');
        // Special case: If the email has been moved to trash and we're not in trash view,
        // remove it from the current view
        if (updatedEmail.labels.includes('TRASH') && categoryParam !== 'trash') {
            setEmails((prevEmails)=>prevEmails.filter((email)=>email.id !== updatedEmail.id));
            setTotalEmails((prev)=>Math.max(0, prev - 1));
            return;
        }
        if (shouldRemoveFromCurrentView) {
            // Remove the email from the current view
            setEmails((prevEmails)=>prevEmails.filter((email)=>email.id !== updatedEmail.id));
            // Update total count
            setTotalEmails((prev)=>Math.max(0, prev - 1));
        } else {
            // Update the email in the list
            setEmails((prevEmails)=>prevEmails.map((email)=>email.id === updatedEmail.id ? updatedEmail : email));
        }
    };
    // Save scroll position when navigating away
    const saveScrollPosition = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "EmailsPage.useCallback[saveScrollPosition]": ()=>{
            const scrollY = window.scrollY;
            sessionStorage.setItem('emailListScrollPosition', scrollY.toString());
            console.log('Saved scroll position:', scrollY);
        }
    }["EmailsPage.useCallback[saveScrollPosition]"], []);
    // Restore scroll position
    const restoreScrollPosition = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "EmailsPage.useCallback[restoreScrollPosition]": ()=>{
            const savedPosition = sessionStorage.getItem('emailListScrollPosition');
            if (savedPosition && !scrollRestored) {
                const position = parseInt(savedPosition, 10);
                console.log('Restoring scroll position to:', position);
                window.scrollTo(0, position);
                setScrollRestored(true);
            }
        }
    }["EmailsPage.useCallback[restoreScrollPosition]"], [
        scrollRestored
    ]);
    // Effect to restore scroll position when returning to this page
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "EmailsPage.useEffect": ()=>{
            if (initialLoadComplete && !scrollRestored) {
                restoreScrollPosition();
            }
        }
    }["EmailsPage.useEffect"], [
        initialLoadComplete,
        restoreScrollPosition,
        scrollRestored
    ]);
    // Set up event handlers for saving scroll position on navigation
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "EmailsPage.useEffect": ()=>{
            // Add click event listener to email cards to save position
            const handleEmailCardClick = {
                "EmailsPage.useEffect.handleEmailCardClick": ()=>{
                    saveScrollPosition();
                }
            }["EmailsPage.useEffect.handleEmailCardClick"];
            // Find all email card links and attach event listeners
            const emailCards = document.querySelectorAll('[data-email-card]');
            emailCards.forEach({
                "EmailsPage.useEffect": (card)=>{
                    card.addEventListener('click', handleEmailCardClick);
                }
            }["EmailsPage.useEffect"]);
            return ({
                "EmailsPage.useEffect": ()=>{
                    // Clean up event listeners
                    emailCards.forEach({
                        "EmailsPage.useEffect": (card)=>{
                            card.removeEventListener('click', handleEmailCardClick);
                        }
                    }["EmailsPage.useEffect"]);
                }
            })["EmailsPage.useEffect"];
        }
    }["EmailsPage.useEffect"], [
        emails,
        saveScrollPosition
    ]);
    // Handle the trash consistency fix
    const handleFixTrashConsistency = async ()=>{
        if (isFixingTrash) return;
        try {
            setIsFixingTrash(true);
            const toastId = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$hot$2d$toast$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["toast"].loading('Fixing trash inconsistencies...');
            const result = await fixTrashConsistency();
            __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$hot$2d$toast$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["toast"].dismiss(toastId);
            if (result.fixed_count > 0) {
                __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$hot$2d$toast$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["toast"].success(`Fixed ${result.fixed_count} emails with trash inconsistencies. Refreshing...`);
                // Reset pagination and reload emails
                setPage(1);
                setEmails([]);
                setHasMore(true);
                setInitialLoadComplete(false);
                fetchEmails(1, true);
            } else {
                __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$hot$2d$toast$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["toast"].success('No inconsistencies found. All emails are correctly labeled.');
            }
        } catch (error) {
            __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$hot$2d$toast$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["toast"].error(`Error fixing trash inconsistencies: ${error instanceof Error ? error.message : 'Unknown error'}`);
            console.error('Failed to fix trash inconsistencies:', error);
        } finally{
            setIsFixingTrash(false);
        }
    };
    // Effect to show notification in trash view
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "EmailsPage.useEffect": ()=>{
            if (categoryParam?.toLowerCase() === 'trash') {
                setShowTrashNotification(true);
            } else {
                setShowTrashNotification(false);
            }
        }
    }["EmailsPage.useEffect"], [
        categoryParam
    ]);
    if (loading) {
        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            className: "flex items-center justify-center h-screen",
            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"
            }, void 0, false, {
                fileName: "[project]/src/app/emails/page.tsx",
                lineNumber: 363,
                columnNumber: 17
            }, this)
        }, void 0, false, {
            fileName: "[project]/src/app/emails/page.tsx",
            lineNumber: 362,
            columnNumber: 13
        }, this);
    }
    if (error) {
        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            className: "flex items-center justify-center h-screen",
            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "bg-white rounded-2xl shadow-lg p-8 max-w-md w-full mx-4",
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: "text-center",
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("h2", {
                            className: "text-xl font-bold text-gray-900 mb-2",
                            children: "Error Loading Emails"
                        }, void 0, false, {
                            fileName: "[project]/src/app/emails/page.tsx",
                            lineNumber: 373,
                            columnNumber: 25
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                            className: "text-gray-600",
                            children: error
                        }, void 0, false, {
                            fileName: "[project]/src/app/emails/page.tsx",
                            lineNumber: 374,
                            columnNumber: 25
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                            onClick: ()=>window.location.reload(),
                            className: "mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-500",
                            children: "Try Again"
                        }, void 0, false, {
                            fileName: "[project]/src/app/emails/page.tsx",
                            lineNumber: 375,
                            columnNumber: 25
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/src/app/emails/page.tsx",
                    lineNumber: 372,
                    columnNumber: 21
                }, this)
            }, void 0, false, {
                fileName: "[project]/src/app/emails/page.tsx",
                lineNumber: 371,
                columnNumber: 17
            }, this)
        }, void 0, false, {
            fileName: "[project]/src/app/emails/page.tsx",
            lineNumber: 370,
            columnNumber: 13
        }, this);
    }
    const filteredEmails = emails.filter((email)=>{
        const matchesSearch = !searchTerm || email.subject?.toLowerCase().includes(searchTerm.toLowerCase()) || email.from_email.toLowerCase().includes(searchTerm.toLowerCase()) || email.snippet.toLowerCase().includes(searchTerm.toLowerCase());
        return matchesSearch;
    });
    // Determine the title based on category, status, or view parameters
    let pageTitle = 'All Emails';
    if (viewParam === 'inbox') {
        pageTitle = 'Inbox';
    } else if (categoryParam) {
        pageTitle = `${categoryParam.charAt(0).toUpperCase() + categoryParam.slice(1)} Emails`;
    } else if (statusParam) {
        pageTitle = `${statusParam.charAt(0).toUpperCase() + statusParam.slice(1)} Emails`;
    }
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "px-4 py-8",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$hot$2d$toast$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Toaster"], {
                position: "top-right",
                toastOptions: {
                    duration: 6000
                }
            }, void 0, false, {
                fileName: "[project]/src/app/emails/page.tsx",
                lineNumber: 407,
                columnNumber: 13
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "w-full max-w-3xl mx-auto sm:px-2 md:px-4",
                children: [
                    categoryParam?.toLowerCase() === 'trash' && showTrashNotification && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "mb-4 p-4 bg-orange-50 border border-orange-200 rounded-lg",
                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "flex items-center justify-between",
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    className: "flex items-center",
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("svg", {
                                            xmlns: "http://www.w3.org/2000/svg",
                                            className: "h-5 w-5 text-orange-500 mr-2",
                                            viewBox: "0 0 20 20",
                                            fill: "currentColor",
                                            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("path", {
                                                fillRule: "evenodd",
                                                d: "M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z",
                                                clipRule: "evenodd"
                                            }, void 0, false, {
                                                fileName: "[project]/src/app/emails/page.tsx",
                                                lineNumber: 415,
                                                columnNumber: 37
                                            }, this)
                                        }, void 0, false, {
                                            fileName: "[project]/src/app/emails/page.tsx",
                                            lineNumber: 414,
                                            columnNumber: 33
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                                className: "text-sm text-orange-800 font-medium",
                                                children: "Some emails may not appear in this Trash view due to inconsistent labeling."
                                            }, void 0, false, {
                                                fileName: "[project]/src/app/emails/page.tsx",
                                                lineNumber: 418,
                                                columnNumber: 37
                                            }, this)
                                        }, void 0, false, {
                                            fileName: "[project]/src/app/emails/page.tsx",
                                            lineNumber: 417,
                                            columnNumber: 33
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/src/app/emails/page.tsx",
                                    lineNumber: 413,
                                    columnNumber: 29
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    className: "flex space-x-2",
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                            onClick: handleFixTrashConsistency,
                                            disabled: isFixingTrash,
                                            className: "px-3 py-1 bg-orange-500 text-white text-sm font-medium rounded hover:bg-orange-600 transition-colors",
                                            children: isFixingTrash ? 'Fixing...' : 'Fix Now'
                                        }, void 0, false, {
                                            fileName: "[project]/src/app/emails/page.tsx",
                                            lineNumber: 424,
                                            columnNumber: 33
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                            onClick: ()=>setShowTrashNotification(false),
                                            className: "text-orange-500 hover:text-orange-700",
                                            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("svg", {
                                                xmlns: "http://www.w3.org/2000/svg",
                                                className: "h-5 w-5",
                                                viewBox: "0 0 20 20",
                                                fill: "currentColor",
                                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("path", {
                                                    fillRule: "evenodd",
                                                    d: "M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z",
                                                    clipRule: "evenodd"
                                                }, void 0, false, {
                                                    fileName: "[project]/src/app/emails/page.tsx",
                                                    lineNumber: 436,
                                                    columnNumber: 41
                                                }, this)
                                            }, void 0, false, {
                                                fileName: "[project]/src/app/emails/page.tsx",
                                                lineNumber: 435,
                                                columnNumber: 37
                                            }, this)
                                        }, void 0, false, {
                                            fileName: "[project]/src/app/emails/page.tsx",
                                            lineNumber: 431,
                                            columnNumber: 33
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/src/app/emails/page.tsx",
                                    lineNumber: 423,
                                    columnNumber: 29
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/src/app/emails/page.tsx",
                            lineNumber: 412,
                            columnNumber: 25
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/src/app/emails/page.tsx",
                        lineNumber: 411,
                        columnNumber: 21
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "flex flex-col mb-6",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "flex flex-col lg:flex-row justify-between items-start lg:items-center mb-4",
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("h1", {
                                        className: "text-2xl font-bold text-gray-900 mb-4 lg:mb-0 flex-shrink-0",
                                        children: [
                                            pageTitle,
                                            totalEmails > 0 && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                className: "text-gray-500 text-lg ml-2",
                                                children: [
                                                    "(",
                                                    totalEmails,
                                                    ")"
                                                ]
                                            }, void 0, true, {
                                                fileName: "[project]/src/app/emails/page.tsx",
                                                lineNumber: 448,
                                                columnNumber: 49
                                            }, this)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/src/app/emails/page.tsx",
                                        lineNumber: 446,
                                        columnNumber: 25
                                    }, this),
                                    categoryParam?.toLowerCase() === 'trash' && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                        onClick: handleFixTrashConsistency,
                                        disabled: isFixingTrash,
                                        className: `px-4 py-2 text-sm bg-orange-500 text-white rounded-md hover:bg-orange-600 transition-colors ${isFixingTrash ? 'opacity-50 cursor-not-allowed' : ''}`,
                                        children: isFixingTrash ? 'Fixing...' : 'Fix Trash Inconsistencies'
                                    }, void 0, false, {
                                        fileName: "[project]/src/app/emails/page.tsx",
                                        lineNumber: 453,
                                        columnNumber: 29
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/src/app/emails/page.tsx",
                                lineNumber: 445,
                                columnNumber: 21
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "w-full",
                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$ui$2f$search$2d$input$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["SearchInput"], {
                                    value: searchTerm,
                                    onChange: setSearchTerm,
                                    placeholder: "Search emails...",
                                    className: "w-full"
                                }, void 0, false, {
                                    fileName: "[project]/src/app/emails/page.tsx",
                                    lineNumber: 463,
                                    columnNumber: 25
                                }, this)
                            }, void 0, false, {
                                fileName: "[project]/src/app/emails/page.tsx",
                                lineNumber: 462,
                                columnNumber: 21
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/src/app/emails/page.tsx",
                        lineNumber: 444,
                        columnNumber: 17
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                        className: "mt-1 text-sm text-gray-600 mb-4",
                        children: [
                            totalEmails,
                            " ",
                            totalEmails === 1 ? 'email' : 'emails',
                            " found"
                        ]
                    }, void 0, true, {
                        fileName: "[project]/src/app/emails/page.tsx",
                        lineNumber: 472,
                        columnNumber: 17
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        children: filteredEmails.length === 0 ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "bg-white rounded-2xl shadow-md p-8 text-center",
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("h3", {
                                    className: "text-lg font-medium text-gray-900",
                                    children: "No emails found"
                                }, void 0, false, {
                                    fileName: "[project]/src/app/emails/page.tsx",
                                    lineNumber: 480,
                                    columnNumber: 29
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                    className: "mt-2 text-sm text-gray-500",
                                    children: "Try adjusting your search or filter to find what you're looking for."
                                }, void 0, false, {
                                    fileName: "[project]/src/app/emails/page.tsx",
                                    lineNumber: 481,
                                    columnNumber: 29
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/src/app/emails/page.tsx",
                            lineNumber: 479,
                            columnNumber: 25
                        }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Fragment"], {
                            children: [
                                filteredEmails.map((email)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$ui$2f$email$2d$card$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["EmailCard"], {
                                        email: email,
                                        onLabelsUpdated: handleLabelsUpdated,
                                        onClick: ()=>{
                                            saveScrollPosition();
                                            router.push(`/emails/${email.id}`);
                                        },
                                        "data-email-card": true
                                    }, email.id, false, {
                                        fileName: "[project]/src/app/emails/page.tsx",
                                        lineNumber: 488,
                                        columnNumber: 33
                                    }, this)),
                                loadingMore && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    className: "flex justify-center py-4",
                                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        className: "animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"
                                    }, void 0, false, {
                                        fileName: "[project]/src/app/emails/page.tsx",
                                        lineNumber: 503,
                                        columnNumber: 37
                                    }, this)
                                }, void 0, false, {
                                    fileName: "[project]/src/app/emails/page.tsx",
                                    lineNumber: 502,
                                    columnNumber: 33
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    ref: observerTarget,
                                    className: "h-10 w-full",
                                    "aria-hidden": "true"
                                }, void 0, false, {
                                    fileName: "[project]/src/app/emails/page.tsx",
                                    lineNumber: 508,
                                    columnNumber: 29
                                }, this),
                                !hasMore && emails.length > 0 && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    className: "text-center py-8 text-gray-500 text-sm",
                                    children: "You've reached the end of the list"
                                }, void 0, false, {
                                    fileName: "[project]/src/app/emails/page.tsx",
                                    lineNumber: 516,
                                    columnNumber: 33
                                }, this)
                            ]
                        }, void 0, true)
                    }, void 0, false, {
                        fileName: "[project]/src/app/emails/page.tsx",
                        lineNumber: 477,
                        columnNumber: 17
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/src/app/emails/page.tsx",
                lineNumber: 408,
                columnNumber: 13
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/src/app/emails/page.tsx",
        lineNumber: 406,
        columnNumber: 9
    }, this);
}
_s(EmailsPage, "8QFCWrfEmL+w70TRsjwATJMuS9g=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRouter"],
        __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useSearchParams"]
    ];
});
_c = EmailsPage;
var _c;
__turbopack_refresh__.register(_c, "EmailsPage");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_refresh__.registerExports(module, globalThis.$RefreshHelpers$);
}
}}),
"[project]/src/app/emails/page.tsx [app-rsc] (ecmascript, Next.js server component, client modules)": ((__turbopack_context__) => {

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, t: __turbopack_require_real__ } = __turbopack_context__;
{
}}),
}]);

//# sourceMappingURL=src_59d8f8._.js.map