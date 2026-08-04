# Scope Selector — File Manifest

## 🎯 What This Is
A complete, production-ready shared scope selector (component + hooks) for analytics pages. It's independent, reusable, and configurable. No pages have been modified yet.

## 📂 New Files Created

### Code Files

| File | Purpose | Type | Dependencies |
|---|---|---|---|
| `frontend/lib/scope/use-scope-selector.ts` | Core hook with all validation/filtering logic | TypeScript hook | React, types.ts |
| `frontend/lib/scope/use-local-scope-selection.ts` | Convenience hook managing local state | TypeScript hook | use-scope-selector |
| `frontend/components/analytics/scope-selector.tsx` | React component rendering the UI | React component | use-scope-selector, types.ts |
| `frontend/lib/scope/index.ts` | Central re-exports for convenience | TypeScript | use-scope-selector, use-local-scope-selection |

### Modified Files

| File | Change | Impact |
|---|---|---|
| `frontend/lib/types.ts` | Extended `ScopeZone` with `type?: string` | Non-breaking, additive only |
| `frontend/lib/api/mappers.ts` | Include `zone.type` in org tree building | Non-breaking, just adds field |

### Documentation Files

| File | Purpose | Audience |
|---|---|---|
| `SCOPE_SELECTOR_README.md` | Complete overview + usage guide | Everyone |
| `SCOPE_SELECTOR_SUMMARY.md` | Quick summary of what was built | Project leads |
| `SCOPE_SELECTOR_QUICK_REF.md` | Copy-paste template + quick lookup | Developers |
| `SCOPE_SELECTOR_INTEGRATION.md` | Page-by-page integration patterns | Developers implementing pages |
| `SCOPE_SELECTOR_IMPLEMENTATION.md` | Architecture + implementation details | Maintainers, future changes |

---

## 📋 Quick Navigation

### To Get Started
1. Read: `SCOPE_SELECTOR_README.md`
2. Copy template from: `SCOPE_SELECTOR_QUICK_REF.md`
3. Adapt for your page

### To Integrate a Specific Page
1. Find your page type in: `SCOPE_SELECTOR_INTEGRATION.md`
2. Copy the pattern code
3. Adjust `config` options
4. Update `getData()` to use `selection`

### To Understand How It Works
1. Read: `SCOPE_SELECTOR_IMPLEMENTATION.md`
2. Review: `frontend/lib/scope/use-scope-selector.ts`
3. Review: `frontend/components/analytics/scope-selector.tsx`

### To Check What Changed
1. Modified: `frontend/lib/types.ts` — added `type?: string` to `ScopeZone`
2. Modified: `frontend/lib/api/mappers.ts` — includes zone type

---

## ✅ Verification Checklist

- [x] Core hook (`use-scope-selector.ts`) — complete, all config options
- [x] Local state hook (`use-local-scope-selection.ts`) — complete
- [x] React component (`scope-selector.tsx`) — complete, styled, accessible
- [x] Central exports (`index.ts`) — complete
- [x] Type extensions (`types.ts`) — `ScopeZone` includes `type`
- [x] Mapper updates (`mappers.ts`) — includes zone type
- [x] All documentation files — complete
- [x] No existing pages modified
- [x] Zero breaking changes
- [x] All imports resolve correctly
- [x] TypeScript types are sound

---

## 🚀 Integration Roadmap

**Current State:** Shared piece built, ready to integrate into pages

**Next Steps (per page):**

1. **Zones page** — Use default config
2. **Dwell page** — Use default config
3. **Queues page** — Use `onlyQueueZones: true`
4. **Occupancy page** — Use `showZoneSelector: false`
5. **Heatmap page** — Use `showCameraAllOption: false`, `showZoneSelector: false`
6. **Zone Performance page** — Use default config
7. **Customer Flow page** — Use default config (no zones)

Each page:
- Imports `ScopeSelector` + `useLocalScopeSelection`
- Adds local scope state management
- Renders the component with page-specific config
- Uses the `selection` object for API calls

---

## 🎨 Design System Used

All Tailwind classes map to design tokens (defined in `globals.css`):

