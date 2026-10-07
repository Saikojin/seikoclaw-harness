# Core Engineering Reference: Accessibility (a11y) Checklist

> **Standard**: WCAG 2.1 Level AA Compliance across all user-facing interfaces.

---

## ⌨️ 1. Keyboard Navigability & Focus Management

- [ ] **Tab Order**: DOM order matches visual tab flow. No positive `tabindex` attributes (only `tabindex="0"` for interactive focusables, `tabindex="-1"` for programmatically focused elements).
- [ ] **Visible Focus Indicators**: Focus rings are prominent, with $\ge 3:1$ contrast against adjacent background colors. Never use `outline: none` without providing an accessible high-contrast replacement.
- [ ] **Modals & Dialogs Focus Trap**:
  - Focus moves into the dialog immediately upon opening.
  - Tab keys are trapped within the modal while open.
  - Pressing `Escape` closes the modal.
  - Focus returns cleanly to the triggering element upon closure.
- [ ] **Skip Links**: Include a "Skip to content" link as the first focusable element on complex pages.

---

## 🎨 2. Color Contrast & Visual Design

- [ ] **Body & Content Text Contrast**: Minimum $4.5:1$ contrast ratio against background for normal text ($< 18\text{pt}$ / $< 14\text{pt}$ bold).
- [ ] **Large Text Contrast**: Minimum $3:1$ contrast ratio for large text ($\ge 18\text{pt}$ or $\ge 14\text{pt}$ bold).
- [ ] **UI Components & Graphical Objects**: Minimum $3:1$ contrast ratio for icons, input borders, button outlines, and active state indicators.
- [ ] **Color Independence**: Color is never the sole visual indicator of state, error, or action (pair red error borders with icon and explanatory text).
- [ ] **Reduced Motion**: All animations, parallax transforms, and auto-playing media respect `prefers-reduced-motion: reduce`. Provide instantaneous or gentle cross-fade fallbacks.

---

## 📢 3. Semantic HTML & Screen Reader Support

- [ ] **Native HTML First**: Always use native semantic elements (`<button>`, `<a>`, `<dialog>`, `<nav>`, `<main>`, `<header>`, `<footer>`) instead of `<div>` with `onClick`.
- [ ] **Accessible Names**: All buttons, links, and form inputs have an unambiguous accessible name via text content, `aria-label`, or `aria-labelledby`.
- [ ] **Forms & Validation**:
  - Every `<input>` has an associated `<label>` using matching `htmlFor` / `id`.
  - Errors are linked via `aria-describedby` and flagged with `aria-invalid="true"`.
- [ ] **Images & Icons**:
  - Meaningful images have descriptive `alt="..."`.
  - Decorative icons and images carry `alt=""` or `aria-hidden="true"`.
- [ ] **Dynamic Updates**: Asynchronous toast notifications, live status bars, or search count updates announce changes via `aria-live="polite"`.

---

## 🧪 4. Automated & Manual Audit Procedure

1. **Automated Scan**: Run `axe-core`, Lighthouse Accessibility audit, or `eslint-plugin-jsx-a11y` during CI/build.
2. **Keyboard Solo Test**: Navigate the entire flow unplugging the mouse—ensure every interactive control is reachable, operable via `Enter` / `Space`, and dismissible via `Escape`.
3. **Screen Reader Verification**: Test critical paths with NVDA, VoiceOver, or JAWS to verify clear semantic announcements without repetitive verbosity.
