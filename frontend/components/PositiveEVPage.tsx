"use client"

import { Zap } from "lucide-react"

export function PositiveEVPage() {
    return (
        <div className="flex flex-col items-center justify-center min-h-[60vh] text-center px-4">
            <div className="h-16 w-16 rounded-2xl bg-blue-500/10 flex items-center justify-center mb-6 border border-blue-500/20">
                <Zap className="h-8 w-8 text-blue-400 animate-pulse" />
            </div>
            <h1 className="text-3xl font-bold text-white mb-3">Positive EV Scanner</h1>
            <p className="text-white/40 max-w-md">
                This feature is currently under development. Stay tuned for real-time expected value analysis across all markets.
            </p>
            <div className="mt-8 px-6 py-2 rounded-full border border-white/5 bg-white/5 text-sm text-white/60">
                Coming Soon
            </div>
        </div>
    )
}
