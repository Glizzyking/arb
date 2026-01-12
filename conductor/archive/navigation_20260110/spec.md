# Specification: Main Navigation and Settings Panel

## Overview
Add a top-level navigation system to the dashboard to support future utility pages ("Positive EV", "Calculators") and provide a central location for application settings.

## Functional Requirements

### 1. Clean Header Layout
A persistent top header bar containing navigation elements.

### 2. Navigation Tabs
| Tab | Content |
|-----|---------|
| Home Page | Displays the existing real-time arbitrage dashboard |
| Positive EV | Displays a "Coming Soon" placeholder |
| Calculators | Displays a "Coming Soon" placeholder |

### 3. Settings Button
- Located in the upper right corner of the header
- Opens a modal for application configuration
- Initial focus: API Key Management (Polymarket, Kalshi)

## Technical Implementation
- **Component Architecture**: Create a new `Header` component in `frontend/components/`
- **Navigation State**: Use React state to manage the active tab (SPA style)
- **Responsiveness**: Ensure the header maintains a premium look on different screen sizes

## Acceptance Criteria
- [ ] Header is visible at the top of the page
- [ ] Users can switch between "Home Page", "Positive EV", and "Calculators"
- [ ] Switching to new tabs shows "Coming Soon" placeholder
- [ ] Switching back to "Home Page" restores the arbitrage dashboard
- [ ] Clicking "Settings" opens a modal for API Key management
