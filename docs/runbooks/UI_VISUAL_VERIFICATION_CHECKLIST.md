# UI Visual Verification Checklist

## Purpose

This checklist ensures all UI changes are visually verified before completion. **Do not claim fixes are complete without following this checklist.**

## Mandatory Verification Steps

### 1. Browser Screenshot
```bash
# Use browser tool to take full-page screenshot
browser_take_screenshot fullPage=true
```
**Verify:**
- No unexpected large elements (check for 1679px+ widths)
- No "giant Q" shapes or malformed spinners
- Layout is correct
- Colors and styling match expectations

### 2. Element Size Verification
```javascript
// Use browser_evaluate to check critical element sizes
browser_evaluate(() => {
  const svg = document.querySelector('svg[viewBox="0 0 24 24"]');
  return {
    width: svg.getBoundingClientRect().width,
    height: svg.getBoundingClientRect().height
  };
})
```
**Critical Checks:**
- SVG icons must be 20px × 20px (or intended size), NOT 1679px+
- Loading spinners must be reasonable size
- Input fields must be properly sized

### 3. Console Error Check
```bash
browser_console_messages
```
**Verify:**
- No JavaScript errors
- No failed API calls (unless expected)
- No missing resource errors (unless optional)

### 4. Interactive Testing
- Test search inputs (type and submit)
- Test toggle switches (verify state changes)
- Test buttons (verify they work)
- Test navigation (verify tabs switch correctly)

## Common Visual Bugs

### SVG Icon Scaling Bug
**Symptom:** Icons appear as huge arcs or "giant Q" shapes
**Cause:** Missing explicit size constraints on SVG elements
**Fix:** Add `style={{ width: '20px', height: '20px', flexShrink: 0 }}` to all SVG icons
**Prevention:** Always include explicit pixel constraints, not just Tailwind classes

### Live Search Default Bug
**Symptom:** Search inputs disabled on page load
**Cause:** `liveMode` defaults to `false` instead of `true`
**Fix:** Change `useState(false)` to `useState(true)` for live mode
**Prevention:** Always default to live mode; static mode is fallback only

### API Endpoint Mismatch
**Symptom:** API calls fail with 400/404 errors
**Cause:** Frontend using wrong HTTP method or parameter names
**Fix:** Check backend router files for exact signatures
**Prevention:** Always verify endpoint contracts before implementing frontend calls

## Verification Workflow

1. **Before claiming fix complete:**
   - Take screenshot
   - Check element sizes
   - Check console for errors
   - Test interactions

2. **If visual issues found:**
   - Fix the issue
   - Re-verify with browser tools
   - Do NOT claim complete until visual verification passes

3. **Documentation:**
   - Update AGENTS.md with patterns
   - Update cursor rules if needed
   - Add to this checklist if new pattern discovered

## Related Rules

- Rule 051: Browser Verification Requirement (MANDATORY)
- Rule 056: UI Generation Standard (SVG sizing, Live Search defaults)
- Rule 067: Atlas Webproof (Browser-Verified UI)

## Quick Reference

```tsx
// ✅ CORRECT: SVG with explicit size constraints
<svg className="h-5 w-5" style={{ width: '20px', height: '20px', flexShrink: 0 }}>
  <path ... />
</svg>

// ❌ WRONG: SVG with only Tailwind classes (can scale to viewport)
<svg className="h-5 w-5">
  <path ... />
</svg>

// ✅ CORRECT: Live mode default
const [liveMode, setLiveMode] = useState(true);

// ❌ WRONG: Static mode default
const [liveMode, setLiveMode] = useState(false);
```

