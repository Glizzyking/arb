"use client"

import { useState } from "react"
import { supabase } from "@/lib/supabase"
import { X, Loader2, Zap, TrendingUp, Clock, Calendar as CalendarIcon } from "lucide-react"
import { format } from "date-fns"

interface AddPositionModalProps {
    isOpen: boolean
    onClose: () => void
    onSuccess: () => void
    selectedDate: Date
}

export function AddPositionModal({ isOpen, onClose, onSuccess, selectedDate }: AddPositionModalProps) {
    const getNextFullHour = () => {
        const now = new Date()
        const nextHour = new Date(now.getTime() + 60 * 60 * 1000)
        nextHour.setMinutes(0, 0, 0)
        return format(nextHour, "HH:mm")
    }

    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [expirationHour, setExpirationHour] = useState(getNextFullHour())
    const [asset, setAsset] = useState("BTC")

    const [polyPrice, setPolyPrice] = useState("")
    const [polyContracts, setPolyContracts] = useState("")

    const [kalshiPrice, setKalshiPrice] = useState("")
    const [kalshiContracts, setKalshiContracts] = useState("")

    if (!isOpen) return null

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        setError(null)

        try {
            const { data: { user } } = await supabase.auth.getUser()
            if (!user) throw new Error("Not authenticated")

            // 1. Create Position
            const { data: position, error: posError } = await supabase
                .from('positions')
                .insert({
                    user_id: user.id,
                    calendar_date: format(selectedDate, 'yyyy-MM-dd'),
                    expiration_hour: expirationHour,
                    asset: asset,
                    status: 'pending'
                })
                .select()
                .single()

            if (posError) throw posError

            // 2. Create Legs
            const legs = [
                {
                    position_id: position.id,
                    network: 'Polymarket',
                    entry_price: parseFloat(polyPrice),
                    contracts: parseFloat(polyContracts)
                },
                {
                    position_id: position.id,
                    network: 'Kalshi',
                    entry_price: parseFloat(kalshiPrice),
                    contracts: parseFloat(kalshiContracts)
                }
            ]

            const { error: legsError } = await supabase
                .from('position_legs')
                .insert(legs)

            if (legsError) throw legsError

            onSuccess()
            onClose()
        } catch (err: any) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
            <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />

            <div className="relative w-full max-w-xl bg-zinc-950 border border-white/10 rounded-3xl shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200">
                <div className="p-6 border-b border-white/5 flex items-center justify-between bg-white/[0.02]">
                    <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-xl bg-blue-600 flex items-center justify-center">
                            <Plus className="h-6 w-6 text-white" />
                        </div>
                        <div>
                            <h2 className="text-xl font-bold text-white tracking-tight">Add Arbitrage Position</h2>
                            <p className="text-xs text-white/40 uppercase tracking-widest font-medium">Log your cross-market entry</p>
                        </div>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-white/5 rounded-full transition-colors">
                        <X className="h-5 w-5 text-white/40" />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="p-8 space-y-8">
                    {error && (
                        <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm text-center font-medium">
                            {error}
                        </div>
                    )}

                    {/* Global Settings */}
                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <label className="text-xs font-bold text-white/20 uppercase tracking-widest ml-1">Execution Day</label>
                            <div className="flex items-center gap-3 bg-white/5 border border-white/5 rounded-2xl p-3">
                                <CalendarIcon className="h-4 w-4 text-white/40" />
                                <span className="text-sm font-bold text-white/80">{format(selectedDate, 'MMM d, yyyy')}</span>
                            </div>
                        </div>
                        <div className="space-y-2">
                            <label className="text-xs font-bold text-white/20 uppercase tracking-widest ml-1">Expiration</label>
                            <div className="relative group">
                                <Clock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-white/20 group-focus-within:text-blue-400 transition-colors" />
                                <input
                                    type="time"
                                    value={expirationHour}
                                    onChange={(e) => setExpirationHour(e.target.value)}
                                    className="w-full bg-white/5 border border-white/5 rounded-2xl p-3 pl-10 text-sm text-white focus:outline-none focus:border-blue-500/50 transition-all font-bold"
                                    required
                                />
                            </div>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-8">
                        {/* Polymarket Leg */}
                        <div className="space-y-4">
                            <div className="flex items-center gap-2 pb-2 border-b border-white/5">
                                <Zap className="h-4 w-4 text-blue-400" />
                                <span className="text-sm font-black text-white uppercase tracking-tighter">Polymarket Leg</span>
                            </div>
                            <div className="space-y-4">
                                <div className="space-y-1.5">
                                    <label className="text-[10px] font-bold text-white/20 uppercase tracking-widest ml-1">Entry Price</label>
                                    <input
                                        type="number"
                                        step="0.0001"
                                        value={polyPrice}
                                        onChange={(e) => setPolyPrice(e.target.value)}
                                        placeholder="0.3500"
                                        className="w-full bg-white/5 border border-white/5 rounded-xl p-3 text-sm text-white placeholder:text-white/10 font-mono"
                                        required
                                    />
                                </div>
                                <div className="space-y-1.5">
                                    <label className="text-[10px] font-bold text-white/20 uppercase tracking-widest ml-1">Contracts</label>
                                    <input
                                        type="number"
                                        value={polyContracts}
                                        onChange={(e) => setPolyContracts(e.target.value)}
                                        placeholder="100"
                                        className="w-full bg-white/5 border border-white/5 rounded-xl p-3 text-sm text-white placeholder:text-white/10 font-mono"
                                        required
                                    />
                                </div>
                            </div>
                        </div>

                        {/* Kalshi Leg */}
                        <div className="space-y-4">
                            <div className="flex items-center gap-2 pb-2 border-b border-white/5">
                                <TrendingUp className="h-4 w-4 text-indigo-400" />
                                <span className="text-sm font-black text-white uppercase tracking-tighter">Kalshi Leg</span>
                            </div>
                            <div className="space-y-4">
                                <div className="space-y-1.5">
                                    <label className="text-[10px] font-bold text-white/20 uppercase tracking-widest ml-1">Entry Price</label>
                                    <input
                                        type="number"
                                        step="0.01"
                                        value={kalshiPrice}
                                        onChange={(e) => setKalshiPrice(e.target.value)}
                                        placeholder="0.35"
                                        className="w-full bg-white/5 border border-white/5 rounded-xl p-3 text-sm text-white placeholder:text-white/10 font-mono"
                                        required
                                    />
                                </div>
                                <div className="space-y-1.5">
                                    <label className="text-[10px] font-bold text-white/20 uppercase tracking-widest ml-1">Contracts</label>
                                    <input
                                        type="number"
                                        value={kalshiContracts}
                                        onChange={(e) => setKalshiContracts(e.target.value)}
                                        placeholder="100"
                                        className="w-full bg-white/5 border border-white/5 rounded-xl p-3 text-sm text-white placeholder:text-white/10 font-mono"
                                        required
                                    />
                                </div>
                            </div>
                        </div>
                    </div>
                    {/* Asset Selection */}
                    <div className="space-y-2">
                        <label className="text-xs font-bold text-white/20 uppercase tracking-widest ml-1">Trading Asset</label>
                        <select
                            value={asset}
                            onChange={(e) => setAsset(e.target.value)}
                            className="w-full bg-white/5 border border-white/5 rounded-2xl p-4 text-sm text-white focus:outline-none focus:border-blue-500/50 transition-all font-bold appearance-none cursor-pointer"
                        >
                            <option value="BTC" className="bg-zinc-950 text-white">Bitcoin (BTC)</option>
                            <option value="ETH" className="bg-zinc-950 text-white">Ethereum (ETH)</option>
                            <option value="XRP" className="bg-zinc-950 text-white">XRP</option>
                            <option value="SOL" className="bg-zinc-950 text-white">Solana (SOL)</option>
                        </select>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-4 rounded-2xl shadow-xl shadow-blue-600/20 transition-all active:scale-[0.98] flex items-center justify-center gap-3"
                    >
                        {loading ? (
                            <Loader2 className="h-5 w-5 animate-spin" />
                        ) : (
                            <>
                                <TrendingUp className="h-5 w-5" />
                                Save Position to Ledger
                            </>
                        )}
                    </button>
                </form>
            </div>
        </div>
    )
}

function Plus({ className }: { className?: string }) {
    return (
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}><path d="M5 12h14" /><path d="M12 5v14" /></svg>
    )
}
