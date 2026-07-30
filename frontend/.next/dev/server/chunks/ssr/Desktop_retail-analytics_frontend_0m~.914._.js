module.exports = [
"[project]/Desktop/retail-analytics/frontend/components/theme-provider.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "ThemeProvider",
    ()=>ThemeProvider,
    "useTheme",
    ()=>useTheme
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
'use client';
;
;
const ThemeContext = /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["createContext"])(null);
function ThemeProvider({ children }) {
    const [mounted, setMounted] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(false);
    const [theme, setTheme] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])('light');
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        // Get stored theme or default to light
        const stored = localStorage.getItem('theme');
        const initialTheme = stored || 'light';
        setTheme(initialTheme);
        document.documentElement.classList.remove('light', 'dark');
        document.documentElement.classList.add(initialTheme);
        setMounted(true);
    }, []);
    const toggleTheme = ()=>{
        setTheme((prev)=>{
            const newTheme = prev === 'light' ? 'dark' : 'light';
            localStorage.setItem('theme', newTheme);
            document.documentElement.classList.remove('light', 'dark');
            document.documentElement.classList.add(newTheme);
            return newTheme;
        });
    };
    // Prevent hydration mismatch by suppressing rendering until mounted
    if (!mounted) {
        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Fragment"], {
            children: children
        }, void 0, false);
    }
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(ThemeContext.Provider, {
        value: {
            theme,
            toggleTheme
        },
        children: children
    }, void 0, false, {
        fileName: "[project]/Desktop/retail-analytics/frontend/components/theme-provider.tsx",
        lineNumber: 44,
        columnNumber: 5
    }, this);
}
function useTheme() {
    const context = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useContext"])(ThemeContext);
    if (!context) {
        return {
            theme: 'light',
            toggleTheme: ()=>{}
        };
    }
    return context;
}
}),
"[project]/Desktop/retail-analytics/frontend/lib/nav-config.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "NAV_ITEMS",
    ()=>NAV_ITEMS,
    "OPEN_ALERT_COUNT",
    ()=>OPEN_ALERT_COUNT
]);
const NAV_ITEMS = [
    {
        label: "Overview",
        href: "/"
    },
    {
        label: "Live Cameras",
        href: "/live-cameras"
    },
    {
        label: "Analytics",
        children: [
            {
                label: "Traffic",
                href: "/analytics/traffic"
            },
            {
                label: "Occupancy",
                href: "/analytics/occupancy"
            },
            {
                label: "Zones",
                href: "/analytics/zones"
            },
            {
                label: "Dwell Time",
                href: "/analytics/dwell-time"
            },
            {
                label: "Queues",
                href: "/analytics/queues"
            }
        ]
    },
    {
        label: "Visual Analytics",
        children: [
            {
                label: "Store Heatmap",
                href: "/visual-analytics/heatmap"
            },
            {
                label: "Zone Performance",
                href: "/visual-analytics/zone-performance"
            },
            {
                label: "Customer Flow",
                href: "/visual-analytics/customer-flow"
            }
        ]
    },
    {
        label: "Reports",
        href: "/reports"
    },
    {
        label: "Alerts",
        href: "/alerts"
    },
    {
        label: "Admin",
        children: [
            {
                label: "Cameras",
                href: "/admin/cameras"
            },
            {
                label: "Zones & Lines",
                href: "/admin/zones-lines"
            },
            {
                label: "Users",
                href: "/admin/users"
            }
        ]
    }
];
const OPEN_ALERT_COUNT = 3;
}),
"[project]/Desktop/retail-analytics/frontend/lib/utils.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "cn",
    ()=>cn
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$clsx$2f$dist$2f$clsx$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/clsx/dist/clsx.mjs [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$tailwind$2d$merge$2f$dist$2f$bundle$2d$mjs$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/tailwind-merge/dist/bundle-mjs.mjs [app-ssr] (ecmascript)");
;
;
function cn(...inputs) {
    return (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$tailwind$2d$merge$2f$dist$2f$bundle$2d$mjs$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["twMerge"])((0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$clsx$2f$dist$2f$clsx$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["clsx"])(inputs));
}
}),
"[project]/Desktop/retail-analytics/frontend/components/dashboard/alert-badge.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "AlertBadge",
    ()=>AlertBadge
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/client/app-dir/link.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$bell$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Bell$3e$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/lucide-react/dist/esm/icons/bell.mjs [app-ssr] (ecmascript) <export default as Bell>");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/lib/utils.ts [app-ssr] (ecmascript)");
;
;
;
;
function AlertBadge({ count, className }) {
    const hasAlerts = count > 0;
    const label = hasAlerts ? `${count} open alert${count === 1 ? "" : "s"}` : "No open alerts";
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"], {
        href: "/alerts",
        "aria-label": label,
        title: label,
        className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["cn"])("relative inline-flex size-8 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-muted hover:text-foreground focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-ring/50", className),
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$bell$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Bell$3e$__["Bell"], {
                className: "size-[18px]",
                "aria-hidden": "true"
            }, void 0, false, {
                fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/alert-badge.tsx",
                lineNumber: 22,
                columnNumber: 7
            }, this),
            hasAlerts && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                className: "absolute -right-0.5 -top-0.5 inline-flex min-w-4 items-center justify-center rounded-full bg-destructive px-1 text-[10px] font-semibold leading-4 text-white tabular-nums",
                "aria-hidden": "true",
                children: count > 99 ? "99+" : count
            }, void 0, false, {
                fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/alert-badge.tsx",
                lineNumber: 24,
                columnNumber: 9
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                className: "sr-only",
                children: label
            }, void 0, false, {
                fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/alert-badge.tsx",
                lineNumber: 31,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/alert-badge.tsx",
        lineNumber: 13,
        columnNumber: 5
    }, this);
}
}),
"[project]/Desktop/retail-analytics/frontend/hooks/use-dismiss.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "useDismiss",
    ()=>useDismiss
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
"use client";
;
function useDismiss(ref, open, onClose) {
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        if (!open) return;
        function onPointerDown(event) {
            if (ref.current && !ref.current.contains(event.target)) {
                onClose();
            }
        }
        function onKeyDown(event) {
            if (event.key === "Escape") onClose();
        }
        document.addEventListener("mousedown", onPointerDown);
        document.addEventListener("keydown", onKeyDown);
        return ()=>{
            document.removeEventListener("mousedown", onPointerDown);
            document.removeEventListener("keydown", onKeyDown);
        };
    }, [
        ref,
        open,
        onClose
    ]);
}
}),
"[project]/Desktop/retail-analytics/frontend/components/dashboard/nav-dropdown.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "NavDropdown",
    ()=>NavDropdown
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/client/app-dir/link.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/navigation.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$down$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronDown$3e$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/lucide-react/dist/esm/icons/chevron-down.mjs [app-ssr] (ecmascript) <export default as ChevronDown>");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/lib/utils.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$hooks$2f$use$2d$dismiss$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/hooks/use-dismiss.ts [app-ssr] (ecmascript)");
"use client";
;
;
;
;
;
;
;
function NavDropdown({ label, items }) {
    const [open, setOpen] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(false);
    const ref = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useRef"])(null);
    const pathname = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["usePathname"])();
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$hooks$2f$use$2d$dismiss$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useDismiss"])(ref, open, ()=>setOpen(false));
    const groupActive = items.some((item)=>pathname === item.href);
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "relative",
        ref: ref,
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                type: "button",
                "aria-haspopup": "menu",
                "aria-expanded": open,
                onClick: ()=>setOpen((v)=>!v),
                className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["cn"])("inline-flex items-center gap-1 rounded-lg px-2.5 py-1.5 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-ring/50", groupActive ? "text-foreground" : "text-muted-foreground hover:text-foreground hover:bg-muted"),
                children: [
                    label,
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$down$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronDown$3e$__["ChevronDown"], {
                        className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["cn"])("size-3.5 transition-transform", open && "rotate-180"),
                        "aria-hidden": "true"
                    }, void 0, false, {
                        fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/nav-dropdown.tsx",
                        lineNumber: 35,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/nav-dropdown.tsx",
                lineNumber: 22,
                columnNumber: 7
            }, this),
            open && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                role: "menu",
                "aria-label": label,
                className: "absolute left-0 top-full z-50 mt-1.5 w-52 overflow-hidden rounded-xl border border-border bg-popover p-1 shadow-lg",
                children: items.map((item)=>{
                    const active = pathname === item.href;
                    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"], {
                        href: item.href,
                        role: "menuitem",
                        onClick: ()=>setOpen(false),
                        "aria-current": active ? "page" : undefined,
                        className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["cn"])("block rounded-lg px-2.5 py-2 text-sm transition-colors", active ? "bg-muted font-medium text-foreground" : "text-foreground hover:bg-muted"),
                        children: item.label
                    }, item.href, false, {
                        fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/nav-dropdown.tsx",
                        lineNumber: 50,
                        columnNumber: 15
                    }, this);
                })
            }, void 0, false, {
                fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/nav-dropdown.tsx",
                lineNumber: 42,
                columnNumber: 9
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/nav-dropdown.tsx",
        lineNumber: 21,
        columnNumber: 5
    }, this);
}
}),
"[project]/Desktop/retail-analytics/frontend/components/dashboard/organization-label.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "OrganizationLabel",
    ()=>OrganizationLabel
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$scope$2f$ScopeContext$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/lib/scope/ScopeContext.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/lib/utils.ts [app-ssr] (ecmascript)");
"use client";
;
;
;
function OrganizationLabel({ className }) {
    const { organization, isLoading } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$scope$2f$ScopeContext$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useScope"])();
    if (isLoading || !organization) {
        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
            className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["cn"])("h-8 w-24 animate-pulse rounded-md bg-muted sm:w-28", className),
            "aria-hidden": "true"
        }, void 0, false, {
            fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/organization-label.tsx",
            lineNumber: 11,
            columnNumber: 7
        }, this);
    }
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["cn"])("flex min-w-0 max-w-[9rem] flex-col leading-tight sm:max-w-xs", className),
        "aria-label": `Organization: ${organization.name}`,
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                className: "text-[10px] font-medium uppercase tracking-wide text-muted-foreground",
                children: "Organization"
            }, void 0, false, {
                fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/organization-label.tsx",
                lineNumber: 26,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                className: "truncate text-sm font-medium text-foreground",
                children: organization.name
            }, void 0, false, {
                fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/organization-label.tsx",
                lineNumber: 29,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/organization-label.tsx",
        lineNumber: 19,
        columnNumber: 5
    }, this);
}
}),
"[project]/Desktop/retail-analytics/frontend/components/ui/button.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "Button",
    ()=>Button,
    "buttonVariants",
    ()=>buttonVariants
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f40$base$2d$ui$2f$react$2f$button$2f$Button$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/@base-ui/react/button/Button.mjs [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$class$2d$variance$2d$authority$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/class-variance-authority/dist/index.mjs [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/lib/utils.ts [app-ssr] (ecmascript)");
;
;
;
;
const buttonVariants = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$class$2d$variance$2d$authority$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["cva"])("group/button inline-flex shrink-0 items-center justify-center rounded-lg border border-transparent bg-clip-padding text-sm font-medium whitespace-nowrap transition-all outline-none select-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 active:not-aria-[haspopup]:translate-y-px disabled:pointer-events-none disabled:opacity-50 aria-invalid:border-destructive aria-invalid:ring-3 aria-invalid:ring-destructive/20 dark:aria-invalid:border-destructive/50 dark:aria-invalid:ring-destructive/40 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4", {
    variants: {
        variant: {
            default: 'bg-primary text-primary-foreground [a]:hover:bg-primary/80',
            outline: 'border-border bg-background hover:bg-muted hover:text-foreground aria-expanded:bg-muted aria-expanded:text-foreground dark:border-input dark:bg-input/30 dark:hover:bg-input/50',
            secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80 aria-expanded:bg-secondary aria-expanded:text-secondary-foreground',
            ghost: 'hover:bg-muted hover:text-foreground aria-expanded:bg-muted aria-expanded:text-foreground dark:hover:bg-muted/50',
            destructive: 'bg-destructive/10 text-destructive hover:bg-destructive/20 focus-visible:border-destructive/40 focus-visible:ring-destructive/20 dark:bg-destructive/20 dark:hover:bg-destructive/30 dark:focus-visible:ring-destructive/40',
            link: 'text-primary underline-offset-4 hover:underline'
        },
        size: {
            default: 'h-8 gap-1.5 px-2.5 has-data-[icon=inline-end]:pr-2 has-data-[icon=inline-start]:pl-2',
            xs: "h-6 gap-1 rounded-[min(var(--radius-md),10px)] px-2 text-xs in-data-[slot=button-group]:rounded-lg has-data-[icon=inline-end]:pr-1.5 has-data-[icon=inline-start]:pl-1.5 [&_svg:not([class*='size-'])]:size-3",
            sm: "h-7 gap-1 rounded-[min(var(--radius-md),12px)] px-2.5 text-[0.8rem] in-data-[slot=button-group]:rounded-lg has-data-[icon=inline-end]:pr-1.5 has-data-[icon=inline-start]:pl-1.5 [&_svg:not([class*='size-'])]:size-3.5",
            lg: 'h-9 gap-1.5 px-2.5 has-data-[icon=inline-end]:pr-2 has-data-[icon=inline-start]:pl-2',
            icon: 'size-8',
            'icon-xs': "size-6 rounded-[min(var(--radius-md),10px)] in-data-[slot=button-group]:rounded-lg [&_svg:not([class*='size-'])]:size-3",
            'icon-sm': 'size-7 rounded-[min(var(--radius-md),12px)] in-data-[slot=button-group]:rounded-lg',
            'icon-lg': 'size-9'
        }
    },
    defaultVariants: {
        variant: 'default',
        size: 'default'
    }
});
function Button({ className, variant = 'default', size = 'default', ...props }) {
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f40$base$2d$ui$2f$react$2f$button$2f$Button$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Button"], {
        "data-slot": "button",
        className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["cn"])(buttonVariants({
            variant,
            size,
            className
        })),
        ...props
    }, void 0, false, {
        fileName: "[project]/Desktop/retail-analytics/frontend/components/ui/button.tsx",
        lineNumber: 50,
        columnNumber: 5
    }, this);
}
;
}),
"[project]/Desktop/retail-analytics/frontend/components/dashboard/theme-toggle.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "ThemeToggle",
    ()=>ThemeToggle
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$moon$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Moon$3e$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/lucide-react/dist/esm/icons/moon.mjs [app-ssr] (ecmascript) <export default as Moon>");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$sun$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Sun$3e$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/lucide-react/dist/esm/icons/sun.mjs [app-ssr] (ecmascript) <export default as Sun>");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$theme$2d$provider$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/components/theme-provider.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$ui$2f$button$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/components/ui/button.tsx [app-ssr] (ecmascript)");
'use client';
;
;
;
;
function ThemeToggle() {
    const { theme, toggleTheme } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$theme$2d$provider$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useTheme"])();
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$ui$2f$button$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Button"], {
        variant: "ghost",
        size: "icon",
        onClick: toggleTheme,
        "aria-label": "Toggle theme",
        className: "h-9 w-9",
        children: theme === 'light' ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$moon$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Moon$3e$__["Moon"], {
            className: "h-4 w-4"
        }, void 0, false, {
            fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/theme-toggle.tsx",
            lineNumber: 19,
            columnNumber: 9
        }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$sun$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Sun$3e$__["Sun"], {
            className: "h-4 w-4"
        }, void 0, false, {
            fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/theme-toggle.tsx",
            lineNumber: 21,
            columnNumber: 9
        }, this)
    }, void 0, false, {
        fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/theme-toggle.tsx",
        lineNumber: 11,
        columnNumber: 5
    }, this);
}
}),
"[project]/Desktop/retail-analytics/frontend/components/dashboard/user-menu.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "UserMenu",
    ()=>UserMenu
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$down$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronDown$3e$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/lucide-react/dist/esm/icons/chevron-down.mjs [app-ssr] (ecmascript) <export default as ChevronDown>");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$log$2d$out$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__LogOut$3e$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/lucide-react/dist/esm/icons/log-out.mjs [app-ssr] (ecmascript) <export default as LogOut>");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$auth$2f$AuthContext$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/lib/auth/AuthContext.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$hooks$2f$use$2d$dismiss$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/hooks/use-dismiss.ts [app-ssr] (ecmascript)");
"use client";
;
;
;
;
;
function userInitials(name) {
    return name.split(" ").map((part)=>part[0]).join("").toUpperCase().slice(0, 2);
}
function UserMenu() {
    const [open, setOpen] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(false);
    const { user, isLoading, logout } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$auth$2f$AuthContext$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useAuth"])();
    const ref = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useRef"])(null);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$hooks$2f$use$2d$dismiss$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useDismiss"])(ref, open, ()=>setOpen(false));
    async function handleLogout() {
        setOpen(false);
        await logout();
    }
    if (isLoading) {
        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            className: "flex items-center gap-2 py-1 pl-1 pr-1.5",
            "aria-label": "Loading user menu",
            children: [
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                    className: "size-8 shrink-0 animate-pulse rounded-full bg-muted"
                }, void 0, false, {
                    fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/user-menu.tsx",
                    lineNumber: 35,
                    columnNumber: 9
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                    className: "hidden min-w-0 flex-col gap-1 sm:flex",
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                            className: "h-3.5 w-20 animate-pulse rounded bg-muted"
                        }, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/user-menu.tsx",
                            lineNumber: 37,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                            className: "h-3 w-24 animate-pulse rounded bg-muted"
                        }, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/user-menu.tsx",
                            lineNumber: 38,
                            columnNumber: 11
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/user-menu.tsx",
                    lineNumber: 36,
                    columnNumber: 9
                }, this)
            ]
        }, void 0, true, {
            fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/user-menu.tsx",
            lineNumber: 31,
            columnNumber: 7
        }, this);
    }
    if (!user) {
        return null;
    }
    const initials = userInitials(user.name);
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "relative",
        ref: ref,
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                type: "button",
                "aria-haspopup": "menu",
                "aria-expanded": open,
                "aria-label": `${user.name}, ${user.role}`,
                onClick: ()=>setOpen((v)=>!v),
                className: "flex items-center gap-2 rounded-lg py-1 pl-1 pr-1.5 text-left transition-colors hover:bg-muted focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-ring/50",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                        className: "flex size-8 shrink-0 items-center justify-center rounded-full bg-primary text-xs font-semibold text-primary-foreground",
                        "aria-hidden": "true",
                        children: initials
                    }, void 0, false, {
                        fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/user-menu.tsx",
                        lineNumber: 60,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                        className: "hidden min-w-0 flex-col leading-tight sm:flex",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                className: "truncate text-sm font-medium text-foreground",
                                children: user.name
                            }, void 0, false, {
                                fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/user-menu.tsx",
                                lineNumber: 67,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                className: "truncate text-xs text-muted-foreground",
                                children: user.role
                            }, void 0, false, {
                                fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/user-menu.tsx",
                                lineNumber: 68,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/user-menu.tsx",
                        lineNumber: 66,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$down$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronDown$3e$__["ChevronDown"], {
                        className: "hidden size-4 text-muted-foreground sm:block",
                        "aria-hidden": "true"
                    }, void 0, false, {
                        fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/user-menu.tsx",
                        lineNumber: 70,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/user-menu.tsx",
                lineNumber: 52,
                columnNumber: 7
            }, this),
            open && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                role: "menu",
                className: "absolute right-0 top-full z-50 mt-1.5 w-56 overflow-hidden rounded-xl border border-border bg-popover p-1 shadow-lg",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "px-2.5 py-2 sm:hidden",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                className: "text-sm font-medium text-foreground",
                                children: user.name
                            }, void 0, false, {
                                fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/user-menu.tsx",
                                lineNumber: 79,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                className: "text-xs text-muted-foreground",
                                children: user.role
                            }, void 0, false, {
                                fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/user-menu.tsx",
                                lineNumber: 80,
                                columnNumber: 13
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/user-menu.tsx",
                        lineNumber: 78,
                        columnNumber: 11
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "my-1 h-px bg-border sm:hidden"
                    }, void 0, false, {
                        fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/user-menu.tsx",
                        lineNumber: 82,
                        columnNumber: 11
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                        type: "button",
                        role: "menuitem",
                        onClick: handleLogout,
                        className: "flex w-full items-center gap-2 rounded-lg px-2.5 py-2 text-sm text-foreground transition-colors hover:bg-muted focus-visible:bg-muted focus-visible:outline-none",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$log$2d$out$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__LogOut$3e$__["LogOut"], {
                                className: "size-4 text-muted-foreground",
                                "aria-hidden": "true"
                            }, void 0, false, {
                                fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/user-menu.tsx",
                                lineNumber: 89,
                                columnNumber: 13
                            }, this),
                            "Log out"
                        ]
                    }, void 0, true, {
                        fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/user-menu.tsx",
                        lineNumber: 83,
                        columnNumber: 11
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/user-menu.tsx",
                lineNumber: 74,
                columnNumber: 9
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/user-menu.tsx",
        lineNumber: 51,
        columnNumber: 5
    }, this);
}
}),
"[project]/Desktop/retail-analytics/frontend/components/dashboard/top-nav.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "TopNav",
    ()=>TopNav
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/client/app-dir/link.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/navigation.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$activity$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Activity$3e$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/lucide-react/dist/esm/icons/activity.mjs [app-ssr] (ecmascript) <export default as Activity>");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$menu$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Menu$3e$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/lucide-react/dist/esm/icons/menu.mjs [app-ssr] (ecmascript) <export default as Menu>");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$x$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__X$3e$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/lucide-react/dist/esm/icons/x.mjs [app-ssr] (ecmascript) <export default as X>");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$nav$2d$config$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/lib/nav-config.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/lib/utils.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$dashboard$2f$alert$2d$badge$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/components/dashboard/alert-badge.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$dashboard$2f$nav$2d$dropdown$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/components/dashboard/nav-dropdown.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$dashboard$2f$organization$2d$label$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/components/dashboard/organization-label.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$dashboard$2f$theme$2d$toggle$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/components/dashboard/theme-toggle.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$dashboard$2f$user$2d$menu$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/components/dashboard/user-menu.tsx [app-ssr] (ecmascript)");
"use client";
;
;
;
;
;
;
;
;
;
;
;
;
function DesktopNav() {
    const pathname = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["usePathname"])();
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("nav", {
        "aria-label": "Primary",
        className: "hidden items-center gap-0.5 lg:flex",
        children: __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$nav$2d$config$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["NAV_ITEMS"].map((item)=>item.children ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$dashboard$2f$nav$2d$dropdown$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["NavDropdown"], {
                label: item.label,
                items: item.children
            }, item.label, false, {
                fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/top-nav.tsx",
                lineNumber: 23,
                columnNumber: 11
            }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"], {
                href: item.href,
                "aria-current": pathname === item.href ? "page" : undefined,
                className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["cn"])("rounded-lg px-2.5 py-1.5 text-sm font-medium transition-colors", pathname === item.href ? "bg-muted text-foreground" : "text-muted-foreground hover:bg-muted hover:text-foreground"),
                children: item.label
            }, item.label, false, {
                fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/top-nav.tsx",
                lineNumber: 25,
                columnNumber: 11
            }, this))
    }, void 0, false, {
        fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/top-nav.tsx",
        lineNumber: 20,
        columnNumber: 5
    }, this);
}
function MobileNav() {
    const [open, setOpen] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(false);
    const pathname = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["usePathname"])();
    // Close the drawer whenever the route changes.
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        setOpen(false);
    }, [
        pathname
    ]);
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "lg:hidden",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                type: "button",
                "aria-label": open ? "Close menu" : "Open menu",
                "aria-expanded": open,
                onClick: ()=>setOpen((v)=>!v),
                className: "inline-flex size-8 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-muted hover:text-foreground focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-ring/50",
                children: open ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$x$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__X$3e$__["X"], {
                    className: "size-5",
                    "aria-hidden": "true"
                }, void 0, false, {
                    fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/top-nav.tsx",
                    lineNumber: 62,
                    columnNumber: 17
                }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$menu$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Menu$3e$__["Menu"], {
                    className: "size-5",
                    "aria-hidden": "true"
                }, void 0, false, {
                    fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/top-nav.tsx",
                    lineNumber: 62,
                    columnNumber: 63
                }, this)
            }, void 0, false, {
                fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/top-nav.tsx",
                lineNumber: 55,
                columnNumber: 7
            }, this),
            open && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Fragment"], {
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "fixed inset-0 top-14 z-40 bg-foreground/20",
                        "aria-hidden": "true",
                        onClick: ()=>setOpen(false)
                    }, void 0, false, {
                        fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/top-nav.tsx",
                        lineNumber: 67,
                        columnNumber: 11
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("nav", {
                        "aria-label": "Primary",
                        className: "fixed inset-x-0 top-14 z-50 max-h-[calc(100dvh-3.5rem)] overflow-auto border-b border-border bg-background p-3 shadow-lg",
                        children: __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$nav$2d$config$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["NAV_ITEMS"].map((item)=>item.children ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "py-1",
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                        className: "px-2.5 pb-1 pt-2 text-[11px] font-semibold uppercase tracking-wide text-muted-foreground",
                                        children: item.label
                                    }, void 0, false, {
                                        fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/top-nav.tsx",
                                        lineNumber: 79,
                                        columnNumber: 19
                                    }, this),
                                    item.children.map((child)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"], {
                                            href: child.href,
                                            "aria-current": pathname === child.href ? "page" : undefined,
                                            className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["cn"])("block rounded-lg px-2.5 py-2 text-sm transition-colors", pathname === child.href ? "bg-muted font-medium text-foreground" : "text-foreground hover:bg-muted"),
                                            children: child.label
                                        }, child.href, false, {
                                            fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/top-nav.tsx",
                                            lineNumber: 83,
                                            columnNumber: 21
                                        }, this))
                                ]
                            }, item.label, true, {
                                fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/top-nav.tsx",
                                lineNumber: 78,
                                columnNumber: 17
                            }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"], {
                                href: item.href,
                                "aria-current": pathname === item.href ? "page" : undefined,
                                className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["cn"])("block rounded-lg px-2.5 py-2 text-sm font-medium transition-colors", pathname === item.href ? "bg-muted text-foreground" : "text-foreground hover:bg-muted"),
                                children: item.label
                            }, item.label, false, {
                                fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/top-nav.tsx",
                                lineNumber: 99,
                                columnNumber: 17
                            }, this))
                    }, void 0, false, {
                        fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/top-nav.tsx",
                        lineNumber: 72,
                        columnNumber: 11
                    }, this)
                ]
            }, void 0, true)
        ]
    }, void 0, true, {
        fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/top-nav.tsx",
        lineNumber: 54,
        columnNumber: 5
    }, this);
}
function TopNav() {
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("header", {
        className: "sticky top-0 z-50 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/80",
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            className: "flex h-14 items-center gap-2 px-4 sm:px-6",
            children: [
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: "flex items-center gap-2 lg:gap-6",
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"], {
                            href: "/",
                            className: "flex items-center gap-2",
                            "aria-label": "Retail Analytics home",
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                    className: "flex size-8 items-center justify-center rounded-lg bg-primary text-primary-foreground",
                                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$activity$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Activity$3e$__["Activity"], {
                                        className: "size-[18px]",
                                        "aria-hidden": "true"
                                    }, void 0, false, {
                                        fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/top-nav.tsx",
                                        lineNumber: 128,
                                        columnNumber: 15
                                    }, this)
                                }, void 0, false, {
                                    fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/top-nav.tsx",
                                    lineNumber: 127,
                                    columnNumber: 13
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                    className: "hidden text-sm font-semibold tracking-tight text-foreground sm:block",
                                    children: [
                                        "Retail",
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                            className: "text-muted-foreground",
                                            children: "IQ"
                                        }, void 0, false, {
                                            fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/top-nav.tsx",
                                            lineNumber: 131,
                                            columnNumber: 21
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/top-nav.tsx",
                                    lineNumber: 130,
                                    columnNumber: 13
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/top-nav.tsx",
                            lineNumber: 126,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "hidden h-8 w-px bg-border md:block",
                            "aria-hidden": "true"
                        }, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/top-nav.tsx",
                            lineNumber: 134,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$dashboard$2f$organization$2d$label$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["OrganizationLabel"], {}, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/top-nav.tsx",
                            lineNumber: 135,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(DesktopNav, {}, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/top-nav.tsx",
                            lineNumber: 136,
                            columnNumber: 11
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/top-nav.tsx",
                    lineNumber: 125,
                    columnNumber: 9
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: "ml-auto flex items-center gap-1 sm:gap-2",
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$dashboard$2f$alert$2d$badge$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["AlertBadge"], {
                            count: __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$nav$2d$config$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["OPEN_ALERT_COUNT"]
                        }, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/top-nav.tsx",
                            lineNumber: 140,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$dashboard$2f$theme$2d$toggle$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["ThemeToggle"], {}, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/top-nav.tsx",
                            lineNumber: 141,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "mx-1 hidden h-6 w-px bg-border sm:block"
                        }, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/top-nav.tsx",
                            lineNumber: 142,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$dashboard$2f$user$2d$menu$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["UserMenu"], {}, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/top-nav.tsx",
                            lineNumber: 143,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(MobileNav, {}, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/top-nav.tsx",
                            lineNumber: 144,
                            columnNumber: 11
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/top-nav.tsx",
                    lineNumber: 139,
                    columnNumber: 9
                }, this)
            ]
        }, void 0, true, {
            fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/top-nav.tsx",
            lineNumber: 124,
            columnNumber: 7
        }, this)
    }, void 0, false, {
        fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/top-nav.tsx",
        lineNumber: 123,
        columnNumber: 5
    }, this);
}
}),
"[project]/Desktop/retail-analytics/frontend/components/dashboard/scope-selector.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "ScopeSelector",
    ()=>ScopeSelector
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$check$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Check$3e$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/lucide-react/dist/esm/icons/check.mjs [app-ssr] (ecmascript) <export default as Check>");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$down$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronDown$3e$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/lucide-react/dist/esm/icons/chevron-down.mjs [app-ssr] (ecmascript) <export default as ChevronDown>");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$right$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronRight$3e$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/lucide-react/dist/esm/icons/chevron-right.mjs [app-ssr] (ecmascript) <export default as ChevronRight>");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$scope$2f$ScopeContext$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/lib/scope/ScopeContext.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/lib/utils.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$hooks$2f$use$2d$dismiss$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/hooks/use-dismiss.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
"use client";
;
;
;
;
;
;
function ScopeSelect({ label, options, value, onChange, disabled }) {
    const [open, setOpen] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(false);
    const ref = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useRef"])(null);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$hooks$2f$use$2d$dismiss$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useDismiss"])(ref, open, ()=>setOpen(false));
    const selected = options.find((o)=>o.id === value);
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "relative min-w-0 flex-1 sm:flex-none",
        ref: ref,
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                type: "button",
                disabled: disabled,
                "aria-haspopup": "listbox",
                "aria-expanded": open,
                "aria-label": `${label}: ${selected?.name ?? "none selected"}`,
                onClick: ()=>setOpen((v)=>!v),
                className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["cn"])("flex h-9 w-full items-center gap-2 rounded-lg border border-border bg-background px-2.5 text-left transition-colors sm:w-52", "hover:bg-muted focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-ring/50", "disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:bg-background"),
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                        className: "flex min-w-0 flex-col leading-tight",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                className: "text-[10px] font-medium uppercase tracking-wide text-muted-foreground",
                                children: label
                            }, void 0, false, {
                                fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/scope-selector.tsx",
                                lineNumber: 47,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                className: "truncate text-sm text-foreground",
                                children: selected?.name ?? "Select…"
                            }, void 0, false, {
                                fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/scope-selector.tsx",
                                lineNumber: 50,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/scope-selector.tsx",
                        lineNumber: 46,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$down$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronDown$3e$__["ChevronDown"], {
                        className: "ml-auto size-4 shrink-0 text-muted-foreground",
                        "aria-hidden": "true"
                    }, void 0, false, {
                        fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/scope-selector.tsx",
                        lineNumber: 54,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/scope-selector.tsx",
                lineNumber: 33,
                columnNumber: 7
            }, this),
            open && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                role: "listbox",
                "aria-label": label,
                className: "absolute left-0 top-full z-50 mt-1.5 max-h-72 w-full min-w-52 overflow-auto rounded-xl border border-border bg-popover p-1 shadow-lg",
                children: options.map((option)=>{
                    const active = option.id === value;
                    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                        type: "button",
                        role: "option",
                        "aria-selected": active,
                        onClick: ()=>{
                            onChange(option.id);
                            setOpen(false);
                        },
                        className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["cn"])("flex w-full items-center gap-2 rounded-lg px-2.5 py-2 text-left text-sm transition-colors", active ? "bg-muted font-medium text-foreground" : "text-foreground hover:bg-muted"),
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                className: "truncate",
                                children: option.name
                            }, void 0, false, {
                                fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/scope-selector.tsx",
                                lineNumber: 80,
                                columnNumber: 17
                            }, this),
                            active && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$check$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Check$3e$__["Check"], {
                                className: "ml-auto size-4 shrink-0 text-primary",
                                "aria-hidden": "true"
                            }, void 0, false, {
                                fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/scope-selector.tsx",
                                lineNumber: 81,
                                columnNumber: 28
                            }, this)
                        ]
                    }, option.id, true, {
                        fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/scope-selector.tsx",
                        lineNumber: 66,
                        columnNumber: 15
                    }, this);
                })
            }, void 0, false, {
                fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/scope-selector.tsx",
                lineNumber: 58,
                columnNumber: 9
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/scope-selector.tsx",
        lineNumber: 32,
        columnNumber: 5
    }, this);
}
function ScopeSelector({ className }) {
    const { isLoading, organization, storeId, cameraId, zoneId, store, camera, setStoreId, setCameraId, setZoneId } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$scope$2f$ScopeContext$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useScope"])();
    if (isLoading || !organization) {
        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["cn"])("flex items-center gap-2 text-xs text-muted-foreground", className),
            children: [
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                    className: "inline-block h-4 w-4 rounded-full border-2 border-muted-foreground/40 border-t-muted-foreground animate-spin"
                }, void 0, false, {
                    fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/scope-selector.tsx",
                    lineNumber: 108,
                    columnNumber: 9
                }, this),
                "Loading scope…"
            ]
        }, void 0, true, {
            fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/scope-selector.tsx",
            lineNumber: 107,
            columnNumber: 7
        }, this);
    }
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["cn"])("flex flex-col gap-2 sm:flex-row sm:flex-wrap sm:items-center", className),
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                className: "hidden items-center gap-1.5 pr-1 text-xs font-medium text-muted-foreground lg:flex",
                children: [
                    "Scope",
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$right$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronRight$3e$__["ChevronRight"], {
                        className: "size-3.5",
                        "aria-hidden": "true"
                    }, void 0, false, {
                        fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/scope-selector.tsx",
                        lineNumber: 123,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/scope-selector.tsx",
                lineNumber: 121,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(ScopeSelect, {
                label: "Store",
                options: organization.stores,
                value: storeId,
                onChange: setStoreId
            }, void 0, false, {
                fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/scope-selector.tsx",
                lineNumber: 126,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(ScopeSelect, {
                label: "Camera",
                options: store?.cameras ?? [],
                value: cameraId,
                disabled: !store,
                onChange: setCameraId
            }, void 0, false, {
                fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/scope-selector.tsx",
                lineNumber: 133,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(ScopeSelect, {
                label: "Zone",
                options: camera?.zones ?? [],
                value: zoneId,
                disabled: !camera,
                onChange: setZoneId
            }, void 0, false, {
                fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/scope-selector.tsx",
                lineNumber: 141,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/scope-selector.tsx",
        lineNumber: 115,
        columnNumber: 5
    }, this);
}
}),
"[project]/Desktop/retail-analytics/frontend/components/dashboard/dashboard-shell.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "DashboardShell",
    ()=>DashboardShell
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$theme$2d$provider$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/components/theme-provider.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$dashboard$2f$top$2d$nav$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/components/dashboard/top-nav.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$dashboard$2f$scope$2d$selector$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/components/dashboard/scope-selector.tsx [app-ssr] (ecmascript)");
"use client";
;
;
;
;
function DashboardShell({ children }) {
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$theme$2d$provider$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["ThemeProvider"], {
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            className: "flex min-h-dvh flex-col bg-background",
            children: [
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$dashboard$2f$top$2d$nav$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["TopNav"], {}, void 0, false, {
                    fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/dashboard-shell.tsx",
                    lineNumber: 13,
                    columnNumber: 9
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: "sticky top-14 z-40 border-b border-border bg-muted/40",
                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "px-4 py-2.5 sm:px-6",
                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$dashboard$2f$scope$2d$selector$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["ScopeSelector"], {}, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/dashboard-shell.tsx",
                            lineNumber: 18,
                            columnNumber: 13
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/dashboard-shell.tsx",
                        lineNumber: 17,
                        columnNumber: 11
                    }, this)
                }, void 0, false, {
                    fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/dashboard-shell.tsx",
                    lineNumber: 16,
                    columnNumber: 9
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("main", {
                    className: "flex-1 px-4 py-6 sm:px-6",
                    children: children
                }, void 0, false, {
                    fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/dashboard-shell.tsx",
                    lineNumber: 22,
                    columnNumber: 9
                }, this)
            ]
        }, void 0, true, {
            fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/dashboard-shell.tsx",
            lineNumber: 12,
            columnNumber: 7
        }, this)
    }, void 0, false, {
        fileName: "[project]/Desktop/retail-analytics/frontend/components/dashboard/dashboard-shell.tsx",
        lineNumber: 11,
        columnNumber: 5
    }, this);
}
}),
"[project]/Desktop/retail-analytics/frontend/components/overview/kpi-card.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "KPICard",
    ()=>KPICard
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$users$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Users$3e$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/lucide-react/dist/esm/icons/users.mjs [app-ssr] (ecmascript) <export default as Users>");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$activity$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Activity$3e$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/lucide-react/dist/esm/icons/activity.mjs [app-ssr] (ecmascript) <export default as Activity>");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$zap$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Zap$3e$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/lucide-react/dist/esm/icons/zap.mjs [app-ssr] (ecmascript) <export default as Zap>");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$clock$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Clock$3e$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/lucide-react/dist/esm/icons/clock.mjs [app-ssr] (ecmascript) <export default as Clock>");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$list$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__List$3e$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/lucide-react/dist/esm/icons/list.mjs [app-ssr] (ecmascript) <export default as List>");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$camera$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Camera$3e$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/lucide-react/dist/esm/icons/camera.mjs [app-ssr] (ecmascript) <export default as Camera>");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$trending$2d$up$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__TrendingUp$3e$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/lucide-react/dist/esm/icons/trending-up.mjs [app-ssr] (ecmascript) <export default as TrendingUp>");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$trending$2d$down$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__TrendingDown$3e$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/lucide-react/dist/esm/icons/trending-down.mjs [app-ssr] (ecmascript) <export default as TrendingDown>");
;
;
const iconMap = {
    users: __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$users$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Users$3e$__["Users"],
    activity: __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$activity$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Activity$3e$__["Activity"],
    zap: __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$zap$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Zap$3e$__["Zap"],
    clock: __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$clock$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Clock$3e$__["Clock"],
    list: __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$list$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__List$3e$__["List"],
    camera: __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$camera$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Camera$3e$__["Camera"]
};
function KPICard({ label, value, unit, subtext, trend, icon, isLoading }) {
    const IconComponent = iconMap[icon];
    const isTrendPositive = trend ? trend > 0 : false;
    if (isLoading) {
        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            className: "rounded-lg border border-border bg-card p-6",
            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "flex items-start justify-between",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "flex-1",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "mb-3 h-5 w-24 animate-pulse rounded bg-muted"
                            }, void 0, false, {
                                fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/kpi-card.tsx",
                                lineNumber: 48,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "mb-2 h-10 w-32 animate-pulse rounded bg-muted"
                            }, void 0, false, {
                                fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/kpi-card.tsx",
                                lineNumber: 49,
                                columnNumber: 13
                            }, this),
                            subtext && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "h-4 w-20 animate-pulse rounded bg-muted"
                            }, void 0, false, {
                                fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/kpi-card.tsx",
                                lineNumber: 51,
                                columnNumber: 15
                            }, this),
                            trend !== undefined && !subtext && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "mt-2 h-4 w-16 animate-pulse rounded bg-muted"
                            }, void 0, false, {
                                fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/kpi-card.tsx",
                                lineNumber: 54,
                                columnNumber: 15
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/kpi-card.tsx",
                        lineNumber: 47,
                        columnNumber: 11
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "h-10 w-10 animate-pulse rounded-lg bg-muted"
                    }, void 0, false, {
                        fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/kpi-card.tsx",
                        lineNumber: 57,
                        columnNumber: 11
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/kpi-card.tsx",
                lineNumber: 46,
                columnNumber: 9
            }, this)
        }, void 0, false, {
            fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/kpi-card.tsx",
            lineNumber: 45,
            columnNumber: 7
        }, this);
    }
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "rounded-lg border border-border bg-card p-6",
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            className: "flex items-start justify-between",
            children: [
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: "flex-1",
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                            className: "text-sm font-medium text-muted-foreground",
                            children: label
                        }, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/kpi-card.tsx",
                            lineNumber: 67,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "mt-2 flex items-baseline gap-1",
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                    className: "text-3xl font-semibold tracking-tight text-foreground",
                                    children: value
                                }, void 0, false, {
                                    fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/kpi-card.tsx",
                                    lineNumber: 69,
                                    columnNumber: 13
                                }, this),
                                unit && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                    className: "text-lg text-muted-foreground",
                                    children: unit
                                }, void 0, false, {
                                    fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/kpi-card.tsx",
                                    lineNumber: 72,
                                    columnNumber: 22
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/kpi-card.tsx",
                            lineNumber: 68,
                            columnNumber: 11
                        }, this),
                        subtext && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                            className: "mt-1 text-xs text-muted-foreground",
                            children: subtext
                        }, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/kpi-card.tsx",
                            lineNumber: 75,
                            columnNumber: 13
                        }, this),
                        trend !== undefined && !subtext && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "mt-2 flex items-center gap-1",
                            children: [
                                isTrendPositive ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$trending$2d$up$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__TrendingUp$3e$__["TrendingUp"], {
                                    className: "h-4 w-4 text-green-600"
                                }, void 0, false, {
                                    fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/kpi-card.tsx",
                                    lineNumber: 80,
                                    columnNumber: 17
                                }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$trending$2d$down$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__TrendingDown$3e$__["TrendingDown"], {
                                    className: "h-4 w-4 text-red-600"
                                }, void 0, false, {
                                    fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/kpi-card.tsx",
                                    lineNumber: 82,
                                    columnNumber: 17
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                    className: `text-xs font-medium ${isTrendPositive ? "text-green-600" : "text-red-600"}`,
                                    children: [
                                        Math.abs(trend),
                                        "% vs last period"
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/kpi-card.tsx",
                                    lineNumber: 84,
                                    columnNumber: 15
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/kpi-card.tsx",
                            lineNumber: 78,
                            columnNumber: 13
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/kpi-card.tsx",
                    lineNumber: 66,
                    columnNumber: 9
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: "ml-4 flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10",
                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(IconComponent, {
                        className: "h-5 w-5 text-primary"
                    }, void 0, false, {
                        fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/kpi-card.tsx",
                        lineNumber: 95,
                        columnNumber: 11
                    }, this)
                }, void 0, false, {
                    fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/kpi-card.tsx",
                    lineNumber: 94,
                    columnNumber: 9
                }, this)
            ]
        }, void 0, true, {
            fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/kpi-card.tsx",
            lineNumber: 65,
            columnNumber: 7
        }, this)
    }, void 0, false, {
        fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/kpi-card.tsx",
        lineNumber: 64,
        columnNumber: 5
    }, this);
}
}),
"[project]/Desktop/retail-analytics/frontend/lib/analytics-data.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "getDwellTimeData",
    ()=>getDwellTimeData,
    "getDwellTimeStats",
    ()=>getDwellTimeStats,
    "getIntervalLabel",
    ()=>getIntervalLabel,
    "getOccupancyData",
    ()=>getOccupancyData,
    "getOccupancyStats",
    ()=>getOccupancyStats,
    "getQueuesData",
    ()=>getQueuesData,
    "getQueuesStats",
    ()=>getQueuesStats,
    "getTrafficData",
    ()=>getTrafficData,
    "getTrafficStats",
    ()=>getTrafficStats,
    "getZonesData",
    ()=>getZonesData,
    "getZonesStats",
    ()=>getZonesStats
]);
// ─── Traffic mock data ────────────────────────────────────────────────────────
/** 24-hour data for a single weekday (Tuesday). */ const HOURLY_WEEKDAY = [
    {
        label: "12 AM",
        current: 124,
        prior: 98
    },
    {
        label: "1 AM",
        current: 87,
        prior: 72
    },
    {
        label: "2 AM",
        current: 52,
        prior: 43
    },
    {
        label: "3 AM",
        current: 38,
        prior: 31
    },
    {
        label: "4 AM",
        current: 45,
        prior: 37
    },
    {
        label: "5 AM",
        current: 62,
        prior: 55
    },
    {
        label: "6 AM",
        current: 128,
        prior: 111
    },
    {
        label: "7 AM",
        current: 241,
        prior: 219
    },
    {
        label: "8 AM",
        current: 389,
        prior: 356
    },
    {
        label: "9 AM",
        current: 512,
        prior: 487
    },
    {
        label: "10 AM",
        current: 634,
        prior: 601
    },
    {
        label: "11 AM",
        current: 687,
        prior: 662
    },
    {
        label: "12 PM",
        current: 724,
        prior: 698
    },
    {
        label: "1 PM",
        current: 712,
        prior: 689
    },
    {
        label: "2 PM",
        current: 689,
        prior: 671
    },
    {
        label: "3 PM",
        current: 758,
        prior: 712
    },
    {
        label: "4 PM",
        current: 823,
        prior: 789
    },
    {
        label: "5 PM",
        current: 891,
        prior: 847
    },
    {
        label: "6 PM",
        current: 934,
        prior: 901
    },
    {
        label: "7 PM",
        current: 856,
        prior: 821
    },
    {
        label: "8 PM",
        current: 742,
        prior: 709
    },
    {
        label: "9 PM",
        current: 521,
        prior: 498
    },
    {
        label: "10 PM",
        current: 347,
        prior: 312
    },
    {
        label: "11 PM",
        current: 203,
        prior: 187
    }
];
/** 7-day data for this week vs last week. */ const DAILY_WEEK = [
    {
        label: "Mon",
        current: 4312,
        prior: 4187
    },
    {
        label: "Tue",
        current: 3847,
        prior: 3712
    },
    {
        label: "Wed",
        current: 4108,
        prior: 3987
    },
    {
        label: "Thu",
        current: 4523,
        prior: 4312
    },
    {
        label: "Fri",
        current: 5214,
        prior: 5087
    },
    {
        label: "Sat",
        current: 6341,
        prior: 6108
    },
    {
        label: "Sun",
        current: 5187,
        prior: 4923
    }
];
/** ~30-day data for this month vs last month (showing weeks for brevity). */ const DAILY_MONTH = [
    {
        label: "Jul 1",
        current: 4123,
        prior: 3987
    },
    {
        label: "Jul 2",
        current: 4387,
        prior: 4201
    },
    {
        label: "Jul 3",
        current: 4512,
        prior: 4389
    },
    {
        label: "Jul 4",
        current: 5021,
        prior: 4876
    },
    {
        label: "Jul 5",
        current: 6234,
        prior: 6012
    },
    {
        label: "Jul 6",
        current: 5891,
        prior: 5734
    },
    {
        label: "Jul 7",
        current: 5123,
        prior: 4987
    },
    {
        label: "Jul 8",
        current: 4234,
        prior: 4098
    },
    {
        label: "Jul 9",
        current: 4456,
        prior: 4312
    },
    {
        label: "Jul 10",
        current: 4678,
        prior: 4523
    },
    {
        label: "Jul 11",
        current: 4912,
        prior: 4756
    },
    {
        label: "Jul 12",
        current: 5234,
        prior: 5089
    },
    {
        label: "Jul 13",
        current: 6123,
        prior: 5978
    },
    {
        label: "Jul 14",
        current: 5678,
        prior: 5512
    },
    {
        label: "Jul 15",
        current: 4389,
        prior: 4234
    },
    {
        label: "Jul 16",
        current: 4512,
        prior: 4367
    },
    {
        label: "Jul 17",
        current: 4823,
        prior: 4689
    },
    {
        label: "Jul 18",
        current: 5123,
        prior: 4978
    },
    {
        label: "Jul 19",
        current: 5456,
        prior: 5312
    },
    {
        label: "Jul 20",
        current: 6278,
        prior: 6134
    },
    {
        label: "Jul 21",
        current: 5934,
        prior: 5789
    },
    {
        label: "Jul 22",
        current: 3847,
        prior: 3712
    }
];
/** Last-hour data (5-minute buckets). */ const LAST_HOUR = [
    {
        label: "6:00",
        current: 48,
        prior: 41
    },
    {
        label: "6:05",
        current: 52,
        prior: 45
    },
    {
        label: "6:10",
        current: 61,
        prior: 53
    },
    {
        label: "6:15",
        current: 57,
        prior: 49
    },
    {
        label: "6:20",
        current: 63,
        prior: 55
    },
    {
        label: "6:25",
        current: 71,
        prior: 62
    },
    {
        label: "6:30",
        current: 78,
        prior: 68
    },
    {
        label: "6:35",
        current: 84,
        prior: 73
    },
    {
        label: "6:40",
        current: 91,
        prior: 79
    },
    {
        label: "6:45",
        current: 87,
        prior: 76
    },
    {
        label: "6:50",
        current: 93,
        prior: 82
    },
    {
        label: "6:55",
        current: 98,
        prior: 87
    }
];
function getTrafficData(range) {
    switch(range){
        case "hour":
            return LAST_HOUR;
        case "day":
            return HOURLY_WEEKDAY;
        case "week":
            return DAILY_WEEK;
        case "month":
            return DAILY_MONTH;
        default:
            return HOURLY_WEEKDAY;
    }
}
function getTrafficStats(range) {
    const data = getTrafficData(range);
    const total = data.reduce((s, r)=>s + r.current, 0);
    const peak = data.reduce((m, r)=>r.current > m.current ? r : m, data[0]);
    const avg = Math.round(total / data.length);
    return [
        {
            label: "Total Visitors",
            value: total.toLocaleString()
        },
        {
            label: "Peak Hour",
            value: peak.current.toLocaleString(),
            subtext: peak.label
        },
        {
            label: "Average Per Interval",
            value: avg.toLocaleString()
        }
    ];
}
function getIntervalLabel(range) {
    switch(range){
        case "hour":
            return "5-min window";
        case "day":
            return "Hour";
        case "week":
        case "month":
            return "Day";
        default:
            return "Period";
    }
}
// ─── Occupancy mock data ──────────────────────────────────────────────────────
const OCCUPANCY_HOURLY_WEEKDAY = [
    {
        label: "12 AM",
        current: 12,
        prior: 10
    },
    {
        label: "1 AM",
        current: 8,
        prior: 7
    },
    {
        label: "2 AM",
        current: 5,
        prior: 4
    },
    {
        label: "3 AM",
        current: 3,
        prior: 3
    },
    {
        label: "4 AM",
        current: 4,
        prior: 3
    },
    {
        label: "5 AM",
        current: 6,
        prior: 5
    },
    {
        label: "6 AM",
        current: 13,
        prior: 11
    },
    {
        label: "7 AM",
        current: 24,
        prior: 22
    },
    {
        label: "8 AM",
        current: 39,
        prior: 36
    },
    {
        label: "9 AM",
        current: 51,
        prior: 49
    },
    {
        label: "10 AM",
        current: 63,
        prior: 60
    },
    {
        label: "11 AM",
        current: 69,
        prior: 66
    },
    {
        label: "12 PM",
        current: 72,
        prior: 70
    },
    {
        label: "1 PM",
        current: 71,
        prior: 69
    },
    {
        label: "2 PM",
        current: 69,
        prior: 67
    },
    {
        label: "3 PM",
        current: 76,
        prior: 71
    },
    {
        label: "4 PM",
        current: 82,
        prior: 79
    },
    {
        label: "5 PM",
        current: 89,
        prior: 85
    },
    {
        label: "6 PM",
        current: 93,
        prior: 90
    },
    {
        label: "7 PM",
        current: 86,
        prior: 82
    },
    {
        label: "8 PM",
        current: 74,
        prior: 71
    },
    {
        label: "9 PM",
        current: 52,
        prior: 50
    },
    {
        label: "10 PM",
        current: 35,
        prior: 31
    },
    {
        label: "11 PM",
        current: 20,
        prior: 19
    }
];
const OCCUPANCY_DAILY_WEEK = [
    {
        label: "Mon",
        current: 45,
        prior: 42
    },
    {
        label: "Tue",
        current: 38,
        prior: 37
    },
    {
        label: "Wed",
        current: 41,
        prior: 40
    },
    {
        label: "Thu",
        current: 45,
        prior: 43
    },
    {
        label: "Fri",
        current: 52,
        prior: 51
    },
    {
        label: "Sat",
        current: 63,
        prior: 61
    },
    {
        label: "Sun",
        current: 52,
        prior: 49
    }
];
const OCCUPANCY_DAILY_MONTH = [
    {
        label: "Jul 1",
        current: 41,
        prior: 40
    },
    {
        label: "Jul 2",
        current: 44,
        prior: 42
    },
    {
        label: "Jul 3",
        current: 45,
        prior: 44
    },
    {
        label: "Jul 4",
        current: 50,
        prior: 49
    },
    {
        label: "Jul 5",
        current: 62,
        prior: 60
    },
    {
        label: "Jul 6",
        current: 59,
        prior: 57
    },
    {
        label: "Jul 7",
        current: 51,
        prior: 50
    },
    {
        label: "Jul 8",
        current: 42,
        prior: 41
    },
    {
        label: "Jul 9",
        current: 45,
        prior: 43
    },
    {
        label: "Jul 10",
        current: 47,
        prior: 45
    },
    {
        label: "Jul 11",
        current: 49,
        prior: 48
    },
    {
        label: "Jul 12",
        current: 52,
        prior: 51
    },
    {
        label: "Jul 13",
        current: 61,
        prior: 60
    },
    {
        label: "Jul 14",
        current: 57,
        prior: 55
    },
    {
        label: "Jul 15",
        current: 44,
        prior: 42
    },
    {
        label: "Jul 16",
        current: 45,
        prior: 44
    },
    {
        label: "Jul 17",
        current: 48,
        prior: 47
    },
    {
        label: "Jul 18",
        current: 51,
        prior: 50
    },
    {
        label: "Jul 19",
        current: 55,
        prior: 53
    },
    {
        label: "Jul 20",
        current: 63,
        prior: 61
    },
    {
        label: "Jul 21",
        current: 59,
        prior: 58
    },
    {
        label: "Jul 22",
        current: 38,
        prior: 37
    }
];
const OCCUPANCY_LAST_HOUR = [
    {
        label: "6:00",
        current: 48,
        prior: 41
    },
    {
        label: "6:05",
        current: 52,
        prior: 45
    },
    {
        label: "6:10",
        current: 61,
        prior: 53
    },
    {
        label: "6:15",
        current: 57,
        prior: 49
    },
    {
        label: "6:20",
        current: 63,
        prior: 55
    },
    {
        label: "6:25",
        current: 71,
        prior: 62
    },
    {
        label: "6:30",
        current: 78,
        prior: 68
    },
    {
        label: "6:35",
        current: 84,
        prior: 73
    },
    {
        label: "6:40",
        current: 91,
        prior: 79
    },
    {
        label: "6:45",
        current: 87,
        prior: 76
    },
    {
        label: "6:50",
        current: 93,
        prior: 82
    },
    {
        label: "6:55",
        current: 98,
        prior: 87
    }
];
function getOccupancyData(range) {
    switch(range){
        case "hour":
            return OCCUPANCY_LAST_HOUR;
        case "day":
            return OCCUPANCY_HOURLY_WEEKDAY;
        case "week":
            return OCCUPANCY_DAILY_WEEK;
        case "month":
            return OCCUPANCY_DAILY_MONTH;
        default:
            return OCCUPANCY_HOURLY_WEEKDAY;
    }
}
function getOccupancyStats(range) {
    const data = getOccupancyData(range);
    const total = data.reduce((s, r)=>s + r.current, 0);
    const peak = data.reduce((m, r)=>r.current > m.current ? r : m, data[0]);
    const avg = Math.round(total / data.length);
    return [
        {
            label: "Average Occupancy",
            value: `${avg}%`
        },
        {
            label: "Peak Occupancy",
            value: `${peak.current}%`,
            subtext: peak.label
        },
        {
            label: "Total Capacity",
            value: "100%"
        }
    ];
}
// ─── Zones mock data ──────────────────────────────────────────────────────────
const ZONES_DATA = [
    {
        label: "Zone A (Entrance)",
        current: 145,
        prior: 132
    },
    {
        label: "Zone B (Retail)",
        current: 287,
        prior: 263
    },
    {
        label: "Zone C (Food Court)",
        current: 412,
        prior: 387
    },
    {
        label: "Zone D (Parking)",
        current: 198,
        prior: 176
    },
    {
        label: "Zone E (VIP Lounge)",
        current: 87,
        prior: 79
    }
];
function getZonesData(_range) {
    // Zones don't vary by time range in this mock
    return ZONES_DATA;
}
function getZonesStats(_range) {
    const total = ZONES_DATA.reduce((s, r)=>s + r.current, 0);
    const busiest = ZONES_DATA.reduce((m, r)=>r.current > m.current ? r : m, ZONES_DATA[0]);
    const avg = Math.round(total / ZONES_DATA.length);
    return [
        {
            label: "Total Visitors",
            value: total.toLocaleString()
        },
        {
            label: "Busiest Zone",
            value: busiest.current.toLocaleString(),
            subtext: busiest.label
        },
        {
            label: "Average Per Zone",
            value: avg.toLocaleString()
        }
    ];
}
// ─── Dwell Time mock data ─────────────────────────────────────────────────────
const DWELL_TIME_BUCKETS = [
    {
        label: "0-30s",
        current: 234,
        prior: 198
    },
    {
        label: "30-60s",
        current: 156,
        prior: 142
    },
    {
        label: "1-3 min",
        current: 289,
        prior: 267
    },
    {
        label: "3-10 min",
        current: 412,
        prior: 387
    },
    {
        label: "10+ min",
        current: 187,
        prior: 168
    }
];
function getDwellTimeData(_range) {
    // Dwell time buckets are fixed regardless of range
    return DWELL_TIME_BUCKETS;
}
function getDwellTimeStats(_range) {
    const total = DWELL_TIME_BUCKETS.reduce((s, r)=>s + r.current, 0);
    const longest = DWELL_TIME_BUCKETS[DWELL_TIME_BUCKETS.length - 1];
    const avg = Math.round(total / DWELL_TIME_BUCKETS.length);
    return [
        {
            label: "Total Visits",
            value: total.toLocaleString()
        },
        {
            label: "Most Common Duration",
            value: "3-10 min"
        },
        {
            label: "Extended Stays (10+)",
            value: longest.current.toLocaleString()
        }
    ];
}
// ─── Queues mock data ─────────────────────────────────────────────────────────
const QUEUES_HOURLY_WEEKDAY = [
    {
        label: "12 AM",
        current: 2,
        prior: 1
    },
    {
        label: "1 AM",
        current: 1,
        prior: 1
    },
    {
        label: "2 AM",
        current: 0,
        prior: 0
    },
    {
        label: "3 AM",
        current: 0,
        prior: 0
    },
    {
        label: "4 AM",
        current: 0,
        prior: 0
    },
    {
        label: "5 AM",
        current: 1,
        prior: 1
    },
    {
        label: "6 AM",
        current: 4,
        prior: 3
    },
    {
        label: "7 AM",
        current: 8,
        prior: 7
    },
    {
        label: "8 AM",
        current: 15,
        prior: 13
    },
    {
        label: "9 AM",
        current: 21,
        prior: 19
    },
    {
        label: "10 AM",
        current: 28,
        prior: 26
    },
    {
        label: "11 AM",
        current: 32,
        prior: 31
    },
    {
        label: "12 PM",
        current: 35,
        prior: 33
    },
    {
        label: "1 PM",
        current: 34,
        prior: 32
    },
    {
        label: "2 PM",
        current: 30,
        prior: 28
    },
    {
        label: "3 PM",
        current: 36,
        prior: 33
    },
    {
        label: "4 PM",
        current: 42,
        prior: 40
    },
    {
        label: "5 PM",
        current: 48,
        prior: 45
    },
    {
        label: "6 PM",
        current: 51,
        prior: 49
    },
    {
        label: "7 PM",
        current: 43,
        prior: 40
    },
    {
        label: "8 PM",
        current: 32,
        prior: 30
    },
    {
        label: "9 PM",
        current: 18,
        prior: 16
    },
    {
        label: "10 PM",
        current: 11,
        prior: 9
    },
    {
        label: "11 PM",
        current: 5,
        prior: 4
    }
];
const QUEUES_DAILY_WEEK = [
    {
        label: "Mon",
        current: 18,
        prior: 16
    },
    {
        label: "Tue",
        current: 15,
        prior: 14
    },
    {
        label: "Wed",
        current: 16,
        prior: 15
    },
    {
        label: "Thu",
        current: 19,
        prior: 17
    },
    {
        label: "Fri",
        current: 24,
        prior: 22
    },
    {
        label: "Sat",
        current: 31,
        prior: 29
    },
    {
        label: "Sun",
        current: 27,
        prior: 25
    }
];
const QUEUES_DAILY_MONTH = [
    {
        label: "Jul 1",
        current: 16,
        prior: 15
    },
    {
        label: "Jul 2",
        current: 18,
        prior: 16
    },
    {
        label: "Jul 3",
        current: 19,
        prior: 17
    },
    {
        label: "Jul 4",
        current: 22,
        prior: 20
    },
    {
        label: "Jul 5",
        current: 28,
        prior: 26
    },
    {
        label: "Jul 6",
        current: 26,
        prior: 24
    },
    {
        label: "Jul 7",
        current: 24,
        prior: 22
    },
    {
        label: "Jul 8",
        current: 17,
        prior: 16
    },
    {
        label: "Jul 9",
        current: 18,
        prior: 17
    },
    {
        label: "Jul 10",
        current: 20,
        prior: 19
    },
    {
        label: "Jul 11",
        current: 21,
        prior: 20
    },
    {
        label: "Jul 12",
        current: 23,
        prior: 22
    },
    {
        label: "Jul 13",
        current: 29,
        prior: 27
    },
    {
        label: "Jul 14",
        current: 25,
        prior: 23
    },
    {
        label: "Jul 15",
        current: 17,
        prior: 16
    },
    {
        label: "Jul 16",
        current: 18,
        prior: 17
    },
    {
        label: "Jul 17",
        current: 21,
        prior: 19
    },
    {
        label: "Jul 18",
        current: 23,
        prior: 22
    },
    {
        label: "Jul 19",
        current: 25,
        prior: 24
    },
    {
        label: "Jul 20",
        current: 32,
        prior: 30
    },
    {
        label: "Jul 21",
        current: 28,
        prior: 26
    },
    {
        label: "Jul 22",
        current: 15,
        prior: 14
    }
];
const QUEUES_LAST_HOUR = [
    {
        label: "6:00",
        current: 18,
        prior: 15
    },
    {
        label: "6:05",
        current: 21,
        prior: 18
    },
    {
        label: "6:10",
        current: 25,
        prior: 22
    },
    {
        label: "6:15",
        current: 23,
        prior: 20
    },
    {
        label: "6:20",
        current: 27,
        prior: 24
    },
    {
        label: "6:25",
        current: 31,
        prior: 28
    },
    {
        label: "6:30",
        current: 34,
        prior: 31
    },
    {
        label: "6:35",
        current: 36,
        prior: 33
    },
    {
        label: "6:40",
        current: 39,
        prior: 36
    },
    {
        label: "6:45",
        current: 37,
        prior: 34
    },
    {
        label: "6:50",
        current: 41,
        prior: 38
    },
    {
        label: "6:55",
        current: 43,
        prior: 40
    }
];
function getQueuesData(range) {
    switch(range){
        case "hour":
            return QUEUES_LAST_HOUR;
        case "day":
            return QUEUES_HOURLY_WEEKDAY;
        case "week":
            return QUEUES_DAILY_WEEK;
        case "month":
            return QUEUES_DAILY_MONTH;
        default:
            return QUEUES_HOURLY_WEEKDAY;
    }
}
function getQueuesStats(range) {
    const data = getQueuesData(range);
    const total = data.reduce((s, r)=>s + r.current, 0);
    const peak = data.reduce((m, r)=>r.current > m.current ? r : m, data[0]);
    const avg = Math.round(total / data.length);
    return [
        {
            label: "Total Queue Minutes",
            value: total.toLocaleString()
        },
        {
            label: "Peak Queue Length",
            value: peak.current.toLocaleString(),
            subtext: peak.label
        },
        {
            label: "Average Queue Length",
            value: avg.toLocaleString()
        }
    ];
}
}),
"[project]/Desktop/retail-analytics/frontend/lib/heatmap-data.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "FLOOR_ZONES",
    ()=>FLOOR_ZONES,
    "HEATMAP_CAMERAS",
    ()=>HEATMAP_CAMERAS,
    "HEAT_BLOBS",
    ()=>HEAT_BLOBS,
    "ZONE_PERFORMANCE",
    ()=>ZONE_PERFORMANCE
]);
const HEATMAP_CAMERAS = [
    {
        id: "cam-overview",
        label: "Overview (Bird's Eye)"
    },
    {
        id: "cam-entrance",
        label: "Main Entrance"
    },
    {
        id: "cam-checkout",
        label: "Checkout Lanes"
    },
    {
        id: "cam-aisle3",
        label: "Aisle 3 — Electronics"
    },
    {
        id: "cam-apparel",
        label: "Apparel"
    }
];
const HEAT_BLOBS = {
    "cam-overview": [
        // Entrance — very hot
        {
            id: "h1",
            cx: 50,
            cy: 86,
            rx: 18,
            ry: 10,
            intensity: 0.88,
            color: "#ff2200"
        },
        // Checkout — hot
        {
            id: "h2",
            cx: 18,
            cy: 24,
            rx: 16,
            ry: 10,
            intensity: 0.72,
            color: "#ff5500"
        },
        // Electronics aisle — medium-hot
        {
            id: "h3",
            cx: 78,
            cy: 38,
            rx: 14,
            ry: 10,
            intensity: 0.60,
            color: "#ff8800"
        },
        // Apparel — medium
        {
            id: "h4",
            cx: 62,
            cy: 62,
            rx: 13,
            ry: 9,
            intensity: 0.45,
            color: "#ffcc00"
        },
        // Back Wall — cool
        {
            id: "h5",
            cx: 36,
            cy: 14,
            rx: 18,
            ry: 8,
            intensity: 0.22,
            color: "#00aaff"
        },
        // Centre aisle drift
        {
            id: "h6",
            cx: 50,
            cy: 50,
            rx: 10,
            ry: 8,
            intensity: 0.35,
            color: "#ffaa00"
        }
    ],
    "cam-entrance": [
        {
            id: "h1",
            cx: 50,
            cy: 80,
            rx: 28,
            ry: 14,
            intensity: 0.92,
            color: "#ff1100"
        },
        {
            id: "h2",
            cx: 30,
            cy: 55,
            rx: 14,
            ry: 10,
            intensity: 0.55,
            color: "#ff6600"
        },
        {
            id: "h3",
            cx: 70,
            cy: 50,
            rx: 12,
            ry: 9,
            intensity: 0.42,
            color: "#ffaa00"
        }
    ],
    "cam-checkout": [
        {
            id: "h1",
            cx: 28,
            cy: 60,
            rx: 20,
            ry: 12,
            intensity: 0.80,
            color: "#ff2200"
        },
        {
            id: "h2",
            cx: 62,
            cy: 55,
            rx: 16,
            ry: 10,
            intensity: 0.65,
            color: "#ff5500"
        },
        {
            id: "h3",
            cx: 48,
            cy: 30,
            rx: 10,
            ry: 7,
            intensity: 0.28,
            color: "#44ddff"
        }
    ],
    "cam-aisle3": [
        {
            id: "h1",
            cx: 50,
            cy: 50,
            rx: 24,
            ry: 16,
            intensity: 0.60,
            color: "#ff8800"
        },
        {
            id: "h2",
            cx: 20,
            cy: 40,
            rx: 10,
            ry: 8,
            intensity: 0.35,
            color: "#ffcc00"
        },
        {
            id: "h3",
            cx: 80,
            cy: 60,
            rx: 10,
            ry: 7,
            intensity: 0.28,
            color: "#00ccff"
        }
    ],
    "cam-apparel": [
        {
            id: "h1",
            cx: 60,
            cy: 55,
            rx: 22,
            ry: 14,
            intensity: 0.50,
            color: "#ffbb00"
        },
        {
            id: "h2",
            cx: 30,
            cy: 40,
            rx: 12,
            ry: 9,
            intensity: 0.30,
            color: "#44eebb"
        },
        {
            id: "h3",
            cx: 75,
            cy: 30,
            rx: 8,
            ry: 6,
            intensity: 0.18,
            color: "#0088ff"
        }
    ]
};
const FLOOR_ZONES = [
    {
        id: "entrance",
        label: "Entrance",
        x: 36,
        y: 76,
        w: 28,
        h: 18
    },
    {
        id: "checkout",
        label: "Checkout",
        x: 6,
        y: 8,
        w: 26,
        h: 24
    },
    {
        id: "electronics",
        label: "Electronics",
        x: 66,
        y: 24,
        w: 28,
        h: 22
    },
    {
        id: "apparel",
        label: "Apparel",
        x: 48,
        y: 50,
        w: 28,
        h: 22
    },
    {
        id: "back-wall",
        label: "Back Wall",
        x: 18,
        y: 4,
        w: 40,
        h: 16
    }
];
const ZONE_PERFORMANCE = [
    {
        id: "entrance",
        zone: "Entrance",
        visits: 1284,
        dwellSec: 62,
        occupancy: 88,
        trend: "up",
        trendPct: 12
    },
    {
        id: "checkout",
        zone: "Checkout",
        visits: 612,
        dwellSec: 186,
        occupancy: 74,
        trend: "down",
        trendPct: 5
    },
    {
        id: "electronics",
        zone: "Electronics",
        visits: 847,
        dwellSec: 241,
        occupancy: 61,
        trend: "up",
        trendPct: 8
    },
    {
        id: "apparel",
        zone: "Apparel",
        visits: 503,
        dwellSec: 178,
        occupancy: 45,
        trend: "flat",
        trendPct: 1
    },
    {
        id: "back-wall",
        zone: "Back Wall",
        visits: 218,
        dwellSec: 94,
        occupancy: 22,
        trend: "down",
        trendPct: 3
    }
];
}),
"[project]/Desktop/retail-analytics/frontend/lib/overview-data.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

