"use client"

import { X, Key, ShieldCheck, Save, User, LogOut, LogIn } from "lucide-react"
import { useState, useEffect } from "react"
import { supabase } from "@/lib/supabase"
import { User as SupabaseUser } from "@supabase/supabase-js"

interface SettingsModalProps {
    isOpen: boolean
    onClose: () => void
    onOpenAuthModal: () => void
}

export function SettingsModal({ isOpen, onClose, onOpenAuthModal }: SettingsModalProps) {
    const [kalshiKey, setKalshiKey] = useState("")
    const [polyKey, setPolyKey] = useState("")
    const [user, setUser] = useState<SupabaseUser | null>(null)
    const [loading, setLoading] = useState(false)

    useEffect(() => {
        const fetchUser = async () => {
            const { data: { user } } = await supabase.auth.getUser()
            setUser(user)
        }
        if (isOpen) {
            fetchUser()
            const savedKalshi = localStorage.getItem("kalshi_api_key")
            const savedPoly = localStorage.getItem("polymarket_api_key")
            if (savedKalshi) setKalshiKey(savedKalshi)
            if (savedPoly) setPolyKey(savedPoly)
        }
    }, [isOpen])

    const handleSave = () => {
        localStorage.setItem("kalshi_api_key", kalshiKey)
        localStorage.setItem("polymarket_api_key", polyKey)
        onClose()
    }

    const handleSignOut = async () => {
        setLoading(true)
        await supabase.auth.signOut()
        setUser(null)
        setLoading(false)
    }

    if (!isOpen) return null

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/60 backdrop-blur-md transition-opacity"
                onClick={onClose}
            />

            {/* Modal Content */}
            <div className="relative w-full max-w-md rounded-3xl border border-white/10 bg-zinc-950 p-8 shadow-2xl animate-in fade-in zoom-in duration-300">
                <div className="flex items-center justify-between mb-8">
                    <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-xl bg-blue-500/10 flex items-center justify-center border border-blue-500/20">
                            <ShieldCheck className="h-6 w-6 text-blue-400" />
                        </div>
                        <div>
                            <h2 className="text-xl font-bold text-white">Settings</h2>
                            <p className="text-xs text-white/40">Account & API Management</p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 rounded-lg hover:bg-white/5 text-white/40 hover:text-white transition-colors"
                    >
                        <X className="h-5 w-5" />
                    </button>
                </div>

                {/* Account Section */}
                <div className="mb-8 p-4 rounded-2xl bg-white/5 border border-white/5">
                    <div className="text-[10px] font-black text-white/30 uppercase tracking-widest mb-3">Account</div>
                    {user ? (
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <div className="h-10 w-10 rounded-full bg-indigo-500/20 flex items-center justify-center border border-indigo-500/30">
                                    <User className="h-5 w-5 text-indigo-400" />
                                </div>
                                <div>
                                    <div className="text-sm font-bold text-white truncate max-w-[180px]">{user.email}</div>
                                    <div className="text-[10px] text-green-400 font-bold uppercase tracking-widest">Signed In</div>
                                </div>
                            </div>
                            <button
                                onClick={handleSignOut}
                                disabled={loading}
                                className="flex items-center gap-2 px-3 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 rounded-lg text-xs font-bold transition-colors"
                            >
                                <LogOut className="h-3.5 w-3.5" />
                                Sign Out
                            </button>
                        </div>
                    ) : (
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <div className="h-10 w-10 rounded-full bg-white/5 flex items-center justify-center border border-white/10">
                                    <User className="h-5 w-5 text-white/20" />
                                </div>
                                <div>
                                    <div className="text-sm font-medium text-white/40">Not signed in</div>
                                    <div className="text-[10px] text-white/20 font-medium">Sign in to save positions</div>
                                </div>
                            </div>
                            <button
                                onClick={() => {
                                    onClose()
                                    onOpenAuthModal()
                                }}
                                className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-bold transition-colors shadow-lg shadow-blue-600/20"
                            >
                                <LogIn className="h-3.5 w-3.5" />
                                Sign In
                            </button>
                        </div>
                    )}
                </div>

                {/* API Keys Section */}
                <div className="space-y-6">
                    <div className="text-[10px] font-black text-white/30 uppercase tracking-widest">API Keys</div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium text-white/60 flex items-center gap-2">
                            <Key className="h-3.5 w-3.5" /> Kalshi API Key
                        </label>
                        <input
                            type="password"
                            value={kalshiKey}
                            onChange={(e) => setKalshiKey(e.target.value)}
                            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-blue-500/50 transition-colors"
                            placeholder="PASTE_YOUR_KALSHI_KEY"
                        />
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium text-white/60 flex items-center gap-2">
                            <Key className="h-3.5 w-3.5" /> Polymarket API Key
                        </label>
                        <input
                            type="password"
                            value={polyKey}
                            onChange={(e) => setPolyKey(e.target.value)}
                            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-blue-500/50 transition-colors"
                            placeholder="PASTE_YOUR_POLY_KEY"
                        />
                    </div>

                    <div className="pt-4">
                        <button
                            onClick={handleSave}
                            className="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 px-6 rounded-xl transition-all duration-200 flex items-center justify-center gap-2 shadow-lg shadow-blue-600/20"
                        >
                            <Save className="h-5 w-5" />
                            Save Configuration
                        </button>
                    </div>
                </div>

                <div className="mt-8 p-4 rounded-xl bg-yellow-500/5 border border-yellow-500/10">
                    <p className="text-[10px] leading-relaxed text-yellow-500/60 uppercase tracking-widest font-bold mb-1">Warning</p>
                    <p className="text-xs text-white/40 leading-relaxed">
                        Keys are stored locally in your browser and are never transmitted to our servers.
                    </p>
                </div>
            </div>
        </div>
    )
}
