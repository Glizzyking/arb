# Specification: Add Clickable Market Links

## Overview
Add external link icons next to the Polymarket slug and Kalshi ticker in the main market summary sections. When clicked, these icons will open the respective market pages in a new browser tab, allowing users to quickly view the actual markets without leaving the dashboard.

## Functional Requirements

### FR1: Polymarket Link Icon
- Display an `ExternalLink` icon (from lucide-react) next to the Polymarket slug text
- The icon should be clickable and styled to indicate it's interactive
- When clicked, open the Polymarket market URL in a new browser tab (`target="_blank"`)
- The URL is already provided by the backend in the response data (`polymarket.url`)

### FR2: Kalshi Link Icon
- Display an `ExternalLink` icon (from lucide-react) next to the Kalshi ticker text
- The icon should be clickable and styled to indicate it's interactive
- When clicked, open the Kalshi market URL in a new browser tab (`target="_blank"`)
- The URL is already provided by the backend in the response data (`kalshi.url`)

### FR3: Placement
- Add the link icons only in the main market summary sections
- Do not add links to the arbitrage opportunities/checks table

### FR4: Visual Design
- Icons should be small and unobtrusive (appropriate size relative to the text)
- No tooltips on hover
- Maintain consistency with the existing dashboard design aesthetic

## Non-Functional Requirements

### NFR1: Accessibility
- Links should include proper ARIA attributes or semantic HTML (e.g., `rel="noopener noreferrer"` for security)

### NFR2: Performance
- Adding links should not impact dashboard rendering performance or data fetching

## Acceptance Criteria

- [ ] External link icons appear next to both Polymarket slug and Kalshi ticker
- [ ] Clicking the Polymarket icon opens the correct market URL in a new tab
- [ ] Clicking the Kalshi icon opens the correct market URL in a new tab
- [ ] Icons are visually consistent with the dashboard design
- [ ] No tooltips are displayed on hover
- [ ] Links open in new tabs without affecting the dashboard

## Out of Scope
- Adding tooltips or hover effects
- Adding links to the arbitrage opportunities table
- Creating custom SVG icons (using existing lucide-react icons)
