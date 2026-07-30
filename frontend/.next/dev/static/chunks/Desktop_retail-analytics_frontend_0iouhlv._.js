(globalThis["TURBOPACK"] || (globalThis["TURBOPACK"] = [])).push([typeof document === "object" ? document.currentScript : undefined,
"[project]/Desktop/retail-analytics/frontend/components/auth/auth-loading.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "AuthLoading",
    ()=>AuthLoading
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
;
function AuthLoading() {
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "flex min-h-dvh items-center justify-center bg-background",
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            className: "text-center",
            children: [
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: "relative mx-auto mb-3 h-10 w-10",
                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "absolute inset-0 animate-spin rounded-full border-4 border-transparent border-t-primary border-r-primary"
                    }, void 0, false, {
                        fileName: "[project]/Desktop/retail-analytics/frontend/components/auth/auth-loading.tsx",
                        lineNumber: 6,
                        columnNumber: 11
                    }, this)
                }, void 0, false, {
                    fileName: "[project]/Desktop/retail-analytics/frontend/components/auth/auth-loading.tsx",
                    lineNumber: 5,
                    columnNumber: 9
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                    className: "text-sm text-muted-foreground",
                    children: "Loading…"
                }, void 0, false, {
                    fileName: "[project]/Desktop/retail-analytics/frontend/components/auth/auth-loading.tsx",
                    lineNumber: 8,
                    columnNumber: 9
                }, this)
            ]
        }, void 0, true, {
            fileName: "[project]/Desktop/retail-analytics/frontend/components/auth/auth-loading.tsx",
            lineNumber: 4,
            columnNumber: 7
        }, this)
    }, void 0, false, {
        fileName: "[project]/Desktop/retail-analytics/frontend/components/auth/auth-loading.tsx",
        lineNumber: 3,
        columnNumber: 5
    }, this);
}
_c = AuthLoading;
var _c;
__turbopack_context__.k.register(_c, "AuthLoading");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/Desktop/retail-analytics/frontend/lib/auth/mock-users.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "DEFAULT_MOCK_PASSWORD",
    ()=>DEFAULT_MOCK_PASSWORD,
    "createMockUser",
    ()=>createMockUser,
    "deleteMockUser",
    ()=>deleteMockUser,
    "findMockUserByEmail",
    ()=>findMockUserByEmail,
    "findMockUserById",
    ()=>findMockUserById,
    "getMockUserPassword",
    ()=>getMockUserPassword,
    "listMockUsers",
    ()=>listMockUsers,
    "resetMockUserPassword",
    ()=>resetMockUserPassword,
    "updateMockUser",
    ()=>updateMockUser
]);
const DEFAULT_MOCK_PASSWORD = "demo";
const SEED_USERS = [
    {
        id: "1",
        name: "Sarah Chen",
        email: "sarah.chen@retailco.com",
        role: "Store Manager",
        assignedStore: "Downtown Mall",
        status: "Active",
        password: DEFAULT_MOCK_PASSWORD
    },
    {
        id: "2",
        name: "Marcus Johnson",
        email: "marcus.johnson@retailco.com",
        role: "Operations Manager",
        assignedStore: "Downtown Mall",
        status: "Active",
        password: DEFAULT_MOCK_PASSWORD
    },
    {
        id: "3",
        name: "Elena Rodriguez",
        email: "elena.rodriguez@retailco.com",
        role: "Retail Analyst",
        assignedStore: "Downtown Mall",
        status: "Active",
        password: DEFAULT_MOCK_PASSWORD
    },
    {
        id: "4",
        name: "David Kim",
        email: "david.kim@retailco.com",
        role: "System Administrator",
        assignedStore: "Westside Center",
        status: "Active",
        password: DEFAULT_MOCK_PASSWORD
    }
];
let users = SEED_USERS.map((user)=>({
        ...user
    }));