// Mock data for the Overview dashboard
__turbopack_context__.s([
    "entriesExitsData",
    ()=>entriesExitsData,
    "kpiData",
    ()=>kpiData,
    "occupancyTrendData",
    ()=>occupancyTrendData,
    "visitorsByHourData",
    ()=>visitorsByHourData
]);
const kpiData = {
    visitorsToday: {
        value: 3847,
        label: "Visitors Today",
        trend: 12.5,
        icon: "users"
    },
    occupancy: {
        value: 68,
        unit: "%",
        label: "Current Occupancy",
        trend: 3.2,
        icon: "activity"
    },
    peakOccupancy: {
        value: 92,
        unit: "%",
        label: "Peak Occupancy",
        subtext: "2:45 PM",
        icon: "zap"
    },
    dwellTime: {
        value: 18,
        unit: "min",
        label: "Average Dwell Time",
        trend: -2.1,
        icon: "clock"
    },
    queueLength: {
        value: 4,
        label: "Current Queue Length",
        trend: 8.7,
        icon: "list"
    },
    activeCameras: {
        value: 4,
        total: 5,
        label: "Active Cameras",
        icon: "camera"
    }
};
const visitorsByHourData = [
    {
        hour: "12 AM",
        visitors: 124
    },
    {
        hour: "1 AM",
        visitors: 87
    },
    {
        hour: "2 AM",
        visitors: 52
    },
    {
        hour: "3 AM",
        visitors: 38
    },
    {
        hour: "4 AM",
        visitors: 45
    },
    {
        hour: "5 AM",
        visitors: 62
    },
    {
        hour: "6 AM",
        visitors: 128
    },
    {
        hour: "7 AM",
        visitors: 241
    },
    {
        hour: "8 AM",
        visitors: 389
    },
    {
        hour: "9 AM",
        visitors: 512
    },
    {
        hour: "10 AM",
        visitors: 634
    },
    {
        hour: "11 AM",
        visitors: 687
    },
    {
        hour: "12 PM",
        visitors: 724
    },
    {
        hour: "1 PM",
        visitors: 712
    },
    {
        hour: "2 PM",
        visitors: 689
    },
    {
        hour: "3 PM",
        visitors: 758
    },
    {
        hour: "4 PM",
        visitors: 823
    },
    {
        hour: "5 PM",
        visitors: 891
    },
    {
        hour: "6 PM",
        visitors: 934
    },
    {
        hour: "7 PM",
        visitors: 856
    },
    {
        hour: "8 PM",
        visitors: 742
    },
    {
        hour: "9 PM",
        visitors: 521
    },
    {
        hour: "10 PM",
        visitors: 347
    },
    {
        hour: "11 PM",
        visitors: 203
    }
];
const entriesExitsData = [
    {
        hour: "12 AM",
        entries: 124,
        exits: 118
    },
    {
        hour: "2 AM",
        entries: 52,
        exits: 48
    },
    {
        hour: "4 AM",
        entries: 45,
        exits: 42
    },
    {
        hour: "6 AM",
        entries: 128,
        exits: 102
    },
    {
        hour: "8 AM",
        entries: 389,
        exits: 245
    },
    {
        hour: "10 AM",
        entries: 634,
        exits: 412
    },
    {
        hour: "12 PM",
        entries: 724,
        exits: 651
    },
    {
        hour: "2 PM",
        entries: 689,
        exits: 704
    },
    {
        hour: "4 PM",
        entries: 823,
        exits: 756
    },
    {
        hour: "6 PM",
        entries: 934,
        exits: 687
    },
    {
        hour: "8 PM",
        entries: 742,
        exits: 821
    },
    {
        hour: "10 PM",
        entries: 347,
        exits: 412
    }
];
const occupancyTrendData = [
    {
        day: "Mon",
        occupancy: 61
    },
    {
        day: "Tue",
        occupancy: 64
    },
    {
        day: "Wed",
        occupancy: 58
    },
    {
        day: "Thu",
        occupancy: 72
    },
    {
        day: "Fri",
        occupancy: 78
    },
    {
        day: "Sat",
        occupancy: 85
    },
    {
        day: "Today",
        occupancy: 68
    }
];
}),
"[project]/Desktop/retail-analytics/frontend/lib/api/analytics.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "fetchDwellTimeData",
    ()=>fetchDwellTimeData,
    "fetchDwellTimeStats",
    ()=>fetchDwellTimeStats,
    "fetchIntervalLabel",
    ()=>fetchIntervalLabel,
    "fetchOccupancyData",
    ()=>fetchOccupancyData,
    "fetchOccupancyStats",
    ()=>fetchOccupancyStats,
    "fetchQueuesData",
    ()=>fetchQueuesData,
    "fetchQueuesStats",
    ()=>fetchQueuesStats,
    "fetchTrafficData",
    ()=>fetchTrafficData,
    "fetchTrafficStats",
    ()=>fetchTrafficStats,
    "fetchZonesData",
    ()=>fetchZonesData,
    "fetchZonesStats",
    ()=>fetchZonesStats,
    "getDwell",
    ()=>getDwell,
    "getEntriesExits",
    ()=>getEntriesExits,
    "getHeatmap",
    ()=>getHeatmap,
    "getHeatmapCameras",
    ()=>getHeatmapCameras,
    "getOccupancy",
    ()=>getOccupancy,
    "getOccupancyTrend",
    ()=>getOccupancyTrend,
    "getOverviewKpis",
    ()=>getOverviewKpis,
    "getQueues",
    ()=>getQueues,
    "getTraffic",
    ()=>getTraffic,
    "getVisitorsByHour",
    ()=>getVisitorsByHour,
    "getZonePerformance",
    ()=>getZonePerformance,
    "getZones",
    ()=>getZones
]);
// MOCK IMPLEMENTATION — swap the function bodies below for real fetch() calls
// to the FastAPI backend when Module 12 is live. Signatures and return types
// must not change.
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$analytics$2d$data$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/lib/analytics-data.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$heatmap$2d$data$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/lib/heatmap-data.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$overview$2d$data$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/lib/overview-data.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$scope$2f$scope$2d$filters$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/lib/scope/scope-filters.ts [app-ssr] (ecmascript)");
;
;
;
;
// ─── Helpers ─────────────────────────────────────────────────────────────────
function inferDateRangeKey(from, to) {
    const start = new Date(from).getTime();
    const end = new Date(to).getTime();
    if (Number.isNaN(start) || Number.isNaN(end)) return "day";
    const diffMs = Math.abs(end - start);
    const diffHours = diffMs / (1000 * 60 * 60);
    const diffDays = diffMs / (1000 * 60 * 60 * 24);
    if (diffHours <= 1.5) return "hour";
    if (diffDays <= 1.5) return "day";
    if (diffDays <= 8) return "week";
    return "month";
}
function getTraffic({ store_id: _store_id, from, to }) {
    const range = inferDateRangeKey(from, to);
    return Promise.resolve((0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$analytics$2d$data$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["getTrafficData"])(range));
}
function getOccupancy({ camera_id: _camera_id, store_id: _store_id } = {}) {
    return Promise.resolve((0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$analytics$2d$data$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["getOccupancyData"])("day"));
}
function getZones({ zone_id, from, to }) {
    const range = inferDateRangeKey(from, to);
    const rows = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$analytics$2d$data$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["getZonesData"])(range);
    const performance = __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$heatmap$2d$data$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["ZONE_PERFORMANCE"].find((z)=>z.id === zone_id);
    return Promise.resolve({
        zone_id,
        from,
        to,
        rows,
        performance
    });
}
function getDwell({ zone_id: _zone_id, from, to }) {
    const range = inferDateRangeKey(from, to);
    return Promise.resolve((0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$analytics$2d$data$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["getDwellTimeData"])(range));
}
function getHeatmap({ camera_id, date, from_time, to_time }) {
    const blobs = __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$heatmap$2d$data$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["HEAT_BLOBS"][camera_id] ?? __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$heatmap$2d$data$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["HEAT_BLOBS"]["cam-overview"] ?? [];
    return Promise.resolve({
        camera_id,
        date,
        from_time,
        to_time,
        blobs,
        floor_zones: __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$heatmap$2d$data$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["FLOOR_ZONES"]
    });
}
function getQueues({ zone_id: _zone_id, from, to }) {
    const range = inferDateRangeKey(from, to);
    return Promise.resolve((0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$analytics$2d$data$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["getQueuesData"])(range));
}
// ─── Overview dashboard ──────────────────────────────────────────────────────
function scaleOverviewKpis(data, factor) {
    return {
        ...data,
        visitorsToday: {
            ...data.visitorsToday,
            value: Math.round(data.visitorsToday.value * factor)
        },
        occupancy: {
            ...data.occupancy,
            value: Math.min(100, Math.round(data.occupancy.value * factor))
        },
        peakOccupancy: {
            ...data.peakOccupancy,
            value: Math.min(100, Math.round(data.peakOccupancy.value * factor))
        },
        queueLength: {
            ...data.queueLength,
            value: Math.round(data.queueLength.value * factor)
        }
    };
}
function getOverviewKpis(params = {}) {
    if (!params.store_id) return Promise.resolve(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$overview$2d$data$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["kpiData"]);
    return Promise.resolve(scaleOverviewKpis(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$overview$2d$data$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["kpiData"], (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$scope$2f$scope$2d$filters$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["scopeScaleFactor"])(params.store_id)));
}
function getVisitorsByHour(params = {}) {
    if (!params.store_id) return Promise.resolve(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$overview$2d$data$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["visitorsByHourData"]);
    const factor = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$scope$2f$scope$2d$filters$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["scopeScaleFactor"])(params.store_id);
    return Promise.resolve(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$overview$2d$data$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["visitorsByHourData"].map((row)=>({
            ...row,
            visitors: Math.round(row.visitors * factor)
        })));
}
function getEntriesExits(params = {}) {
    if (!params.store_id) return Promise.resolve(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$overview$2d$data$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["entriesExitsData"]);
    const factor = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$scope$2f$scope$2d$filters$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["scopeScaleFactor"])(params.store_id);
    return Promise.resolve(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$overview$2d$data$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["entriesExitsData"].map((row)=>({
            ...row,
            entries: Math.round(row.entries * factor),
            exits: Math.round(row.exits * factor)
        })));
}
function getOccupancyTrend(params = {}) {
    if (!params.store_id) return Promise.resolve(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$overview$2d$data$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["occupancyTrendData"]);
    const factor = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$scope$2f$scope$2d$filters$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["scopeScaleFactor"])(params.store_id);
    return Promise.resolve(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$overview$2d$data$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["occupancyTrendData"].map((row)=>({
            ...row,
            occupancy: Math.min(100, Math.round(row.occupancy * factor))
        })));
}
function fetchTrafficData(range) {
    return Promise.resolve((0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$analytics$2d$data$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["getTrafficData"])(range));
}
function fetchTrafficStats(range) {
    return Promise.resolve((0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$analytics$2d$data$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["getTrafficStats"])(range));
}
function fetchOccupancyData(range) {
    return Promise.resolve((0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$analytics$2d$data$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["getOccupancyData"])(range));
}
function fetchOccupancyStats(range) {
    return Promise.resolve((0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$analytics$2d$data$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["getOccupancyStats"])(range));
}
function fetchZonesData(range) {
    return Promise.resolve((0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$analytics$2d$data$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["getZonesData"])(range));
}
function fetchZonesStats(range) {
    return Promise.resolve((0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$analytics$2d$data$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["getZonesStats"])(range));
}
function fetchDwellTimeData(range) {
    return Promise.resolve((0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$analytics$2d$data$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["getDwellTimeData"])(range));
}
function fetchDwellTimeStats(range) {
    return Promise.resolve((0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$analytics$2d$data$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["getDwellTimeStats"])(range));
}
function fetchQueuesData(range) {
    return Promise.resolve((0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$analytics$2d$data$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["getQueuesData"])(range));
}
function fetchQueuesStats(range) {
    return Promise.resolve((0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$analytics$2d$data$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["getQueuesStats"])(range));
}
function fetchIntervalLabel(range) {
    return (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$analytics$2d$data$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["getIntervalLabel"])(range);
}
function getHeatmapCameras() {
    return Promise.resolve(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$heatmap$2d$data$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["HEATMAP_CAMERAS"]);
}
function getZonePerformance(params = {}) {
    if (!params.store_id && !params.zone_id) {
        return Promise.resolve(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$heatmap$2d$data$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["ZONE_PERFORMANCE"]);
    }
    return Promise.resolve((0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$scope$2f$scope$2d$filters$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["filterZonePerformanceRows"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$heatmap$2d$data$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["ZONE_PERFORMANCE"], params.zone_id ?? null, params.store_id ?? null));
}
}),
"[project]/Desktop/retail-analytics/frontend/components/overview/visitors-by-hour-chart.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "VisitorsByHourChart",
    ()=>VisitorsByHourChart
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$chart$2f$BarChart$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/recharts/es6/chart/BarChart.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$cartesian$2f$Bar$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/recharts/es6/cartesian/Bar.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$cartesian$2f$XAxis$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/recharts/es6/cartesian/XAxis.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$cartesian$2f$YAxis$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/recharts/es6/cartesian/YAxis.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$cartesian$2f$CartesianGrid$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/recharts/es6/cartesian/CartesianGrid.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$component$2f$Tooltip$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/recharts/es6/component/Tooltip.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$component$2f$ResponsiveContainer$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/recharts/es6/component/ResponsiveContainer.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$api$2f$analytics$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/lib/api/analytics.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$scope$2f$ScopeContext$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/lib/scope/ScopeContext.tsx [app-ssr] (ecmascript)");
'use client';
;
;
;
;
;
function VisitorsByHourChart() {
    const { storeId } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$scope$2f$ScopeContext$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useScope"])();
    const [data, setData] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])([]);
    const [loading, setLoading] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(true);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        let cancelled = false;
        async function load() {
            setLoading(true);
            const rows = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$api$2f$analytics$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["getVisitorsByHour"])({
                store_id: storeId ?? undefined
            });
            if (!cancelled) {
                setData(rows);
                setLoading(false);
            }
        }
        load();
        return ()=>{
            cancelled = true;
        };
    }, [
        storeId
    ]);
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "rounded-lg border border-border bg-card p-6",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("h3", {
                className: "mb-4 text-sm font-semibold text-foreground",
                children: "Visitors by Hour"
            }, void 0, false, {
                fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/visitors-by-hour-chart.tsx",
                lineNumber: 44,
                columnNumber: 7
            }, this),
            loading ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "flex h-[300px] items-center justify-center",
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: "h-full w-full animate-pulse rounded bg-muted"
                }, void 0, false, {
                    fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/visitors-by-hour-chart.tsx",
                    lineNumber: 49,
                    columnNumber: 11
                }, this)
            }, void 0, false, {
                fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/visitors-by-hour-chart.tsx",
                lineNumber: 48,
                columnNumber: 9
            }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$component$2f$ResponsiveContainer$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["ResponsiveContainer"], {
                width: "100%",
                height: 300,
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$chart$2f$BarChart$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["BarChart"], {
                    data: data,
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$cartesian$2f$CartesianGrid$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["CartesianGrid"], {
                            strokeDasharray: "3 3",
                            stroke: "var(--color-border)"
                        }, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/visitors-by-hour-chart.tsx",
                            lineNumber: 54,
                            columnNumber: 13
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$cartesian$2f$XAxis$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["XAxis"], {
                            dataKey: "hour",
                            tick: {
                                fontSize: 12,
                                fill: 'var(--color-muted-foreground)'
                            },
                            interval: 2
                        }, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/visitors-by-hour-chart.tsx",
                            lineNumber: 55,
                            columnNumber: 13
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$cartesian$2f$YAxis$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["YAxis"], {
                            tick: {
                                fontSize: 12,
                                fill: 'var(--color-muted-foreground)'
                            }
                        }, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/visitors-by-hour-chart.tsx",
                            lineNumber: 60,
                            columnNumber: 13
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$component$2f$Tooltip$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Tooltip"], {
                            contentStyle: {
                                backgroundColor: 'var(--color-card)',
                                border: `1px solid var(--color-border)`,
                                borderRadius: '6px'
                            },
                            labelStyle: {
                                color: 'var(--color-foreground)'
                            }
                        }, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/visitors-by-hour-chart.tsx",
                            lineNumber: 63,
                            columnNumber: 13
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$cartesian$2f$Bar$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Bar"], {
                            dataKey: "visitors",
                            fill: "var(--color-primary)",
                            radius: [
                                4,
                                4,
                                0,
                                0
                            ]
                        }, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/visitors-by-hour-chart.tsx",
                            lineNumber: 71,
                            columnNumber: 13
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/visitors-by-hour-chart.tsx",
                    lineNumber: 53,
                    columnNumber: 11
                }, this)
            }, void 0, false, {
                fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/visitors-by-hour-chart.tsx",
                lineNumber: 52,
                columnNumber: 9
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/visitors-by-hour-chart.tsx",
        lineNumber: 43,
        columnNumber: 5
    }, this);
}
}),
"[project]/Desktop/retail-analytics/frontend/components/overview/entries-exits-chart.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "EntriesExitsChart",
    ()=>EntriesExitsChart
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$chart$2f$LineChart$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/recharts/es6/chart/LineChart.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$cartesian$2f$Line$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/recharts/es6/cartesian/Line.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$cartesian$2f$XAxis$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/recharts/es6/cartesian/XAxis.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$cartesian$2f$YAxis$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/recharts/es6/cartesian/YAxis.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$cartesian$2f$CartesianGrid$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/recharts/es6/cartesian/CartesianGrid.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$component$2f$Tooltip$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/recharts/es6/component/Tooltip.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$component$2f$Legend$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/recharts/es6/component/Legend.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$component$2f$ResponsiveContainer$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/recharts/es6/component/ResponsiveContainer.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$api$2f$analytics$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/lib/api/analytics.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$scope$2f$ScopeContext$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/lib/scope/ScopeContext.tsx [app-ssr] (ecmascript)");
'use client';
;
;
;
;
;
function EntriesExitsChart() {
    const { storeId } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$scope$2f$ScopeContext$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useScope"])();
    const [data, setData] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])([]);
    const [loading, setLoading] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(true);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        let cancelled = false;
        async function load() {
            setLoading(true);
            const rows = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$api$2f$analytics$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["getEntriesExits"])({
                store_id: storeId ?? undefined
            });
            if (!cancelled) {
                setData(rows);
                setLoading(false);
            }
        }
        load();
        return ()=>{
            cancelled = true;
        };
    }, [
        storeId
    ]);
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "rounded-lg border border-border bg-card p-6",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("h3", {
                className: "mb-4 text-sm font-semibold text-foreground",
                children: "Entries vs Exits"
            }, void 0, false, {
                fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/entries-exits-chart.tsx",
                lineNumber: 45,
                columnNumber: 7
            }, this),
            loading ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "flex h-[300px] items-center justify-center",
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: "h-full w-full animate-pulse rounded bg-muted"
                }, void 0, false, {
                    fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/entries-exits-chart.tsx",
                    lineNumber: 50,
                    columnNumber: 11
                }, this)
            }, void 0, false, {
                fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/entries-exits-chart.tsx",
                lineNumber: 49,
                columnNumber: 9
            }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$component$2f$ResponsiveContainer$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["ResponsiveContainer"], {
                width: "100%",
                height: 300,
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$chart$2f$LineChart$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["LineChart"], {
                    data: data,
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$cartesian$2f$CartesianGrid$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["CartesianGrid"], {
                            strokeDasharray: "3 3",
                            stroke: "var(--color-border)"
                        }, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/entries-exits-chart.tsx",
                            lineNumber: 55,
                            columnNumber: 13
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$cartesian$2f$XAxis$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["XAxis"], {
                            dataKey: "hour",
                            tick: {
                                fontSize: 12,
                                fill: 'var(--color-muted-foreground)'
                            }
                        }, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/entries-exits-chart.tsx",
                            lineNumber: 56,
                            columnNumber: 13
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$cartesian$2f$YAxis$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["YAxis"], {
                            tick: {
                                fontSize: 12,
                                fill: 'var(--color-muted-foreground)'
                            }
                        }, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/entries-exits-chart.tsx",
                            lineNumber: 60,
                            columnNumber: 13
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$component$2f$Tooltip$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Tooltip"], {
                            contentStyle: {
                                backgroundColor: 'var(--color-card)',
                                border: `1px solid var(--color-border)`,
                                borderRadius: '6px'
                            },
                            labelStyle: {
                                color: 'var(--color-foreground)'
                            }
                        }, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/entries-exits-chart.tsx",
                            lineNumber: 63,
                            columnNumber: 13
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$component$2f$Legend$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Legend"], {
                            wrapperStyle: {
                                color: 'var(--color-foreground)',
                                fontSize: 12
                            }
                        }, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/entries-exits-chart.tsx",
                            lineNumber: 71,
                            columnNumber: 13
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$cartesian$2f$Line$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Line"], {
                            type: "monotone",
                            dataKey: "entries",
                            stroke: "var(--color-primary)",
                            strokeWidth: 2,
                            dot: false
                        }, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/entries-exits-chart.tsx",
                            lineNumber: 77,
                            columnNumber: 13
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$cartesian$2f$Line$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Line"], {
                            type: "monotone",
                            dataKey: "exits",
                            stroke: "var(--color-muted-foreground)",
                            strokeWidth: 2,
                            dot: false
                        }, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/entries-exits-chart.tsx",
                            lineNumber: 84,
                            columnNumber: 13
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/entries-exits-chart.tsx",
                    lineNumber: 54,
                    columnNumber: 11
                }, this)
            }, void 0, false, {
                fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/entries-exits-chart.tsx",
                lineNumber: 53,
                columnNumber: 9
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/entries-exits-chart.tsx",
        lineNumber: 44,
        columnNumber: 5
    }, this);
}
}),
"[project]/Desktop/retail-analytics/frontend/components/overview/occupancy-trend-chart.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "OccupancyTrendChart",
    ()=>OccupancyTrendChart
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$chart$2f$AreaChart$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/recharts/es6/chart/AreaChart.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$cartesian$2f$Area$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/recharts/es6/cartesian/Area.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$cartesian$2f$XAxis$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/recharts/es6/cartesian/XAxis.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$cartesian$2f$YAxis$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/recharts/es6/cartesian/YAxis.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$cartesian$2f$CartesianGrid$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/recharts/es6/cartesian/CartesianGrid.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$component$2f$Tooltip$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/recharts/es6/component/Tooltip.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$component$2f$ResponsiveContainer$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/recharts/es6/component/ResponsiveContainer.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$api$2f$analytics$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/lib/api/analytics.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$scope$2f$ScopeContext$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/lib/scope/ScopeContext.tsx [app-ssr] (ecmascript)");
'use client';
;
;
;
;
;
function OccupancyTrendChart() {
    const { storeId } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$scope$2f$ScopeContext$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useScope"])();
    const [data, setData] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])([]);
    const [loading, setLoading] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(true);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        let cancelled = false;
        async function load() {
            setLoading(true);
            const rows = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$api$2f$analytics$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["getOccupancyTrend"])({
                store_id: storeId ?? undefined
            });
            if (!cancelled) {
                setData(rows);
                setLoading(false);
            }
        }
        load();
        return ()=>{
            cancelled = true;
        };
    }, [
        storeId
    ]);
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "rounded-lg border border-border bg-card p-6",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("h3", {
                className: "mb-4 text-sm font-semibold text-foreground",
                children: "Occupancy Trend (7 Days)"
            }, void 0, false, {
                fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/occupancy-trend-chart.tsx",
                lineNumber: 44,
                columnNumber: 7
            }, this),
            loading ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "flex h-[300px] items-center justify-center",
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: "h-full w-full animate-pulse rounded bg-muted"
                }, void 0, false, {
                    fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/occupancy-trend-chart.tsx",
                    lineNumber: 49,
                    columnNumber: 11
                }, this)
            }, void 0, false, {
                fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/occupancy-trend-chart.tsx",
                lineNumber: 48,
                columnNumber: 9
            }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$component$2f$ResponsiveContainer$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["ResponsiveContainer"], {
                width: "100%",
                height: 300,
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$chart$2f$AreaChart$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["AreaChart"], {
                    data: data,
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("defs", {
                            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("linearGradient", {
                                id: "colorOccupancy",
                                x1: "0",
                                y1: "0",
                                x2: "0",
                                y2: "1",
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("stop", {
                                        offset: "5%",
                                        stopColor: "var(--color-primary)",
                                        stopOpacity: 0.3
                                    }, void 0, false, {
                                        fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/occupancy-trend-chart.tsx",
                                        lineNumber: 56,
                                        columnNumber: 17
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("stop", {
                                        offset: "95%",
                                        stopColor: "var(--color-primary)",
                                        stopOpacity: 0
                                    }, void 0, false, {
                                        fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/occupancy-trend-chart.tsx",
                                        lineNumber: 61,
                                        columnNumber: 17
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/occupancy-trend-chart.tsx",
                                lineNumber: 55,
                                columnNumber: 15
                            }, this)
                        }, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/occupancy-trend-chart.tsx",
                            lineNumber: 54,
                            columnNumber: 13
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$cartesian$2f$CartesianGrid$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["CartesianGrid"], {
                            strokeDasharray: "3 3",
                            stroke: "var(--color-border)"
                        }, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/occupancy-trend-chart.tsx",
                            lineNumber: 68,
                            columnNumber: 13
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$cartesian$2f$XAxis$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["XAxis"], {
                            dataKey: "day",
                            tick: {
                                fontSize: 12,
                                fill: 'var(--color-muted-foreground)'
                            }
                        }, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/occupancy-trend-chart.tsx",
                            lineNumber: 69,
                            columnNumber: 13
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$cartesian$2f$YAxis$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["YAxis"], {
                            tick: {
                                fontSize: 12,
                                fill: 'var(--color-muted-foreground)'
                            },
                            domain: [
                                0,
                                100
                            ]
                        }, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/occupancy-trend-chart.tsx",
                            lineNumber: 73,
                            columnNumber: 13
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$component$2f$Tooltip$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Tooltip"], {
                            contentStyle: {
                                backgroundColor: 'var(--color-card)',
                                border: `1px solid var(--color-border)`,
                                borderRadius: '6px'
                            },
                            labelStyle: {
                                color: 'var(--color-foreground)'
                            },
                            formatter: (value)=>[
                                    `${value}%`,
                                    'Occupancy'
                                ]
                        }, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/occupancy-trend-chart.tsx",
                            lineNumber: 77,
                            columnNumber: 13
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$recharts$2f$es6$2f$cartesian$2f$Area$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Area"], {
                            type: "monotone",
                            dataKey: "occupancy",
                            stroke: "var(--color-primary)",
                            strokeWidth: 2,
                            fillOpacity: 1,
                            fill: "url(#colorOccupancy)"
                        }, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/occupancy-trend-chart.tsx",
                            lineNumber: 86,
                            columnNumber: 13
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/occupancy-trend-chart.tsx",
                    lineNumber: 53,
                    columnNumber: 11
                }, this)
            }, void 0, false, {
                fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/occupancy-trend-chart.tsx",
                lineNumber: 52,
                columnNumber: 9
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/Desktop/retail-analytics/frontend/components/overview/occupancy-trend-chart.tsx",
        lineNumber: 43,
        columnNumber: 5
    }, this);
}
}),
"[project]/Desktop/retail-analytics/frontend/app/page.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>OverviewPage
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$dashboard$2f$dashboard$2d$shell$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/components/dashboard/dashboard-shell.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$overview$2f$kpi$2d$card$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/components/overview/kpi-card.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$overview$2f$visitors$2d$by$2d$hour$2d$chart$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/components/overview/visitors-by-hour-chart.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$overview$2f$entries$2d$exits$2d$chart$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/components/overview/entries-exits-chart.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$overview$2f$occupancy$2d$trend$2d$chart$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/components/overview/occupancy-trend-chart.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$api$2f$analytics$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/lib/api/analytics.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$scope$2f$ScopeContext$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/lib/scope/ScopeContext.tsx [app-ssr] (ecmascript)");
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
function OverviewPage() {
    const { storeId } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$scope$2f$ScopeContext$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useScope"])();
    const [kpis, setKpis] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(null);
    const [loading, setLoading] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(true);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        let cancelled = false;
        async function load() {
            setLoading(true);
            const kpiData = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$api$2f$analytics$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["getOverviewKpis"])({
                store_id: storeId ?? undefined
            });
            if (!cancelled) {
                setKpis(kpiData);
                setLoading(false);
            }
        }
        load();
        return ()=>{
            cancelled = true;
        };
    }, [
        storeId
    ]);
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$dashboard$2f$dashboard$2d$shell$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["DashboardShell"], {
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            className: "mx-auto w-full max-w-7xl space-y-8",
            children: [
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("h1", {
                            className: "text-2xl font-semibold tracking-tight text-foreground",
                            children: "Overview"
                        }, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/app/page.tsx",
                            lineNumber: 42,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                            className: "mt-1 text-sm text-muted-foreground",
                            children: "High-level performance across the selected scope."
                        }, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/app/page.tsx",
                            lineNumber: 45,
                            columnNumber: 11
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/Desktop/retail-analytics/frontend/app/page.tsx",
                    lineNumber: 41,
                    columnNumber: 9
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: "grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3",
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$overview$2f$kpi$2d$card$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["KPICard"], {
                            label: kpis?.visitorsToday.label ?? 'Visitors Today',
                            value: kpis ? kpis.visitorsToday.value.toLocaleString() : '',
                            trend: kpis?.visitorsToday.trend,
                            icon: "users",
                            isLoading: loading
                        }, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/app/page.tsx",
                            lineNumber: 51,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$overview$2f$kpi$2d$card$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["KPICard"], {
                            label: kpis?.occupancy.label ?? 'Current Occupancy',
                            value: kpis?.occupancy.value ?? '',
                            unit: kpis?.occupancy.unit,
                            trend: kpis?.occupancy.trend,
                            icon: "activity",
                            isLoading: loading
                        }, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/app/page.tsx",
                            lineNumber: 58,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$overview$2f$kpi$2d$card$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["KPICard"], {
                            label: kpis?.peakOccupancy.label ?? 'Peak Occupancy',
                            value: kpis?.peakOccupancy.value ?? '',
                            unit: kpis?.peakOccupancy.unit,
                            subtext: kpis?.peakOccupancy.subtext,
                            icon: "zap",
                            isLoading: loading
                        }, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/app/page.tsx",
                            lineNumber: 66,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$overview$2f$kpi$2d$card$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["KPICard"], {
                            label: kpis?.dwellTime.label ?? 'Average Dwell Time',
                            value: kpis?.dwellTime.value ?? '',
                            unit: kpis?.dwellTime.unit,
                            trend: kpis?.dwellTime.trend,
                            icon: "clock",
                            isLoading: loading
                        }, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/app/page.tsx",
                            lineNumber: 74,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$overview$2f$kpi$2d$card$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["KPICard"], {
                            label: kpis?.queueLength.label ?? 'Current Queue Length',
                            value: kpis?.queueLength.value ?? '',
                            trend: kpis?.queueLength.trend,
                            icon: "list",
                            isLoading: loading
                        }, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/app/page.tsx",
                            lineNumber: 82,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$overview$2f$kpi$2d$card$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["KPICard"], {
                            label: kpis?.activeCameras.label ?? 'Active Cameras',
                            value: kpis ? `${kpis.activeCameras.value} / ${kpis.activeCameras.total} online` : '',
                            icon: "camera",
                            isLoading: loading
                        }, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/app/page.tsx",
                            lineNumber: 89,
                            columnNumber: 11
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/Desktop/retail-analytics/frontend/app/page.tsx",
                    lineNumber: 50,
                    columnNumber: 9
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: "grid grid-cols-1 gap-6 lg:grid-cols-2",
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "lg:col-span-2",
                            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$overview$2f$visitors$2d$by$2d$hour$2d$chart$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["VisitorsByHourChart"], {}, void 0, false, {
                                fileName: "[project]/Desktop/retail-analytics/frontend/app/page.tsx",
                                lineNumber: 103,
                                columnNumber: 13
                            }, this)
                        }, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/app/page.tsx",
                            lineNumber: 102,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$overview$2f$entries$2d$exits$2d$chart$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["EntriesExitsChart"], {}, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/app/page.tsx",
                            lineNumber: 105,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$overview$2f$occupancy$2d$trend$2d$chart$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["OccupancyTrendChart"], {}, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/app/page.tsx",
                            lineNumber: 106,
                            columnNumber: 11
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/Desktop/retail-analytics/frontend/app/page.tsx",
                    lineNumber: 101,
                    columnNumber: 9
                }, this)
            ]
        }, void 0, true, {
            fileName: "[project]/Desktop/retail-analytics/frontend/app/page.tsx",
            lineNumber: 40,
            columnNumber: 7
        }, this)
    }, void 0, false, {
        fileName: "[project]/Desktop/retail-analytics/frontend/app/page.tsx",
        lineNumber: 39,
        columnNumber: 5
    }, this);
}
}),
];

//# sourceMappingURL=Desktop_retail-analytics_frontend_0m~.914._.js.map