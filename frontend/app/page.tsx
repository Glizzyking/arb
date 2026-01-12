"use client"

import { useEffect, useState, useRef, Suspense } from "react"
import { useSearchParams } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { AlertCircle, TrendingUp, ExternalLink } from "lucide-react"
import { TabNavigation } from "@/components/TabNavigation"
import { AddTokenModal, CustomToken } from "@/components/AddTokenModal"
import { Header } from "@/components/Header"
import { PositiveEVPage } from "@/components/PositiveEVPage"
import { CalculatorsPage } from "@/components/CalculatorsPage"
import { TrackerPage } from "@/components/TrackerPage"
import { SettingsModal } from "@/components/SettingsModal"
import { AuthModal } from "@/components/AuthModal"
import LoginPage from "@/components/LoginPage"
import { supabase } from "@/lib/supabase"
import { cn } from "@/lib/utils"

interface MarketData {
  timestamp: string
  asset?: string
  polymarket: {
    price_to_beat: number
    current_price: number
    prices: {
      Up: number
      Down: number
    }
    slug: string
    url: string
  }
  kalshi: {
    event_ticker: string
    current_price: number
    markets: Array<{
      strike: number
      yes_ask: number
      no_ask: number
      subtitle: string
    }>
    url: string
  }
  checks: Array<{
    kalshi_strike: number
    type: string
    poly_leg: string
    kalshi_leg: string
    poly_cost: number
    kalshi_cost: number
    total_cost: number
    is_arbitrage: boolean
    margin: number
  }>
  opportunities: Array<any>
  errors: string[]
}

interface Opportunity {
  margin: number
  poly_leg: string
  poly_cost: number
  kalshi_leg: string
  kalshi_strike: number
  kalshi_cost: number
  total_cost: number
  polymarket_url: string
  kalshi_url: string
}

// Preset assets with their display names
const PRESET_ASSETS = [
  { symbol: "BTC", name: "Bitcoin" },
  { symbol: "ETH", name: "Ethereum" },
  { symbol: "XRP", name: "XRP" },
  { symbol: "SOL", name: "Solana" },
]

const CUSTOM_TOKENS_KEY = "custom_arb_tokens"

