import { Cell, Pie, PieChart, ResponsiveContainer } from "recharts"
import type { DashboardMetrics } from "@/hooks/useAnalysis"
import { EmptyState } from "@/components/common/States"

const COLORS: Record<string, string> = {
  bullish: "var(--color-bullish)",
  bearish: "var(--color-bearish)",
  neutral: "var(--color-neutral)",
}

const LABELS: Record<string, string> = {
  bullish: "Bullish",
  bearish: "Bearish",
  neutral: "Neutral",
}

export function SentimentDonut({ metrics }: { metrics: DashboardMetrics }) {
  if (metrics.total === 0) {
    return <EmptyState title="No sentiment data" description="Analyzed posts will populate this chart." />
  }

  const data = metrics.sentimentBreakdown.map((d) => ({
    name: LABELS[d.bucket],
    key: d.bucket,
    value: d.count,
  }))

  return (
    <div className="flex flex-col items-center gap-4 sm:flex-row sm:justify-around">
      <div className="relative h-44 w-44 shrink-0">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              innerRadius={54}
              outerRadius={80}
              paddingAngle={2}
              stroke="var(--color-surface)"
              strokeWidth={2}
              startAngle={90}
              endAngle={-270}
              isAnimationActive
            >
              {data.map((entry) => (
                <Cell key={entry.key} fill={COLORS[entry.key]} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
          <span className="tabular text-2xl font-semibold text-foreground">{metrics.total}</span>
          <span className="text-[10px] uppercase tracking-wider text-muted">Posts</span>
        </div>
      </div>

      <div className="w-full max-w-[220px] space-y-2.5">
        {data.map((d) => {
          const pct = metrics.total > 0 ? (d.value / metrics.total) * 100 : 0
          return (
            <div key={d.key}>
              <div className="flex items-center justify-between text-xs">
                <span className="flex items-center gap-2 text-muted">
                  <span className="h-2.5 w-2.5 rounded-sm" style={{ backgroundColor: COLORS[d.key] }} />
                  {d.name}
                </span>
                <span className="tabular font-medium text-foreground">
                  {d.value} <span className="text-muted">({pct.toFixed(0)}%)</span>
                </span>
              </div>
              <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-surface-2">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{ width: `${pct}%`, backgroundColor: COLORS[d.key] }}
                />
              </div>
            </div>
          )
        })}
        <p className="pt-1 text-[10px] leading-relaxed text-muted">
          Based on the <span className="text-primary">CryptoBERT</span> model label per post.
        </p>
      </div>
    </div>
  )
}
