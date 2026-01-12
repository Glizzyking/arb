"use client"

import { Plus } from "lucide-react"

interface TabNavigationProps {
    assets: Array<{ symbol: string; name: string; isCustom?: boolean }>
    activeAsset: string
    onAssetChange: (symbol: string) => void
    onAddCustom: () => void
}

export function TabNavigation({
    assets,
    activeAsset,
    onAssetChange,
    onAddCustom
}: TabNavigationProps) {
    return (
        <div className="flex items-center gap-1 mb-6 border-b border-slate-200 pb-2 overflow-x-auto">
            {assets.map((asset) => (
                <button
                    key={asset.symbol}
                    onClick={() => onAssetChange(asset.symbol)}
                    className={`
            px-4 py-2 rounded-t-lg font-medium text-sm transition-all whitespace-nowrap
            ${activeAsset === asset.symbol
                            ? "bg-white text-slate-900 border border-b-white border-slate-200 -mb-[1px]"
                            : "text-slate-500 hover:text-slate-700 hover:bg-slate-100"
                        }
            ${asset.isCustom ? "italic" : ""}
          `}
                >
                    {asset.name}
                    {asset.isCustom && (
                        <span className="ml-1 text-xs text-slate-400">(custom)</span>
                    )}
                </button>
            ))}

            {/* Add Custom Token Button */}
            <button
                onClick={onAddCustom}
                className="p-2 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
                title="Add custom token"
            >
                <Plus className="h-5 w-5" />
            </button>
        </div>
    )
}
