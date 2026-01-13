# Implementation Plan: Tracker Feature

This plan outlines the steps to implement a calendar-based arbitrage tracker with Supabase authentication and storage.

## Phase 1: Authentication & Supabase Setup
Initialize Supabase and implement the login gate.

- [x] Task: Set up Supabase project and obtain `SUPABASE_URL` and `SUPABASE_ANON_KEY`
- [x] Task: Update `.env` and `.env.local` with Supabase credentials
- [x] Task: Install `@supabase/supabase-js` in the frontend
- [x] Task: Create `frontend/lib/supabase.ts` client initialization
- [x] Task: Create `frontend/components/LoginPage.tsx` with premium dark mode design
- [x] Task: Implement authentication logic (middleware or layout-level gate)
- [x] Task: Conductor - User Manual Verification 'Phase 1: Authentication & Supabase Setup' (Protocol in workflow.md)

## Phase 2: Database Schema Implementation
Define the data structure for tracking positions.

- [x] Task: Create `positions` table in Supabase
- [x] Task: Create `position_legs` table (linked to `positions`)
- [x] Task: Set up Row Level Security (RLS) policies in Supabase
- [x] Task: Conductor - User Manual Verification 'Phase 2: Database Schema Implementation' (Protocol in workflow.md)

## Phase 3: Tracker UI: Layout and Navigation
Add the Tracker tab and main page structure.

- [x] Task: Update `Header.tsx` to include Tracker tab and icon
- [x] Task: Create `frontend/components/TrackerPage.tsx` skeleton
- [x] Task: Update `App` component to handle tab state and render `TrackerPage`
- [x] Task: Conductor - User Manual Verification 'Phase 3: Tracker UI: Layout and Navigation' (Protocol in workflow.md)

## Phase 4: Tracker UI: Calendar View
Implement the monthly calendar interface.

- [x] Task: Implement month navigation logic (prev/next)
- [x] Task: Build the calendar grid with day indicators (showing tracked positions)
- [x] Task: Integrate Supabase data fetching to display indicators on the calendar
- [x] Task: Implement day selection and side panel display for daily details
- [x] Task: Conductor - User Manual Verification 'Phase 4: Tracker UI: Calendar View' (Protocol in workflow.md)

## Phase 5: Tracker UI: Position Management
Implement the functionality to add, edit, and resolve positions.

- [x] Task: Build `AddPositionModal.tsx` for inputting network, price, and contracts
- [x] Task: Implement Supabase insertion logic for new positions and legs
- [x] Task: Implement outcome resolution flow (Polymarket Won / Kalshi Won / Both Lost)
- [x] Task: Implement profit/loss calculation based on outcomes ($1 payout assumption)
- [x] Task: Conductor - User Manual Verification 'Phase 5: Tracker UI: Position Management' (Protocol in workflow.md)

## Phase 6: Final Polish & Verification
Fine-tune the UI and ensure everything is working as expected.

- [x] Task: Verify authentication flow end-to-end
- [x] Task: Test adding and resolving positions across multiple days
- [x] Task: Final UI polish (animations, responsive adjustments)
- [x] Task: Conductor - Final Track Verification (Protocol in workflow.md)
