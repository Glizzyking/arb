"use client"

import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { calculateExpectedValue, formatCurrency, formatPercentage } from "@/lib/calculator-utils"
import { HelpCircle, Sparkles } from "lucide-react"

export function EVCalculator() {
    const [marketPrice, setMarketPrice] = useState("65")
    const [trueProb, setTrueProb] = useState("75")
    const [stake, setStake] = useState("100")

    const results = calculateExpectedValue(
        parseFloat(marketPrice) || 0,
        parseFloat(trueProb) || 0,
        parseFloat(stake) || 0
    )

    const isPositive = results.evDollars > 0

    return (
        <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                    <label className="text-[10px] font-black text-white/30 uppercase tracking-widest flex items-center gap-1.5">
                        Market Price (¢)
                        <HelpCircle className="h-3 w-3 text-white/10" />
                    </label>
                    <Input type="number" value={marketPrice} onChange={(e) => setMarketPrice(e.target.value)} placeholder="Price..." />
                </div>
                <div className="space-y-2">
                    <label className="text-[10px] font-black text-white/30 uppercase tracking-widest flex items-center gap-1.5">
                        Estimated True Prob (%)
                        <HelpCircle className="h-3 w-3 text-white/10" />
                    </label>
                    <Input type="number" value={trueProb} onChange={(e) => setTrueProb(e.target.value)} placeholder="0-100..." className="border-indigo-500/20" />
                </div>
                <div className="space-y-2">
                    <label className="text-[10px] font-black text-white/30 uppercase tracking-widest">Stake ($)</label>
                    <Input type="number" value={stake} onChange={(e) => setStake(e.target.value)} placeholder="Stake..." />
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className={`p-6 rounded-2xl border transition-all duration-500 flex flex-col items-center justify-center text-center ${isPositive ? "bg-green-500/10 border-green-500/20" : "bg-red-500/10 border-red-500/20"}`}>
                    <div className="text-[10px] font-black uppercase tracking-[0.2em] text-white/40 mb-2">EXPECTED VALUE</div>
                    <div className={`text-3xl font-mono font-bold mb-1 ${isPositive ? "text-green-400" : "text-red-400"}`}>
                        {isPositive ? "+" : ""}{formatCurrency(results.evDollars)}
                    </div>
                    <Badge className={`${isPositive ? "bg-green-500/20 text-green-300 border-green-500/30" : "bg-red-500/20 text-red-300 border-red-500/30"}`}>
                        {isPositive ? "+" : ""}{formatPercentage(results.evPercentage)}
                    </Badge>
                </div>

                <div className="bg-white/5 border border-white/5 rounded-2xl p-6 space-y-4">
                    <div className="flex justify-between items-center">
                        <span className="text-xs font-bold text-white/40 uppercase tracking-widest">Breakeven Prob</span>
                        <span className="text-lg font-mono text-white">{results.breakevenProb.toFixed(1)}%</span>
                    </div>
                    <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
                        <div className="h-full bg-white/20" style={{ width: `${results.breakevenProb}%` }} />
                    </div>

                    <div className="flex justify-between items-center pt-2">
                        <div className="flex flex-col">
                            <span className="text-xs font-bold text-white/40 uppercase tracking-widest">Model Alpha</span>
                            <span className="text-[10px] text-white/20 font-medium">Edge vs Market Implied</span>
                        </div>
                        <span className={`text-lg font-mono font-bold ${parseFloat(trueProb) > parseFloat(marketPrice) ? "text-indigo-400" : "text-white/40"}`}>
                            {(parseFloat(trueProb) - parseFloat(marketPrice)).toFixed(1)}%
                        </span>
                    </div>
                </div>
            </div>

            <div className="flex items-center gap-3 p-4 bg-white/5 border border-white/5 rounded-xl text-xs text-white/40 italic">
                <Sparkles className="h-4 w-4 text-indigo-400 shrink-0" />
                If you took this bet 100 times, you would expect to {isPositive ? "win" : "lose"} {formatCurrency(Math.abs(results.evDollars * 100))} in total.
            </div>
        </div>
    )
}