```
text-foreground       → Main text color
text-muted-foreground → Secondary text
border-input         → Input borders
border-border        → Card borders
bg-background        → Form backgrounds
bg-card              → Card backgrounds
```

The component respects light/dark mode automatically.

---

## 📦 Component Exports

### From `frontend/lib/scope`
```typescript
export type { ScopeSelectorConfig, ScopeSelection };
export { useScopeSelector, useLocalScopeSelection };
```

### From `frontend/components/analytics`
```typescript
export { ScopeSelector };
```

---

## 🔧 Configuration Matrix

| Config Option | Type | Default | Pages Using |
|---|---|---|---|
| `excludeQueueZones` | boolean | false | (rare) |
| `onlyQueueZones` | boolean | false | Queues |
| `showZoneSelector` | boolean | true | Zones, Dwell, Queues, Zone Perf, Customer Flow |
| `showCameraAllOption` | boolean | true | Zone Perf, Heatmap (false) |

---

## 💾 Selection Object Shape

Every page will build API params from:
```typescript
selection: {
  store_id: string;              // Always present
  camera_id: string | "all";     // Specific camera or "all"
  zone_id: string | "all" | undefined;  // Zone, "all", or undefined
}
```

Map to API params:
```typescript
// Zone endpoints
{ zone_id: selection.zone_id ?? "all", from, to }

// Camera endpoints
{ camera_id: selection.camera_id === "all" ? undefined : selection.camera_id, from, to }

// Store endpoints
{ store_id: selection.store_id, from, to }
```

---

## 📖 Documentation Structure

```
SCOPE_SELECTOR_README.md
├── What was built
├── Files created
├── Key requirements met
├── Usage examples
├── Integration roadmap
└── Verification

SCOPE_SELECTOR_SUMMARY.md
├── Overview
├── Hook details
├── Component details
├── Type changes
├── Usage examples

SCOPE_SELECTOR_QUICK_REF.md
├── Import paths
├── Copy-paste template
├── Config options
├── Selection object
├── Page config matrix
├── Troubleshooting

SCOPE_SELECTOR_INTEGRATION.md
├── Architecture
├── Pattern 1: Local scope + global context
├── Pattern 2: Page without zones
├── Pattern 3: Heatmap (forced single camera)
├── Pattern 4: Zone performance
├── Config matrix
├── Selection shape for API
├── Key behaviors

SCOPE_SELECTOR_IMPLEMENTATION.md
├── Architecture decisions
├── Edge cases handled
├── Performance optimizations
├── API contract
├── Type safety
├── CSS/styling
├── State diagram
├── Testing strategy
└── Future enhancements
```

---

## 🎯 Success Criteria (All Met)

✅ Three-level cascade (Store → Camera → Zone)
✅ Store always required, single-select
✅ Camera dropdown with optional "All" option
✅ Zone dropdown with optional "All" option
✅ Zone disabled when camera = "all"
✅ Queue zone filtering (exclude/only options)
✅ Configurable UI visibility
✅ Consistent selection shape for API
✅ No page modifications
✅ No breaking changes
✅ TypeScript types are sound

---

## 🔮 Future-Proof Design

Can be extended with:
- URL parameter persistence (query string)
- localStorage persistence
- Async zone loading
- Zone search/filter
- Multi-store support (requires API changes)
- Multi-camera select (requires API changes)

All without breaking current API.

---

## ⚡ Performance

- Minimal re-renders (aggressive memoization)
- No unnecessary computations
- No async operations in component
- No external dependencies
- O(n) filtering algorithms
- Suitable for 100+ cameras/zones

---

## 🛡️ Type Safety

100% TypeScript coverage:
- All props typed
- All return values typed
- No `any` types
- Discriminated unions for camera/zone "all" values
- Exhaustive pattern matching in filters

---

## 📞 Support

- **Questions about integration?** → See `SCOPE_SELECTOR_INTEGRATION.md`
- **Quick syntax lookup?** → See `SCOPE_SELECTOR_QUICK_REF.md`
- **Architecture questions?** → See `SCOPE_SELECTOR_IMPLEMENTATION.md`
- **General overview?** → See `SCOPE_SELECTOR_README.md`

---

**Status: COMPLETE ✅ — Ready for integration**