let userCounter = users.length + 1;
function toPublicUser({ password: _password, ...user }) {
    return {
        ...user
    };
}
function nextUserId() {
    const id = `USR-${String(userCounter).padStart(3, "0")}`;
    userCounter += 1;
    return id;
}
function listMockUsers() {
    return users.map(toPublicUser);
}
function findMockUserByEmail(email) {
    return users.find((user)=>user.email === email);
}
function findMockUserById(id) {
    return users.find((user)=>user.id === id);
}
function getMockUserPassword(id) {
    return findMockUserById(id)?.password;
}
function createMockUser(data) {
    const stored = {
        id: data.id ?? nextUserId(),
        name: data.name,
        email: data.email,
        role: data.role,
        assignedStore: data.assignedStore,
        status: data.status ?? "Active",
        password: data.password
    };
    users = [
        ...users,
        stored
    ];
    return toPublicUser(stored);
}
function updateMockUser(id, data) {
    const index = users.findIndex((user)=>user.id === id);
    if (index === -1) return null;
    const updated = {
        ...users[index],
        ...data,
        id
    };
    users = users.map((user)=>user.id === id ? updated : user);
    return toPublicUser(updated);
}
function deleteMockUser(id) {
    const before = users.length;
    users = users.filter((user)=>user.id !== id);
    return users.length < before;
}
function resetMockUserPassword(id, newPassword) {
    const index = users.findIndex((user)=>user.id === id);
    if (index === -1) return false;
    users = users.map((user)=>user.id === id ? {
            ...user,
            password: newPassword
        } : user);
    return true;
}
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/Desktop/retail-analytics/frontend/lib/constants.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "ACTION_STATUS_COLORS",
    ()=>ACTION_STATUS_COLORS,
    "ALERT_STATUS_COLORS",
    ()=>ALERT_STATUS_COLORS,
    "CAMERA_STATUS_COLORS",
    ()=>CAMERA_STATUS_COLORS,
    "LIVE_CAMERA_STATUS_COLORS",
    ()=>LIVE_CAMERA_STATUS_COLORS,
    "OCCUPANCY_THRESHOLDS",
    ()=>OCCUPANCY_THRESHOLDS,
    "OCCUPANCY_THRESHOLD_COLORS",
    ()=>OCCUPANCY_THRESHOLD_COLORS,
    "SEVERITY_COLORS",
    ()=>SEVERITY_COLORS,
    "STATUS_COLORS",
    ()=>STATUS_COLORS,
    "USER_STATUS_COLORS",
    ()=>USER_STATUS_COLORS,
    "getOccupancyThresholdColor",
    ()=>getOccupancyThresholdColor,
    "getRatioThresholdColor",
    ()=>getRatioThresholdColor
]);
const SEVERITY_COLORS = {
    critical: {
        hex: "#ff4444",
        badge: "bg-red-900/20 text-red-400 border-red-800",
        dot: "bg-red-500"
    },
    warning: {
        hex: "#fbbf24",
        badge: "bg-amber-900/20 text-amber-400 border-amber-800",
        dot: "bg-amber-500"
    },
    info: {
        hex: "#3b82f6",
        badge: "bg-blue-900/20 text-blue-400 border-blue-800",
        dot: "bg-blue-500"
    }
};
const ALERT_STATUS_COLORS = {
    open: "bg-gray-800/40 text-gray-300 border-gray-700",
    acknowledged: "bg-blue-900/20 text-blue-400 border-blue-800",
    resolved: "bg-green-900/20 text-green-400 border-green-800"
};
const LIVE_CAMERA_STATUS_COLORS = {
    online: {
        label: "Online",
        dot: "bg-green-500",
        text: "text-green-700 dark:text-green-400",
        bg: "bg-green-500/10"
    },
    offline: {
        label: "Offline",
        dot: "bg-muted-foreground",
        text: "text-muted-foreground",
        bg: "bg-muted"
    },
    error: {
        label: "Error",
        dot: "bg-red-500",
        text: "text-red-700 dark:text-red-400",
        bg: "bg-red-500/10"
    }
};
const CAMERA_STATUS_COLORS = {
    online: "bg-green-500/10 text-green-700 dark:text-green-400",
    offline: "bg-red-500/10 text-red-700 dark:text-red-400",
    error: "bg-amber-500/10 text-amber-700 dark:text-amber-400",
    disabled: "bg-gray-500/10 text-gray-700 dark:text-gray-400"
};
const USER_STATUS_COLORS = {
    Active: "bg-green-500/10 text-green-700 dark:text-green-400",
    Disabled: "bg-gray-500/10 text-gray-700 dark:text-gray-400"
};
const STATUS_COLORS = {
    alert: ALERT_STATUS_COLORS,
    camera: CAMERA_STATUS_COLORS,
    liveCamera: LIVE_CAMERA_STATUS_COLORS,
    user: USER_STATUS_COLORS
};
const ACTION_STATUS_COLORS = {
    positive: "hover:bg-green-500/10 text-green-600 dark:text-green-400",
    negative: "hover:bg-red-500/10 text-red-600 dark:text-red-400",
    positiveIcon: "text-green-500",
    negativeIcon: "text-red-500",
    negativePanel: "bg-red-500/10 border border-red-500/20"
};
const OCCUPANCY_THRESHOLDS = {
    high: 75,
    medium: 50,
    low: 30
};
const OCCUPANCY_THRESHOLD_COLORS = {
    high: "#ef4444",
    medium: "#f97316",
    elevated: "#38bdf8",
    low: "#3b82f6"
};
function getOccupancyThresholdColor(value) {
    if (value >= OCCUPANCY_THRESHOLDS.high) return OCCUPANCY_THRESHOLD_COLORS.high;
    if (value >= OCCUPANCY_THRESHOLDS.medium) return OCCUPANCY_THRESHOLD_COLORS.medium;
    if (value >= OCCUPANCY_THRESHOLDS.low) return OCCUPANCY_THRESHOLD_COLORS.elevated;
    return OCCUPANCY_THRESHOLD_COLORS.low;
}
function getRatioThresholdColor(ratio) {
    if (ratio >= 0.75) return OCCUPANCY_THRESHOLD_COLORS.high;
    if (ratio >= 0.5) return OCCUPANCY_THRESHOLD_COLORS.medium;
    if (ratio >= 0.3) return OCCUPANCY_THRESHOLD_COLORS.elevated;
    return OCCUPANCY_THRESHOLD_COLORS.low;
}
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/Desktop/retail-analytics/frontend/lib/admin-users-data.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "ROLE_COLORS",
    ()=>ROLE_COLORS,
    "STORES",
    ()=>STORES,
    "USER_ROLES",
    ()=>USER_ROLES,
    "getStatusColor",
    ()=>getStatusColor,
    "getStatusLabel",
    ()=>getStatusLabel
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$constants$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/lib/constants.ts [app-client] (ecmascript)");
;
const STORES = [
    'Downtown Mall',
    'Westside Center'
];
const USER_ROLES = [
    'Store Manager',
    'Operations Manager',
    'Retail Analyst',
    'System Administrator'
];
const ROLE_COLORS = {
    'Store Manager': 'bg-blue-500/10 text-blue-700 dark:text-blue-400',
    'Operations Manager': 'bg-purple-500/10 text-purple-700 dark:text-purple-400',
    'Retail Analyst': 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-400',
    'System Administrator': 'bg-rose-500/10 text-rose-700 dark:text-rose-400'
};
function getStatusColor(status) {
    return __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$constants$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["USER_STATUS_COLORS"][status];
}
function getStatusLabel(status) {
    return status;
}
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/Desktop/retail-analytics/frontend/lib/api/users.ts [app-client] (ecmascript) <locals>", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "createUser",
    ()=>createUser,
    "deleteUser",
    ()=>deleteUser,
    "getUsers",
    ()=>getUsers,
    "resetPassword",
    ()=>resetPassword,
    "updateUser",
    ()=>updateUser
]);
// MOCK IMPLEMENTATION — swap the function bodies below for real fetch() calls
// to the FastAPI backend when Module 12 is live. Signatures and return types
// must not change.
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$auth$2f$mock$2d$users$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/lib/auth/mock-users.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$admin$2d$users$2d$data$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/lib/admin-users-data.ts [app-client] (ecmascript)");
;
;
;
function getUsers() {
    return Promise.resolve((0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$auth$2f$mock$2d$users$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["listMockUsers"])());
}
function createUser(data) {
    return Promise.resolve((0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$auth$2f$mock$2d$users$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["createMockUser"])(data));
}
function updateUser(id, data) {
    return Promise.resolve((0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$auth$2f$mock$2d$users$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["updateMockUser"])(id, data));
}
function deleteUser(id) {
    return Promise.resolve((0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$auth$2f$mock$2d$users$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["deleteMockUser"])(id));
}
function resetPassword(id, newPassword) {
    const success = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$auth$2f$mock$2d$users$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["resetMockUserPassword"])(id, newPassword);
    return Promise.resolve({
        user_id: id,
        success
    });
}
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/Desktop/retail-analytics/frontend/lib/api/auth.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "getCurrentUser",
    ()=>getCurrentUser,
    "login",
    ()=>login,
    "loginByRole",
    ()=>loginByRole,
    "logout",
    ()=>logout
]);
// MOCK IMPLEMENTATION — swap the function bodies below for real fetch() calls
// to the FastAPI backend when Module 12 is live. Signatures and return types
// must not change.
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$api$2f$users$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/lib/api/users.ts [app-client] (ecmascript) <locals>");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$auth$2f$mock$2d$users$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/lib/auth/mock-users.ts [app-client] (ecmascript)");
;
;
const SESSION_KEY = "auth_session";
function login(email, password) {
    return (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$api$2f$users$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__["getUsers"])().then((allUsers)=>{
        if (password !== __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$auth$2f$mock$2d$users$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["DEFAULT_MOCK_PASSWORD"]) {
            throw new Error('Invalid email or password. (Hint: try password "demo")');
        }
        const user = allUsers.find((u)=>u.email === email);
        if (!user) {
            throw new Error('Invalid email or password. (Hint: try password "demo")');
        }
        const session = {
            id: user.id,
            name: user.name,
            email: user.email,
            role: user.role
        };
        if ("TURBOPACK compile-time truthy", 1) {
            localStorage.setItem(SESSION_KEY, JSON.stringify(session));
        }
        return session;
    });
}
function loginByRole(role, password) {
    return (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$api$2f$users$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__["getUsers"])().then((allUsers)=>{
        if (password !== __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$auth$2f$mock$2d$users$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["DEFAULT_MOCK_PASSWORD"]) {
            throw new Error('Invalid email or password. (Hint: try password "demo")');
        }
        const user = allUsers.find((u)=>u.role === role);
        if (!user) {
            throw new Error('Invalid email or password. (Hint: try password "demo")');
        }
        return login(user.email, password);
    });
}
function logout() {
    if ("TURBOPACK compile-time truthy", 1) {
        localStorage.removeItem(SESSION_KEY);
    }
    return Promise.resolve();
}
function getCurrentUser() {
    if ("TURBOPACK compile-time falsy", 0) //TURBOPACK unreachable
    ;
    const session = localStorage.getItem(SESSION_KEY);
    return session ? JSON.parse(session) : null;
}
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/Desktop/retail-analytics/frontend/lib/auth/AuthContext.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "AuthProvider",
    ()=>AuthProvider,
    "useAuth",
    ()=>useAuth
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/navigation.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$api$2f$auth$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/lib/api/auth.ts [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature(), _s1 = __turbopack_context__.k.signature();
"use client";
;
;
;
const AuthContext = /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["createContext"])(null);
function sessionToAuthUser(session) {
    return {
        id: session.id,
        name: session.name,
        email: session.email,
        role: session.role,
        mustChangePassword: false
    };
}
function AuthProvider({ children }) {
    _s();
    const router = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRouter"])();
    const [user, setUser] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [isLoading, setIsLoading] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(true);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "AuthProvider.useEffect": ()=>{
            const session = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$api$2f$auth$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["getCurrentUser"])();
            setUser(session ? sessionToAuthUser(session) : null);
            setIsLoading(false);
        }
    }["AuthProvider.useEffect"], []);
    const login = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "AuthProvider.useCallback[login]": async (email, password)=>{
            const session = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$api$2f$auth$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["login"])(email, password);
            setUser(sessionToAuthUser(session));
        }
    }["AuthProvider.useCallback[login]"], []);
    const logout = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "AuthProvider.useCallback[logout]": async ()=>{
            await (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$api$2f$auth$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["logout"])();
            setUser(null);
            router.push("/login");
        }
    }["AuthProvider.useCallback[logout]"], [
        router
    ]);
    const value = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useMemo"])({
        "AuthProvider.useMemo[value]": ()=>({
                user,
                isLoading,
                login,
                logout
            })
    }["AuthProvider.useMemo[value]"], [
        user,
        isLoading,
        login,
        logout
    ]);
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(AuthContext.Provider, {
        value: value,
        children: children
    }, void 0, false, {
        fileName: "[project]/Desktop/retail-analytics/frontend/lib/auth/AuthContext.tsx",
        lineNumber: 82,
        columnNumber: 5
    }, this);
}
_s(AuthProvider, "D5A/AAd0yfCy3Pzsq0/9VcTFewE=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRouter"]
    ];
});
_c = AuthProvider;
function useAuth() {
    _s1();
    const context = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useContext"])(AuthContext);
    if (!context) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
}
_s1(useAuth, "b9L3QQ+jgeyIrH0NfHrJ8nn7VMU=");
var _c;
__turbopack_context__.k.register(_c, "AuthProvider");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/Desktop/retail-analytics/frontend/components/auth/auth-guard.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "AuthGuard",
    ()=>AuthGuard
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/navigation.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$auth$2f$auth$2d$loading$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/components/auth/auth-loading.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$auth$2f$AuthContext$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/lib/auth/AuthContext.tsx [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature();
"use client";
;
;
;
;
const PUBLIC_ROUTES = new Set([
    "/login"
]);
function AuthGuard({ children }) {
    _s();
    const { user, isLoading } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$auth$2f$AuthContext$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useAuth"])();
    const pathname = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["usePathname"])();
    const router = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRouter"])();
    const isPublicRoute = PUBLIC_ROUTES.has(pathname);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "AuthGuard.useEffect": ()=>{
            if (!isLoading && !user && !isPublicRoute) {
                router.replace("/login");
            }
        }
    }["AuthGuard.useEffect"], [
        isLoading,
        user,
        isPublicRoute,
        router
    ]);
    if (isLoading) {
        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$auth$2f$auth$2d$loading$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["AuthLoading"], {}, void 0, false, {
            fileName: "[project]/Desktop/retail-analytics/frontend/components/auth/auth-guard.tsx",
            lineNumber: 24,
            columnNumber: 12
        }, this);
    }
    if (!user && !isPublicRoute) {
        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$auth$2f$auth$2d$loading$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["AuthLoading"], {}, void 0, false, {
            fileName: "[project]/Desktop/retail-analytics/frontend/components/auth/auth-guard.tsx",
            lineNumber: 28,
            columnNumber: 12
        }, this);
    }
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Fragment"], {
        children: children
    }, void 0, false);
}
_s(AuthGuard, "b9R0/CoP0BCV1LzdSVzG4MLU2KA=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$auth$2f$AuthContext$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useAuth"],
        __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["usePathname"],
        __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRouter"]
    ];
});
_c = AuthGuard;
var _c;
__turbopack_context__.k.register(_c, "AuthGuard");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/Desktop/retail-analytics/frontend/lib/scope-data.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "DEPLOYMENT_ORGANIZATION",
    ()=>DEPLOYMENT_ORGANIZATION,
    "DEPLOYMENT_ORG_ID",
    ()=>DEPLOYMENT_ORG_ID,
    "ORGANIZATIONS",
    ()=>ORGANIZATIONS
]);
function zones(...names) {
    return names.map((name, i)=>({
            id: `${i}-${name}`,
            name
        }));
}
const DEPLOYMENT_ORG_ID = "org-northwind";
const DEPLOYMENT_ORGANIZATION = {
    id: DEPLOYMENT_ORG_ID,
    name: "Northwind Retail Group",
    stores: [
        {
            id: "store-downtown",
            name: "Downtown Flagship",
            cameras: [
                {
                    id: "cam-entrance",
                    name: "Entrance Cam",
                    zones: zones("Vestibule", "Greeter Area")
                },
                {
                    id: "cam-checkout",
                    name: "Checkout Cam",
                    zones: zones("Registers", "Queue Lane")
                },
                {
                    id: "cam-apparel",
                    name: "Apparel Cam",
                    zones: zones("Menswear", "Womenswear", "Fitting Rooms")
                }
            ]
        },
        {
            id: "store-mall",
            name: "Riverside Mall",
            cameras: [
                {
                    id: "cam-atrium",
                    name: "Atrium Cam",
                    zones: zones("Main Aisle", "Promo Display")
                },
                {
                    id: "cam-electronics",
                    name: "Electronics Cam",
                    zones: zones("TVs", "Mobile", "Accessories")
                }
            ]
        },
        {
            id: "store-westside",
            name: "Westside Market",
            cameras: [
                {
                    id: "cam-produce",
                    name: "Produce Cam",
                    zones: zones("Fresh Produce", "Floral")
                },
                {
                    id: "cam-deli",
                    name: "Deli Cam",
                    zones: zones("Deli Counter", "Bakery")
                }
            ]
        }
    ]
};
const ORGANIZATIONS = [
    DEPLOYMENT_ORGANIZATION
];
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/Desktop/retail-analytics/frontend/lib/api/stores.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "getOrganization",
    ()=>getOrganization,
    "getOrganizations",
    ()=>getOrganizations,
    "getStores",
    ()=>getStores
]);
// MOCK IMPLEMENTATION — swap the function bodies below for real fetch() calls
// to the FastAPI backend when Module 12 is live. Signatures and return types
// must not change.
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$scope$2d$data$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/lib/scope-data.ts [app-client] (ecmascript)");
;
function getOrganization() {
    return Promise.resolve(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$scope$2d$data$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["DEPLOYMENT_ORGANIZATION"]);
}
function getStores() {
    return Promise.resolve([
        ...__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$scope$2d$data$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["DEPLOYMENT_ORGANIZATION"].stores
    ]);
}
function getOrganizations() {
    return Promise.resolve(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$scope$2d$data$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["ORGANIZATIONS"]);
}
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/Desktop/retail-analytics/frontend/lib/scope/scope-filters.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "CUSTOMER_FLOW_CAMERAS",
    ()=>CUSTOMER_FLOW_CAMERAS,
    "filterCustomerFlowCameras",
    ()=>filterCustomerFlowCameras,
    "filterHeatmapCameras",
    ()=>filterHeatmapCameras,
    "filterLiveCameras",
    ()=>filterLiveCameras,
    "filterZonePerformanceRows",
    ()=>filterZonePerformanceRows,
    "getStoreCameraIds",
    ()=>getStoreCameraIds,
    "heatmapCameraIdsForScope",
    ()=>heatmapCameraIdsForScope,
    "resolveCustomerFlowCameraId",
    ()=>resolveCustomerFlowCameraId,
    "resolveEffectiveCameraId",
    ()=>resolveEffectiveCameraId,
    "resolveZoneId",
    ()=>resolveZoneId,
    "scaleDataRows",
    ()=>scaleDataRows,
    "scaleStatSummaries",
    ()=>scaleStatSummaries,
    "scopeScaleFactor",
    ()=>scopeScaleFactor,
    "trajectoryIdsForFlowCamera",
    ()=>trajectoryIdsForFlowCamera
]);
function scopeScaleFactor(id) {
    if (!id) return 1;
    let hash = 0;
    for(let i = 0; i < id.length; i++){
        hash = (hash + id.charCodeAt(i) * (i + 1)) % 97;
    }
    return 0.85 + hash % 30 / 100;
}
function scaleDataRows(rows, factor) {
    return rows.map((row)=>({
            ...row,
            current: Math.round(row.current * factor),
            prior: row.prior !== undefined ? Math.round(row.prior * factor) : undefined
        }));
}
function scaleStatSummaries(stats, factor) {
    return stats.map((stat)=>{
        const numeric = Number.parseInt(stat.value.replace(/[^\d]/g, ""), 10);
        if (Number.isNaN(numeric)) return stat;
        const scaled = Math.round(numeric * factor);
        const value = stat.value.includes("%") ? `${scaled}%` : scaled.toLocaleString();
        return {
            ...stat,
            value
        };
    });
}
function getStoreCameraIds(store) {
    return store?.cameras.map((camera)=>camera.id) ?? [];
}
function filterLiveCameras(cameras, cameraId, storeCameraIds) {
    if (cameraId) {
        return cameras.filter((camera)=>camera.id === cameraId);
    }
    if (storeCameraIds.length > 0) {
        return cameras.filter((camera)=>storeCameraIds.includes(camera.id));
    }
    return cameras;
}
const SCOPE_TO_HEATMAP = {
    "cam-entrance": "cam-entrance",
    "cam-checkout": "cam-checkout",
    "cam-apparel": "cam-apparel",
    "cam-atrium": "cam-overview",
    "cam-electronics": "cam-aisle3",
    "cam-produce": "cam-overview",
    "cam-deli": "cam-overview"
};
function heatmapCameraIdsForScope(cameraId, storeCameraIds) {
    const ids = new Set();
    if (cameraId) {
        ids.add(SCOPE_TO_HEATMAP[cameraId] ?? "cam-overview");
    }
    for (const id of storeCameraIds){
        ids.add(SCOPE_TO_HEATMAP[id] ?? "cam-overview");
    }
    return [
        ...ids
    ];
}
function filterHeatmapCameras(cameras, cameraId, storeCameraIds) {
    const allowed = heatmapCameraIdsForScope(cameraId, storeCameraIds);
    if (allowed.length === 0) return cameras;
    const filtered = cameras.filter((camera)=>allowed.includes(camera.id));
    return filtered.length > 0 ? filtered : cameras;
}
function resolveEffectiveCameraId(globalCameraId, pageCameraId, allowedIds) {
    if (pageCameraId && allowedIds.includes(pageCameraId)) return pageCameraId;
    if (globalCameraId) {
        const mapped = SCOPE_TO_HEATMAP[globalCameraId] ?? globalCameraId;
        if (allowedIds.includes(mapped)) return mapped;
    }
    return allowedIds[0] ?? pageCameraId ?? globalCameraId ?? "";
}
function resolveZoneId(zoneId, camera, store) {
    if (zoneId) return zoneId;
    if (camera?.zones[0]?.id) return camera.zones[0].id;
    if (store?.cameras[0]?.zones[0]?.id) return store.cameras[0].zones[0].id;
    return "entrance";
}
function filterZonePerformanceRows(rows, zoneId, storeId) {
    if (zoneId) {
        const match = rows.find((row)=>row.id === zoneId || row.zone.toLowerCase().includes(zoneId.split("-").pop()?.toLowerCase() ?? ""));
        return match ? [
            match
        ] : rows;
    }
    if (storeId) {
        const factor = scopeScaleFactor(storeId);
        return rows.map((row)=>({
                ...row,
                visits: Math.round(row.visits * factor),
                occupancy: Math.min(100, Math.round(row.occupancy * factor))
            }));
    }
    return rows;
}
const CUSTOMER_FLOW_CAMERAS = [
    {
        id: "main",
        label: "Main Floor"
    },
    {
        id: "entrance",
        label: "Entrance"
    },
    {
        id: "retail",
        label: "Retail Section"
    }
];
const SCOPE_TO_FLOW_CAMERAS = {
    "cam-entrance": [
        "entrance",
        "main"
    ],
    "cam-checkout": [
        "retail",
        "main"
    ],
    "cam-apparel": [
        "retail",
        "main"
    ],
    "cam-atrium": [
        "main",
        "entrance"
    ],
    "cam-electronics": [
        "retail",
        "main"
    ],
    "cam-produce": [
        "entrance",
        "main"
    ],
    "cam-deli": [
        "retail",
        "main"
    ]
};
const FLOW_CAMERA_TRAJECTORIES = {
    main: [
        "path1",
        "path2",
        "path3",
        "path4"
    ],
    entrance: [
        "path1",
        "path3"
    ],
    retail: [
        "path2",
        "path3",
        "path4"
    ]
};
function filterCustomerFlowCameras(globalCameraId, storeCameraIds) {
    const allowed = new Set();
    if (globalCameraId) {
        for (const id of SCOPE_TO_FLOW_CAMERAS[globalCameraId] ?? [
            "main"
        ]){
            allowed.add(id);
        }
    }
    if (storeCameraIds.length > 0 && !globalCameraId) {
        for (const scopeCameraId of storeCameraIds){
            for (const flowId of SCOPE_TO_FLOW_CAMERAS[scopeCameraId] ?? [
                "main"
            ]){
                allowed.add(flowId);
            }
        }
    }
    if (allowed.size === 0) return CUSTOMER_FLOW_CAMERAS;
    return CUSTOMER_FLOW_CAMERAS.filter((camera)=>allowed.has(camera.id));
}
function resolveCustomerFlowCameraId(globalCameraId, pageCameraId, allowedIds) {
    if (allowedIds.includes(pageCameraId)) return pageCameraId;
    if (globalCameraId) {
        const mapped = SCOPE_TO_FLOW_CAMERAS[globalCameraId]?.[0];
        if (mapped && allowedIds.includes(mapped)) return mapped;
    }
    return allowedIds[0] ?? pageCameraId;
}
function trajectoryIdsForFlowCamera(cameraId) {
    return FLOW_CAMERA_TRAJECTORIES[cameraId] ?? FLOW_CAMERA_TRAJECTORIES.main;
}
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/Desktop/retail-analytics/frontend/lib/scope/ScopeContext.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "ScopeProvider",
    ()=>ScopeProvider,
    "useScope",
    ()=>useScope
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$api$2f$stores$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/lib/api/stores.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$scope$2d$data$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/lib/scope-data.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$scope$2f$scope$2d$filters$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/lib/scope/scope-filters.ts [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature(), _s1 = __turbopack_context__.k.signature();
"use client";
;
;
;
;
const ScopeContext = /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["createContext"])(null);
function ScopeProvider({ children }) {
    _s();
    const [organization, setOrganization] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [isLoading, setIsLoading] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(true);
    const [storeId, setStoreIdState] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [cameraId, setCameraIdState] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [zoneId, setZoneIdState] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "ScopeProvider.useEffect": ()=>{
            let cancelled = false;
            async function load() {
                const org = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$api$2f$stores$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["getOrganization"])();
                if (cancelled) return;
                setOrganization(org);
                setStoreIdState(org.stores[0]?.id ?? null);
                setCameraIdState(null);
                setZoneIdState(null);
                setIsLoading(false);
            }
            load();
            return ({
                "ScopeProvider.useEffect": ()=>{
                    cancelled = true;
                }
            })["ScopeProvider.useEffect"];
        }
    }["ScopeProvider.useEffect"], []);
    const orgId = organization?.id ?? __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$scope$2d$data$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["DEPLOYMENT_ORG_ID"];
    const store = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useMemo"])({
        "ScopeProvider.useMemo[store]": ()=>organization?.stores.find({
                "ScopeProvider.useMemo[store]": (item)=>item.id === storeId
            }["ScopeProvider.useMemo[store]"]) ?? null
    }["ScopeProvider.useMemo[store]"], [
        organization,
        storeId
    ]);
    const camera = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useMemo"])({
        "ScopeProvider.useMemo[camera]": ()=>store?.cameras.find({
                "ScopeProvider.useMemo[camera]": (item)=>item.id === cameraId
            }["ScopeProvider.useMemo[camera]"]) ?? null
    }["ScopeProvider.useMemo[camera]"], [
        store,
        cameraId
    ]);
    const zone = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useMemo"])({
        "ScopeProvider.useMemo[zone]": ()=>camera?.zones.find({
                "ScopeProvider.useMemo[zone]": (item)=>item.id === zoneId
            }["ScopeProvider.useMemo[zone]"]) ?? null
    }["ScopeProvider.useMemo[zone]"], [
        camera,
        zoneId
    ]);
    const storeCameraIds = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useMemo"])({
        "ScopeProvider.useMemo[storeCameraIds]": ()=>(0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$scope$2f$scope$2d$filters$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["getStoreCameraIds"])(store)
    }["ScopeProvider.useMemo[storeCameraIds]"], [
        store
    ]);
    const setStoreId = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "ScopeProvider.useCallback[setStoreId]": (id)=>{
            setStoreIdState(id);
            setCameraIdState(null);
            setZoneIdState(null);
        }
    }["ScopeProvider.useCallback[setStoreId]"], []);
    const setCameraId = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "ScopeProvider.useCallback[setCameraId]": (id)=>{
            setCameraIdState(id);
            setZoneIdState(null);
        }
    }["ScopeProvider.useCallback[setCameraId]"], []);
    const setZoneId = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "ScopeProvider.useCallback[setZoneId]": (id)=>{
            setZoneIdState(id);
        }
    }["ScopeProvider.useCallback[setZoneId]"], []);
    const value = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useMemo"])({
        "ScopeProvider.useMemo[value]": ()=>({
                isLoading,
                orgId,
                organization,
                storeId,
                cameraId,
                zoneId,
                store,
                camera,
                zone,
                storeCameraIds,
                setStoreId,
                setCameraId,
                setZoneId
            })
    }["ScopeProvider.useMemo[value]"], [
        isLoading,
        orgId,
        organization,
        storeId,
        cameraId,
        zoneId,
        store,
        camera,
        zone,
        storeCameraIds,
        setStoreId,
        setCameraId,
        setZoneId
    ]);
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(ScopeContext.Provider, {
        value: value,
        children: children
    }, void 0, false, {
        fileName: "[project]/Desktop/retail-analytics/frontend/lib/scope/ScopeContext.tsx",
        lineNumber: 137,
        columnNumber: 5
    }, this);
}
_s(ScopeProvider, "ppSR8GxJTmmyQ4eS1wXpREuz3rg=");
_c = ScopeProvider;
function useScope() {
    _s1();
    const context = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useContext"])(ScopeContext);
    if (!context) {
        throw new Error("useScope must be used within a ScopeProvider");
    }
    return context;
}
_s1(useScope, "b9L3QQ+jgeyIrH0NfHrJ8nn7VMU=");
var _c;
__turbopack_context__.k.register(_c, "ScopeProvider");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/Desktop/retail-analytics/frontend/components/providers.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "Providers",
    ()=>Providers
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$auth$2f$auth$2d$guard$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/components/auth/auth-guard.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$auth$2f$AuthContext$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/lib/auth/AuthContext.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$scope$2f$ScopeContext$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/retail-analytics/frontend/lib/scope/ScopeContext.tsx [app-client] (ecmascript)");
"use client";
;
;
;
;
function Providers({ children }) {
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$auth$2f$AuthContext$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["AuthProvider"], {
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$components$2f$auth$2f$auth$2d$guard$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["AuthGuard"], {
            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$retail$2d$analytics$2f$frontend$2f$lib$2f$scope$2f$ScopeContext$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["ScopeProvider"], {
                children: children
            }, void 0, false, {
                fileName: "[project]/Desktop/retail-analytics/frontend/components/providers.tsx",
                lineNumber: 13,
                columnNumber: 9
            }, this)
        }, void 0, false, {
            fileName: "[project]/Desktop/retail-analytics/frontend/components/providers.tsx",
            lineNumber: 12,
            columnNumber: 7
        }, this)
    }, void 0, false, {
        fileName: "[project]/Desktop/retail-analytics/frontend/components/providers.tsx",
        lineNumber: 11,
        columnNumber: 5
    }, this);
}
_c = Providers;
var _c;
__turbopack_context__.k.register(_c, "Providers");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
]);

//# sourceMappingURL=Desktop_retail-analytics_frontend_0iouhlv._.js.map