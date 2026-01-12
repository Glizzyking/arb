# Implementation Plan: Prediction Market Calculator Tools

## Overview
This plan outlines the implementation of five prediction market calculator tools to replace the "Coming Soon" placeholder on the Calculators page. All calculators will be client-side React components with real-time calculations.

## User Review Required

> [!IMPORTANT]
> **No Breaking Changes** - This feature is additive only. The existing Calculators tab currently shows a "Coming Soon" placeholder, which will be replaced with functional calculators. No existing functionality will be affected.

## Proposed Changes

### Frontend Components

#### [NEW] [calculator-utils.ts](file:///Users/george/Desktop/bitcoin%20arb/polymarket-kalshi-btc-arbitrage-bot/frontend/lib/calculator-utils.ts)

**Purpose:** Centralized utility functions for all calculator mathematics

**Functions to implement:**
- `oddsConverter()` - Convert between Cents, Percentage, American Odds, Decimal Odds
- `calculateImpliedProbability()` - Calculate implied probability from odds
- `calculateArbitrage()` - Detect arbitrage opportunities and calculate net profit
- `calculatePlatformFees()` - Apply platform-specific fee structures
- `calculateExpectedValue()` - Compute EV based on market price and true probability
- `calculateKellyCriterion()` - Calculate optimal bet size using Kelly formula
- `formatCurrency()` - Format numbers as currency
- `formatPercentage()` - Format numbers as percentages

**Why separate file:** Keeps calculator logic testable and reusable across components

---

#### [NEW] [OddsConverterCalculator.tsx](file:///Users/george/Desktop/bitcoin%20arb/polymarket-kalshi-btc-arbitrage-bot/frontend/components/calculators/OddsConverterCalculator.tsx)

**Purpose:** Convert between odds formats and display implied probability

**State:**
- `oddsFormat` - Selected format (Cents, Percentage, American, Decimal)
- `oddsValue` - Input value

**Components used:** `Card`, `Select`, `Input`, `Tooltip`, `Badge`

**Real-time calculation:** Updates all formats on keystroke using `oddsConverter()`

---

#### [NEW] [ArbitrageCalculator.tsx](file:///Users/george/Desktop/bitcoin%20arb/polymarket-kalshi-btc-arbitrage-bot/frontend/components/calculators/ArbitrageCalculator.tsx)

**Purpose:** Calculate arbitrage profit/loss with platform fees

**State:**
- `platform1`, `platform2` - Selected platforms
- `price1Yes`, `price2No` - Input prices
- `stakeAmount` - Optional stake for fee calculation

**Components used:** `Card`, `Select`, `Input`, `Badge`, `Tooltip`

**Fee mapping:**
```typescript
const PLATFORM_FEES = {
  'polymarket-us': 0.0001,
  'polymarket-intl': 0.02,
  'kalshi': 0.007
}
```

**Real-time calculation:** Green badge for arbitrage opportunity, red/gray for no opportunity

---

#### [NEW] [MultiMarketComparison.tsx](file:///Users/george/Desktop/bitcoin%20arb/polymarket-kalshi-btc-arbitrage-bot/frontend/components/calculators/MultiMarketComparison.tsx)

**Purpose:**Compare same market across multiple platforms

**State:**
- `numPlatforms` - Number of platforms to compare (2-4)
- `platforms` - Array of platform data objects

**Components used:** `Card`, `Table`, `Select`, `Input`, `Badge`, `Tooltip`

**Features:**
- Sortable table by price or platform name
- Highlight best "Yes" price (lowest cost)
- Highlight best "No" price (lowest cost)
- Show price discrepancies

---

#### [NEW] [EVCalculator.tsx](file:///Users/george/Desktop/bitcoin%20arb/polymarket-kalshi-btc-arbitrage-bot/frontend/components/calculators/EVCalculator.tsx)

**Purpose:** Calculate expected value of a bet

**State:**
- `marketPrice` - Current market price (0-100)
- `trueProbability` - User's estimated probability (0-100)
- `stakeSize` - Bet amount in dollars

**Components used:** `Card`, `Input`, `Badge`, `Tooltip`

