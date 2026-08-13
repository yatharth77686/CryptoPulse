import { cn } from "@/lib/utils"
import { topSignals } from "@/lib/signals"
import { AssetTag, SentimentBadge } from "@/components/common/Indicators"
import { EmptyState } from "@/components/common/States"
import type { AnalyzedPost } from "@/types/api"

export function TopSignals({
  posts,
  onSelect,
}: {
  posts: AnalyzedPost[] | null
  onSelect?: (post: AnalyzedPost) => void
}) {
  const signals = topSignals(posts, 6)
  const max = signals[0]?.signal_strength ?? 1

  if (signals.length === 0) {
    return <EmptyState title="No signals yet" description="Strong crypto signals will appear here." />
  }

  return (
    <ul className="divide-y divide-border">
      {signals.map((post) => {
        const strength = post.signal_strength ?? 0
        const width = max > 0 ? (strength / max) * 100 : 0
        return (
          <li key={post.id}>
            <button
              onClick={() => onSelect?.(post)}
              className="group flex w-full items-center gap-3 px-1 py-2.5 text-left transition-colors hover:bg-surface-2/50"
            >
              <div className="flex w-14 shrink-0 flex-col items-start">
                {post.assets?.primary ? (
                  <AssetTag symbol={post.assets.primary} />
                ) : (
                  <span className="text-[11px] text-muted">N/A</span>
                )}
              </div>

              <div className="min-w-0 flex-1">
                <p className="truncate text-xs text-foreground/90">{post.text}</p>
                <div className="mt-1.5 h-1 overflow-hidden rounded-full bg-surface-2">
                  <div
                    className="h-full rounded-full bg-primary transition-all duration-500"
                    style={{ width: `${width}%` }}
                  />
                </div>
              </div>

              <div className="flex w-24 shrink-0 flex-col items-end gap-1">
                <span className="tabular text-sm font-semibold text-primary">{strength.toFixed(2)}</span>
                <SentimentBadge label={post.sentiment?.cryptobert?.label} size="sm" />
              </div>
            </button>
          </li>
        )
      })}
    </ul>
  )
}

export function SignalDistributionBars({ buckets }: { buckets: { label: string; count: number; tier: string }[] }) {
  const total = buckets.reduce((a, b) => a + b.count, 0)
  const tierColor: Record<string, string> = {
    "very-strong": "bg-bullish",
    strong: "bg-primary",
    moderate: "bg-neutral",
    weak: "bg-muted",
  }
  if (total === 0) {
    return <EmptyState title="No distribution data" />
  }
  return (
    <div className="space-y-3">
      {buckets.map((b) => {
        const pct = total > 0 ? (b.count / total) * 100 : 0
        return (
          <div key={b.tier}>
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted">{b.label}</span>
              <span className="tabular font-medium text-foreground">
                {b.count} <span className="text-muted">({pct.toFixed(0)}%)</span>
              </span>
            </div>
            <div className="mt-1 h-2 overflow-hidden rounded-full bg-surface-2">
              <div
                className={cn("h-full rounded-full transition-all duration-500", tierColor[b.tier])}
                style={{ width: `${pct}%` }}
              />
            </div>
          </div>
        )
      })}
    </div>
  )
}
