# Core Engineering Reference: Performance & Web Vitals Checklist

> **Rule of Thumb**: Measure first. Never optimize without a baseline profile or reproduction trace.

---

## 🎯 1. Core Web Vitals (CWV) Thresholds

Every web-facing feature or release must satisfy the 75th percentile of real-user visits (p75):

| Metric | Target (Good) | Needs Work | Poor (Blocker) | Primary Root Causes |
| :--- | :--- | :--- | :--- | :--- |
| **LCP** (Largest Contentful Paint) | $\le 2.5\text{s}$ | $2.5\text{s} - 4.0\text{s}$ | $> 4.0\text{s}$ | Slow server TTFB, render-blocking resources, unoptimized hero images, client-side rendering bottlenecks |
| **INP** (Interaction to Next Paint) | $\le 200\text{ms}$ | $200\text{ms} - 500\text{ms}$ | $> 500\text{ms}$ | Heavy JS long tasks ($> 50\text{ms}$), un-debounced event handlers, synchronous DOM recalcs during interactions |
| **CLS** (Cumulative Layout Shift) | $\le 0.10$ | $0.10 - 0.25$ | $> 0.25$ | Images/videos without explicit aspect ratios, dynamic injected DOM above fold, late-loading web fonts (FOUT/FOIT) |

---

## ⚡ 2. Asset & Bundle Budgets

- [ ] **Initial JS Bundle**: $\le 170\text{ KB}$ gzipped / brotli for critical entry chunks.
- [ ] **Dynamic Code Splitting**: Route-level and interaction-level splitting using `React.lazy()`, dynamic `import()`, or framework-native sub-chunking.
- [ ] **Dependency Audit**: Inspect bundle using `source-map-explorer`, `webpack-bundle-analyzer`, or `rollup-plugin-visualizer`.
- [ ] **Tree-Shaking Verification**: Ensure `package.json` specifies `"sideEffects": false` where applicable, avoiding blanket namespace imports (`import * as _ from 'lodash'`).
- [ ] **Fonts**: Use `font-display: swap` or `optional`, self-host modern `.woff2` font files, and pre-connect/preload critical above-the-fold typefaces.
- [ ] **Images & Media**: Always declare explicit `width` and `height` or `aspect-ratio` on `<img>` tags. Use modern formats (AVIF / WebP) with responsive `srcset` and `loading="lazy"` for below-the-fold media.

---

## 🔄 3. Runtime & Execution Polish

- [ ] **Zero Main-Thread Blocking**: Keep individual task execution under $50\text{ms}$. Yield execution to the browser between chunks (`scheduler.yield()` or `requestIdleCallback()`).
- [ ] **Memory Leaks & Event Listeners**: All `addEventListener`, timers (`setInterval`), WebSocket listeners, and canvas render loops must have deterministic cleanup in teardown hooks (`useEffect` return or `disconnectedCallback`).
- [ ] **Layout Thrashing**: Never read geometry (`offsetHeight`, `getBoundingClientRect()`) immediately after mutating style or DOM in the same frame. Batch writes using `requestAnimationFrame`.
- [ ] **DOM Complexity Budget**: Keep total DOM tree depth $\le 32$ levels and total DOM nodes $\le 1,400$ per page.

---

## 🔬 4. Pre-Launch Performance Verification Protocol

1. **Profile Baseline**: Run a CPU-throttled ($4\times$ or $6\times$) trace in DevTools Performance panel before introducing optimization changes.
2. **Isolate the Limiter**: Confirm whether the bottleneck is Network I/O, JavaScript parse/eval, main-thread render, or GPU composite.
3. **Reproduce & Prove**: Measure delta in identical test conditions. Never ship an optimization that cannot demonstrate measured speedup in a local trace or synthetic run.
