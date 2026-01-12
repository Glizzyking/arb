# Specification: Fix Asset Switching Race Condition

## Overview
When switching between cryptocurrency tabs (BTC → ETH), the backend receives simultaneous requests for both assets. The polling interval continues fetching the old asset due to a stale closure in React's useEffect.

## Bug Details
- **Location:** `frontend/app/page.tsx` lines 96-133
- **Root Cause:** The `fetchData` function captures `activeAsset` in closure scope, but when the interval fires, it may use a stale value
- **Symptom:** Backend logs show alternating BTC/ETH requests instead of only the selected asset

## Functional Requirements
1. **FR-1:** When asset tab changes, immediately stop all polling for the previous asset
2. **FR-2:** Cancel any in-flight API requests from the previous asset using AbortController
3. **FR-3:** Clear dashboard data (set to null/loading) before fetching new asset data
4. **FR-4:** Display loading indicator while fetching new asset data
5. **FR-5:** Only one asset's data should be fetched at any given time

## Acceptance Criteria
- [ ] Switching from BTC to ETH: Only ETH requests appear in backend logs
- [ ] No race conditions or data flickering between assets
- [ ] Loading state displays during asset transitions
- [ ] Old asset data clears immediately on tab switch

## Out of Scope
- Changes to backend API endpoints
- Adding new assets or modifying asset configuration
