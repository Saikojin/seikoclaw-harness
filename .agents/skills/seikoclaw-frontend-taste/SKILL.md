---
name: seikoclaw-frontend-taste
description: Enforces design systems, high-craft UI polish, Emil Kowalski motion physics, optical alignment, and mobile-native ergonomics.
author: Saikojin (SeikoClaw)
aliases:
  - frontend-taste
  - ui-craft
  - motion-standards
  - design-engineering
---

# Seikoclaw Frontend Taste System

A rigorous design engineering skill to eliminate generic "AI slop" and enforce high-craft user interfaces, fluid physics-based motion, optical typography, and mobile-native ergonomics.

---

## 1. Surface & Component Craft

### Translucent Alpha Borders
* **Rule**: Never use stark, 1px solid opaque borders (e.g. `#000` or `#e5e7eb` on complex backgrounds).
* **Implementation**: Use subtle alpha-channel borders that blend with underlying surfaces:
  * Dark mode: `border: 1px solid rgba(255, 255, 255, 0.08)` to `rgba(255, 255, 255, 0.12)`.
  * Light mode: `border: 1px solid rgba(0, 0, 0, 0.06)` to `rgba(0, 0, 0, 0.08)`.

### Layered Shadows & Inset Highlights
* **Rule**: Avoid muddy single-value drop shadows (`box-shadow: 0 4px 10px #888`).
* **Implementation**: Combine an ambient soft blur, a tight contact shadow, and an inset top highlight for depth:
  ```css
  /* Elevated Card / Popover */
  box-shadow: 
    0 1px 2px rgba(0, 0, 0, 0.05),
    0 4px 16px rgba(0, 0, 0, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  ```

### Tiered Dark Mode Elevation
* **Rule**: Avoid pure flat `#000000` backgrounds across all components.
* **Implementation**: Create depth using tiered background lightness:
  * Canvas / Page: `hsl(0 0% 6%)` or `#09090b`
  * Card / Panel: `hsl(0 0% 9%)` or `#121215`
  * Modal / Popover / Tooltip: `hsl(0 0% 14%)` or `#1e1e24`

---

## 2. Typography & Optical Discipline

### Tracking (Letter Spacing) Rules
* **Large Headings (`text-2xl` and above)**: Tighten tracking to remove loose letter gaps (`letter-spacing: -0.02em` to `-0.035em` or `tracking-tight`).
* **Body Text (`text-sm` to `text-base`)**: Neutral / normal tracking (`letter-spacing: 0`).
* **Uppercase Metadata / Badges (`text-xs uppercase`)**: Expand tracking for legibility (`letter-spacing: 0.05em` to `0.08em` or `tracking-wider`).

### Tabular Numbers (`tabular-nums`)
* **Rule**: Any dynamic number, price, timer, counter, percentage, or data table column **must** use tabular figures.
* **Implementation**: `font-variant-numeric: tabular-nums` (or `tabular-nums` in Tailwind) to eliminate horizontal jitter during live updates.

### Optical Alignment over Geometric Alignment
* **Play / Directional Icons**: A geometric center on asymmetric shapes (e.g. triangle play icon) looks shifted to the left. Apply optical compensation (e.g. `transform: translateX(1px)`).
* **Icon-Text Pairs**: Vertically center icons with text cap-height rather than font bounding boxes.

---

## 3. Motion & Animation Physics (Kowalski Standards)

### Frequency Decision Matrix
Match the animation presence and duration to how often the user encounters it:

| Frequency | Target Duration | Easing / Physics | Examples |
| :--- | :--- | :--- | :--- |
| **High Frequency (100+ times/day)** | **0ms (Instant)** or $<80\text{ms}$ | Linear / instant snap | Command palette toggle, keyboard shortcuts, select dropdown items |
| **Medium Frequency (Tens of times/day)** | **100ms – 150ms** | Quick ease-out | Hover states, tab switches, list row highlights, button active press |
| **Occasional (Few times/day)** | **200ms – 300ms** | Custom spring / Deceleration | Modals, drawer sheets, toast notifications, expandable accordions |

### Easing & Trajectory Rules
* **Enter Transitions**: Fast entrance with smooth deceleration $\rightarrow$ `ease-out` (e.g. `cubic-bezier(0.16, 1, 0.3, 1)`). **Never use `ease-in` on enter.**
* **Exit Transitions**: Accelerate out of the viewport quickly $\rightarrow$ `ease-in` or fast linear fade ($\le 150\text{ms}$).
* **Move / Morph Transitions**: Symmetrical acceleration/deceleration $\rightarrow$ `cubic-bezier(0.4, 0, 0.2, 1)` or physical spring (stiffness: 300, damping: 30).

### GPU Acceleration & Zero-Reflow Performance
* **Allowed Animatable Properties**: Animate **only** `transform` (`translate`, `scale`, `rotate`) and `opacity`.
* **Forbidden Animatable Properties**: **Never** animate layout properties (`width`, `height`, `top`, `left`, `margin`, `padding`). Use CSS `transform: scale()` or FLIP techniques instead.
* **No `transition: all`**: Always specify explicit properties (e.g. `transition: transform 200ms ease-out, opacity 150ms ease-out`).
* **Avoid `scale(0)` Entrances**: Never scale in from zero. Start from `scale(0.95)` with `opacity: 0`—nothing in the physical world expands from a singularity.
* **Origin-Aware Popovers**: Popovers, tooltips, and dropdowns scale from their trigger (`transform-origin: var(--transform-origin)` or trigger coordinate), not center. (Modals remain centered).
* **Framer Motion Hardware Acceleration**: `<motion.div animate={{ x: 100 }} />` is not hardware-accelerated and drops frames during heavy page loads. Use `<motion.div animate={{ transform: "translateX(100px)" }} />` or off-main-thread CSS animations.
* **Use WAAPI for Programmatic Motion**: Web Animations API (`element.animate(...)`) provides JavaScript control with hardware-accelerated, off-main-thread CSS performance.
* **Blur Cap**: Keep animated `filter: blur(...)` values below `20px` to avoid dropped frames on mobile GPUs.
* **Stagger Transitions**: When cascading multiple items, use short delays (30–80ms per item). Long stagger delays feel sluggish; never block interaction during staggers.
* **Accessibility**: Respect `@media (prefers-reduced-motion: reduce)`. Keep gentle opacity/color fades for comprehension; eliminate transform/spatial displacement.

