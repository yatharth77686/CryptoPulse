import type { ReactNode } from "react"
import { AlertTriangle, Inbox, RefreshCw, WifiOff } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/common/Button"

export function Skeleton({ className }: { className?: string }) {
  return <div className={cn("skeleton rounded-md", className)} />
}

export function ErrorState({
  message,
  onRetry,
  compact = false,
}: {
  message: string
  onRetry?: () => void
  compact?: boolean
}) {
  const isNetwork = /reach|running|network/i.test(message)
  const Icon = isNetwork ? WifiOff : AlertTriangle
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-3 text-center",
        compact ? "py-8" : "py-16",
      )}
    >
      <span className="flex h-11 w-11 items-center justify-center rounded-full border border-bearish/30 bg-bearish/10 text-bearish">
        <Icon className="h-5 w-5" />
      </span>
      <div className="max-w-sm">
        <p className="text-sm font-medium text-foreground">
          {isNetwork ? "Cannot connect to backend" : "Something went wrong"}
        </p>
        <p className="mt-1 text-xs text-muted leading-relaxed">{message}</p>
      </div>
      {onRetry && (
        <Button variant="secondary" size="sm" onClick={onRetry}>
          <RefreshCw className="h-3.5 w-3.5" />
          Retry
        </Button>
      )}
    </div>
  )
}

export function EmptyState({
  title = "No data yet",
  description,
  icon,
}: {
  title?: string
  description?: ReactNode
  icon?: ReactNode
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-14 text-center">
      <span className="flex h-11 w-11 items-center justify-center rounded-full border border-border bg-surface-2 text-muted">
        {icon ?? <Inbox className="h-5 w-5" />}
      </span>
      <div className="max-w-sm">
        <p className="text-sm font-medium text-foreground">{title}</p>
        {description && <p className="mt-1 text-xs text-muted leading-relaxed">{description}</p>}
      </div>
    </div>
  )
}