function Dashboard() {
  const [data, setData] = useState<MarketData | null>(null)
  const [loading, setLoading] = useState(true)
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date())
  const [activeAsset, setActiveAsset] = useState("BTC")
  const [customTokens, setCustomTokens] = useState<CustomToken[]>([])
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [topTab, setTopTab] = useState("home")
  const searchParams = useSearchParams()

  useEffect(() => {
    const tab = searchParams.get("tab")
    if (tab && ["home", "positive-ev", "calculators", "tracker"].includes(tab)) {
      setTopTab(tab)
    }
  }, [searchParams])
  const [isSettingsOpen, setIsSettingsOpen] = useState(false)
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false)
  const [user, setUser] = useState<any>(null)
  const [authLoading, setAuthLoading] = useState(true)

  // Refs to track current values and prevent stale closures
  const activeAssetRef = useRef(activeAsset)
  const customTokensRef = useRef(customTokens)
  const abortControllerRef = useRef<AbortController | null>(null)

  // Keep refs in sync with state
  useEffect(() => {
    activeAssetRef.current = activeAsset
  }, [activeAsset])

  useEffect(() => {
    customTokensRef.current = customTokens
  }, [customTokens])

  // Load custom tokens from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem(CUSTOM_TOKENS_KEY)
    if (saved) {
      try {
        setCustomTokens(JSON.parse(saved))
      } catch (e) {
        console.error("Failed to parse custom tokens", e)
      }
    }
  }, [])

  // Save custom tokens to localStorage when they change
  useEffect(() => {
    localStorage.setItem(CUSTOM_TOKENS_KEY, JSON.stringify(customTokens))
  }, [customTokens])

  // Auth Session Check
  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null)
      setAuthLoading(false)
    })

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null)
    })

    return () => subscription.unsubscribe()
  }, [])

  const fetchData = async (signal: AbortSignal, assetToFetch: string, tokensToCheck: CustomToken[]) => {
    try {
      // Check if this is a custom token
      const customToken = tokensToCheck.find(t => t.symbol === assetToFetch)

      let res
      if (customToken) {
        // Use POST endpoint for custom tokens
        res = await fetch("http://localhost:8000/arbitrage/custom", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            name: customToken.name,
            kalshi_series: customToken.kalshiTicker,
            polymarket_slug_prefix: customToken.polymarketSlug
          }),
          signal
        })
      } else {
        // Use GET endpoint for preset assets
        res = await fetch(`http://localhost:8000/arbitrage?asset=${assetToFetch}`, { signal })
      }

      // Check if request was aborted or asset changed during fetch
      if (signal.aborted || activeAssetRef.current !== assetToFetch) {
        return // Discard stale response
      }

      const json = await res.json()
      setData(json)
      setLastUpdated(new Date())
      setLoading(false)
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        // Request was aborted, ignore
        return
      }
      console.error("Failed to fetch data", err)
    }
  }

  useEffect(() => {
    // Clear data and show loading when switching assets
    setData(null)
    setLoading(true)

    let socket: WebSocket | null = null
    let retryTimeout: NodeJS.Timeout
    let fallbackInterval: NodeJS.Timeout
    let wsConnected = false

    // Fallback: Use REST API if WebSocket isn't providing data
    const startFallback = () => {
      fallbackInterval = setInterval(async () => {
        if (wsConnected) return // Skip if WS is working

        try {
          const res = await fetch(`http://localhost:8000/arbitrage?asset=${activeAssetRef.current}`)
          const json = await res.json()
          if (json.asset === activeAssetRef.current) {
            setData(json)
            setLastUpdated(new Date())
            setLoading(false)
          }
        } catch (err) {
          console.error("Fallback fetch error:", err)
        }
      }, 1000)
    }

    const connectWS = () => {
      socket = new WebSocket("ws://localhost:8000/ws/arbitrage")

      socket.onopen = () => {
        console.log("WebSocket connected, subscribing to:", activeAsset)
        socket?.send(JSON.stringify({ type: "subscribe", asset: activeAsset }))
      }

      socket.onmessage = (event) => {
        try {
          const json = JSON.parse(event.data)
          if (json.type === "ping") return // Ignore pings

          // Check if data is for the current active asset
          if (json.asset === activeAssetRef.current) {
            wsConnected = true
            setData(json)
            setLastUpdated(new Date())
            setLoading(false)
          }
        } catch (e) {
          console.error("WS message parse error:", e)
        }
      }

      socket.onclose = () => {
        console.log("WebSocket closed, retrying in 2s...")
        wsConnected = false
        retryTimeout = setTimeout(connectWS, 2000)
      }

      socket.onerror = (err) => {
        console.error("WebSocket error:", err)
        socket?.close()
      }
    }

    connectWS()

    // Start REST polling immediately as backup (don't wait)
    startFallback()


    // Cleanup
    return () => {
      if (socket) socket.close()
      if (retryTimeout) clearTimeout(retryTimeout)
      if (fallbackInterval) clearInterval(fallbackInterval)
    }
  }, [activeAsset])


  const handleBuyBoth = (opp: Opportunity) => {
    if (opp.polymarket_url) window.open(opp.polymarket_url, '_blank')
    if (opp.kalshi_url) window.open(opp.kalshi_url, '_blank')
  }

  const handleAddCustomToken = (token: CustomToken) => {
    setCustomTokens(prev => [...prev, token])
    setActiveAsset(token.symbol)
  }

  // Combine preset and custom assets for tabs
  const allAssets = [
    ...PRESET_ASSETS,
    ...customTokens.map(t => ({ symbol: t.symbol, name: t.name, isCustom: true }))
  ]

  if (authLoading) return <div className="flex items-center justify-center h-screen bg-black text-white">Initializing...</div>

  // TEMPORARILY DISABLED FOR TESTING - Uncomment to re-enable auth
  // if (!user) return <LoginPage onLoginSuccess={() => { }} />

  if (loading && !data) return <div className="flex items-center justify-center h-screen bg-black text-white">Loading Market Intelligence...</div>

  if (!data && topTab === "home") return <div className="p-8 text-white">No data available</div>

  const bestOpp: Opportunity | null = data?.opportunities.length
    ? data.opportunities.reduce((prev: Opportunity, current: Opportunity) => (prev.margin > current.margin) ? prev : current)
    : null

  return (
    <div className="flex flex-col min-h-screen bg-black">
      <Header
        activeTab={topTab}
        onTabChange={setTopTab}
        onSettingsClick={() => setIsSettingsOpen(true)}
      />

      <main className="flex-1 p-4 md:p-8">
        {topTab === "home" && data ? (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            {bestOpp && (
              <Card className="bg-gradient-to-br from-blue-600/20 via-blue-900/10 to-transparent border-blue-500/20 shadow-2xl overflow-hidden relative group">
                <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:scale-110 transition-transform duration-700">
                  <TrendingUp className="h-24 w-24 text-blue-400" />
                </div>
                <CardHeader className="pb-2">
                  <div className="flex items-center gap-2 text-blue-400">
                    <TrendingUp className="h-5 w-5" />
                    <CardTitle className="text-white">Optimal Arb Strategy</CardTitle>
                  </div>
                  <CardDescription className="text-white/40 font-medium">Risk-zero execution with maximized yield</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-col md:flex-row justify-between items-center gap-8 py-4">
                    <div className="text-center md:text-left">
                      <div className="text-xs text-white/40 uppercase tracking-widest font-bold mb-1">Net Margin</div>
                      <div className="text-5xl font-black text-white tracking-tighter">${bestOpp.margin.toFixed(3)}</div>
                      <div className="text-xs text-blue-400/80 font-semibold mt-1">per contract unit</div>
                    </div>

                    <div className="flex-1 bg-white/5 backdrop-blur-sm p-6 rounded-2xl border border-white/10 w-full">
                      <div className="flex justify-between items-center mb-4">
                        <span className="text-sm font-semibold text-white/60">Execution Plan</span>
                        <button
                          className="bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold px-4 py-2 rounded-lg transition-all duration-200 active:scale-95 shadow-lg shadow-blue-600/20"
                          onClick={() => handleBuyBoth(bestOpp)}
                        >
                          Execute Both Markets ↗
                        </button>
                      </div>
                      <div className="space-y-3">
                        <div className="flex justify-between text-sm">
                          <span className="text-white/80">Polymarket {bestOpp.poly_leg}</span>
                          <span className="font-mono text-white font-bold">${bestOpp.poly_cost.toFixed(3)}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-white/80">Kalshi {bestOpp.kalshi_leg} (${bestOpp.kalshi_strike.toLocaleString()})</span>
                          <span className="font-mono text-white font-bold">${bestOpp.kalshi_cost.toFixed(3)}</span>
                        </div>
                        <div className="pt-3 border-t border-white/5 flex justify-between">
                          <span className="text-sm font-bold text-white/40">Aggregated Entry</span>
                          <span className="text-lg font-black text-white">${bestOpp.total_cost.toFixed(3)}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
              <div className="flex items-center gap-3">
                <h1 className="text-3xl font-bold tracking-tight text-white">Market Intelligence</h1>
                <Badge variant="outline" className="animate-pulse bg-blue-500/10 text-blue-400 border-blue-500/20">
                  <span className="w-2 h-2 rounded-full bg-blue-500 mr-2"></span>
                  Live Data
                </Badge>
              </div>
              <div className="flex items-center gap-4 bg-white/5 px-4 py-2 rounded-xl border border-white/5">
                <div className="text-xs text-white/40 uppercase tracking-widest font-semibold">Discovery</div>
                <div className="text-sm font-medium text-white/80">
                  Refreshed: {lastUpdated.toLocaleTimeString()}
                </div>
              </div>
            </div>

            {/* Tab Navigation */}
            <TabNavigation
              assets={allAssets}
              activeAsset={activeAsset}
              onAssetChange={setActiveAsset}
              onAddCustom={() => setIsModalOpen(true)}
            />

            {data.errors.length > 0 && (
              <div className="bg-red-500/10 border border-red-500/20 text-red-400 px-4 py-3 rounded-2xl flex items-start gap-3">
                <AlertCircle className="h-5 w-5 mt-0.5" />
                <div>
                  <strong className="font-bold block mb-1">Errors Detected</strong>
                  <ul className="list-disc ml-5 text-sm opacity-80">
                    {data.errors.map((err, i) => (
                      <li key={i}>{err}</li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            {/* Best Opportunity Hero Card */}
            {bestOpp && (
              <Card className="bg-gradient-to-br from-blue-600/20 via-blue-900/10 to-transparent border-blue-500/20 shadow-2xl overflow-hidden relative group">
                <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:scale-110 transition-transform duration-700">
                  <TrendingUp className="h-24 w-24 text-blue-400" />
                </div>
                <CardHeader className="pb-2">
                  <div className="flex items-center gap-2 text-blue-400">
                    <TrendingUp className="h-5 w-5" />
                    <CardTitle className="text-white">Optimal Arb Strategy</CardTitle>
                  </div>
                  <CardDescription className="text-white/40 font-medium">Risk-zero execution with maximized yield</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-col md:flex-row justify-between items-center gap-8 py-4">
                    <div className="text-center md:text-left">
                      <div className="text-xs text-white/40 uppercase tracking-widest font-bold mb-1">Net Margin</div>
                      <div className="text-5xl font-black text-white tracking-tighter">${bestOpp.margin.toFixed(3)}</div>
                      <div className="text-xs text-blue-400/80 font-semibold mt-1">per contract unit</div>
                    </div>

                    <div className="flex-1 bg-white/5 backdrop-blur-sm p-6 rounded-2xl border border-white/10 w-full">
                      <div className="flex justify-between items-center mb-4">
                        <span className="text-sm font-semibold text-white/60">Execution Plan</span>
                        <button
                          className="bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold px-4 py-2 rounded-lg transition-all duration-200 active:scale-95 shadow-lg shadow-blue-600/20"
                          onClick={() => handleBuyBoth(bestOpp)}
                        >
                          Execute Both Markets ↗
                        </button>
                      </div>
                      <div className="space-y-3">
                        <div className="flex justify-between text-sm">
                          <span className="text-white/80">Polymarket {bestOpp.poly_leg}</span>
                          <span className="font-mono text-white font-bold">${bestOpp.poly_cost.toFixed(3)}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-white/80">Kalshi {bestOpp.kalshi_leg} (${bestOpp.kalshi_strike.toLocaleString()})</span>
                          <span className="font-mono text-white font-bold">${bestOpp.kalshi_cost.toFixed(3)}</span>
                        </div>
                        <div className="pt-3 border-t border-white/5 flex justify-between">
                          <span className="text-sm font-bold text-white/40">Aggregated Entry</span>
                          <span className="text-lg font-black text-white">${bestOpp.total_cost.toFixed(3)}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Polymarket Card */}
              {data.polymarket && (
                <Card className="bg-zinc-950 border-white/5">
                  <CardHeader>
                    <CardTitle className="text-white">Polymarket</CardTitle>
                    <CardDescription className="flex items-center gap-1.5 text-white/40">
                      Event:
                      <a
                        href={data.polymarket?.url || '#'}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-400 hover:text-blue-300 transition-colors flex items-center gap-1"
                      >
                        {data.polymarket?.slug || 'N/A'}
                        <ExternalLink className="h-3 w-3" />
                      </a>
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-5">
                      <div className="bg-white/5 border border-white/5 p-3 rounded-xl">
                        <div className="text-[10px] text-white/30 uppercase tracking-[0.2em] font-black text-center">Prediction Venue</div>
                      </div>

                      <div className="space-y-4">
                        <div className="space-y-1.5">
                          <div className="flex justify-between items-center text-xs font-bold text-white/60">
                            <span className="uppercase">UP CONTRACT</span>
                            <span className="font-mono text-white">${data.polymarket?.prices.Up?.toFixed(3) || 'N/A'}</span>
                          </div>
                          <Progress value={(data.polymarket?.prices.Up ?? 0) * 100} className="h-2.5 bg-white/5" indicatorClassName="bg-blue-500 rounded-full" />
                        </div>

                        <div className="space-y-1.5">
                          <div className="flex justify-between items-center text-xs font-bold text-white/60">
                            <span className="uppercase">DOWN CONTRACT</span>
                            <span className="font-mono text-white">${data.polymarket?.prices.Down?.toFixed(3) || 'N/A'}</span>
                          </div>
                          <Progress value={(data.polymarket?.prices.Down ?? 0) * 100} className="h-2.5 bg-white/5" indicatorClassName="bg-zinc-700 rounded-full" />
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Kalshi Card */}
              <Card className="bg-zinc-950 border-white/5">
                <CardHeader>
                  <CardTitle className="text-white">Kalshi</CardTitle>
                  <CardDescription className="flex items-center gap-1.5 text-white/40">
                    Market:
                    <a
                      href={data.kalshi?.url || '#'}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-400 hover:text-blue-300 transition-colors flex items-center gap-1"
                    >
                      {data.kalshi?.event_ticker || 'N/A'}
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-5">
                    <div className="bg-white/5 border border-white/5 p-3 rounded-xl text-center">
                      <div className="text-[10px] text-white/30 uppercase tracking-[0.2em] font-black">Trade Venue</div>
                    </div>

                    <div className="space-y-3 max-h-[180px] overflow-y-auto pr-2 custom-scrollbar">
                      {data.kalshi?.markets
                        .map((m, i) => (
                          <div key={i} className="text-sm border-b border-white/5 pb-3 last:border-0 group">
                            <div className="flex justify-between font-bold text-white/80 mb-2 group-hover:text-white transition-colors">
                              <span>{m.subtitle}</span>
                            </div>
                            <div className="flex items-center gap-3">
                              <div className="flex-1 h-1.5 bg-white/5 rounded-full overflow-hidden flex">
                                <div className="bg-blue-600 h-full border-r border-black/20" style={{ width: `${m.yes_ask}%` }}></div>
                                <div className="bg-zinc-800 h-full" style={{ width: `${m.no_ask}%` }}></div>
                              </div>
                              <div className="flex gap-2 text-[10px] font-black tracking-widest text-white/30 shrink-0">
                                <span>YES: {m.yes_ask}¢</span>
                                <span>NO: {m.no_ask}¢</span>
                              </div>
                            </div>
                          </div>
                        ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Arbitrage Checks Table */}
            <Card className="bg-zinc-950 border-white/5">
              <CardHeader>
                <CardTitle className="text-white">Arbitrage Analysis Matrix</CardTitle>
                <CardDescription className="text-white/40 font-medium">Cross-market strategy evaluation</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader className="bg-white/5">
                      <TableRow className="hover:bg-transparent border-white/10">
                        <TableHead className="text-white/60 font-bold uppercase tracking-widest text-[10px]">Strategy</TableHead>
                        <TableHead className="text-white/60 font-bold uppercase tracking-widest text-[10px]">Strike</TableHead>
                        <TableHead className="text-white/60 font-bold uppercase tracking-widest text-[10px]">Leg Configuration</TableHead>
                        <TableHead className="text-white/60 font-bold uppercase tracking-widest text-[10px] w-[25%]">Entry Cost</TableHead>
                        <TableHead className="text-right text-white/60 font-bold uppercase tracking-widest text-[10px]">Aggregated</TableHead>
                        <TableHead className="text-right text-white/60 font-bold uppercase tracking-widest text-[10px]">Liquidity Exit</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {data.checks.map((check, i) => {
                        const isProfitable = check.total_cost < 1.00
                        const percentCost = Math.min(check.total_cost * 100, 100)

                        return (
                          <TableRow key={i} className={cn("border-white/5 hover:bg-white/5 transition-colors", isProfitable ? "bg-blue-500/5 animate-pulse" : "")}>
                            <TableCell>
                              <Badge variant="outline" className={cn("text-[10px] border-white/10 text-white/60 px-2 py-0.5 whitespace-nowrap", isProfitable && "bg-blue-500/20 text-blue-400 border-blue-500/40")}>
                                {check.type.replace("Poly", "P").replace("Kalshi", "K")}
                              </Badge>
                            </TableCell>
                            <TableCell className="font-mono text-xs text-white/80 font-bold">
                              ${check.kalshi_strike.toLocaleString()}
                            </TableCell>
                            <TableCell className="text-[11px]">
                              <div className="flex flex-col gap-0.5 text-white/60">
                                <span>P-{check.poly_leg}</span>
                                <span>K-{check.kalshi_leg}</span>
                              </div>
                            </TableCell>
                            <TableCell>
                              <div className="space-y-1.5">
                                <div className="flex justify-between text-[10px] font-black text-white/30 tracking-tight">
                                  <span>${check.poly_cost.toFixed(3)} + ${check.kalshi_cost.toFixed(3)}</span>
                                  <span className={isProfitable ? "text-blue-400" : ""}>{Math.round(check.total_cost * 100)}%</span>
                                </div>
                                <Progress
                                  value={percentCost}
                                  className="h-1.5 bg-white/5"
                                  indicatorClassName={isProfitable ? "bg-blue-500" : "bg-white/10"}
                                />
                              </div>
                            </TableCell>
                            <TableCell className={cn("text-right font-mono font-black text-sm", isProfitable ? "text-white" : "text-white/40")}>
                              ${check.total_cost.toFixed(3)}
                            </TableCell>
                            <TableCell className="text-right">
                              {isProfitable ? (
                                <div className="flex flex-col items-end">
                                  <Badge className="bg-blue-600 hover:bg-blue-500 text-white font-black shadow-lg shadow-blue-600/30 border-none">
                                    +${check.margin.toFixed(3)}
                                  </Badge>
                                </div>
                              ) : (
                                <span className="text-white/10 text-xs font-black">—</span>
                              )}
                            </TableCell>
                          </TableRow>
                        )
                      })}
                    </TableBody>
                  </Table>
                </div>
              </CardContent>
            </Card>
          </div>
        ) : topTab === "positive-ev" ? (
          <PositiveEVPage />
        ) : topTab === "calculators" ? (
          <CalculatorsPage />
        ) : (
          <TrackerPage user={user} onRequireAuth={() => setIsAuthModalOpen(true)} />
        )}
      </main>

      {/* Modals */}
      <AddTokenModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onAdd={handleAddCustomToken}
      />
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        onOpenAuthModal={() => setIsAuthModalOpen(true)}
      />
      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        onAuthSuccess={() => { }}
      />
    </div>
  )
}
export default function DashboardPage() {
  return (
    <Suspense fallback={<div className="flex h-screen items-center justify-center text-white">Loading...</div>}>
      <Dashboard />
    </Suspense>
  )
}