**Outputs:**
- EV in dollars
- EV as percentage
- Breakeven probability
- Long-term profit over 100 bets

**Color coding:** Green for +EV, red for -EV

---

#### [NEW] [KellyCalculator.tsx](file:///Users/george/Desktop/bitcoin%20arb/polymarket-kalshi-btc-arbitrage-bot/frontend/components/calculators/KellyCalculator.tsx)

**Purpose:** Calculate optimal bet size using Kelly Criterion

**State:**
- `bankroll` - Current bankroll
- `marketOdds` - Market price (0-100)
- `trueProbability` - User's estimated probability
- `kellyFraction` - Selected fraction (Full, Half, Quarter, Custom)
- `customFraction` - Custom fraction value (0-1)

**Components used:** `Card`, `Input`, `Select`, `Badge`, `Tooltip`

**Outputs:**
- Edge percentage
- Full Kelly percentage
- Selected Kelly percentage
- Recommended stake in dollars
- Risk assessment (Low/Medium/High)

**Warning:** Show alert if recommended stake >10% of bankroll

---

#### [NEW] [InfoTooltip.tsx](file:///Users/george/Desktop/bitcoin%20arb/polymarket-kalshi-btc-arbitrage-bot/frontend/components/calculators/InfoTooltip.tsx)

**Purpose:** Reusable tooltip component for educational content

**Props:**
- `term` - Technical term keyword
- `children` - Tooltip content

**Component:** Wraps shadcn/ui `Tooltip` with question mark icon from Lucide

**Tooltip definitions:**
```typescript
const TOOLTIP_CONTENT = {
  'implied-probability': 'The probability implied by the market price...',
  'arbitrage': 'A risk-free profit opportunity...',
  'expected-value': 'The average amount you expect to win or lose...',
  'kelly-criterion': 'A formula to calculate optimal bet size...',
  // ... more definitions
}
```

---

#### [MODIFY] [CalculatorsPage.tsx](file:///Users/george/Desktop/bitcoin%20arb/polymarket-kalshi-btc-arbitrage-bot/frontend/components/CalculatorsPage.tsx)

**Changes:**
- Remove "Coming Soon" placeholder
- Add shadcn/ui `Accordion` component
- Import all 5 calculator components
- Render accordion with 5 sections (one per calculator)
- Each accordion item contains one calculator component
- Default state: all sections collapsed
- Style to match dark theme

**Structure:**
```tsx
<Accordion type="multiple" className="space-y-4">
  <AccordionItem value="odds-converter">
    <AccordionTrigger>Odds Converter & Probability Calculator</AccordionTrigger>
    <AccordionContent><OddsConverterCalculator /></AccordionContent>
  </AccordionItem>
  {/* ... 4 more items */}
</Accordion>
```

---

## Verification Plan

### Automated Tests
Currently, the frontend project does not have a test framework configured. Testing will be manual via browser verification.

### Manual Verification

#### Test 1: Visual Verification - Accordion Layout
1. Navigate to `http://localhost:3000/?tab=calculators`
2. Verify all 5 calculator sections are visible in collapsed state
3. Click each accordion header to expand/collapse
4. Verify only one section can be expanded at a time (accordion behavior)
5. Verify dark theme styling matches existing app design

**Expected Result:** Accordion layout displays correctly with consistent dark theme

---

#### Test 2: Odds Converter Calculator
1. Expand "Odds Converter & Probability Calculator" section
2. Select "Cents" format and enter `65`
3. Verify conversion displays:
   - Percentage: `65%`
   - American Odds: approximately `-186`
   - Decimal Odds: approximately `1.54`
   - Implied Probability: `65%`
   - Complementary Probability: `35%`
4. Change format to "American Odds" and enter `-200`
5. Verify all other formats update in real-time

**Expected Result:** Odds converter accurately converts between all 4 formats

---

#### Test 3: Arbitrage Calculator
1. Expand "Arbitrage Calculator" section
2. Set Platform 1: Polymarket US, Yes price: `45`
3. Set Platform 2: Kalshi, No price: `53`
4. Enter stake amount: `100`
5. Verify output shows:
   - Total cost: `$0.98` (0.45 + 0.53)
   - Gross profit: `$0.02`
   - Platform fees: approximately `$0.0045` for Polymarket US + `$0.70` for Kalshi
   - Net profit after fees
   - Verdict: "Arbitrage Opportunity" with green badge
