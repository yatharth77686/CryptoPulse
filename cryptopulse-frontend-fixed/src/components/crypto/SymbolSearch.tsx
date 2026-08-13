import { useState } from "react"
import { Search } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/common/Button"

export function SymbolSearch({
  value,
  suggestions,
  onSelect,
  placeholder = "Search symbol (BTC, ETH, SOL...)",
}: {
  value: string
  suggestions: string[]
  onSelect: (symbol: string) => void
  placeholder?: string
}) {
  const [input, setInput] = useState("")

  const submit = () => {
    const sym = input.trim().toUpperCase()
    if (sym) {
      onSelect(sym)
      setInput("")
    }
  }

  return (
    <div className="space-y-3">
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.nativeEvent.isComposing && e.keyCode !== 229) submit()
            }}
            placeholder={placeholder}
            className="h-9 w-full rounded-md border border-border bg-surface-2/50 pl-9 pr-3 text-sm uppercase text-foreground placeholder:normal-case placeholder:text-muted focus:border-primary/60 focus:outline-none focus:ring-1 focus:ring-primary/40"
          />
        </div>
        <Button variant="primary" onClick={submit}>
          Explore
        </Button>
      </div>

      {suggestions.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {suggestions.map((s) => (
            <button
              key={s}
              onClick={() => onSelect(s)}
              className={cn(
                "rounded-md border px-2.5 py-1 text-xs font-semibold tabular transition-colors",
                s === value
                  ? "border-primary/40 bg-primary/12 text-primary"
                  : "border-border bg-surface-2/50 text-muted hover:border-border-strong hover:text-foreground",
              )}
            >
              {s}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
