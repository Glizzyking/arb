# Implementation Plan: Main Navigation and Settings Panel

## Phase 1: Planning
- [x] Gather requirements for new pages
- [x] Define Settings functionality
- [x] Draft spec.md
- [x] Draft plan.md
- [x] Task: Conductor - User Manual Verification 'Phase 1 Planning' (Protocol in workflow.md)

## Phase 2: Implementation

### 2.1 Header Component
- [x] Create `Header.tsx` component with navigation tabs
- [x] Add "Settings" button with gear icon
- [x] Style header with Tailwind CSS (dark theme, premium look)

### 2.2 Page Routing
- [x] Update `page.tsx` to use state-based tab switching
- [x] Create `PositiveEVPage.tsx` placeholder component
- [x] Create `CalculatorsPage.tsx` placeholder component

### 2.3 Settings Modal
- [x] Create `SettingsModal.tsx` component
- [x] Add API Key input fields (Polymarket, Kalshi)
- [x] Wire Settings button to open modal

### 2.4 Integration
- [x] Integrate Header into main layout
- [x] Test tab switching preserves dashboard state
- [x] Task: Conductor - User Manual Verification 'Phase 2 Implementation' (Protocol in workflow.md)

## Phase 3: Verification
- [x] Verify tab switching works correctly
- [x] Verify Settings modal opens and closes
- [x] Visual UI review for aesthetics
- [x] Task: Conductor - User Manual Verification 'Phase 3 Verification' (Protocol in workflow.md)
