"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ChevronLeft, ChevronRight, Plus, Calendar as CalendarIcon, Filter, X, CheckCircle2, AlertCircle } from "lucide-react"
import {
    format,
    addMonths,
    subMonths,
    startOfMonth,
    endOfMonth,
    startOfWeek,
    endOfWeek,
    eachDayOfInterval,
    isSameMonth,
    isSameDay,
    isToday
} from "date-fns"
import { supabase } from "@/lib/supabase"
import { cn } from "@/lib/utils"
import { AddPositionModal } from "./AddPositionModal"

interface PositionLeg {
    id: string
    network: string
    entry_price: number
    contracts: number
}

interface Position {
    id: string
    calendar_date: string
    expiration_hour: string
    asset: string
    status: string
    position_legs: PositionLeg[]
}

interface TrackerPageProps {
    user?: any
    onRequireAuth?: () => void
}

export function TrackerPage({ user, onRequireAuth }: TrackerPageProps) {
    const [currentMonth, setCurrentMonth] = useState(new Date())
    const [selectedDate, setSelectedDate] = useState(new Date())
    const [isPanelOpen, setIsPanelOpen] = useState(false)
    const [isAddModalOpen, setIsAddModalOpen] = useState(false)
    const [positions, setPositions] = useState<Position[]>([])
    const [refreshTrigger, setRefreshTrigger] = useState(0)

    // Month Navigation
    const nextMonth = () => setCurrentMonth(addMonths(currentMonth, 1))
    const prevMonth = () => setCurrentMonth(subMonths(currentMonth, 1))

    // Auth-gated add position handler
    const handleAddPosition = () => {
        if (!user && onRequireAuth) {
            onRequireAuth()
            return
        }
        setIsAddModalOpen(true)
    }

    // Calendar Calculations
    const monthStart = startOfMonth(currentMonth)
    const monthEnd = endOfMonth(monthStart)
    const startDate = startOfWeek(monthStart)
    const endDate = endOfWeek(monthEnd)
    const calendarDays = eachDayOfInterval({ start: startDate, end: endDate })

    // Fetch positions for the current month
    useEffect(() => {
        const fetchPositions = async () => {
            const { data, error } = await supabase
                .from('positions')
                .select('*, position_legs(*)')
                .gte('calendar_date', format(monthStart, 'yyyy-MM-01'))
                .lte('calendar_date', format(monthEnd, 'yyyy-MM-dd'))

            if (data) setPositions(data as Position[])
            if (error) console.error("Error fetching positions:", error)
        }
        fetchPositions()
    }, [currentMonth, refreshTrigger])

    const handleDayClick = (day: Date) => {
        setSelectedDate(day)
        setIsPanelOpen(true)
    }

    const resolvePosition = async (positionId: string, outcome: string) => {
        const { error } = await supabase
            .from('positions')
            .update({ status: outcome })
            .eq('id', positionId)

        if (error) console.error("Error resolving position:", error)
        else setRefreshTrigger(prev => prev + 1)
    }

    const calculateProfit = (pos: Position) => {
        if (pos.status === 'pending') return 0
        const polyLeg = pos.position_legs.find(l => l.network === 'Polymarket')
        const kalshiLeg = pos.position_legs.find(l => l.network === 'Kalshi')
        if (!polyLeg || !kalshiLeg) return 0

        const totalCost = (polyLeg.entry_price * polyLeg.contracts) + (kalshiLeg.entry_price * kalshiLeg.contracts)

        if (pos.status === 'polymarket_won') return (polyLeg.contracts * 1.0) - totalCost
        if (pos.status === 'kalshi_won') return (kalshiLeg.contracts * 1.0) - totalCost
        if (pos.status === 'both_lost') return -totalCost
        return 0
    }

    const totalProfit = positions.reduce((acc, pos) => acc + calculateProfit(pos), 0)

    return (
        <div className="flex gap-6 h-[calc(100vh-140px)] animate-in fade-in slide-in-from-bottom-4 duration-700">
            {/* Main Content */}
            <div className="flex-1 space-y-6 overflow-y-auto pr-2 custom-scrollbar">
                {/* Header Summary */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <Card className="bg-zinc-950 border-white/5">
                        <CardContent className="pt-6">
                            <div className="text-xs text-white/40 uppercase tracking-widest font-bold mb-1">Total Positions</div>
                            <div className="text-2xl font-bold text-white">{positions.length}</div>
                        </CardContent>
                    </Card>
                    <Card className="bg-zinc-950 border-white/5">
                        <CardContent className="pt-6">
                            <div className="text-xs text-white/40 uppercase tracking-widest font-bold mb-1">Resolved</div>
                            <div className="text-2xl font-bold text-green-500">
                                {positions.filter(p => p.status !== 'pending').length}
                            </div>
                        </CardContent>
                    </Card>
                    <Card className="bg-zinc-950 border-white/5">
                        <CardContent className="pt-6">
                            <div className="text-xs text-white/40 uppercase tracking-widest font-bold mb-1">Pending</div>
                            <div className="text-2xl font-bold text-blue-500">
                                {positions.filter(p => p.status === 'pending').length}
                            </div>
                        </CardContent>
                    </Card>
                    <Card className={cn(
                        "bg-gradient-to-br border-blue-500/20 shadow-lg",
                        totalProfit >= 0 ? "from-green-600/20 to-transparent border-green-500/20" : "from-red-600/20 to-transparent border-red-500/20"
                    )}>
                        <CardContent className="pt-6">
                            <div className="text-xs text-blue-400/60 uppercase tracking-widest font-bold mb-1">Total Profit</div>
                            <div className={cn(
                                "text-2xl font-bold tracking-tighter",
                                totalProfit >= 0 ? "text-green-400" : "text-red-400"
                            )}>
                                {totalProfit >= 0 ? `+$${totalProfit.toFixed(2)}` : `-$${Math.abs(totalProfit).toFixed(2)}`}
                            </div>
                        </CardContent>
                    </Card>
                </div>

                {/* Calendar Controls */}
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                            <CalendarIcon className="h-6 w-6 text-blue-500" />
                            {format(currentMonth, 'MMMM yyyy')}
                        </h2>
                        <div className="flex items-center gap-1 bg-white/5 p-1 rounded-lg border border-white/5">
                            <button
                                onClick={prevMonth}
                                className="p-1.5 hover:bg-white/5 rounded-md text-white/60 hover:text-white transition-colors"
                            >
                                <ChevronLeft className="h-4 w-4" />
                            </button>
                            <button
                                onClick={nextMonth}
                                className="p-1.5 hover:bg-white/5 rounded-md text-white/60 hover:text-white transition-colors"
                            >
                                <ChevronRight className="h-4 w-4" />
                            </button>
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        <button className="flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-sm font-medium text-white/60 hover:text-white hover:bg-white/10 transition-all">
                            <Filter className="h-4 w-4" />
                            Filters
                        </button>
                        <button
                            onClick={handleAddPosition}
                            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-sm font-bold shadow-lg shadow-blue-600/20 transition-all active:scale-95"
                        >
                            <Plus className="h-4 w-4" />
                            Add Position
                        </button>
                    </div>
                </div>

                {/* Calendar Grid */}
                <Card className="bg-zinc-950 border-white/5 overflow-hidden font-sans">
                    <CardContent className="p-0">
                        <div className="grid grid-cols-7 border-b border-white/5">
                            {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
                                <div key={day} className="py-4 text-center text-xs font-bold text-white/20 uppercase tracking-widest">
                                    {day}
                                </div>
                            ))}
                        </div>
                        <div className="grid grid-cols-7 border-collapse">
                            {calendarDays.map((day, idx) => {
                                const dayPositions = positions.filter(p => p.calendar_date === format(day, 'yyyy-MM-dd'))
                                const isSelected = isSameDay(day, selectedDate)

                                return (
                                    <div
                                        key={idx}
                                        onClick={() => handleDayClick(day)}
                                        className={cn(
                                            "min-h-[120px] border-r border-b border-white/5 p-3 transition-all cursor-pointer group relative",
                                            !isSameMonth(day, monthStart) && "opacity-20 bg-white/[0.01]",
                                            isSelected && "bg-blue-500/10",
                                            !isSelected && "hover:bg-white/5"
                                        )}
                                    >
                                        <div className="flex justify-between items-start mb-2">
                                            <span className={cn(
                                                "text-sm font-bold transition-colors",
                                                isToday(day) ? "text-blue-400" : "text-white/40 group-hover:text-white/80",
                                                isSelected && "text-blue-400"
                                            )}>
                                                {format(day, 'd')}
                                            </span>
                                            {dayPositions.length > 0 && (
                                                <div className="flex flex-col gap-1 items-end">
                                                    <div className="h-2 w-2 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.5)]" />
                                                    <span className="text-[10px] font-black text-white/40">{dayPositions.length} Pos</span>
                                                </div>
                                            )}
                                        </div>

                                        {/* Day Previews */}
                                        <div className="space-y-1 overflow-hidden">
                                            {dayPositions.slice(0, 2).map((pos, pIdx) => (
                                                <div key={pIdx} className={cn(
                                                    "text-[10px] px-1.5 py-0.5 rounded truncate font-medium",
                                                    pos.status === 'pending' ? "bg-white/5 text-white/60" : "bg-green-500/10 text-green-400"
                                                )}>
                                                    {pos.asset} • {pos.expiration_hour} • {pos.status.replace('_won', '').replace('both_', 'L')}
                                                </div>
                                            ))}
                                            {dayPositions.length > 2 && (
                                                <div className="text-[9px] text-white/20 font-bold px-1.5">+{dayPositions.length - 2} more</div>
                                            )}
                                        </div>
                                    </div>
                                )
                            })}
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Side Panel (Day Detail) */}
            {isPanelOpen && (
                <div className="w-[450px] bg-zinc-950 border-l border-white/10 flex flex-col animate-in slide-in-from-right-4 duration-300">
                    <div className="p-6 border-b border-white/10 flex items-center justify-between">
                        <div>
                            <h3 className="text-xl font-bold text-white">{format(selectedDate, 'MMMM d, yyyy')}</h3>
                            <p className="text-sm text-white/40">Daily Position Ledger</p>
                        </div>
                        <button
                            onClick={() => setIsPanelOpen(false)}
                            className="p-2 hover:bg-white/5 rounded-xl text-white/40 hover:text-white transition-colors"
                        >
                            <X className="h-5 w-5" />
                        </button>
                    </div>

                    <div className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar">
                        {positions.filter(p => p.calendar_date === format(selectedDate, 'yyyy-MM-dd')).length === 0 ? (
                            <div className="flex flex-col items-center justify-center h-40 text-center space-y-3 opacity-20">
                                <Plus className="h-8 w-8" />
                                <p className="text-xs font-bold uppercase tracking-widest text-white">No positions tracked</p>
                            </div>
                        ) : (
                            positions.filter(p => p.calendar_date === format(selectedDate, 'yyyy-MM-dd')).map((pos, idx) => {
                                const profit = calculateProfit(pos)
                                return (
                                    <div key={idx} className="space-y-3">
                                        <Card className="bg-white/5 border-white/5 hover:border-white/10 transition-colors overflow-hidden group">
                                            <CardContent className="p-4">
                                                <div className="flex justify-between items-center mb-4">
                                                    <div className="flex items-center gap-2">
                                                        <span className="text-xs font-black text-white bg-white/10 px-2 py-1 rounded uppercase">{pos.asset}</span>
                                                        <span className="text-xs font-black text-blue-400 bg-blue-400/10 px-2 py-1 rounded uppercase">{pos.expiration_hour}</span>
                                                        {pos.status !== 'pending' && (
                                                            <span className={cn(
                                                                "text-[10px] font-bold px-2 py-0.5 rounded flex items-center gap-1",
                                                                profit >= 0 ? "bg-green-500/10 text-green-400" : "bg-red-500/10 text-red-400"
                                                            )}>
                                                                <CheckCircle2 className="h-3 w-3" />
                                                                {profit >= 0 ? `+$${profit.toFixed(2)}` : `-$${Math.abs(profit).toFixed(2)}`}
                                                            </span>
                                                        )}
                                                    </div>
                                                    <Badge className={cn(
                                                        "capitalize",
                                                        pos.status === 'pending' ? "bg-zinc-800 text-white/40" : "bg-green-600 text-white"
                                                    )}>{pos.status.replace('_', ' ')}</Badge>
                                                </div>

                                                <div className="grid grid-cols-2 gap-4 pb-4 border-b border-white/5">
                                                    {pos.position_legs?.map((leg) => (
                                                        <div key={leg.id} className="space-y-1">
                                                            <div className="text-[10px] font-bold text-white/20 uppercase tracking-widest">{leg.network}</div>
                                                            <div className="text-xs font-mono text-white/80">${leg.entry_price.toFixed(4)}</div>
                                                            <div className="text-[10px] text-white/40">{leg.contracts} units</div>
                                                        </div>
                                                    ))}
                                                </div>

                                                {pos.status === 'pending' && (
                                                    <div className="pt-4 space-y-2">
                                                        <div className="text-[10px] font-bold text-white/20 uppercase tracking-widest text-center mb-2">Mark Outcome</div>
                                                        <div className="grid grid-cols-3 gap-2">
                                                            <button
                                                                onClick={() => resolvePosition(pos.id, 'polymarket_won')}
                                                                className="py-2 px-1 text-[10px] font-bold bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 border border-blue-500/20 rounded-lg transition-all active:scale-95"
                                                            >
                                                                Poly Won
                                                            </button>
                                                            <button
                                                                onClick={() => resolvePosition(pos.id, 'kalshi_won')}
                                                                className="py-2 px-1 text-[10px] font-bold bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-400 border border-indigo-500/20 rounded-lg transition-all active:scale-95"
                                                            >
                                                                Kalshi Won
                                                            </button>
                                                            <button
                                                                onClick={() => resolvePosition(pos.id, 'both_lost')}
                                                                className="py-2 px-1 text-[10px] font-bold bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/20 rounded-lg transition-all active:scale-95"
                                                            >
                                                                Both Lost
                                                            </button>
                                                        </div>
                                                    </div>
                                                )}
                                            </CardContent>
                                        </Card>
                                    </div>
                                )
                            })
                        )}

                        <button
                            onClick={handleAddPosition}
                            className="w-full py-4 border-2 border-dashed border-white/5 rounded-2xl flex items-center justify-center gap-2 text-white/20 hover:text-blue-500 hover:border-blue-500/20 hover:bg-blue-500/5 transition-all group"
                        >
                            <Plus className="h-4 w-4 group-hover:scale-125 transition-transform" />
                            <span className="text-sm font-bold uppercase tracking-widest">Add Position</span>
                        </button>
                    </div>
                </div>
            )}

            <AddPositionModal
                isOpen={isAddModalOpen}
                onClose={() => setIsAddModalOpen(false)}
                onSuccess={() => setRefreshTrigger(prev => prev + 1)}
                selectedDate={selectedDate}
            />
        </div>
    )
}

function Badge({ children, className }: { children: React.ReactNode, className?: string }) {
    return (
        <span className={cn("px-2 py-0.5 rounded text-[10px] font-bold", className)}>
            {children}
        </span>
    )
}
