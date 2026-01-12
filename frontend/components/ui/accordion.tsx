"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { ChevronDown } from "lucide-react"

const AccordionContext = React.createContext<{
    openItems: string[]
    toggleItem: (value: string) => void
    type: "single" | "multiple"
}>({
    openItems: [],
    toggleItem: () => { },
    type: "single"
})

export function Accordion({
    children,
    type = "single",
    defaultValue = [],
    className
}: {
    children: React.ReactNode,
    type?: "single" | "multiple",
    defaultValue?: string[],
    className?: string
}) {
    const [openItems, setOpenItems] = React.useState<string[]>(defaultValue)

    const toggleItem = (value: string) => {
        if (type === "single") {
            setOpenItems(openItems.includes(value) ? [] : [value])
        } else {
            setOpenItems(openItems.includes(value)
                ? openItems.filter(item => item !== value)
                : [...openItems, value]
            )
        }
    }

    return (
        <AccordionContext.Provider value={{ openItems, toggleItem, type }}>
            <div className={cn("divide-y divide-white/5", className)}>
                {children}
            </div>
        </AccordionContext.Provider>
    )
}

export function AccordionItem({ value, children, className }: { value: string, children: React.ReactNode, className?: string }) {
    return (
        <div className={cn("border-b border-white/5", className)}>
            {React.Children.map(children, child => {
                if (React.isValidElement(child)) {
                    return React.cloneElement(child as React.ReactElement<any>, { value })
                }
                return child
            })}
        </div>
    )
}

export function AccordionTrigger({ value, children, className }: { value?: string, children: React.ReactNode, className?: string }) {
    const { openItems, toggleItem } = React.useContext(AccordionContext)
    const isOpen = value ? openItems.includes(value) : false

    return (
        <button
            onClick={() => value && toggleItem(value)}
            className={cn(
                "flex w-full items-center justify-between py-4 font-bold text-left text-white transition-all hover:text-indigo-400 group",
                className
            )}
        >
            {children}
            <ChevronDown className={cn(
                "h-4 w-4 shrink-0 transition-transform duration-200 text-white/20 group-hover:text-indigo-400",
                isOpen && "rotate-180"
            )} />
        </button>
    )
}

export function AccordionContent({ value, children, className }: { value?: string, children: React.ReactNode, className?: string }) {
    const { openItems } = React.useContext(AccordionContext)
    const isOpen = value ? openItems.includes(value) : false

    if (!isOpen) return null

    return (
        <div className={cn("pb-6 pt-0 overflow-hidden text-sm transition-all", className)}>
            {children}
        </div>
    )
}
