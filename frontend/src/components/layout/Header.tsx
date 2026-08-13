import { Menu, RefreshCw } from "lucide-react"
import { cn, timeAgo } from "@/lib/utils"
import { Button } from "@/components/common/Button"

interface HeaderProps {
  title: string
  subtitle?: string
  lastUpdated: Date | null
  isRefreshing?: boolean
  onRefresh?: () => void
  onMenu: () => void
  live?: boolean
}

export function Header({
  title,
  subtitle,
  lastUpdated,
  isRefreshing,
  onRefresh,
  onMenu,
  live = true,
}: HeaderProps) {
  return (
    <header className="sticky top-0 z-20 flex h-14 items-center gap-3 border-b border-border bg-background/85 px-4 backdrop-blur-md">
      <button className="text-muted hover:text-foreground lg:hidden" onClick={onMenu} aria-label="Open menu">
        <Menu className="h-5 w-5" />
      </button>

      <div className="min-w-0 flex-1">
        <h1 className="truncate text-base font-semibold tracking-tight text-foreground">{title}</h1>
        {subtitle && <p className="truncate text-xs text-muted">{subtitle}</p>}
      </div>

      {live && (
        <div className="hidden items-center gap-2 rounded-full border border-bullish/25 bg-bullish/10 px-2.5 py-1 sm:flex">
          <span className="h-1.5 w-1.5 rounded-full bg-bullish animate-pulse-dot" />
          <span className="text-[11px] font-semibold uppercase tracking-wider text-bullish">Live</span>
        </div>
      )}

      <div className="hidden text-right md:block">
        <p className="text-[10px] uppercase tracking-wider text-muted">Last updated</p>
        <p className="text-xs font-medium tabular text-foreground">
          {lastUpdated ? timeAgo(lastUpdated.toISOString()) : "—"}
        </p>
      </div>

      {onRefresh && (
        <Button variant="secondary" size="sm" onClick={onRefresh} disabled={isRefreshing}>
          <RefreshCw className={cn("h-3.5 w-3.5", isRefreshing && "animate-spin")} />
          <span className="hidden sm:inline">Refresh</span>
        </Button>
      )}
    </header>
  )
}
