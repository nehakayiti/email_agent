(globalThis.TURBOPACK = globalThis.TURBOPACK || []).push(["static/chunks/src_01f8c7._.js", {

"[project]/src/components/ui/iframe-email-viewer.tsx [app-client] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, k: __turbopack_refresh__, m: module, z: __turbopack_require_stub__ } = __turbopack_context__;
{
__turbopack_esm__({
    "IframeEmailViewer": (()=>IframeEmailViewer),
    "default": (()=>__TURBOPACK__default__export__)
});
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
;
var _s = __turbopack_refresh__.signature();
;
function IframeEmailViewer({ htmlContent }) {
    _s();
    const iframeRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(null);
    const [iframeHeight, setIframeHeight] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(600);
    /**
   * Called when the iframe loads. Measures the content height and updates state.
   */ const handleIframeLoad = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "IframeEmailViewer.useCallback[handleIframeLoad]": ()=>{
            if (!iframeRef.current) return;
            const iframe = iframeRef.current;
            const iframeDoc = iframe.contentDocument || iframe.contentWindow?.document;
            if (!iframeDoc) return;
            // Use scrollHeight to get the total height of the iframe content.
            const newHeight = iframeDoc.body.scrollHeight;
            setIframeHeight(newHeight);
        }
    }["IframeEmailViewer.useCallback[handleIframeLoad]"], []);
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("iframe", {
        ref: iframeRef,
        srcDoc: htmlContent,
        onLoad: handleIframeLoad,
        sandbox: "allow-same-origin allow-popups allow-scripts",
        style: {
            width: '100%',
            border: 'none',
            // Dynamically set the height
            height: `${iframeHeight}px`,
            // Optional: smooth scrolling inside the iframe
            overflow: 'auto'
        }
    }, void 0, false, {
        fileName: "[project]/src/components/ui/iframe-email-viewer.tsx",
        lineNumber: 31,
        columnNumber: 5
    }, this);
}
_s(IframeEmailViewer, "WquDs1iNoixL7cFuf77nLYzlkyc=");
_c = IframeEmailViewer;
const __TURBOPACK__default__export__ = IframeEmailViewer;
var _c;
__turbopack_refresh__.register(_c, "IframeEmailViewer");
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
"[project]/src/components/email-content.tsx [app-client] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, k: __turbopack_refresh__, m: module, z: __turbopack_require_stub__ } = __turbopack_context__;
{
__turbopack_esm__({
    "EmailContent": (()=>EmailContent)
});
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/src/lib/api.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$hot$2d$toast$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/react-hot-toast/dist/index.mjs [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$ui$2f$iframe$2d$email$2d$viewer$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/src/components/ui/iframe-email-viewer.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$utils$2f$toast$2d$config$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/src/utils/toast-config.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$ui$2f$email$2d$label$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/src/components/ui/email-label.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$category$2d$context$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/src/lib/category-context.tsx [app-client] (ecmascript)");
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
function decodeBase64Url(str) {
    const base64 = str.replace(/-/g, '+').replace(/_/g, '/');
    try {
        return atob(base64);
    } catch (e) {
        console.error('Failed to decode Base64 string', e);
        return '';
    }
}
function normalizeCategory(cat) {
    if (!cat) return 'primary';
    // Process specific category mappings if needed
    const lowerCat = cat.toLowerCase();
    if (lowerCat === 'promotional') return 'promotions';
    if (lowerCat === 'important') return 'important';
    // For all others, keep the original case from the API
    // This ensures consistent display between list and detail views
    return cat;
}
function extractEmailBody(payload) {
    if (payload.body && payload.body.data) {
        return decodeBase64Url(payload.body.data);
    }
    if (payload.parts && payload.parts.length > 0) {
        const htmlPart = payload.parts.find((part)=>part.mimeType === 'text/html');
        if (htmlPart?.body?.data) {
            return decodeBase64Url(htmlPart.body.data);
        }
        const textPart = payload.parts.find((part)=>part.mimeType === 'text/plain');
        if (textPart?.body?.data) {
            return decodeBase64Url(textPart.body.data);
        }
    }
    return '';
}
function EmailContent({ email, onLabelsUpdated }) {
    _s();
    const [bodyContent, setBodyContent] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])('');
    const [selectedCategory, setSelectedCategory] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])({
        "EmailContent.useState": ()=>{
            // Initialize with the exact category from the API without normalization
            return (email.category || 'primary').toLowerCase();
        }
    }["EmailContent.useState"]);
    const [updating, setUpdating] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const { categories } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$category$2d$context$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCategoryContext"])();
    const decodedContent = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useMemo"])({
        "EmailContent.useMemo[decodedContent]": ()=>{
            if (email?.raw_data?.payload) {
                return extractEmailBody(email.raw_data.payload);
            }
            return '';
        }
    }["EmailContent.useMemo[decodedContent]"], [
        email
    ]);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "EmailContent.useEffect": ()=>{
            setBodyContent(decodedContent);
        }
    }["EmailContent.useEffect"], [
        decodedContent
    ]);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "EmailContent.useEffect": ()=>{
            // When email.category changes, update selectedCategory with exact value from the API
            if (email.category) {
                setSelectedCategory(email.category.toLowerCase());
            }
        }
    }["EmailContent.useEffect"], [
        email.category
    ]);
    // Get category options from the CategoryContext
    const categoryOptions = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useMemo"])({
        "EmailContent.useMemo[categoryOptions]": ()=>{
            // First, grab categories from context and format for dropdown
            const contextCategories = categories.map({
                "EmailContent.useMemo[categoryOptions].contextCategories": (cat)=>({
                        value: cat.name.toLowerCase(),
                        label: cat.display_name,
                        priority: cat.priority
                    })
            }["EmailContent.useMemo[categoryOptions].contextCategories"]);
            // Sort by priority (lower number = higher priority)
            return contextCategories.sort({
                "EmailContent.useMemo[categoryOptions]": (a, b)=>a.priority - b.priority
            }["EmailContent.useMemo[categoryOptions]"]);
        }
    }["EmailContent.useMemo[categoryOptions]"], [
        categories
    ]);
    const handleCategoryChange = async (e)=>{
        const newCategory = e.target.value.toLowerCase();
        // Set the category exactly as selected from the dropdown
        setSelectedCategory(newCategory);
        try {
            setUpdating(true);
            // Show a toast with the loading state that can be dismissed
            const toastId = (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$utils$2f$toast$2d$config$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["showLoadingToast"])('Updating category...');
            // Pass the exact category value to the API
            const response = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["updateEmailCategory"])(email.id, newCategory);
            // Always dismiss the loading toast
            __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$hot$2d$toast$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["toast"].dismiss(toastId);
            if (response.status === 'success') {
                (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$utils$2f$toast$2d$config$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["showSuccessToast"])(response.message || 'Category updated successfully');
                // Update the email object with new category and labels from the API response
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
                // Handle error in successful response but with error status
                (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$utils$2f$toast$2d$config$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["showErrorToast"])(response.message || 'Failed to update category');
            }
        } catch (error) {
            // Dismiss all loading toasts
            (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$utils$2f$toast$2d$config$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["dismissAllToasts"])();
            // Show a meaningful error toast
            const errorMessage = error instanceof Error ? error.message : 'Error updating category';
            (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$utils$2f$toast$2d$config$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["showErrorToast"])(errorMessage);
            console.error('Error updating category:', error);
        } finally{
            setUpdating(false);
        }
    };
    const handleArchive = async ()=>{
        try {
            // Determine if we're archiving or unarchiving
            const isArchived = !email.labels.includes('INBOX');
            const actionText = isArchived ? 'Unarchiving' : 'Archiving';
            // Show a toast with the loading state that can be dismissed
            const toastId = (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$utils$2f$toast$2d$config$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["showLoadingToast"])(`${actionText} email...`);
            const response = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["archiveEmail"])(email.id);
            // Always dismiss the loading toast
            __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$hot$2d$toast$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["toast"].dismiss(toastId);
            if (response.status === 'success') {
                (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$utils$2f$toast$2d$config$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["showSuccessToast"])(response.message || `Email ${isArchived ? 'unarchived' : 'archived'} successfully`);
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
                // Handle error in successful response but with error status
                (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$utils$2f$toast$2d$config$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["showErrorToast"])(response.message || `Failed to ${isArchived ? 'unarchive' : 'archive'} email`);
            }
        } catch (error) {
            // Dismiss all loading toasts
            (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$utils$2f$toast$2d$config$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["dismissAllToasts"])();
            // Show a meaningful error toast
            const errorMessage = error instanceof Error ? error.message : `Error ${email.labels.includes('INBOX') ? 'archiving' : 'unarchiving'} email`;
            (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$utils$2f$toast$2d$config$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["showErrorToast"])(errorMessage);
            console.error(`Error ${email.labels.includes('INBOX') ? 'archiving' : 'unarchiving'} email:`, error);
        }
    };
    // Filter out inconsistent labels - don't show INBOX if email is in TRASH
    const filteredLabels = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useMemo"])({
        "EmailContent.useMemo[filteredLabels]": ()=>{
            if (!email.labels) return [];
            // If this email has TRASH label, don't display INBOX label
            if (email.labels.includes('TRASH')) {
                return email.labels.filter({
                    "EmailContent.useMemo[filteredLabels]": (label)=>label !== 'INBOX'
                }["EmailContent.useMemo[filteredLabels]"]);
            }
            return email.labels;
        }
    }["EmailContent.useMemo[filteredLabels]"], [
        email.labels
    ]);
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "bg-white rounded-lg shadow-md p-6",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("h1", {
                className: "text-xl font-bold mb-2",
                children: email.subject
            }, void 0, false, {
                fileName: "[project]/src/components/email-content.tsx",
                lineNumber: 201,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                className: "mb-2 text-gray-700",
                children: [
                    "From: ",
                    email.from_email
                ]
            }, void 0, true, {
                fileName: "[project]/src/components/email-content.tsx",
                lineNumber: 202,
                columnNumber: 7
            }, this),
            email.labels.includes('TRASH') && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "my-3 px-4 py-3 bg-red-50 border-l-4 border-red-500 text-red-700",
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                    className: "font-semibold",
                    children: "⚠️ This email is in Trash"
                }, void 0, false, {
                    fileName: "[project]/src/components/email-content.tsx",
                    lineNumber: 206,
                    columnNumber: 11
                }, this)
            }, void 0, false, {
                fileName: "[project]/src/components/email-content.tsx",
                lineNumber: 205,
                columnNumber: 9
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "mb-4",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                        className: "font-medium text-sm mb-1",
                        children: "Labels:"
                    }, void 0, false, {
                        fileName: "[project]/src/components/email-content.tsx",
                        lineNumber: 211,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "flex flex-wrap gap-2",
                        children: filteredLabels.length > 0 ? (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$ui$2f$email$2d$label$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["mapLabelsToComponents"])(filteredLabels) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                            className: "text-gray-500",
                            children: "None"
                        }, void 0, false, {
                            fileName: "[project]/src/components/email-content.tsx",
                            lineNumber: 216,
                            columnNumber: 13
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/src/components/email-content.tsx",
                        lineNumber: 212,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/src/components/email-content.tsx",
                lineNumber: 210,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "flex items-center justify-between mb-4",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "flex space-x-2",
                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                            onClick: handleArchive,
                            className: "px-3 py-1 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-md flex items-center text-sm",
                            disabled: updating,
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("svg", {
                                    xmlns: "http://www.w3.org/2000/svg",
                                    className: "h-4 w-4 mr-1",
                                    fill: "none",
                                    viewBox: "0 0 24 24",
                                    stroke: "currentColor",
                                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("path", {
                                        strokeLinecap: "round",
                                        strokeLinejoin: "round",
                                        strokeWidth: 2,
                                        d: "M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8"
                                    }, void 0, false, {
                                        fileName: "[project]/src/components/email-content.tsx",
                                        lineNumber: 229,
                                        columnNumber: 15
                                    }, this)
                                }, void 0, false, {
                                    fileName: "[project]/src/components/email-content.tsx",
                                    lineNumber: 228,
                                    columnNumber: 13
                                }, this),
                                email.labels.includes('INBOX') ? 'Archive' : 'Unarchive'
                            ]
                        }, void 0, true, {
                            fileName: "[project]/src/components/email-content.tsx",
                            lineNumber: 223,
                            columnNumber: 11
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/src/components/email-content.tsx",
                        lineNumber: 222,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "mb-4",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                className: "font-semibold mr-2",
                                children: "Category:"
                            }, void 0, false, {
                                fileName: "[project]/src/components/email-content.tsx",
                                lineNumber: 236,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("select", {
                                value: selectedCategory,
                                onChange: handleCategoryChange,
                                disabled: updating,
                                className: "bg-gray-100 text-gray-800 rounded px-3 py-1 text-xs font-semibold",
                                children: categoryOptions.map((option)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                        value: option.value,
                                        children: option.label
                                    }, option.value, false, {
                                        fileName: "[project]/src/components/email-content.tsx",
                                        lineNumber: 244,
                                        columnNumber: 15
                                    }, this))
                            }, void 0, false, {
                                fileName: "[project]/src/components/email-content.tsx",
                                lineNumber: 237,
                                columnNumber: 11
                            }, this),
                            updating && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                className: "ml-2 text-gray-500 text-xs",
                                children: "Updating..."
                            }, void 0, false, {
                                fileName: "[project]/src/components/email-content.tsx",
                                lineNumber: 249,
                                columnNumber: 24
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/src/components/email-content.tsx",
                        lineNumber: 235,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/src/components/email-content.tsx",
                lineNumber: 221,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "border border-gray-200 rounded",
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$ui$2f$iframe$2d$email$2d$viewer$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["IframeEmailViewer"], {
                    htmlContent: bodyContent
                }, void 0, false, {
                    fileName: "[project]/src/components/email-content.tsx",
                    lineNumber: 255,
                    columnNumber: 9
                }, this)
            }, void 0, false, {
                fileName: "[project]/src/components/email-content.tsx",
                lineNumber: 254,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/src/components/email-content.tsx",
        lineNumber: 200,
        columnNumber: 5
    }, this);
}
_s(EmailContent, "x0oDxAjIATar6SiEWs7Zj5z1QWc=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$category$2d$context$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCategoryContext"]
    ];
});
_c = EmailContent;
var _c;
__turbopack_refresh__.register(_c, "EmailContent");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_refresh__.registerExports(module, globalThis.$RefreshHelpers$);
}
}}),
"[project]/src/components/email-detail.tsx [app-client] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, k: __turbopack_refresh__, m: module, z: __turbopack_require_stub__ } = __turbopack_context__;
{
__turbopack_esm__({
    "default": (()=>EmailDetail)
});
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/next/navigation.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/src/lib/api.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$auth$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/src/lib/auth.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$email$2d$content$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/src/components/email-content.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$hot$2d$toast$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/react-hot-toast/dist/index.mjs [app-client] (ecmascript)");
;
var _s = __turbopack_refresh__.signature();
'use client';
;
;
;
;
;
;
function EmailDetail({ emailId }) {
    _s();
    const router = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRouter"])();
    const searchParams = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useSearchParams"])();
    const [email, setEmail] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [loading, setLoading] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(true);
    const [error, setError] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    // Get any filter parameters that we need to preserve
    const backToEmailsUrl = constructBackUrl(searchParams);
    function constructBackUrl(params) {
        // Start with base URL
        let url = '/emails';
        // Check if we have any params to add
        const category = params?.get('category') ?? null;
        const status = params?.get('status') ?? null;
        const label = params?.get('label') ?? null;
        const queryParams = [];
        if (category) queryParams.push(`category=${category}`);
        if (status) queryParams.push(`status=${status}`);
        if (label) queryParams.push(`label=${label}`);
        // If we're in a trash email detail but no category was specified in URL,
        // and the email has the TRASH label, add the trash category filter
        if (!category && email?.labels?.includes('TRASH')) {
            queryParams.push('category=trash');
        }
        // Add query params if any exist
        if (queryParams.length > 0) {
            url += `?${queryParams.join('&')}`;
        }
        return url;
    }
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "EmailDetail.useEffect": ()=>{
            const fetchEmail = {
                "EmailDetail.useEffect.fetchEmail": async ()=>{
                    try {
                        if (!(0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$auth$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["isAuthenticated"])()) {
                            console.log('User not authenticated, redirecting to authentication');
                            (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$auth$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["handleAuthError"])();
                            return;
                        }
                        setLoading(true);
                        console.log('Fetching email details...');
                        const data = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["getEmailById"])(emailId);
                        console.log('Email details fetched:', data);
                        setEmail(data);
                        setError(null);
                    } catch (err) {
                        console.error('Error in email detail page:', err);
                        const errorMessage = err instanceof Error ? err.message : 'Failed to fetch email';
                        // Check if this is an authentication error
                        if (errorMessage.includes('Authentication failed') || errorMessage.includes('token') || errorMessage.includes('401')) {
                            (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$auth$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["handleAuthError"])();
                            return;
                        }
                        setError(errorMessage);
                    } finally{
                        setLoading(false);
                    }
                }
            }["EmailDetail.useEffect.fetchEmail"];
            if (emailId) {
                fetchEmail();
            }
        }
    }["EmailDetail.useEffect"], [
        emailId,
        router
    ]);
    // Handle label updates
    const handleLabelsUpdated = (updatedEmail)=>{
        setEmail(updatedEmail);
    };
    if (loading) {
        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            className: "flex items-center justify-center h-full",
            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"
            }, void 0, false, {
                fileName: "[project]/src/components/email-detail.tsx",
                lineNumber: 98,
                columnNumber: 17
            }, this)
        }, void 0, false, {
            fileName: "[project]/src/components/email-detail.tsx",
            lineNumber: 97,
            columnNumber: 13
        }, this);
    }
    if (error) {
        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            className: "p-6 bg-white rounded-2xl shadow-lg border border-gray-300",
            children: [
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                    className: "text-blue-600 text-sm mb-4",
                    onClick: ()=>router.push(backToEmailsUrl),
                    children: "← Back to Emails"
                }, void 0, false, {
                    fileName: "[project]/src/components/email-detail.tsx",
                    lineNumber: 106,
                    columnNumber: 17
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: "text-center",
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("h2", {
                            className: "text-xl font-bold text-gray-900 mb-2",
                            children: "Error"
                        }, void 0, false, {
                            fileName: "[project]/src/components/email-detail.tsx",
                            lineNumber: 113,
                            columnNumber: 21
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                            className: "text-gray-600",
                            children: error
                        }, void 0, false, {
                            fileName: "[project]/src/components/email-detail.tsx",
                            lineNumber: 114,
                            columnNumber: 21
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/src/components/email-detail.tsx",
                    lineNumber: 112,
                    columnNumber: 17
                }, this)
            ]
        }, void 0, true, {
            fileName: "[project]/src/components/email-detail.tsx",
            lineNumber: 105,
            columnNumber: 13
        }, this);
    }
    if (!email) {
        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            className: "p-6 bg-white rounded-2xl shadow-lg border border-gray-300",
            children: [
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                    className: "text-blue-600 text-sm mb-4",
                    onClick: ()=>router.push(backToEmailsUrl),
                    children: "← Back to Emails"
                }, void 0, false, {
                    fileName: "[project]/src/components/email-detail.tsx",
                    lineNumber: 123,
                    columnNumber: 17
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: "text-center",
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("h2", {
                            className: "text-xl font-bold text-gray-900 mb-2",
                            children: "Email not found"
                        }, void 0, false, {
                            fileName: "[project]/src/components/email-detail.tsx",
                            lineNumber: 130,
                            columnNumber: 21
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                            className: "text-gray-600",
                            children: "The requested email could not be found."
                        }, void 0, false, {
                            fileName: "[project]/src/components/email-detail.tsx",
                            lineNumber: 131,
                            columnNumber: 21
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/src/components/email-detail.tsx",
                    lineNumber: 129,
                    columnNumber: 17
                }, this)
            ]
        }, void 0, true, {
            fileName: "[project]/src/components/email-detail.tsx",
            lineNumber: 122,
            columnNumber: 13
        }, this);
    }
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "p-6 bg-white rounded-2xl shadow-lg border border-gray-300",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$hot$2d$toast$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Toaster"], {
                position: "top-right",
                toastOptions: {
                    duration: 6000
                }
            }, void 0, false, {
                fileName: "[project]/src/components/email-detail.tsx",
                lineNumber: 139,
                columnNumber: 13
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                className: "text-blue-600 text-sm mb-4",
                onClick: ()=>router.push(backToEmailsUrl),
                children: "← Back to Emails"
            }, void 0, false, {
                fileName: "[project]/src/components/email-detail.tsx",
                lineNumber: 140,
                columnNumber: 13
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$email$2d$content$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["EmailContent"], {
                email: email,
                onLabelsUpdated: handleLabelsUpdated
            }, void 0, false, {
                fileName: "[project]/src/components/email-detail.tsx",
                lineNumber: 146,
                columnNumber: 13
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/src/components/email-detail.tsx",
        lineNumber: 138,
        columnNumber: 9
    }, this);
}
_s(EmailDetail, "oLS/dJNnIgR/vp+jTDcrbOAXTDU=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRouter"],
        __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useSearchParams"]
    ];
});
_c = EmailDetail;
var _c;
__turbopack_refresh__.register(_c, "EmailDetail");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_refresh__.registerExports(module, globalThis.$RefreshHelpers$);
}
}}),
"[project]/src/app/emails/[id]/page.tsx [app-rsc] (ecmascript, Next.js server component, client modules)": ((__turbopack_context__) => {

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, t: __turbopack_require_real__ } = __turbopack_context__;
{
}}),
}]);

//# sourceMappingURL=src_01f8c7._.js.map