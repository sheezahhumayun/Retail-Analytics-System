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
"[project]/Desktop/retail-analytics/frontend/components/cameras/overlay-toggles.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "DEFAULT_OVERLAYS",
    ()=>DEFAULT_OVERLAYS,
    "OverlayToggles",
    ()=>OverlayToggles
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$box$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Box$3e$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/lucide-react/dist/esm/icons/box.mjs [app-ssr] (ecmascript) <export default as Box>");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$hash$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Hash$3e$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/lucide-react/dist/esm/icons/hash.mjs [app-ssr] (ecmascript) <export default as Hash>");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$shapes$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Shapes$3e$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/lucide-react/dist/esm/icons/shapes.mjs [app-ssr] (ecmascript) <export default as Shapes>");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$minus$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Minus$3e$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/lucide-react/dist/esm/icons/minus.mjs [app-ssr] (ecmascript) <export default as Minus>");
"use client";
;
;
const DEFAULT_OVERLAYS = {
    boundingBoxes: true,
    trackIds: true,
    zones: true,
    countingLines: true
};
const TOGGLES = [
    {
        key: "boundingBoxes",
        label: "Bounding Boxes",
        icon: __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$box$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Box$3e$__["Box"]
    },
    {
        key: "trackIds",
        label: "Track IDs",
        icon: __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$hash$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Hash$3e$__["Hash"]
    },
    {
        key: "zones",
        label: "Zones",
        icon: __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$shapes$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Shapes$3e$__["Shapes"]
    },
    {
        key: "countingLines",
        label: "Counting Lines",
        icon: __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$minus$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Minus$3e$__["Minus"]
    }
];
function OverlayToggles({ value, onChange, size = "sm" }) {
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "flex flex-wrap gap-1.5",
        children: TOGGLES.map(({ key, label, icon: Icon })=>{
            const active = value[key];
            return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                type: "button",
                "aria-pressed": active,
                onClick: ()=>onChange({
                        ...value,
                        [key]: !active
                    }),
                className: `inline-flex items-center gap-1.5 rounded-full border font-medium transition-colors ${size === "md" ? "px-3 py-1.5 text-sm" : "px-2.5 py-1 text-xs"} ${active ? "border-primary bg-primary/10 text-primary" : "border-border bg-transparent text-muted-foreground hover:bg-muted"}`,
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(Icon, {
                        className: size === "md" ? "h-4 w-4" : "h-3.5 w-3.5"
                    }, void 0, false, {
                        fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/overlay-toggles.tsx",
                        lineNumber: 50,
                        columnNumber: 13
                    }, this),
                    label
                ]
            }, key, true, {
                fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/overlay-toggles.tsx",
                lineNumber: 37,
                columnNumber: 11
            }, this);
        })
    }, void 0, false, {
        fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/overlay-toggles.tsx",
        lineNumber: 33,
        columnNumber: 5
    }, this);
}
}),
"[project]/Desktop/retail-analytics/frontend/components/cameras/camera-frame.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "CameraFrame",
    ()=>CameraFrame
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$camera$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Camera$3e$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/lucide-react/dist/esm/icons/camera.mjs [app-ssr] (ecmascript) <export default as Camera>");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$video$2d$off$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__VideoOff$3e$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/lucide-react/dist/esm/icons/video-off.mjs [app-ssr] (ecmascript) <export default as VideoOff>");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$triangle$2d$alert$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__TriangleAlert$3e$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/lucide-react/dist/esm/icons/triangle-alert.mjs [app-ssr] (ecmascript) <export default as TriangleAlert>");
"use client";
;
;
/** The frame uses a true 16:9 coordinate space (160 x 90) so overlays scale
 *  uniformly and text/arrows never distort. Data is stored in 0-100 percentages. */ const SX = 1.6;
