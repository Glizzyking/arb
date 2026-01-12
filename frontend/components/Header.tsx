"use client"

import { Settings, Home, Zap, Calculator, Calendar } from "lucide-react"
import { cn } from "@/lib/utils"

interface HeaderProps {
    activeTab: string
    onTabChange: (tab: string) => void
    onSettingsClick: () => void
}

export function Header({ activeTab, onTabChange, onSettingsClick }: HeaderProps) {
    const tabs = [
        { id: "home", label: "Home Page", icon: Home },
        { id: "positive-ev", label: "Positive EV", icon: Zap },
        { id: "calculators", label: "Calculators", icon: Calculator },
        { id: "tracker", label: "Tracker", icon: Calendar },
    ]

    return (
        <header className="sticky top-0 z-50 w-full border-b border-white/5 bg-black/80 backdrop-blur-xl">
            <div className="container mx-auto flex h-16 items-center justify-between px-4">
                {/* Logo / Title */}
                <div className="flex items-center gap-2">
                    <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
                        <Zap className="h-5 w-5 text-white" />
                    </div>
                    <span className="text-lg font-bold bg-gradient-to-r from-white to-white/60 bg-clip-text text-transparent hidden sm:block">
                        Arb Bot
                    </span>
                </div>

                {/* Navigation Tabs */}
                <nav className="flex items-center gap-1 bg-white/5 p-1 rounded-xl">
                    {tabs.map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => onTabChange(tab.id)}
                            className={cn(
                                "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200",
                                activeTab === tab.id
                                    ? "bg-white/10 text-white shadow-[0_0_15px_rgba(255,255,255,0.05)]"
                                    : "text-white/40 hover:text-white/70 hover:bg-white/5"
                            )}
                        >
                            <tab.icon className={cn("h-4 w-4", activeTab === tab.id ? "text-blue-400" : "text-white/20")} />
                            {tab.label}
                        </button>
                    ))}
                </nav>

                {/* Settings Button */}
                <button
                    onClick={onSettingsClick}
                    className="p-2.5 rounded-xl border border-white/5 bg-white/5 text-white/60 hover:text-white hover:bg-white/10 hover:border-white/10 transition-all duration-200 group"
                    title="Settings"
                >
                    <Settings className="h-5 w-5 group-hover:rotate-45 transition-transform duration-300" />
                </button>
            </div>
        </header>
    )
}
