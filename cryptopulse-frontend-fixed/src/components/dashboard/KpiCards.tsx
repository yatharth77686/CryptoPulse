import {
  Activity,
  Gauge,
  MessagesSquare,
  Minus,
  TrendingDown,
  TrendingUp,
  Users,
} from "lucide-react"
import { cn, formatNumber } from "@/lib/utils"
import { Skeleton } from "@/components/common/States"
import type { DashboardMetrics } from "@/hooks/useAnalysis"

interface KpiDef {
  key: string
  label: string
  value: string
  icon: typeof Activity
  accent: string
  hint?: string
}

function buildKpis(m: DashboardMetrics): KpiDef[] {
  const pct = (n: number) => (m.total > 0 ? `${Math.round((n / m.total) * 100)}%` : "N/A")
  return [
    {
      key: "total",
      label: "Analyzed Tweets",
      value: formatNumber(m.total),
      icon: MessagesSquare,
      accent: "text-primary",
    },
    {
      key: "bullish",
      label: "Bullish",
      value: formatNumber(m.bullish),
      hint: pct(m.bullish),
      icon: TrendingUp,
      accent: "text-bullish",
    },
    {
      key: "bearish",
      label: "Bearish",
      value: formatNumber(m.bearish),
      hint: pct(m.bearish),
      icon: TrendingDown,
      accent: "text-bearish",
    },
    {
      key: "neutral",
      label: "Neutral",
      value: formatNumber(m.neutral),
      hint: pct(m.neutral),
      icon: Minus,
      accent: "text-neutral",
    },
    {
      key: "signal",
      label: "Avg Signal Strength",
      value: m.avgSignal != null ? m.avgSignal.toFixed(2) : "N/A",
      icon: Gauge,
      accent: "text-primary",
    },
    {
      key: "influence",
      label: "Avg Social Influence",
      value: m.avgInfluence != null ? m.avgInfluence.toFixed(2) : "N/A",
      icon: Users,
      accent: "text-primary",
    },
  ]
}

export function KpiCards({ metrics, loading }: { metrics: DashboardMetrics; loading?: boolean }) {
  if (loading) {
    return (
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 xl:grid-cols-6">
        {Array.from({ length: 6 }).map((_, i) => (
          <Skeleton key={i} className="h-[92px]" />
        ))}
      </div>
    )
  }

  const kpis = buildKpis(metrics)
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 xl:grid-cols-6">
      {kpis.map(({ key, label, value, hint, icon: Icon, accent }) => (
        <div
          key={key}
          className="rounded-[var(--radius)] border border-border bg-surface/80 p-4 transition-colors hover:border-border-strong"
        >
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-medium uppercase tracking-wider text-muted">{label}</span>
            <Icon className={cn("h-4 w-4", accent)} />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="tabular text-2xl font-semibold text-foreground">{value}</span>
            {hint && <span className={cn("text-xs font-medium tabular", accent)}>{hint}</span>}
          </div>
        </div>
      ))}
    </div>
  )
}
