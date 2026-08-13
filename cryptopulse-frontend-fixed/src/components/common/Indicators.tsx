import { TrendingUp, TrendingDown, Minus } from "lucide-react"
import { cn } from "@/lib/utils"
import { SIGNAL_TIER_LABEL, toSentimentBucket, toSignalTier } from "@/lib/utils"
import type { SentimentBucket, SignalTier } from "@/types/api"

const sentimentStyles: Record<SentimentBucket, string> = {
  bullish: "text-bullish bg-bullish/10 border-bullish/25",
  bearish: "text-bearish bg-bearish/10 border-bearish/25",
  neutral: "text-neutral bg-neutral/10 border-neutral/25",
}

const sentimentIcon = {
  bullish: TrendingUp,
  bearish: TrendingDown,
  neutral: Minus,
}

export function SentimentBadge({
  label,
  confidence,
  size = "md",
}: {
  label: string | null | undefined
  confidence?: number
  size?: "sm" | "md"
}) {
  const bucket = toSentimentBucket(label)
  const Icon = sentimentIcon[bucket]
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded border font-medium capitalize",
        sentimentStyles[bucket],
        size === "sm" ? "px-1.5 py-0.5 text-[10px]" : "px-2 py-1 text-xs",
      )}
    >
      <Icon className={size === "sm" ? "h-3 w-3" : "h-3.5 w-3.5"} />
      {label ?? "N/A"}
      {confidence != null && (
        <span className="opacity-70 tabular">{Math.round(confidence * 100)}%</span>
      )}
    </span>
  )
}

const tierStyles: Record<SignalTier, string> = {
  "very-strong": "text-bullish",
  strong: "text-primary",
  moderate: "text-neutral",
  weak: "text-muted",
}

const tierBar: Record<SignalTier, number> = {
  "very-strong": 4,
  strong: 3,
  moderate: 2,
  weak: 1,
}

export function SignalTierBadge({ strength }: { strength: number | null | undefined }) {
  const tier = toSignalTier(strength)
  const bars = tierBar[tier]
  return (
    <span className={cn("inline-flex items-center gap-1.5 text-xs font-medium", tierStyles[tier])}>
      <span className="flex items-end gap-0.5" aria-hidden>
        {[1, 2, 3, 4].map((i) => (
          <span
            key={i}
            className={cn(
              "w-1 rounded-sm transition-colors",
              i <= bars ? "bg-current" : "bg-border-strong",
            )}
            style={{ height: `${4 + i * 2}px` }}
          />
        ))}
      </span>
      {SIGNAL_TIER_LABEL[tier]}
    </span>
  )
}

export function AssetTag({ symbol, muted = false }: { symbol: string; muted?: boolean }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded px-1.5 py-0.5 text-[11px] font-semibold tabular tracking-wide",
        muted
          ? "border border-border text-muted"
          : "bg-primary/15 text-primary border border-primary/25",
      )}
    >
      {symbol}
    </span>
  )
}
