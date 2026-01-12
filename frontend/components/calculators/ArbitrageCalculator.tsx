"use client"

import { useState, useEffect } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Select } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { calculateArbitrage, formatCurrency, formatPercentage } from "@/lib/calculator-utils"
import { HelpCircle, ArrowRightLeft } from "lucide-react"

export function ArbitrageCalculator() {
    const [platform1, setPlatform1] = useState('polymarket-us')
    const [price1, setPrice1] = useState("48")
    const [platform2, setPlatform2] = useState('kalshi')
    const [price2, setPrice2] = useState("50")
    const [stake, setStake] = useState("100")

    const results = calculateArbitrage(
        parseFloat(price1) || 0,
        platform1,
        parseFloat(price2) || 0,
        platform2,
        parseFloat(stake) || 100
    )

    return (
        <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="space-y-4">
                    <div className="flex items-center gap-2 text-indigo-400 mb-2">
                        <Badge className="bg-indigo-500/20 text-indigo-400 border-indigo-500/30">Leg 1</Badge>
                        <span className="text-xs font-bold uppercase tracking-widest text-white/60">"YES" CONTRACT</span>
                    </div>
                    <div className="grid grid-cols-1 gap-4">
                        <div className="space-y-2">
                            <label className="text-[10px] font-black text-white/30 uppercase tracking-widest">Platform</label>
                            <Select value={platform1} onChange={(e) => setPlatform1(e.target.value)}>
                                <option value="polymarket-us">Polymarket US (0.01% fee)</option>
                                <option value="polymarket-intl">Polymarket Intl (2% winnings)</option>
                                <option value="kalshi">Kalshi (0.7% fee)</option>
                            </Select>
                        </div>
                        <div className="space-y-2">
                            <label className="text-[10px] font-black text-white/30 uppercase tracking-widest">Price (Cents)</label>
                            <Input type="number" value={price1} onChange={(e) => setPrice1(e.target.value)} placeholder="0-100" />
                        </div>
                    </div>
                </div>

                <div className="space-y-4">
                    <div className="flex items-center gap-2 text-zinc-400 mb-2">
                        <Badge className="bg-white/5 text-white/40 border-white/10">Leg 2</Badge>
                        <span className="text-xs font-bold uppercase tracking-widest text-white/60">"NO" CONTRACT</span>
                    </div>
                    <div className="grid grid-cols-1 gap-4">
                        <div className="space-y-2">
                            <label className="text-[10px] font-black text-white/30 uppercase tracking-widest">Platform</label>
                            <Select value={platform2} onChange={(e) => setPlatform2(e.target.value)}>
                                <option value="polymarket-us">Polymarket US</option>
                                <option value="polymarket-intl">Polymarket Intl</option>
                                <option value="kalshi">Kalshi</option>
                            </Select>
                        </div>
                        <div className="space-y-2">
                            <label className="text-[10px] font-black text-white/30 uppercase tracking-widest">Price (Cents)</label>
                            <Input type="number" value={price2} onChange={(e) => setPrice2(e.target.value)} placeholder="0-100" />
                        </div>
                    </div>
                </div>
            </div>

            <div className="p-4 bg-white/5 border border-white/5 rounded-2xl">
                <div className="flex items-center justify-between mb-4">
                    <div className="text-xs font-bold text-white/40 uppercase tracking-widest">Investment Details</div>
                    <div className="flex items-center gap-2">
                        <span className="text-xs text-white/40">Stake:</span>
                        <div className="w-24">
                            <Input
                                type="number"
                                value={stake}
                                onChange={(e) => setStake(e.target.value)}
                                className="h-8 bg-black/40 border-white/5 text-right font-mono"
                            />
                        </div>
                    </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                        <div className="text-[10px] text-white/30 uppercase font-black mb-1">Total Cost</div>
                        <div className="text-lg font-mono text-white">{(results.totalCost * 100).toFixed(1)}¢</div>
                    </div>
                    <div>
                        <div className="text-[10px] text-white/30 uppercase font-black mb-1">Gross Profit</div>
                        <div className={results.grossProfit > 0 ? "text-lg font-mono text-green-400" : "text-lg font-mono text-white/60"}>
                            {formatCurrency(results.grossProfit)}
                        </div>
                    </div>
                    <div>
                        <div className="text-[10px] text-white/30 uppercase font-black mb-1">Total Fees</div>
                        <div className="text-lg font-mono text-red-400/60">-{formatCurrency(results.totalFees)}</div>
                    </div>
                    <div>
                        <div className="text-[10px] text-white/30 uppercase font-black mb-1">Net ROI</div>
                        <div className={results.netProfit > 0 ? "text-lg font-mono text-green-400 underline decoration-green-500/30" : "text-lg font-mono text-white/30"}>
                            {formatPercentage(results.roi)}
                        </div>
                    </div>
                </div>
            </div>

            <div className={`p-5 rounded-2xl border flex items-center justify-between transition-all duration-500 ${results.isArbitrage && results.netProfit > 0 ? "bg-green-500/10 border-green-500/20" : "bg-white/5 border-white/5"}`}>
                <div>
                    <div className="text-xs font-black uppercase tracking-widest text-white/40 mb-1">Final Verdict</div>
                    <div className="flex items-center gap-2">
                        {results.isArbitrage && results.netProfit > 0 ? (
                            <>
                                <Badge className="bg-green-500 text-black font-black border-none px-3">ARBITRAGE FOUND</Badge>
                                <span className="text-sm font-medium text-green-400">Locked Profit: {formatCurrency(results.netProfit)}</span>
                            </>
                        ) : (
                            <Badge className="bg-white/10 text-white/40 border-white/10 px-3">NO OPPORTUNITY</Badge>
                        )}
                    </div>
                </div>
                <ArrowRightLeft className={`h-8 w-8 transition-all duration-700 ${results.isArbitrage && results.netProfit > 0 ? "text-green-500 rotate-0 scale-110" : "text-white/5 rotate-90 scale-90"}`} />
            </div>
        </div>
    )
}