---

## 4. The Sonner Principles (Loved Component Craft)

Principles distilled from world-class UI primitives:
1. **Frictionless Developer Experience**: Avoid complex hook plumbing and context requirements where a clean top-level component (`<Toaster />`) and global imperative call (`toast(...)`) suffice.
2. **Superior Defaults Over Infinite Configuration**: Ship high-craft easing, typography, and contrast out of the box. Most users will not customize.
3. **Handle Edge Cases Invisibly**:
   - Pause timers when the document/tab is hidden (`visibilitychange`).
   - Fill gaps between stacked interactive items with pseudo-elements to maintain hover states without flickering.
   - Capture pointer events during dragging gestures to avoid accidental background clicks.
4. **Transitions Over Keyframes for Rapid Interactivity**: Keyframes restart from zero when interrupted; CSS transitions retarget smoothly mid-flight.

---

## 5. Mobile-Web Native Ergonomics

| Area | Issue | Taste Solution |
| :--- | :--- | :--- |
| **Viewport** | Dynamic browser address bars cause layout jumps with `100vh`. | Use `height: 100dvh` (or `100svh`). |
| **Tap Feedback** | Mobile browsers show gray/blue flash on click. | Add `-webkit-tap-highlight-color: transparent;` to root/buttons. |
| **Hover Sticky Bug** | Mobile taps leave permanent `:hover` styles on touch screens. | Wrap hover styles in `@media (hover: hover) and (pointer: fine)`. |
| **Form Zoom** | iOS Safari auto-zooms when tapping inputs with font $<16\text{px}$. | Ensure text input `font-size` is at least `16px` (`1rem`). |
| **Notch & Safe Areas** | Fixed headers/footers clip under iPhone dynamic island or home bar. | Use `padding-top: env(safe-area-inset-top)` and `padding-bottom: env(safe-area-inset-bottom)`. |
| **Scroll Bounces** | Dragging a modal or sheet triggers the entire body pull-to-refresh. | Set `overscroll-behavior-y: contain;` on inner scroll containers. |
| **Accidental Selection**| Long-pressing buttons selects the button label text. | Set `user-select: none;` on buttons, chips, tabs, and interactive pills. |

---

## 6. Execution & Audit Workflow

When auditing or styling a frontend UI component:
1. **Discover Tokens**: Check existing design tokens (Tailwind classes, CSS variables in `index.css`/`globals.css`).
2. **Surface & Depth Check**:
   - Replace opaque borders with subtle alpha borders.
   - Replace flat drop shadows with multi-stop layered shadows.
   - Verify dark-mode elevation contrast.
3. **Typography & Numbers Check**:
   - Add `tabular-nums` to numbers, dates, timers, and prices.
   - Apply `tracking-tight` to large headers and `tracking-wider` to uppercase chips.
4. **Motion & Interaction Check**:
   - Eliminate slow animations on high-frequency controls (command palettes, dropdowns).
   - Ensure enter transitions use `ease-out` and exits use `ease-in`.
   - Restrict transitions strictly to `transform` and `opacity`.
5. **Mobile Readiness Check**:
   - Replace `100vh` with `100dvh`.
   - Verify safe area insets and touch target padding ($\ge 44 \times 44\text{px}$).
6. **Performance & Accessibility Inspection Gates**:
   - **Core Web Vitals Audit**: Audit LCP ($\le 2.5\text{s}$), INP ($\le 200\text{ms}$), and CLS ($\le 0.10$) per [references/performance-checklist.md](../../../references/performance-checklist.md).
   - **WCAG 2.1 AA Audit**: Verify focus rings ($\ge 3:1$ contrast), keyboard tab flows, modal focus traps, and accessible labels per [references/accessibility-checklist.md](../../../references/accessibility-checklist.md).
7. **Required Audit Output Format**:
   - When reviewing frontend code, you **must** output findings in a concise Before/After/Why table:
     | Before | After | Why |
     | :--- | :--- | :--- |
     | `transition: all 300ms` | `transition: transform 200ms ease-out` | Avoid `all`; specify exact GPU properties. |
     | `transform: scale(0)` | `transform: scale(0.95); opacity: 0` | Avoid unnatural scale from 0 singularity. |
     | `ease-in` on dropdown | `ease-out` with custom curve | Entrance must feel responsive immediately. |
8. **Handoff for QA & Specialized Skills**:
   - Stress-test with realistic worst-case boundary data using [break-ui](../break-ui/SKILL.md).
   - For strict 10-point animation gatekeeping, run [review-animations](../review-animations/SKILL.md).
   - For mobile touch and gesture depth, consult [mobile-native](../mobile-native/SKILL.md) and [apple-design](../apple-design/SKILL.md).
   - Pass completed components to `seikoclaw-browser-qa-workflow` or `seikojin-qa` for visual verification.

