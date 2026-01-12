/**
 * Utility functions for prediction market calculations
 */

export interface ConversionResult {
    cents: number
    percentage: number
    american: number
    decimal: number
    impliedProbability: number
}

/**
 * Converts odds between different formats
 */
export const oddsConverter = (value: number, format: 'cents' | 'percentage' | 'american' | 'decimal'): ConversionResult => {
    let percentage = 0

    switch (format) {
        case 'cents':
            percentage = value
            break
        case 'percentage':
            percentage = value
            break
        case 'american':
            if (value > 0) {
                percentage = 100 / (value / 100 + 1)
            } else {
                percentage = (Math.abs(value) / (Math.abs(value) + 100)) * 100
            }
            break
        case 'decimal':
            percentage = (1 / value) * 100
            break
    }

    // Sanitize percentage
    percentage = Math.max(0.01, Math.min(99.99, percentage))

    return {
        cents: percentage,
        percentage: percentage,
        american: percentage > 50
            ? Math.round(-(percentage / (100 - percentage)) * 100)
            : Math.round(((100 - percentage) / percentage) * 100),
        decimal: 100 / percentage,
        impliedProbability: percentage
    }
}

/**
 * Calculates net arbitrage profit after platform fees
 */
export const calculateArbitrage = (
    price1: number,
    platform1: string,
    price2: number,
    platform2: string,
    stake: number = 100
) => {
    const PLATFORM_FEES: Record<string, number> = {
        'polymarket-us': 0.0001,
        'polymarket-intl': 0.02, // Note: Intl is 2% on winnings, not volume
        'kalshi': 0.007
    }

    const cost1 = price1 / 100
    const cost2 = price2 / 100
    const totalCost = cost1 + cost2

    let totalFees = 0

    // Apply Platform 1 fees
    if (platform1 === 'polymarket-intl') {
        // 2% on net winnings (Payout - Stake)
        const winnings = (stake / totalCost) - (stake * cost1 / totalCost)
        totalFees += winnings * 0.02
    } else {
        totalFees += (stake * cost1 / totalCost) * (PLATFORM_FEES[platform1] || 0)
    }

    // Apply Platform 2 fees
    if (platform2 === 'polymarket-intl') {
        const winnings = (stake / totalCost) - (stake * cost2 / totalCost)
        totalFees += winnings * 0.02
    } else {
        totalFees += (stake * cost2 / totalCost) * (PLATFORM_FEES[platform2] || 0)
    }

    const grossProfit = (stake / totalCost) - stake
    const netProfit = grossProfit - totalFees

    return {
        totalCost,
        grossProfit,
        totalFees,
        netProfit,
        roi: (netProfit / stake) * 100,
        isArbitrage: totalCost < 1.0
    }
}

/**
 * Calculates Expected Value (EV)
 */
export const calculateExpectedValue = (marketPrice: number, trueProb: number, stake: number) => {
    const price = marketPrice / 100
    const prob = trueProb / 100

    // Payout is 1/price. Profit is (1/price - 1) * stake
    const profitIfWin = (1 / price - 1) * stake
    const ev = (prob * profitIfWin) - ((1 - prob) * stake)

    return {
        evDollars: ev,
        evPercentage: (ev / stake) * 100,
        breakevenProb: price * 100
    }
}

/**
 * Calculates Kelly Criterion stake
 */
export const calculateKellyCriterion = (bankroll: number, marketPrice: number, trueProb: number, fraction: number = 1) => {
    const p = trueProb / 100
    const price = marketPrice / 100
    const b = (1 / price) - 1 // Net odds (payout - stake)
    const q = 1 - p

    // Kelly Formula: f = (bp - q) / b
    const f = (b * p - q) / b

    const recommendedFraction = Math.max(0, f * fraction)
    const recommendedStake = bankroll * recommendedFraction

    return {
        edge: (p - price) * 100,
        fullKelly: f * 100,
        recommendedPercentage: recommendedFraction * 100,
        recommendedStake: recommendedStake
    }
}

/**
 * Formatter for currency
 */
export const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
    }).format(value)
}

/**
 * Formatter for percentage
 */
export const formatPercentage = (value: number, decimals: number = 2) => {
    return `${value.toFixed(decimals)}%`
}
