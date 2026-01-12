"use client"

import { Calculator, Percent, ArrowRightLeft, Target, TrendingUp, Info } from "lucide-react"
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from "@/components/ui/accordion"
import { OddsConverterCalculator } from "./calculators/OddsConverterCalculator"
import { ArbitrageCalculator } from "./calculators/ArbitrageCalculator"
import { MultiMarketComparison } from "./calculators/MultiMarketComparison"
import { EVCalculator } from "./calculators/EVCalculator"
import { KellyCalculator } from "./calculators/KellyCalculator"
import { Badge } from "@/components/ui/badge"

export function CalculatorsPage() {
    return (
        <div className="max-w-4xl mx-auto px-4 py-8">
            <div className="flex flex-col mb-8">
                <div className="flex items-center gap-3 mb-2">
                    <div className="h-10 w-10 rounded-xl bg-indigo-500/10 flex items-center justify-center border border-indigo-500/20">
                        <Calculator className="h-5 w-5 text-indigo-400" />
                    </div>
                    <h1 className="text-2xl font-bold text-white tracking-tight">Market Intelligence Tools</h1>
                </div>
                <p className="text-white/40 text-sm max-w-2xl">
                    Professional-grade calculators for probability analysis, risk management, and arbitrage discovery across prediction markets.
                </p>
            </div>

            <Accordion type="multiple" defaultValue={["odds-converter"]} className="space-y-4">
                <AccordionItem value="odds-converter" className="bg-zinc-950/50 border border-white/5 rounded-2xl px-6">
                    <AccordionTrigger>
                        <div className="flex items-center gap-4">
                            <div className="p-2 bg-indigo-500/10 rounded-lg">
                                <Percent className="h-4 w-4 text-indigo-400" />
                            </div>
                            <div>
                                <div className="text-sm font-bold text-white uppercase tracking-wider">Odds Converter</div>
                                <div className="text-[10px] text-white/30 font-medium">CONVERSION & IMPLIED PROBABILITY</div>
                            </div>
                        </div>
                    </AccordionTrigger>
                    <AccordionContent>
                        <OddsConverterCalculator />
                    </AccordionContent>
                </AccordionItem>

                <AccordionItem value="arbitrage" className="bg-zinc-950/50 border border-white/5 rounded-2xl px-6">
                    <AccordionTrigger>
                        <div className="flex items-center gap-4">
                            <div className="p-2 bg-green-500/10 rounded-lg">
                                <ArrowRightLeft className="h-4 w-4 text-green-400" />
                            </div>
                            <div>
                                <div className="text-sm font-bold text-white uppercase tracking-wider">Arbitrage Calculator</div>
                                <div className="text-[10px] text-white/30 font-medium">MULTI-PLATFORM HEDGING & FEES</div>
                            </div>
                        </div>
                    </AccordionTrigger>
                    <AccordionContent>
                        <ArbitrageCalculator />
                    </AccordionContent>
                </AccordionItem>

                <AccordionItem value="multi-market" className="bg-zinc-950/50 border border-white/5 rounded-2xl px-6">
                    <AccordionTrigger>
                        <div className="flex items-center gap-4">
                            <div className="p-2 bg-amber-500/10 rounded-lg">
                                <Info className="h-4 w-4 text-amber-400" />
                            </div>
                            <div>
                                <div className="text-sm font-bold text-white uppercase tracking-wider">Multi-Market Comparison</div>
                                <div className="text-[10px] text-white/30 font-medium">CROSS-PLATFORM VALUE DISCOVERY</div>
                            </div>
                        </div>
                    </AccordionTrigger>
                    <AccordionContent>
                        <MultiMarketComparison />
                    </AccordionContent>
                </AccordionItem>

                <AccordionItem value="ev-calc" className="bg-zinc-950/50 border border-white/5 rounded-2xl px-6">
                    <AccordionTrigger>
                        <div className="flex items-center gap-4">
                            <div className="p-2 bg-blue-500/10 rounded-lg">
                                <Target className="h-4 w-4 text-blue-400" />
                            </div>
                            <div>
                                <div className="text-sm font-bold text-white uppercase tracking-wider">EV Calculator</div>
                                <div className="text-[10px] text-white/30 font-medium">EXPECTED VALUE & BREAKEVEN</div>
                            </div>
                        </div>
                    </AccordionTrigger>
                    <AccordionContent>
                        <EVCalculator />
                    </AccordionContent>
                </AccordionItem>

                <AccordionItem value="kelly" className="bg-zinc-950/50 border border-white/5 rounded-2xl px-6">
                    <AccordionTrigger>
                        <div className="flex items-center gap-4">
                            <div className="p-2 bg-purple-500/10 rounded-lg">
                                <TrendingUp className="h-4 w-4 text-purple-400" />
                            </div>
                            <div>
                                <div className="text-sm font-bold text-white uppercase tracking-wider">Kelly Criterion</div>
                                <div className="text-[10px] text-white/30 font-medium">OPTIMAL STAKE & RISK SIZING</div>
                            </div>
                        </div>
                    </AccordionTrigger>
                    <AccordionContent>
                        <KellyCalculator />
                    </AccordionContent>
                </AccordionItem>
            </Accordion>

            <div className="mt-12 flex items-center justify-center gap-2">
                <Badge className="bg-white/5 text-white/20 border-white/5 hover:bg-white/10 transition-colors cursor-help px-6 py-2 rounded-full font-medium tracking-tight">
                    Mathematics based on DeFiRate.com methodologies
                </Badge>
            </div>
        </div>
    )
}

