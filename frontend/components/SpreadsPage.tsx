"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { AlertCircle, ExternalLink, RefreshCw, TrendingUp, ChevronRight } from "lucide-react"
import { cn } from "@/lib/utils"
import GapSettings from "./GapSettings"

interface Spread {
    asset: string
    strike: number
    kalshi_strike: number
    poly_strike: number
    gap: number
    type: string
    profit_pct: number
    kalshi_price: number
    poly_price: number
    kalshi_url: string
    poly_url: string
    expiry: string
    max_volume?: number
}

interface SpreadsPageProps {
    onTrack?: (data: any) => void
}

export function SpreadsPage({ onTrack }: SpreadsPageProps) {
    const [spreads, setSpreads] = useState<Spread[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [lastUpdated, setLastUpdated] = useState<Date>(new Date())
    const [selectedId, setSelectedId] = useState<string | null>(null)

    const fetchSpreads = async () => {
        try {
            const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
            const assets = ["BTC", "ETH", "SOL", "XRP"]

            // Fetch arbitrage data for each asset in parallel
            const promises = assets.map(asset =>
                fetch(`${apiBase}/arbitrage?asset=${asset}`)
                    .then(res => res.ok ? res.json() : null)
                    .catch(() => null)
            )

            const results = await Promise.all(promises)

            // Merge all opportunities from all assets
            const allSpreads: Spread[] = []
            results.forEach((data, index) => {
                if (data && data.opportunities && data.polymarket) {
                    const polyStrike = data.polymarket.price_to_beat || 0

                    // Convert opportunities to spread format
                    data.opportunities.forEach((opp: any) => {
                        allSpreads.push({
                            asset: assets[index],
                            strike: opp.kalshi_strike || 0,
                            kalshi_strike: opp.kalshi_strike || 0,
                            poly_strike: polyStrike,
                            gap: Math.abs(opp.gap || 0),
                            type: opp.type || "Unknown",
                            profit_pct: (opp.margin || 0) * 100,
                            kalshi_price: (opp.kalshi_cost || 0) * 100,
                            poly_price: (opp.poly_cost || 0) * 100,
                            kalshi_url: opp.kalshi_url || "",
                            poly_url: opp.polymarket_url || "",
                            expiry: opp.expiry || new Date().toISOString(),
                            max_volume: opp.available_contracts || 0
                        })
                    })
                }
            })

            // Sort by profit percentage descending
            allSpreads.sort((a, b) => b.profit_pct - a.profit_pct)

            setSpreads(allSpreads)
            setLastUpdated(new Date())
            setError(null)
            setLoading(false)
        } catch (err) {
            console.error(err)
            setError("Connection to backend lost")
        }
    }

    useEffect(() => {
        fetchSpreads()
        const interval = setInterval(fetchSpreads, 5000) // Reduced polling to 5s
        return () => clearInterval(interval)
    }, [])

    return (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <GapSettings />
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div className="flex items-center gap-3">
                    <h1 className="text-3xl font-bold tracking-tight text-white">Arbitrage Spreads</h1>
                    <Badge variant="outline" className="animate-pulse bg-emerald-500/10 text-emerald-400 border-emerald-500/20">
                        <span className="w-2 h-2 rounded-full bg-emerald-500 mr-2"></span>
                        Scanning All Assets
                    </Badge>
                </div>
                <div className="flex items-center gap-2 bg-white/5 px-3 py-1.5 rounded-lg border border-white/5 text-xs text-white/40">
                    <RefreshCw className={cn("h-3 w-3", loading && "animate-spin")} />
                    <span>Last Update: {lastUpdated.toLocaleTimeString()}</span>
                </div>
            </div>

            {/* Helper function to round to next hour */}
            {(() => {
                const formatExpiration = (expiry: string) => {
                    const date = new Date(expiry);
                    const rounded = new Date(date);
                    if (rounded.getMinutes() > 0) {
                        rounded.setHours(rounded.getHours() + 1);
                    }
                    rounded.setMinutes(0);
                    return rounded.toLocaleTimeString([], { hour: 'numeric', hour12: true });
                };
                // Attach to context or just use locally
                (window as any)._formatExpiration = formatExpiration;
                return null;
            })()}

            {error && (
                <div className="bg-red-500/10 border border-red-500/20 text-red-400 px-4 py-3 rounded-xl flex items-center gap-3">
                    <AlertCircle className="h-5 w-5" />
                    <span className="text-sm font-medium">{error}</span>
                </div>
            )}

            <Card className="bg-zinc-950 border-white/5">
                <CardHeader>
                    <div className="flex justify-between items-end">
                        <div className="space-y-1">
                            <CardTitle className="text-white">Active Profitable Spreads</CardTitle>
                            <CardDescription className="text-white/40">Real-time cross-platform arbitrage opportunities with &gt;0% profit</CardDescription>
                        </div>
                    </div>
                </CardHeader>
                <CardContent>
                    {loading && spreads.length === 0 ? (
                        <div className="py-20 flex flex-col items-center justify-center opacity-40">
                            <RefreshCw className="h-10 w-10 animate-spin mb-4 text-emerald-500" />
                            <p className="text-sm">Matching markets across Kalshi & Polymarket...</p>
                        </div>
                    ) : spreads.length === 0 ? (
                        <div className="py-20 flex flex-col items-center justify-center opacity-40 border-2 border-dashed border-white/5 rounded-2xl text-center">
                            <TrendingUp className="h-10 w-10 mb-4" />
                            <p className="text-sm font-medium">No profitable spreads detected at this moment.</p>
                            <p className="text-xs mt-2 text-white/20 px-10">Searching BTC, ETH, SOL, and XRP hourly markets.</p>
                        </div>
                    ) : (
                        <div className="overflow-x-auto">
                            <Table>
                                <TableHeader className="bg-white/5">
                                    <TableRow className="hover:bg-transparent border-white/10">
                                        <TableHead className="text-white/60 font-bold uppercase tracking-widest text-[10px]">Profit %</TableHead>
                                        <TableHead className="text-white/60 font-bold uppercase tracking-widest text-[10px]">Asset & Details</TableHead>
                                        <TableHead className="text-white/60 font-bold uppercase tracking-widest text-[10px]">Kalshi Leg</TableHead>
                                        <TableHead className="text-white/60 font-bold uppercase tracking-widest text-[10px]">Poly Leg</TableHead>
                                        <TableHead className="text-white/60 font-bold uppercase tracking-widest text-[10px]">Liquidity</TableHead>
                                        <TableHead className="text-right text-white/60 font-bold uppercase tracking-widest text-[10px]">Execution</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {spreads.map((spread, i) => {
                                        const spreadId = `${spread.asset}-${spread.kalshi_strike}-${spread.type}`
                                        const isSelected = selectedId === spreadId

                                        return (
                                            <TableRow
                                                key={i}
                                                onClick={() => setSelectedId(spreadId)}
                                                className={cn(
                                                    "border-white/5 hover:bg-white/5 transition-colors group cursor-pointer",
                                                    isSelected && "bg-blue-500/10 border-blue-500/30"
                                                )}
                                            >
                                                <TableCell>
                                                    <div className="flex flex-col">
                                                        <span className="text-xl font-black text-emerald-400 tracking-tighter">
                                                            {spread.profit_pct.toFixed(2)}%
                                                        </span>
                                                        <span className="text-[9px] text-white/20 font-bold uppercase tracking-widest">Net Margin</span>
                                                    </div>
                                                </TableCell>
                                                <TableCell>
                                                    <div className="flex flex-col gap-1">
                                                        <div className="flex items-center gap-2">
                                                            <Badge variant="outline" className="text-[10px] border-white/10 text-white/60">
                                                                {spread.asset}
                                                            </Badge>
                                                            <div className="flex flex-col">
                                                                <div className="flex items-center gap-1.5 text-xs font-black text-white/90">
                                                                    <span>${spread.kalshi_strike.toLocaleString()}</span>
                                                                    <ChevronRight size={10} className="text-white/20" />
                                                                    <span>${spread.poly_strike.toLocaleString()}</span>
                                                                </div>
                                                                <span className="text-[9px] text-blue-400 font-bold uppercase tracking-wider italic">
                                                                    Strike Gap: ${spread.gap.toFixed(2)}
                                                                </span>
                                                            </div>
                                                        </div>
                                                        <span className="text-[10px] text-white/30 truncate max-w-[200px] font-mono">
                                                            Exp: {((window as any)._formatExpiration ? (window as any)._formatExpiration(spread.expiry) : new Date(spread.expiry).toLocaleTimeString())}
                                                        </span>
                                                    </div>
                                                </TableCell>
                                                <TableCell>
                                                    <div className="flex flex-col">
                                                        <span className="text-xs font-bold text-white/70">Kalshi</span>
                                                        <span className="text-[10px] font-mono text-emerald-400/60">${(spread.kalshi_price / 100).toFixed(2)}</span>
                                                    </div>
                                                </TableCell>
                                                <TableCell>
                                                    <div className="flex flex-col">
                                                        <span className="text-xs font-bold text-white/70">Polymarket</span>
                                                        <span className="text-[10px] font-mono text-emerald-400/60">${(spread.poly_price / 100).toFixed(2)}</span>
                                                    </div>
                                                </TableCell>
                                                <TableCell>
                                                    <div className="flex flex-col">
                                                        <span className="text-xs font-bold text-white/90">
                                                            {spread.max_volume ? spread.max_volume.toLocaleString() : "-"}
                                                        </span>
                                                        <span className="text-[9px] text-white/30 font-mono">contracts</span>
                                                    </div>
                                                </TableCell>
                                                <TableCell className="text-right">
                                                    <div className="flex justify-end gap-2">
                                                        <a
                                                            href={spread.kalshi_url}
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                            className="h-8 w-8 rounded-lg bg-white/5 border border-white/5 flex items-center justify-center hover:bg-white/10 hover:border-white/10 transition-all text-white/40 hover:text-white"
                                                            title="Open Kalshi"
                                                        >
                                                            K
                                                        </a>
                                                        <a
                                                            href={spread.poly_url}
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                            className="h-8 w-8 rounded-lg bg-white/5 border border-white/5 flex items-center justify-center hover:bg-white/10 hover:border-white/10 transition-all text-white/40 hover:text-white"
                                                            title="Open Polymarket"
                                                        >
                                                            P
                                                        </a>
                                                        <button
                                                            onClick={() => {
                                                                window.open(spread.kalshi_url, '_blank')
                                                                window.open(spread.poly_url, '_blank')
                                                            }}
                                                            className="px-3 h-8 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-[10px] font-bold transition-all flex items-center gap-1.5 shadow-lg shadow-emerald-600/20"
                                                        >
                                                            Execute Both <ArrowUpRight className="h-3 w-3" />
                                                        </button>
                                                        {onTrack && (
                                                            <button
                                                                onClick={() => onTrack({
                                                                    asset: spread.asset,
                                                                    priceDirection: "Up", // Default for spreads
                                                                    polyPrice: spread.poly_price / 100,
                                                                    kalshiPrice: spread.kalshi_price / 100,
                                                                    expirationHour: (window as any)._formatExpiration ? (window as any)._formatExpiration(spread.expiry) : new Date(spread.expiry).toLocaleTimeString()
                                                                })}
                                                                className="px-3 h-8 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 text-white/60 hover:text-white text-[10px] font-bold transition-all flex items-center gap-1.5"
                                                                title="Track this arbitrage"
                                                            >
                                                                Track
                                                            </button>
                                                        )}
                                                    </div>
                                                </TableCell>
                                            </TableRow>
                                        )
                                    })}
                                </TableBody>
                            </Table>
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    )
}

function ArrowUpRight(props: any) {
    return (
        <svg
            {...props}
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
        >
            <path d="M7 7h10v10" />
            <path d="M7 17 17 7" />
        </svg>
    )
}
