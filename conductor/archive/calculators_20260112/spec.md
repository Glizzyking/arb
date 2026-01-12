# Specification: Prediction Market Calculator Tools

## Overview
Add five comprehensive prediction market calculator tools to the Calculators page, replacing the current "Coming Soon" placeholder. These calculators will help users make informed betting decisions across Polymarket, Kalshi, and other prediction markets by providing odds conversion, arbitrage detection, expected value calculations, optimal bet sizing, and multi-market comparison.

## Functional Requirements

### FR1: Page Layout
- Replace the "Coming Soon" content on the Calculators tab with a scrollable page containing all five calculators
- Use an accordion layout where each calculator is a collapsible section
- All calculators should be visible on page load in their collapsed state
- Users can expand/collapse any calculator independently
- Maintain the existing dark theme design consistent with the rest of the application

### FR2: Odds Converter & Probability Calculator
**Purpose:** Convert between different odds formats and display implied probability

**Inputs:**
- Odds format selector (dropdown): Cents, Percentage, American Odds (e.g., -200/+150), Decimal Odds
- Odds value (numeric input)

**Outputs:**
- Display converted values in all other formats
- Show implied probability as a percentage
- Show complementary probability (for the opposite outcome)

**Features:**
- Real-time conversion as user types
- Tooltip explaining implied probability
- Clear labeling of each format

### FR3: Arbitrage Calculator
**Purpose:** Calculate if buying all outcomes across platforms yields guaranteed profit

**Inputs:**
- Platform 1 selector (dropdown): Polymarket US, Polymarket International, Kalshi
- Platform 1 price for "Yes" (numeric, 0-100 cents or 0-100%)
- Platform 2 selector (dropdown): Polymarket US, Polymarket International, Kalshi  
- Platform 2 price for "No" (numeric, 0-100 cents or 0-100%)
- Stake amount (optional, for fee calculation)

**Outputs:**
- Total cost (Platform 1 + Platform 2)
- Gross profit/loss
- Platform-specific fees breakdown
- Net profit after fees
- ROI percentage
- Verdict: "Arbitrage Opportunity" (green) or "No Arbitrage" (red/gray)

**Features:**
- Auto-populate fees based on platform selection:
  - Polymarket US: 0.01%
  - Polymarket International: 2% on net winnings
  - Kalshi: 0.7%
- Color-coded results (green for profit, red for loss)
- Tooltip explaining arbitrage concept
- Tooltip explaining fee structures

### FR4: Multi-Market Comparison Tool
**Purpose:** Compare the same market across multiple platforms to find best value

**Inputs:**
- Number of platforms to compare (2-4)
- For each platform:
  - Platform name (dropdown: Polymarket, Kalshi, PredictIt, Robinhood)
  - "Yes" price (numeric, 0-100)
  - "No" price (numeric, 0-100)

**Outputs:**
- Side-by-side comparison table showing:
  - Platform name
  - Yes price
  - No price
  - Implied probability for Yes
  - Implied probability for No
  - Fee structure
- Highlight best "Yes" price (lowest cost, highest value)
- Highlight best "No" price (lowest cost, highest value)
- Show price discrepancies between platforms

**Features:**
- Sortable table by price or platform
- Tooltips explaining why lower price = better value
- Visual indicators (badges or color coding) for best prices

### FR5: Expected Value (EV) Calculator
**Purpose:** Calculate if a bet is mathematically profitable over time

**Inputs:**
- Market price (numeric, 0-100 cents or %)
- Your estimated true probability (numeric, 0-100%)
- Stake size (numeric, dollars)

**Outputs:**
- Expected value in dollars
- Expected value as a percentage
- Breakeven probability
- Verdict: "+EV" (positive, green) or "-EV" (negative, red)
- Long-term expected profit/loss over 100 bets

**Features:**
- Formula display: EV = (Probability × Payout) - (1 - Probability) × Stake
- Color-coded results (green for +EV, red for -EV)
- Tooltip explaining EV concept
- Tooltip explaining importance of accurate probability estimates

### FR6: Kelly Criterion Calculator  
**Purpose:** Calculate optimal bet size as a percentage of bankroll

**Inputs:**
- Current bankroll (numeric, dollars)
- Market odds (numeric, 0-100 cents or %)
- Your estimated true probability (numeric, 0-100%)
- Kelly fraction selector (dropdown): Full Kelly, Half Kelly, Quarter Kelly, Custom
- If Custom: Custom fraction (numeric, 0-1)

**Outputs:**
- Your edge (percentage)
- Full Kelly percentage
- Selected Kelly fraction percentage
- Recommended stake in dollars
- Expected bankroll growth rate
- Risk assessment (Low/Medium/High based on fraction selected)

**Features:**
- Formula display: Kelly % = (Edge / Odds)
- Tooltips explaining:
  - What is Kelly Criterion
  - Why full Kelly is aggressive
  - Why fractional Kelly reduces variance
- Warning message if recommended stake >10% of bankroll
- Color-coded risk levels

### FR7: Educational Tooltips
**Requirements:**
- Add question mark icons (?) next to technical terms
- On hover, show tooltip with clear explanation
- Terms requiring tooltips:
  - Implied probability
  - Arbitrage
  - Expected value (EV)
  - Kelly Criterion
  - Edge
  - Variance/Drawdown
  - Platform fees
  - Breakeven probability
- Tooltips should be concise (1-2 sentences)
- Use shadcn/ui Tooltip component for consistent styling

## Non-Functional Requirements

### NFR1: Performance
- All calculator results should update in real-time (<100ms) as users type
- No backend API calls required (all calculations client-side)
- Page should load instantly (no data fetching needed)

### NFR2: Design Consistency
- Follow existing dark theme design patterns
- Use shadcn/ui components (Accordion, Card, Input, Select, Badge, Tooltip)
- Match the visual style of the existing Home Page and Tracker tabs
- Use Lucide React icons for question marks and visual indicators

### NFR3: Accessibility
- All inputs must have proper labels
- Keyboard navigation support
- Screen reader compatible
- High contrast for readability

### NFR4: Mobile Responsiveness
- Calculator layouts should stack vertically on mobile
- Inputs should be touch-friendly (minimum 44px tap targets)
- Text should remain readable at all viewport sizes

## Acceptance Criteria

1. ✅ Calculators page shows accordion layout with 5 calculator sections
2. ✅ Each calculator can be independently expanded/collapsed
3. ✅ Odds Converter correctly converts between all 4 formats
4. ✅ Arbitrage Calculator correctly factors in platform-specific fees
5. ✅ Multi-Market Comparison highlights best prices across platforms
6. ✅ EV Calculator accurately computes expected value
7. ✅ Kelly Criterion Calculator provides Full/Half/Quarter/Custom options
8. ✅ All tooltips display explanations on hover
9. ✅ Real-time calculation updates as user types
10. ✅ Design matches existing dark theme aesthetic
11. ✅ All calculators work on mobile devices

## Out of Scope

- Backend storage of calculator history
- Saving/loading calculator presets
- Exporting calculator results
- Integration with live market data (calculators are standalone tools)
- Multi-language support
- User authentication for calculator access
