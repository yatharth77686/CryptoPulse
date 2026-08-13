import { useMemo, useState } from "react"
import { Activity, TrendingDown, TrendingUp } from "lucide-react"
import { PageShell } from "@/components/layout/PageShell"
import { Card, CardBody, CardHeader } from "@/components/common/Card"
import { EmptyState, ErrorState, Skeleton } from "@/components/common/States"
import { Field, Select } from "@/components/common/Controls"
import { SentimentBadge } from "@/components/common/Indicators"
import { aggregateMarketReactions, WINDOWS } from "@/lib/marketAgg"
import { useAnalysisContext } from "@/context/AnalysisContext"
import { cn, formatPercent } from "@/lib/utils"
import type { TimeWindow } from "@/types/api"

function changeColor(v: number | null | undefined) {
  if (v == null || Number.isNaN(v)) return "text-muted"
  if (v > 0) return "text-bullish"
  if (v < 0) return "text-bearish"
  return "text-neutral"
}

function AlignmentBar({ value }: { value: number }) {
  if (Number.isNaN(value)) return <span className="text-xs text-muted">N/A</span>
  const color = value >= 60 ? "bg-bullish" : value >= 40 ? "bg-neutral" : "bg-bearish"
  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 w-16 overflow-hidden rounded-full bg-surface-2">
        <div className={cn("h-full rounded-full", color)} style={{ width: `${value}%` }} />
      </div>
      <span className="tabular text-xs text-muted">{value.toFixed(0)}%</span>
    </div>
  )
}

export function MarketReaction({ onMenu }: { onMenu: () => void }) {
  const { data, error, isLoading, isRefreshing, lastUpdated, refresh } = useAnalysisContext()
  const [sortWindow, setSortWindow] = useState<TimeWindow>("1h")

  const rows = useMemo(() => {
    const agg = aggregateMarketReactions(data)
    return [...agg].sort((a, b) => {
      const av = a.avg[sortWindow]
      const bv = b.avg[sortWindow]
      return (bv ?? -Infinity) - (av ?? -Infinity)
    })
  }, [data, sortWindow])

  const summary = useMemo(() => {
    const valid = rows.filter((r) => r.avg[sortWindow] != null)
    const up = valid.filter((r) => (r.avg[sortWindow] ?? 0) > 0).length
    const down = valid.filter((r) => (r.avg[sortWindow] ?? 0) < 0).length
    return { total: rows.length, up, down }
  }, [rows, sortWindow])

  return (
    <PageShell
      title="Market Reaction"
      subtitle="Price movement following analyzed posts"
      lastUpdated={lastUpdated}
      isRefreshing={isRefreshing}
      onRefresh={refresh}
      onMenu={onMenu}
    >
      {error && !data ? (
        <Card>
          <ErrorState message={error} onRetry={refresh} />
        </Card>
      ) : isLoading ? (
        <Skeleton className="h-96" />
      ) : rows.length === 0 ? (
        <Card>
          <EmptyState
            title="No market reaction data"
            description="Analyzed posts do not yet contain linked market reactions."
            icon={<Activity className="h-5 w-5" />}
          />
        </Card>
      ) : (
        <div className="space-y-4">
          <div className="grid grid-cols-3 gap-3">
            <Card>
              <CardBody className="text-center">
                <p className="text-[10px] uppercase tracking-wider text-muted">Tracked Assets</p>
                <p className="tabular mt-1 text-2xl font-semibold text-foreground">{summary.total}</p>
              </CardBody>
            </Card>
            <Card>
              <CardBody className="text-center">
                <p className="flex items-center justify-center gap-1 text-[10px] uppercase tracking-wider text-muted">
                  <TrendingUp className="h-3 w-3 text-bullish" /> Moved Up
                </p>
                <p className="tabular mt-1 text-2xl font-semibold text-bullish">{summary.up}</p>
              </CardBody>
            </Card>
            <Card>
              <CardBody className="text-center">
                <p className="flex items-center justify-center gap-1 text-[10px] uppercase tracking-wider text-muted">
                  <TrendingDown className="h-3 w-3 text-bearish" /> Moved Down
                </p>
                <p className="tabular mt-1 text-2xl font-semibold text-bearish">{summary.down}</p>
              </CardBody>
            </Card>
          </div>

          <Card>
            <CardHeader
              title="Average Price Reaction by Asset"
              subtitle={`Sorted by ${sortWindow} move`}
              action={
                <div className="w-28">
                  <Field label="Sort window">
                    <Select value={sortWindow} onChange={(e) => setSortWindow(e.target.value as TimeWindow)}>
                      {WINDOWS.map((w) => (
                        <option key={w} value={w}>
                          {w} reaction
                        </option>
                      ))}
                    </Select>
                  </Field>
                </div>
              }
            />
            <CardBody className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border text-left text-[10px] uppercase tracking-wider text-muted">
                      <th className="px-4 py-2.5 font-medium">Asset</th>
                      <th className="px-4 py-2.5 font-medium">Posts</th>
                      <th className="px-4 py-2.5 font-medium">Dominant</th>
                      {WINDOWS.map((w) => (
                        <th key={w} className="px-4 py-2.5 text-right font-medium">
                          {w}
                        </th>
                      ))}
                      <th className="px-4 py-2.5 font-medium">Sentiment-Price Align</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map((r) => (
                      <tr
                        key={r.symbol}
                        className="border-b border-border/60 transition-colors last:border-0 hover:bg-surface-2/40"
                      >
                        <td className="px-4 py-3">
                          <span className="tabular font-semibold text-primary">{r.symbol}</span>
                        </td>
                        <td className="tabular px-4 py-3 text-muted">{r.count}</td>
                        <td className="px-4 py-3">
                          <SentimentBadge label={r.dominant} />
                        </td>
                        {WINDOWS.map((w) => (
                          <td key={w} className={cn("tabular px-4 py-3 text-right font-medium", changeColor(r.avg[w]))}>
                            {formatPercent(r.avg[w])}
                          </td>
                        ))}
                        <td className="px-4 py-3">
                          <AlignmentBar value={r.aligned} />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardBody>
          </Card>

          <p className="text-[11px] leading-relaxed text-muted">
            {'"'}Sentiment-Price Align{'"'} estimates how often price direction matched the dominant sentiment
            (bullish posts followed by price up, bearish by price down) using the longest available reaction window.
          </p>
        </div>
      )}
    </PageShell>
  )
}
