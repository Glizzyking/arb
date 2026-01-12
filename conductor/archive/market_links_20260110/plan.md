# Implementation Plan: Add Clickable Market Links

## Phase 1: Planning
- [x] Define requirements in spec.md
- [x] Create implementation plan in plan.md
- [x] User reviews and approves plan

## Phase 2: Implementation

### Task 1: Import External Link Icon
- [x] Add `ExternalLink` import from `lucide-react` to `app/page.tsx`

### Task 2: Update TypeScript Interfaces
- [x] Add `url` field to `polymarket` interface in `MarketData` type
- [x] Add `url` field to `kalshi` interface in `MarketData` type
- [x] Verify backend already provides these URLs (confirmed in backend code review)

### Task 3: Add Link Component to Polymarket Section
- [x] Locate Polymarket `CardDescription` in `app/page.tsx` (line ~296)
- [x] Wrap the slug text and icon in a clickable anchor tag
- [x] Add `ExternalLink` icon next to the slug text
- [x] Configure link to open in new tab (`target="_blank"` and `rel="noopener noreferrer"`)
- [x] Use `data.polymarket.url` for the href
- [x] Style icon to be small and aligned with text

### Task 4: Add Link Component to Kalshi Section
- [x] Locate Kalshi `CardDescription` in `app/page.tsx` (line ~332)
- [x] Wrap the ticker text and icon in a clickable anchor tag
- [x] Add `ExternalLink` icon next to the ticker text
- [x] Configure link to open in new tab (`target="_blank"` and `rel="noopener noreferrer"`)
- [x] Use `data.kalshi.url` for the href
- [x] Style icon to match Polymarket section

### Task 5: Verify Build
- [x] Run `npm run build` to check for TypeScript errors
- [x] Verify dev server still runs without errors

### Task 6: Self-Test Functionality
- [x] Test Polymarket link opens correct URL in new tab
- [x] Test Kalshi link opens correct URL in new tab
- [x] Verify icons are properly sized and positioned
- [x] Verify dashboard functionality is not affected

- [x] Task: Conductor - User Manual Verification 'Phase 2: Implementation' (Protocol in workflow.md)

## Phase 3: Verification

### Task 1: Visual Verification via Browser
- [x] Navigate to dashboard at `http://localhost:3000`
- [x] Verify external link icons appear next to slug/ticker
- [x] Click Polymarket icon and verify correct market opens
- [x] Click Kalshi icon and verify correct market opens
- [x] Test with multiple assets (BTC, ETH, etc.)

### Task 2: Update Walkthrough
- [ ] Document changes made
- [ ] Add screenshots showing link icons
- [ ] Include verification results

- [ ] Task: Conductor - User Manual Verification 'Phase 3: Verification' (Protocol in workflow.md)