const SY = 0.9;
const ZONE_COLORS = {
    accent: "236 72 153",
    warm: "245 158 11",
    cool: "20 184 166"
};
const BOX_COLOR = "16 185 129" // emerald
;
const LINE_COLOR = "37 99 235" // blue
;
function scalePoints(points) {
    return points.split(" ").map((pair)=>{
        const [x, y] = pair.split(",").map(Number);
        return `${x * SX},${y * SY}`;
    }).join(" ");
}
function centroid(points) {
    const coords = points.split(" ").map((p)=>p.split(",").map(Number));
    const x = coords.reduce((s, c)=>s + c[0], 0) / coords.length;
    const y = coords.reduce((s, c)=>s + c[1], 0) / coords.length;
    return {
        x: x * SX,
        y: y * SY
    };
}
function CameraFrame({ camera, overlays }) {
    const isLive = camera.status === "online";
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "relative aspect-video w-full overflow-hidden rounded-md bg-muted",
        children: [
            camera.frameUrl ? // eslint-disable-next-line @next/next/no-img-element
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("img", {
                src: camera.frameUrl || "/placeholder.svg",
                alt: `${camera.name} live frame`,
                className: "h-full w-full object-cover",
                crossOrigin: "anonymous"
            }, void 0, false, {
                fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-frame.tsx",
                lineNumber: 52,
                columnNumber: 9
            }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "flex h-full w-full flex-col items-center justify-center gap-2 bg-[repeating-linear-gradient(45deg,transparent,transparent_10px,rgba(0,0,0,0.02)_10px,rgba(0,0,0,0.02)_20px)] text-muted-foreground",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$camera$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Camera$3e$__["Camera"], {
                        className: "h-8 w-8 opacity-40",
                        "aria-hidden": "true"
                    }, void 0, false, {
                        fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-frame.tsx",
                        lineNumber: 60,
                        columnNumber: 11
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                        className: "text-xs font-medium opacity-60",
                        children: "No frame source"
                    }, void 0, false, {
                        fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-frame.tsx",
                        lineNumber: 61,
                        columnNumber: 11
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-frame.tsx",
                lineNumber: 59,
                columnNumber: 9
            }, this),
            !isLive && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "absolute inset-0 flex flex-col items-center justify-center gap-2 bg-background/70 backdrop-blur-[1px]",
                children: [
                    camera.status === "offline" ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$video$2d$off$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__VideoOff$3e$__["VideoOff"], {
                        className: "h-7 w-7 text-muted-foreground",
                        "aria-hidden": "true"
                    }, void 0, false, {
                        fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-frame.tsx",
                        lineNumber: 69,
                        columnNumber: 13
                    }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$triangle$2d$alert$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__TriangleAlert$3e$__["TriangleAlert"], {
                        className: "h-7 w-7 text-destructive",
                        "aria-hidden": "true"
                    }, void 0, false, {
                        fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-frame.tsx",
                        lineNumber: 71,
                        columnNumber: 13
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                        className: "text-sm font-medium text-foreground",
                        children: camera.status === "offline" ? "Camera Offline" : "Signal Error"
                    }, void 0, false, {
                        fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-frame.tsx",
                        lineNumber: 73,
                        columnNumber: 11
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-frame.tsx",
                lineNumber: 67,
                columnNumber: 9
            }, this),
            isLive && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("svg", {
                viewBox: "0 0 160 90",
                className: "pointer-events-none absolute inset-0 h-full w-full",
                "aria-hidden": "true",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("defs", {
                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("marker", {
                            id: `arrow-${camera.id}`,
                            viewBox: "0 0 10 10",
                            refX: "8",
                            refY: "5",
                            markerWidth: "5",
                            markerHeight: "5",
                            orient: "auto-start-reverse",
                            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("path", {
                                d: "M 0 0 L 10 5 L 0 10 z",
                                fill: `rgb(${LINE_COLOR})`
                            }, void 0, false, {
                                fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-frame.tsx",
                                lineNumber: 96,
                                columnNumber: 15
                            }, this)
                        }, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-frame.tsx",
                            lineNumber: 87,
                            columnNumber: 13
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-frame.tsx",
                        lineNumber: 86,
                        columnNumber: 11
                    }, this),
                    overlays.zones && camera.zones.map((zone)=>{
                        const c = centroid(zone.points);
                        const color = ZONE_COLORS[zone.variant];
                        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("g", {
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("polygon", {
                                    points: scalePoints(zone.points),
                                    fill: `rgb(${color} / 0.16)`,
                                    stroke: `rgb(${color})`,
                                    strokeWidth: 0.6,
                                    strokeDasharray: "2 1.5"
                                }, void 0, false, {
                                    fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-frame.tsx",
                                    lineNumber: 107,
                                    columnNumber: 19
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("text", {
                                    x: c.x,
                                    y: c.y,
                                    textAnchor: "middle",
                                    fontSize: 3.4,
                                    fontWeight: 600,
                                    fill: `rgb(${color})`,
                                    children: zone.label
                                }, void 0, false, {
                                    fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-frame.tsx",
                                    lineNumber: 114,
                                    columnNumber: 19
                                }, this)
                            ]
                        }, zone.id, true, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-frame.tsx",
                            lineNumber: 106,
                            columnNumber: 17
                        }, this);
                    }),
                    overlays.countingLines && camera.countingLines.map((line)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("g", {
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("line", {
                                    x1: line.x1 * SX,
                                    y1: line.y1 * SY,
                                    x2: line.x2 * SX,
                                    y2: line.y2 * SY,
                                    stroke: `rgb(${LINE_COLOR})`,
                                    strokeWidth: 0.8,
                                    markerEnd: `url(#arrow-${camera.id})`
                                }, void 0, false, {
                                    fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-frame.tsx",
                                    lineNumber: 132,
                                    columnNumber: 17
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("text", {
                                    x: line.x1 * SX + 1.5,
                                    y: line.y1 * SY + 3.5,
                                    fontSize: 3.2,
                                    fontWeight: 600,
                                    fill: `rgb(${LINE_COLOR})`,
                                    children: line.label
                                }, void 0, false, {
                                    fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-frame.tsx",
                                    lineNumber: 141,
                                    columnNumber: 17
                                }, this)
                            ]
                        }, line.id, true, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-frame.tsx",
                            lineNumber: 131,
                            columnNumber: 15
                        }, this)),
                    overlays.boundingBoxes && camera.boundingBoxes.map((box)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("g", {
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("rect", {
                                    x: box.x * SX,
                                    y: box.y * SY,
                                    width: box.width * SX,
                                    height: box.height * SY,
                                    fill: "none",
                                    stroke: `rgb(${BOX_COLOR})`,
                                    strokeWidth: 0.7,
                                    rx: 0.5
                                }, void 0, false, {
                                    fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-frame.tsx",
                                    lineNumber: 157,
                                    columnNumber: 17
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("g", {
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("rect", {
                                            x: box.x * SX,
                                            y: box.y * SY - 4.2,
                                            width: overlays.trackIds ? 22 : 14,
                                            height: 4.2,
                                            fill: `rgb(${BOX_COLOR})`,
                                            rx: 0.4
                                        }, void 0, false, {
                                            fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-frame.tsx",
                                            lineNumber: 169,
                                            columnNumber: 19
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("text", {
                                            x: box.x * SX + 0.8,
                                            y: box.y * SY - 1.1,
                                            fontSize: 2.9,
                                            fontWeight: 600,
                                            fill: "white",
                                            children: [
                                                box.label,
                                                " ",
                                                Math.round(box.confidence * 100),
                                                "%",
                                                overlays.trackIds ? ` · #${box.trackId}` : ""
                                            ]
                                        }, void 0, true, {
                                            fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-frame.tsx",
                                            lineNumber: 177,
                                            columnNumber: 19
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-frame.tsx",
                                    lineNumber: 168,
                                    columnNumber: 17
                                }, this)
                            ]
                        }, box.id, true, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-frame.tsx",
                            lineNumber: 156,
                            columnNumber: 15
                        }, this))
                ]
            }, void 0, true, {
                fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-frame.tsx",
                lineNumber: 81,
                columnNumber: 9
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-frame.tsx",
        lineNumber: 48,
        columnNumber: 5
    }, this);
}
}),
"[project]/Desktop/retail-analytics/frontend/components/cameras/status-badge.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "StatusBadge",
    ()=>StatusBadge
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$constants$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/lib/constants.ts [app-ssr] (ecmascript)");
;
;
function StatusBadge({ status }) {
    const config = __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$constants$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["LIVE_CAMERA_STATUS_COLORS"][status];
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
        className: `inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-xs font-medium ${config.bg} ${config.text}`,
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                className: `h-1.5 w-1.5 rounded-full ${config.dot}`,
                "aria-hidden": "true"
            }, void 0, false, {
                fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/status-badge.tsx",
                lineNumber: 10,
                columnNumber: 7
            }, this),
            config.label
        ]
    }, void 0, true, {
        fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/status-badge.tsx",
        lineNumber: 7,
        columnNumber: 5
    }, this);
}
}),
"[project]/Desktop/retail-analytics/frontend/components/cameras/camera-modal.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "CameraModal",
    ()=>CameraModal
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$x$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__X$3e$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/lucide-react/dist/esm/icons/x.mjs [app-ssr] (ecmascript) <export default as X>");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$users$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Users$3e$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/lucide-react/dist/esm/icons/users.mjs [app-ssr] (ecmascript) <export default as Users>");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$log$2d$in$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__LogIn$3e$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/lucide-react/dist/esm/icons/log-in.mjs [app-ssr] (ecmascript) <export default as LogIn>");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$log$2d$out$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__LogOut$3e$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/lucide-react/dist/esm/icons/log-out.mjs [app-ssr] (ecmascript) <export default as LogOut>");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$cameras$2f$overlay$2d$toggles$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/components/cameras/overlay-toggles.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$cameras$2f$camera$2d$frame$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/components/cameras/camera-frame.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$cameras$2f$status$2d$badge$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/components/cameras/status-badge.tsx [app-ssr] (ecmascript)");
"use client";
;
;
;
;
;
;
function CameraModal({ camera, overlays, onOverlaysChange, onClose }) {
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        const onKey = (e)=>{
            if (e.key === "Escape") onClose();
        };
        document.addEventListener("keydown", onKey);
        document.body.style.overflow = "hidden";
        return ()=>{
            document.removeEventListener("keydown", onKey);
            document.body.style.overflow = "";
        };
    }, [
        onClose
    ]);
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6",
        role: "dialog",
        "aria-modal": "true",
        "aria-label": `${camera.name} focused view`,
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "absolute inset-0 bg-background/80 backdrop-blur-sm",
                onClick: onClose,
                "aria-hidden": "true"
            }, void 0, false, {
                fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-modal.tsx",
                lineNumber: 41,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "relative z-10 flex max-h-[90dvh] w-full max-w-4xl flex-col overflow-hidden rounded-xl border border-border bg-card shadow-lg",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "flex items-center justify-between gap-4 border-b border-border px-5 py-3.5",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "flex items-center gap-3",
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("h2", {
                                        className: "text-base font-semibold text-foreground",
                                        children: camera.name
                                    }, void 0, false, {
                                        fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-modal.tsx",
                                        lineNumber: 50,
                                        columnNumber: 13
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$cameras$2f$status$2d$badge$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["StatusBadge"], {
                                        status: camera.status
                                    }, void 0, false, {
                                        fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-modal.tsx",
                                        lineNumber: 51,
                                        columnNumber: 13
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                        className: "hidden text-sm text-muted-foreground sm:inline",
                                        children: camera.location
                                    }, void 0, false, {
                                        fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-modal.tsx",
                                        lineNumber: 52,
                                        columnNumber: 13
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-modal.tsx",
                                lineNumber: 49,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                type: "button",
                                onClick: onClose,
                                "aria-label": "Close",
                                className: "flex h-8 w-8 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-muted hover:text-foreground",
                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$x$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__X$3e$__["X"], {
                                    className: "h-4 w-4"
                                }, void 0, false, {
                                    fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-modal.tsx",
                                    lineNumber: 62,
                                    columnNumber: 13
                                }, this)
                            }, void 0, false, {
                                fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-modal.tsx",
                                lineNumber: 56,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-modal.tsx",
                        lineNumber: 48,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "flex-1 overflow-y-auto p-5",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "mb-3",
                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$cameras$2f$overlay$2d$toggles$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["OverlayToggles"], {
                                    value: overlays,
                                    onChange: onOverlaysChange,
                                    size: "md"
                                }, void 0, false, {
                                    fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-modal.tsx",
                                    lineNumber: 69,
                                    columnNumber: 13
                                }, this)
                            }, void 0, false, {
                                fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-modal.tsx",
                                lineNumber: 68,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$cameras$2f$camera$2d$frame$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["CameraFrame"], {
                                camera: camera,
                                overlays: overlays
                            }, void 0, false, {
                                fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-modal.tsx",
                                lineNumber: 71,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "mt-4 grid grid-cols-3 gap-3",
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(CountStat, {
                                        icon: "occupancy",
                                        label: "Occupancy",
                                        value: camera.occupancy
                                    }, void 0, false, {
                                        fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-modal.tsx",
                                        lineNumber: 75,
                                        columnNumber: 13
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(CountStat, {
                                        icon: "entries",
                                        label: "Entries Today",
                                        value: camera.entriesToday
                                    }, void 0, false, {
                                        fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-modal.tsx",
                                        lineNumber: 76,
                                        columnNumber: 13
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(CountStat, {
                                        icon: "exits",
                                        label: "Exits Today",
                                        value: camera.exitsToday
                                    }, void 0, false, {
                                        fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-modal.tsx",
                                        lineNumber: 77,
                                        columnNumber: 13
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-modal.tsx",
                                lineNumber: 74,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-modal.tsx",
                        lineNumber: 67,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-modal.tsx",
                lineNumber: 46,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-modal.tsx",
        lineNumber: 35,
        columnNumber: 5
    }, this);
}
function CountStat({ icon, label, value }) {
    const Icon = icon === "occupancy" ? __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$users$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Users$3e$__["Users"] : icon === "entries" ? __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$log$2d$in$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__LogIn$3e$__["LogIn"] : __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$log$2d$out$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__LogOut$3e$__["LogOut"];
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "rounded-lg border border-border bg-background p-3",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "flex items-center gap-1.5 text-muted-foreground",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(Icon, {
                        className: "h-3.5 w-3.5"
                    }, void 0, false, {
                        fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-modal.tsx",
                        lineNumber: 98,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                        className: "text-xs font-medium",
                        children: label
                    }, void 0, false, {
                        fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-modal.tsx",
                        lineNumber: 99,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-modal.tsx",
                lineNumber: 97,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                className: "mt-1 text-2xl font-semibold tracking-tight text-foreground",
                children: value.toLocaleString()
            }, void 0, false, {
                fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-modal.tsx",
                lineNumber: 101,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-modal.tsx",
        lineNumber: 96,
        columnNumber: 5
    }, this);
}
}),
"[project]/Desktop/retail-analytics/frontend/components/cameras/camera-tile.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "CameraTile",
    ()=>CameraTile
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$users$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Users$3e$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/lucide-react/dist/esm/icons/users.mjs [app-ssr] (ecmascript) <export default as Users>");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$log$2d$in$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__LogIn$3e$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/lucide-react/dist/esm/icons/log-in.mjs [app-ssr] (ecmascript) <export default as LogIn>");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$log$2d$out$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__LogOut$3e$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/lucide-react/dist/esm/icons/log-out.mjs [app-ssr] (ecmascript) <export default as LogOut>");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$maximize$2d$2$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Maximize2$3e$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/lucide-react/dist/esm/icons/maximize-2.mjs [app-ssr] (ecmascript) <export default as Maximize2>");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$cameras$2f$overlay$2d$toggles$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/components/cameras/overlay-toggles.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$cameras$2f$camera$2d$frame$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/components/cameras/camera-frame.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$cameras$2f$camera$2d$modal$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/components/cameras/camera-modal.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$cameras$2f$status$2d$badge$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/components/cameras/status-badge.tsx [app-ssr] (ecmascript)");
"use client";
;
;
;
;
;
;
;
function CameraTile({ camera }) {
    const [overlays, setOverlays] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$cameras$2f$overlay$2d$toggles$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["DEFAULT_OVERLAYS"]);
    const [expanded, setExpanded] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(false);
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Fragment"], {
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "flex flex-col rounded-lg border border-border bg-card p-4",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "mb-3 flex items-start justify-between gap-2",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("h3", {
                                        className: "text-sm font-semibold text-foreground",
                                        children: camera.name
                                    }, void 0, false, {
                                        fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-tile.tsx",
                                        lineNumber: 25,
                                        columnNumber: 13
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                        className: "text-xs text-muted-foreground",
                                        children: camera.location
                                    }, void 0, false, {
                                        fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-tile.tsx",
                                        lineNumber: 26,
                                        columnNumber: 13
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-tile.tsx",
                                lineNumber: 24,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$cameras$2f$status$2d$badge$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["StatusBadge"], {
                                status: camera.status
                            }, void 0, false, {
                                fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-tile.tsx",
                                lineNumber: 28,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-tile.tsx",
                        lineNumber: 23,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "mb-2.5",
                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$cameras$2f$overlay$2d$toggles$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["OverlayToggles"], {
                            value: overlays,
                            onChange: setOverlays
                        }, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-tile.tsx",
                            lineNumber: 33,
                            columnNumber: 11
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-tile.tsx",
                        lineNumber: 32,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                        type: "button",
                        onClick: ()=>setExpanded(true),
                        "aria-label": `Expand ${camera.name}`,
                        className: "group relative block w-full rounded-md focus:outline-none focus-visible:ring-2 focus-visible:ring-ring",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$cameras$2f$camera$2d$frame$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["CameraFrame"], {
                                camera: camera,
                                overlays: overlays
                            }, void 0, false, {
                                fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-tile.tsx",
                                lineNumber: 43,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                className: "absolute right-2 top-2 flex h-7 w-7 items-center justify-center rounded-md bg-background/80 text-foreground opacity-0 backdrop-blur transition-opacity group-hover:opacity-100",
                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$maximize$2d$2$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Maximize2$3e$__["Maximize2"], {
                                    className: "h-3.5 w-3.5"
                                }, void 0, false, {
                                    fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-tile.tsx",
                                    lineNumber: 45,
                                    columnNumber: 13
                                }, this)
                            }, void 0, false, {
                                fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-tile.tsx",
                                lineNumber: 44,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-tile.tsx",
                        lineNumber: 37,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "mt-3 grid grid-cols-3 gap-2",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(Stat, {
                                icon: __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$users$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Users$3e$__["Users"],
                                label: "Occupancy",
                                value: camera.occupancy
                            }, void 0, false, {
                                fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-tile.tsx",
                                lineNumber: 51,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(Stat, {
                                icon: __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$log$2d$in$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__LogIn$3e$__["LogIn"],
                                label: "Entries",
                                value: camera.entriesToday
                            }, void 0, false, {
                                fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-tile.tsx",
                                lineNumber: 52,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(Stat, {
                                icon: __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$log$2d$out$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__LogOut$3e$__["LogOut"],
                                label: "Exits",
                                value: camera.exitsToday
                            }, void 0, false, {
                                fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-tile.tsx",
                                lineNumber: 53,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-tile.tsx",
                        lineNumber: 50,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-tile.tsx",
                lineNumber: 21,
                columnNumber: 7
            }, this),
            expanded && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$cameras$2f$camera$2d$modal$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["CameraModal"], {
                camera: camera,
                overlays: overlays,
                onOverlaysChange: setOverlays,
                onClose: ()=>setExpanded(false)
            }, void 0, false, {
                fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-tile.tsx",
                lineNumber: 58,
                columnNumber: 9
            }, this)
        ]
    }, void 0, true);
}
function Stat({ icon: Icon, label, value }) {
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "rounded-md bg-muted/50 px-2.5 py-2",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "flex items-center gap-1 text-muted-foreground",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(Icon, {
                        className: "h-3 w-3"
                    }, void 0, false, {
                        fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-tile.tsx",
                        lineNumber: 81,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                        className: "text-[11px] font-medium",
                        children: label
                    }, void 0, false, {
                        fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-tile.tsx",
                        lineNumber: 82,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-tile.tsx",
                lineNumber: 80,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                className: "mt-0.5 text-lg font-semibold tracking-tight text-foreground",
                children: value.toLocaleString()
            }, void 0, false, {
                fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-tile.tsx",
                lineNumber: 84,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/Desktop/retail-analytics/frontend/components/cameras/camera-tile.tsx",
        lineNumber: 79,
        columnNumber: 5
    }, this);
}
}),
"[project]/Desktop/retail-analytics/frontend/lib/admin-cameras-data.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "ANALYTICS_MODULES_LABELS",
    ()=>ANALYTICS_MODULES_LABELS,
    "MOCK_CAMERAS",
    ()=>MOCK_CAMERAS,
    "STORES",
    ()=>STORES,
    "getStatusColor",
    ()=>getStatusColor,
    "getStatusLabel",
    ()=>getStatusLabel
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$constants$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/lib/constants.ts [app-ssr] (ecmascript)");
;
const STORES = [
    'Downtown Mall',
    'Westside Center'
];
const ANALYTICS_MODULES_LABELS = {
    'entry-exit': 'Entry/Exit',
    'occupancy': 'Occupancy',
    'zones': 'Zones',
    'dwell': 'Dwell',
    'heatmap': 'Heatmap',
    'queue': 'Queue'
};
const MOCK_CAMERAS = [
    {
        id: 'CAM-001',
        name: 'Entrance - Left',
        store: 'Downtown Mall',
        location: 'Main entrance, left side',
        status: 'online',
        resolution: '2k',
        fps: 30,
        rtspUrl: 'rtsp://192.168.1.100:554/stream',
        cameraType: 'fixed',
        analyticsModules: [
            'entry-exit',
            'occupancy',
            'queue',
            'heatmap'
        ],
        enabled: true
    },
    {
        id: 'CAM-002',
        name: 'Entrance - Right',
        store: 'Downtown Mall',
        location: 'Main entrance, right side',
        status: 'online',
        resolution: '2k',
        fps: 30,
        rtspUrl: 'rtsp://192.168.1.101:554/stream',
        cameraType: 'fixed',
        analyticsModules: [
            'entry-exit',
            'occupancy',
            'queue',
            'heatmap'
        ],
        enabled: true
    },
    {
        id: 'CAM-003',
        name: 'Electronics Section',
        store: 'Downtown Mall',
        location: 'Electronics aisle 3-4',
        status: 'offline',
        resolution: '1080p',
        fps: 25,
        rtspUrl: 'rtsp://192.168.1.102:554/stream',
        cameraType: 'fixed',
        analyticsModules: [
            'occupancy',
            'zones',
            'dwell',
            'heatmap'
        ],
        enabled: true
    },
    {
        id: 'CAM-004',
        name: 'Checkout Lane 1-3',
        store: 'Downtown Mall',
        location: 'Checkout lanes 1-3',
        status: 'error',
        resolution: '2k',
        fps: 30,
        rtspUrl: 'rtsp://192.168.1.103:554/stream',
        cameraType: 'fixed',
        analyticsModules: [
            'queue',
            'entry-exit',
            'dwell'
        ],
        enabled: true
    },
    {
        id: 'CAM-005',
        name: 'Westside Main Floor',
        store: 'Westside Center',
        location: 'Main floor overview',
        status: 'online',
        resolution: '4k',
        fps: 30,
        rtspUrl: 'rtsp://192.168.2.100:554/stream',
        cameraType: 'ptz',
        analyticsModules: [
            'occupancy',
            'zones',
            'heatmap',
            'entry-exit'
        ],
        enabled: true
    }
];
function getStatusColor(status) {
    return __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$constants$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["CAMERA_STATUS_COLORS"][status];
}
function getStatusLabel(status) {
    return status.charAt(0).toUpperCase() + status.slice(1);
}
}),
"[project]/Desktop/retail-analytics/frontend/lib/camera-data.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "CAMERAS",
    ()=>CAMERAS
]);
const CAMERAS = [
    {
        id: "cam-entrance",
        name: "Main Entrance",
        location: "Front of store",
        status: "online",
        frameUrl: null,
        occupancy: 23,
        entriesToday: 847,
        exitsToday: 824,
        boundingBoxes: [
            {
                id: "b1",
                x: 14,
                y: 42,
                width: 13,
                height: 34,
                confidence: 0.94,
                trackId: 1042,
                label: "person"
            },
            {
                id: "b2",
                x: 38,
                y: 48,
                width: 11,
                height: 30,
                confidence: 0.89,
                trackId: 1055,
                label: "person"
            },
            {
                id: "b3",
                x: 63,
                y: 39,
                width: 14,
                height: 37,
                confidence: 0.97,
                trackId: 1061,
                label: "person"
            }
        ],
        zones: [
            {
                id: "z1",
                label: "Entry Vestibule",
                points: "4,64 40,58 40,94 4,94",
                variant: "accent"
            }
        ],
        countingLines: [
            {
                id: "l1",
                label: "Door Line",
                x1: 48,
                y1: 30,
                x2: 48,
                y2: 92
            }
        ]
    },
    {
        id: "cam-checkout",
        name: "Checkout Lanes",
        location: "Register area",
        status: "online",
        frameUrl: null,
        occupancy: 12,
        entriesToday: 612,
        exitsToday: 598,
        boundingBoxes: [
            {
                id: "b1",
                x: 20,
                y: 45,
                width: 12,
                height: 32,
                confidence: 0.91,
                trackId: 2210,
                label: "person"
            },
            {
                id: "b2",
                x: 52,
                y: 50,
                width: 12,
                height: 31,
                confidence: 0.86,
                trackId: 2231,
                label: "person"
            }
        ],
        zones: [
            {
                id: "z1",
                label: "Queue Zone",
                points: "10,60 55,55 58,92 8,92",
                variant: "warm"
            },
            {
                id: "z2",
                label: "Register",
                points: "66,40 92,40 92,84 66,84",
                variant: "cool"
            }
        ],
        countingLines: [
            {
                id: "l1",
                label: "Lane Line",
                x1: 62,
                y1: 24,
                x2: 62,
                y2: 90
            }
        ]
    },
    {
        id: "cam-aisle3",
        name: "Aisle 3",
        location: "Grocery, center",
        status: "error",
        frameUrl: null,
        occupancy: 0,
        entriesToday: 0,
        exitsToday: 0,
        boundingBoxes: [],
        zones: [
            {
                id: "z1",
                label: "Aisle Zone",
                points: "30,20 70,20 70,94 30,94",
                variant: "accent"
            }
        ],
        countingLines: []
    },
    {
        id: "cam-stockroom",
        name: "Stockroom",
        location: "Rear, staff only",
        status: "offline",
        frameUrl: null,
        occupancy: 0,
        entriesToday: 38,
        exitsToday: 41,
        boundingBoxes: [],
        zones: [],
        countingLines: [
            {
                id: "l1",
                label: "Dock Line",
                x1: 20,
                y1: 30,
                x2: 84,
                y2: 66
            }
        ]
    }
];
}),
"[project]/Desktop/retail-analytics/frontend/lib/api/cameras.ts [app-ssr] (ecmascript) <locals>", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "createCamera",
    ()=>createCamera,
    "deleteCamera",
    ()=>deleteCamera,
    "getCameraStatus",
    ()=>getCameraStatus,
    "getCameras",
    ()=>getCameras,
    "getLiveCameras",
    ()=>getLiveCameras,
    "testCamera",
    ()=>testCamera,
    "updateCamera",
    ()=>updateCamera
]);
// MOCK IMPLEMENTATION — swap the function bodies below for real fetch() calls
// to the FastAPI backend when Module 12 is live. Signatures and return types
// must not change.
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$admin$2d$cameras$2d$data$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/lib/admin-cameras-data.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$camera$2d$data$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/lib/camera-data.ts [app-ssr] (ecmascript)");
;
;
;
// ─── In-memory store (persists for the session) ──────────────────────────────
let cameras = __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$admin$2d$cameras$2d$data$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["MOCK_CAMERAS"].map((c)=>({
        ...c
    }));