6. Change Yes price to `55` (total = 1.08)
7. Verify verdict changes to "No Arbitrage" with red/gray styling

**Expected Result:** Arbitrage calculator correctly identifies opportunities and calculates fees

---

#### Test 4: Multi-Market Comparison
1. Expand "Multi-Market Comparison" section
2. Set number of platforms to compare: `3`
3. Enter platform data:
   - Polymarket: Yes `60`, No `42`
   - Kalshi: Yes `62`, No `40`
   - PredictIt: Yes `58`, No `44`
4. Verify table displays all 3 platforms with:
   - Yes/No prices
   - Implied probabilities
   - Fee structures
5. Verify PredictIt Yes price (`58`) is highlighted as best value (lowest)
6. Verify Kalshi No price (`40`) is highlighted as best value (lowest)

**Expected Result:** Comparison tool highlights best prices across platforms

---

#### Test 5: Expected Value Calculator
1. Expand "Expected Value Calculator" section
2. Enter market price: `70` (cents)
3. Enter your estimated probability: `80` (%)
4. Enter stake size: `100` (dollars)
5. Verify output shows:
   - EV in dollars: positive value
   - EV as percentage: positive percentage
   - Breakeven probability
   - "+EV" verdict with green badge
6. Change estimated probability to `60` (making it -EV)
7. Verify verdict changes to "-EV" with red badge

**Expected Result:** EV calculator accurately computes expected value and displays color-coded verdict

---

#### Test 6: Kelly Criterion Calculator
1. Expand "Kelly Criterion Calculator" section
2. Enter bankroll: `1000`
3. Enter market odds: `65` (cents)
4. Enter true probability: `75` (%)
5. Select Kelly fraction: "Full Kelly"
6. Verify output shows:
   - Edge: `10%` (75% - 65%)
   - Full Kelly percentage
   - Recommended stake in dollars
   - Risk assessment
7. Change Kelly fraction to "Half Kelly"
8. Verify recommended stake is half of Full Kelly
9. Change recommended stake to >10% of bankroll
10. Verify warning message appears

**Expected Result:** Kelly calculator provides accurate bet sizing with risk warnings

---

#### Test 7: Educational Tooltips
1. Hover over question mark (?) icons next to technical terms
2. Verify tooltip appears with explanation
3. Test tooltips for:
   - "Implied Probability"
   - "Arbitrage"
   - "Expected Value"
   - "Kelly Criterion"
   - "Edge"
   - "Platform Fees"
4. Verify tooltips are concise (1-2 sentences)
5. Verify tooltip styling matches shadcn/ui theme

**Expected Result:** All tooltips display educational content on hover

---

#### Test 8: Mobile Responsiveness
1. Resize browser window to mobile width (375px)
2. Navigate to Calculators tab
3. Verify accordion layout stacks vertically
4. Verify all inputs are touch-friendly (44px minimum)
5. Verify text remains readable
6. Test expanding/collapsing sections on mobile
7. Verify calculator inputs and outputs fit within viewport

**Expected Result:** Calculators work on mobile with responsive layout

---

#### Test 9: Real-Time Calculation Updates
1. Open any calculator
2. Type values in input fields character by character
3. Verify results update in real-time (<100ms delay)
4. Verify no lag or stuttering during typing
5. Test with multiple calculators expanded simultaneously
6. Verify calculations remain accurate during rapid input changes

**Expected Result:** All calculations update instantly without performance issues

---

#### Test 10: Integration with Existing App
1. Navigate between all 4 tabs (Home Page, Positive EV, Calculators, Tracker)
2. Verify tab switching works smoothly
3. Verify Calculators tab maintains state when switching away and back
4. Verify no console errors or warnings
5. Verify dark theme consistency across all tabs
6. Verify Settings modal still works from Calculators page

**Expected Result:** Calculators integrate seamlessly with existing navigation and features
