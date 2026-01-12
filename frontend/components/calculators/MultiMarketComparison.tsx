"use client"

import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Select } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { HelpCircle, Trophy, TrendingDown } from "lucide-react"

interface MarketRow {
    platform: string
    yesPrice: string
    noPrice: string
}

export function MultiMarketComparison() {
    const [rows, setRows] = useState<MarketRow[]>([
        { platform: 'polymarket', yesPrice: '68', noPrice: '35' },
        { platform: 'kalshi', yesPrice: '65', noPrice: '38' },
        { platform: 'predictit', yesPrice: '70', noPrice: '33' }
    ])

    const addRow = () => {
        setRows([...rows, { platform: 'robinhood', yesPrice: '', noPrice: '' }])
    }

    const updateRow = (index: number, field: keyof MarketRow, value: string) => {
        const newRows = [...rows]
        newRows[index] = { ...newRows[index], [field]: value }
        setRows(newRows)
    }

    const removeRow = (index: number) => {
        setRows(rows.filter((_, i) => i !== index))
    }

    // Calculate best prices
    const validYesPrices = rows.map(r => parseFloat(r.yesPrice)).filter(p => !isNaN(p))
    const bestYes = validYesPrices.length > 0 ? Math.min(...validYesPrices) : null

    const validNoPrices = rows.map(r => parseFloat(r.noPrice)).filter(p => !isNaN(p))
    const bestNo = validNoPrices.length > 0 ? Math.min(...validNoPrices) : null

    return (
        <div className="space-y-6">
            <div className="overflow-x-auto">
                <Table>
                    <TableHeader>
                        <TableRow className="border-white/5 hover:bg-transparent">
                            <TableHead className="text-[10px] font-black uppercase tracking-widest text-white/30">Platform</TableHead>
                            <TableHead className="text-[10px] font-black uppercase tracking-widest text-white/30 text-center">Yes Price (¢)</TableHead>
                            <TableHead className="text-[10px] font-black uppercase tracking-widest text-white/30 text-center">No Price (¢)</TableHead>
                            <TableHead className="w-[50px]"></TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {rows.map((row, i) => (
                            <TableRow key={i} className="border-white/5 hover:bg-white/5 transition-colors group">
                                <TableCell>
                                    <Select
                                        value={row.platform}
                                        onChange={(e) => updateRow(i, 'platform', e.target.value)}
                                        className="h-9 border-none bg-transparent font-bold capitalize"
                                    >
                                        <option value="polymarket">Polymarket</option>
                                        <option value="kalshi">Kalshi</option>
                                        <option value="predictit">PredictIt</option>
                                        <option value="robinhood">Robinhood</option>
                                    </Select>
                                </TableCell>
                                <TableCell>
                                    <div className="relative">
                                        <Input
                                            type="number"
                                            value={row.yesPrice}
                                            onChange={(e) => updateRow(i, 'yesPrice', e.target.value)}
                                            className={`h-9 text-center font-mono ${parseFloat(row.yesPrice) === bestYes ? "border-indigo-500/50 bg-indigo-500/10 text-indigo-300" : "bg-transparent border-white/5"}`}
                                        />
                                        {parseFloat(row.yesPrice) === bestYes && (
                                            <Trophy className="absolute -right-1 -top-1 h-3 w-3 text-indigo-400 fill-indigo-400/20" />
                                        )}
                                    </div>
                                </TableCell>
                                <TableCell>
                                    <div className="relative">
                                        <Input
                                            type="number"
                                            value={row.noPrice}
                                            onChange={(e) => updateRow(i, 'noPrice', e.target.value)}
                                            className={`h-9 text-center font-mono ${parseFloat(row.noPrice) === bestNo ? "border-green-500/50 bg-green-500/10 text-green-300" : "bg-transparent border-white/5"}`}
                                        />
                                        {parseFloat(row.noPrice) === bestNo && (
                                            <Trophy className="absolute -right-1 -top-1 h-3 w-3 text-green-400 fill-green-400/20" />
                                        )}
                                    </div>
                                </TableCell>
                                <TableCell>
                                    <button
                                        onClick={() => removeRow(i)}
                                        className="text-white/20 hover:text-red-400 p-2 opacity-0 group-hover:opacity-100 transition-all"
                                    >
                                        ×
                                    </button>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </div>

            <div className="flex justify-between items-center">
                <button
                    onClick={addRow}
                    className="text-[10px] font-black uppercase tracking-widest text-indigo-400 hover:text-indigo-300 flex items-center gap-2 transition-colors"
                >
                    <span className="text-lg">+</span> Add Platform to Compare
                </button>

                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2">
                        <div className="h-2 w-2 rounded-full bg-indigo-500 shadow-[0_0_5px_rgba(99,102,241,0.5)]" />
                        <span className="text-[10px] uppercase font-bold text-white/30 tracking-widest">Best "YES"</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="h-2 w-2 rounded-full bg-green-500 shadow-[0_0_5px_rgba(34,197,94,0.5)]" />
                        <span className="text-[10px] uppercase font-bold text-white/30 tracking-widest">Best "NO"</span>
                    </div>
                </div>
            </div>
        </div>
    )
}