function getCameras() {
    return Promise.resolve(cameras.map((c)=>({
            ...c
        })));
}
function getLiveCameras() {
    return Promise.resolve(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$camera$2d$data$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["CAMERAS"].map((c)=>({
            ...c
        })));
}
function getCameraStatus(id) {
    const camera = cameras.find((c)=>c.id === id);
    return Promise.resolve(camera?.status ?? null);
}
function createCamera(data) {
    const camera = {
        ...data
    };
    cameras = [
        ...cameras,
        camera
    ];
    return Promise.resolve({
        ...camera
    });
}
function updateCamera(id, data) {
    const index = cameras.findIndex((c)=>c.id === id);
    if (index === -1) return Promise.resolve(null);
    const updated = {
        ...cameras[index],
        ...data,
        id
    };
    cameras = cameras.map((c)=>c.id === id ? updated : c);
    return Promise.resolve({
        ...updated
    });
}
function deleteCamera(id) {
    const before = cameras.length;
    cameras = cameras.filter((c)=>c.id !== id);
    return Promise.resolve(cameras.length < before);
}
function testCamera(id) {
    const camera = cameras.find((c)=>c.id === id);
    if (!camera) {
        return Promise.resolve({
            status: "error",
            camera_id: id,
            error: "Camera not found"
        });
    }
    if (camera.status === "error") {
        return Promise.resolve({
            status: "error",
            camera_id: camera.id,
            error: "Connection timeout: Camera at " + camera.rtspUrl + " did not respond within 30 seconds."
        });
    }
    if (camera.status === "offline") {
        return Promise.resolve({
            status: "error",
            camera_id: camera.id,
            error: "Camera is currently offline. Please check the power and network connection."
        });
    }
    return Promise.resolve({
        status: "success",
        camera_id: camera.id,
        resolution: camera.resolution,
        fps: camera.fps,
        latency_ms: 45
    });
}
}),
"[project]/Desktop/retail-analytics/frontend/app/live-cameras/page.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>LiveCamerasPage
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$dashboard$2f$dashboard$2d$shell$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/components/dashboard/dashboard-shell.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$cameras$2f$camera$2d$tile$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/components/cameras/camera-tile.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$api$2f$cameras$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/lib/api/cameras.ts [app-ssr] (ecmascript) <locals>");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$scope$2f$scope$2d$filters$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/lib/scope/scope-filters.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$scope$2f$ScopeContext$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/lib/scope/ScopeContext.tsx [app-ssr] (ecmascript)");
'use client';
;
;
;
;
;
;
;
function LiveCamerasPage() {
    const { cameraId, storeCameraIds } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$scope$2f$ScopeContext$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useScope"])();
    const [cameras, setCameras] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])([]);
    const [loading, setLoading] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(true);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        let cancelled = false;
        async function load() {
            setLoading(true);
            const data = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$api$2f$cameras$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__["getLiveCameras"])();
            if (!cancelled) {
                setCameras((0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$scope$2f$scope$2d$filters$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["filterLiveCameras"])(data, cameraId, storeCameraIds));
                setLoading(false);
            }
        }
        load();
        return ()=>{
            cancelled = true;
        };
    }, [
        cameraId,
        storeCameraIds
    ]);
    const onlineCount = cameras.filter((c)=>c.status === 'online').length;
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$dashboard$2f$dashboard$2d$shell$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["DashboardShell"], {
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            className: "mx-auto w-full max-w-7xl space-y-6",
            children: [
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: "flex flex-wrap items-end justify-between gap-2",
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("h1", {
                                    className: "text-2xl font-semibold tracking-tight text-foreground",
                                    children: "Live Cameras"
                                }, void 0, false, {
                                    fileName: "[project]/Desktop/retail-analytics/frontend/app/live-cameras/page.tsx",
                                    lineNumber: 41,
                                    columnNumber: 13
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                    className: "mt-1 text-sm text-muted-foreground",
                                    children: "Real-time detection feeds across the selected scope."
                                }, void 0, false, {
                                    fileName: "[project]/Desktop/retail-analytics/frontend/app/live-cameras/page.tsx",
                                    lineNumber: 44,
                                    columnNumber: 13
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/app/live-cameras/page.tsx",
                            lineNumber: 40,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                            className: "text-sm text-muted-foreground",
                            children: loading ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                className: "inline-block h-4 w-24 animate-pulse rounded bg-muted"
                            }, void 0, false, {
                                fileName: "[project]/Desktop/retail-analytics/frontend/app/live-cameras/page.tsx",
                                lineNumber: 50,
                                columnNumber: 15
                            }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Fragment"], {
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                        className: "font-medium text-foreground",
                                        children: onlineCount
                                    }, void 0, false, {
                                        fileName: "[project]/Desktop/retail-analytics/frontend/app/live-cameras/page.tsx",
                                        lineNumber: 53,
                                        columnNumber: 17
                                    }, this),
                                    " /",
                                    ' ',
                                    cameras.length,
                                    " online"
                                ]
                            }, void 0, true)
                        }, void 0, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/app/live-cameras/page.tsx",
                            lineNumber: 48,
                            columnNumber: 11
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/Desktop/retail-analytics/frontend/app/live-cameras/page.tsx",
                    lineNumber: 39,
                    columnNumber: 9
                }, this),
                loading ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: "grid grid-cols-1 gap-5 lg:grid-cols-2",
                    children: Array.from({
                        length: 4
                    }).map((_, i)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "aspect-video animate-pulse rounded-lg border border-border bg-muted"
                        }, i, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/app/live-cameras/page.tsx",
                            lineNumber: 63,
                            columnNumber: 15
                        }, this))
                }, void 0, false, {
                    fileName: "[project]/Desktop/retail-analytics/frontend/app/live-cameras/page.tsx",
                    lineNumber: 61,
                    columnNumber: 11
                }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: "grid grid-cols-1 gap-5 lg:grid-cols-2",
                    children: cameras.map((camera)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$cameras$2f$camera$2d$tile$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["CameraTile"], {
                            camera: camera
                        }, camera.id, false, {
                            fileName: "[project]/Desktop/retail-analytics/frontend/app/live-cameras/page.tsx",
                            lineNumber: 72,
                            columnNumber: 15
                        }, this))
                }, void 0, false, {
                    fileName: "[project]/Desktop/retail-analytics/frontend/app/live-cameras/page.tsx",
                    lineNumber: 70,
                    columnNumber: 11
                }, this)
            ]
        }, void 0, true, {
            fileName: "[project]/Desktop/retail-analytics/frontend/app/live-cameras/page.tsx",
            lineNumber: 38,
            columnNumber: 7
        }, this)
    }, void 0, false, {
        fileName: "[project]/Desktop/retail-analytics/frontend/app/live-cameras/page.tsx",
        lineNumber: 37,
        columnNumber: 5
    }, this);
}
}),
];

//# sourceMappingURL=Desktop_retail-analytics_frontend_0~ma_i2._.js.map