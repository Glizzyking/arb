"use client"

import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Select } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { calculateKellyCriterion, formatCurrency, formatPercentage } from "@/lib/calculator-utils"
import { HelpCircle, ShieldAlert, TrendingUp } from "lucide-react"

export function KellyCalculator() {
    const [bankroll, setBankroll] = useState("1000")
    const [marketPrice, setMarketPrice] = useState("65")
    const [trueProb, setTrueProb] = useState("75")
    const [fraction, setFraction] = useState("0.5")

    const results = calculateKellyCriterion(
        parseFloat(bankroll) || 0,
        parseFloat(marketPrice) || 0,
        parseFloat(trueProb) || 0,
        parseFloat(fraction) || 0.5
    )

    const isPositive = results.fullKelly > 0
    const isHighRisk = results.recommendedPercentage > 10

    return (
        <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                    <label className="text-[10px] font-black text-white/30 uppercase tracking-widest">Bankroll Balance ($)</label>
                    <Input type="number" value={bankroll} onChange={(e) => setBankroll(e.target.value)} placeholder="Available funds..." />
                </div>
                <div className="space-y-2">
                    <label className="text-[10px] font-black text-white/30 uppercase tracking-widest">Risk Tolerance</label>
                    <Select value={fraction} onChange={(e) => setFraction(e.target.value)}>
                        <option value="1">Full Kelly (Aggressive)</option>
                        <option value="0.5">Half Kelly (Balanced)</option>
                        <option value="0.25">Quarter Kelly (Conservative)</option>
                        <option value="0.1">One-Tenth Kelly (Safe)</option>
                    </Select>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                    <label className="text-[10px] font-black text-white/30 uppercase tracking-widest">Market Price (¢)</label>
                    <Input type="number" value={marketPrice} onChange={(e) => setMarketPrice(e.target.value)} placeholder="Price..." />
                </div>
                <div className="space-y-2">
                    <label className="text-[10px] font-black text-white/30 uppercase tracking-widest">Your Estimated Prob (%)</label>
                    <Input type="number" value={trueProb} onChange={(e) => setTrueProb(e.target.value)} placeholder="0-100..." className="border-indigo-500/20" />
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white/5 border border-white/5 rounded-2xl p-5 text-center flex flex-col items-center justify-center">
                    <div className="text-[10px] uppercase font-black text-white/30 tracking-widest mb-1">Your Edge</div>
                    <div className={`text-2xl font-mono font-bold ${results.edge > 0 ? "text-green-400" : "text-white/20"}`}>
                        {formatPercentage(results.edge)}
                    </div>
                </div>

                <div className={`col-span-1 md:col-span-2 p-5 rounded-2xl border flex items-center justify-between transition-all duration-500 ${isPositive ? "bg-indigo-500/10 border-indigo-500/20" : "bg-white/5 border-white/5 opacity-50"}`}>
                    <div>
                        <div className="text-[10px] uppercase font-black text-indigo-400/80 tracking-widest mb-1 flex items-center gap-1.5">
                            Recommended Stake
                            <TrendingUp className="h-3 w-3" />
                        </div>
                        <div className="text-3xl font-mono font-bold text-white">
                            {isPositive ? formatCurrency(results.recommendedStake) : "$0.00"}
                        </div>
                        <div className="text-[10px] font-bold text-white/40 uppercase tracking-widest mt-1">
                            {isPositive ? `(${formatPercentage(results.recommendedPercentage)} of bankroll)` : "No bet recommended"}
                        </div>
                    </div>

                    {isHighRisk && isPositive && (
                        <div className="flex flex-col items-end gap-1">
                            <Badge className="bg-red-500 text-black font-black border-none animate-pulse">HIGH VARIANCE</Badge>
                            <span className="text-[10px] text-red-400/80 font-bold uppercase tracking-widest">Reduce Size</span>
                        </div>
                    )}
                </div>
            </div>

            {isHighRisk && isPositive && (
                <div className="flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/20 rounded-xl">
                    <ShieldAlert className="h-5 w-5 text-red-500 shrink-0" />
                    <p className="text-xs text-red-300">
                        <span className="font-bold">Caution:</span> Betting more than 10% of your bankroll significantly increases drawdown risk. Consider shifting to Half or Quarter Kelly for better long-term compounding.
                    </p>
                </div>
            )}

            {!isPositive && parseFloat(trueProb) > 0 && parseFloat(marketPrice) > 0 && (
                <div className="text-center p-4 bg-white/5 border border-white/5 rounded-xl">
                    <p className="text-xs text-white/40">Your estimated probability is lower than or equal to the market price. This is a negative edge bet.</p>
                </div>
            )}
        </div>
    )
}
