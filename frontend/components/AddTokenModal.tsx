"use client"

import { useState } from "react"
import { X } from "lucide-react"

interface AddTokenModalProps {
    isOpen: boolean
    onClose: () => void
    onAdd: (token: CustomToken) => void
}

export interface CustomToken {
    symbol: string
    name: string
    polymarketSlug: string
    kalshiTicker: string
}

export function AddTokenModal({ isOpen, onClose, onAdd }: AddTokenModalProps) {
    const [name, setName] = useState("")
    const [polymarketSlug, setPolymarketSlug] = useState("")
    const [kalshiTicker, setKalshiTicker] = useState("")

    if (!isOpen) return null

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()

        if (!name || !polymarketSlug || !kalshiTicker) {
            alert("Please fill in all required fields")
            return
        }

        const token: CustomToken = {
            symbol: name.toUpperCase().replace(/\s+/g, "_"),
            name,
            polymarketSlug,
            kalshiTicker
        }

        onAdd(token)

        // Reset form
        setName("")
        setPolymarketSlug("")
        setKalshiTicker("")
        onClose()
    }

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white rounded-xl shadow-2xl w-full max-w-md mx-4 overflow-hidden">
                {/* Header */}
                <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
                    <h2 className="text-lg font-semibold text-slate-900">Add Custom Token</h2>
                    <button
                        onClick={onClose}
                        className="p-1 rounded-lg hover:bg-slate-100 transition-colors"
                    >
                        <X className="h-5 w-5 text-slate-500" />
                    </button>
                </div>

                {/* Form */}
                <form onSubmit={handleSubmit} className="p-6 space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">
                            Token Name *
                        </label>
                        <input
                            type="text"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            placeholder="e.g., Dogecoin"
                            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">
                            Polymarket Slug Prefix *
                        </label>
                        <input
                            type="text"
                            value={polymarketSlug}
                            onChange={(e) => setPolymarketSlug(e.target.value)}
                            placeholder="e.g., dogecoin-up-or-down"
                            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            required
                        />
                        <p className="mt-1 text-xs text-slate-500">
                            The slug prefix from Polymarket event URLs
                        </p>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">
                            Kalshi Series Ticker *
                        </label>
                        <input
                            type="text"
                            value={kalshiTicker}
                            onChange={(e) => setKalshiTicker(e.target.value)}
                            placeholder="e.g., KXDOGEDAILY"
                            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            required
                        />
                        <p className="mt-1 text-xs text-slate-500">
                            The Kalshi event series ticker
                        </p>
                    </div>


                    {/* Actions */}
                    <div className="flex gap-3 pt-4">
                        <button
                            type="button"
                            onClick={onClose}
                            className="flex-1 px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                        >
                            Add Token
                        </button>
                    </div>
                </form>
            </div>
        </div>
    )
}
