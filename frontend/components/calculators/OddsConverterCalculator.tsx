"use client"

import { useState, useEffect } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Select } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { oddsConverter, formatPercentage } from "@/lib/calculator-utils"
import { HelpCircle } from "lucide-react"

export function OddsConverterCalculator() {
    const [format, setFormat] = useState<'cents' | 'percentage' | 'american' | 'decimal'>('cents')
    const [value, setValue] = useState<string>("50")
    const [results, setResults] = useState(oddsConverter(50, 'cents'))

    useEffect(() => {
        const numValue = parseFloat(value)
        if (!isNaN(numValue)) {
            setResults(oddsConverter(numValue, format))
        }
    }, [value, format])

    return (
        <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                    <label className="text-xs font-bold text-white/40 uppercase tracking-wider flex items-center gap-1.5">
                        Input Format
                    </label>
                    <Select
                        value={format}
                        onChange={(e) => setFormat(e.target.value as any)}
                    >
                        <option value="cents">Cents (e.g. 73¢)</option>
                        <option value="percentage">Percentage (e.g. 73%)</option>
                        <option value="american">American Odds (e.g. -270)</option>
                        <option value="decimal">Decimal Odds (e.g. 1.37)</option>
                    </Select>
                </div>
                <div className="space-y-2">
                    <label className="text-xs font-bold text-white/40 uppercase tracking-wider flex items-center gap-1.5">
                        Odds Value
                    </label>
                    <Input
                        type="number"
                        value={value}
                        onChange={(e) => setValue(e.target.value)}
                        placeholder="Enter odds..."
                    />
                </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                    { label: 'Cents', value: `${results.cents.toFixed(1)}¢` },
                    { label: 'Percentage', value: formatPercentage(results.percentage) },
                    { label: 'American', value: results.american > 0 ? `+${results.american}` : results.american.toString() },
                    { label: 'Decimal', value: results.decimal.toFixed(2) },
                ].map((item, i) => (
                    <div key={i} className="bg-white/5 border border-white/5 rounded-xl p-4 text-center">
                        <div className="text-[10px] text-white/30 uppercase tracking-[0.1em] font-black mb-1">{item.label}</div>
                        <div className="text-xl font-mono font-bold text-white">{item.value}</div>
                    </div>
                ))}
            </div>

            <div className="p-4 bg-indigo-500/10 border border-indigo-500/20 rounded-xl">
                <div className="flex items-center justify-between mb-2">
                    <div className="text-xs font-bold text-indigo-400 uppercase tracking-wider flex items-center gap-1.5">
                        Implied Probability
                        <HelpCircle className="h-3 w-3 text-indigo-400/50" />
                    </div>
                    <Badge className="bg-indigo-500/20 text-indigo-300 border-indigo-500/30">
                        {formatPercentage(results.impliedProbability)}
                    </Badge>
                </div>
                <div className="h-2 w-full bg-indigo-950 rounded-full overflow-hidden">
                    <div
                        className="h-full bg-indigo-500 transition-all duration-500 shadow-[0_0_10px_rgba(99,102,241,0.5)]"
                        style={{ width: `${results.impliedProbability}%` }}
                    />
                </div>
            </div>
        </div>
    )
}
