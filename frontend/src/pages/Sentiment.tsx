import { useMemo } from "react"
import { BarChart3, Brain, TrendingDown, TrendingUp, Minus } from "lucide-react"
import { PageShell } from "@/components/layout/PageShell"
import { Card, CardBody, CardHeader } from "@/components/common/Card"
import { ErrorState, Skeleton } from "@/components/common/States"
import { SentimentDonut } from "@/components/sentiment/SentimentDonut"
import { useAnalysisContext } from "@/context/AnalysisContext"
import { useMetrics } from "@/hooks/useAnalysis"

export function Sentiment({ onMenu }: { onMenu: () => void }) {
  const { data, error, isLoading, isRefreshing, lastUpdated, refresh } = useAnalysisContext()
  const metrics = useMetrics(data)

  const confidence = useMemo(() => {
    const values = (data ?? []).map((p) => p.sentiment?.cryptobert?.confidence).filter((v): v is number => typeof v === "number")
    return values.length ? values.reduce((a, b) => a + b, 0) / values.length : null
  }, [data])

  return (
    <PageShell title="Sentiment" subtitle="CryptoBERT sentiment intelligence" lastUpdated={lastUpdated} isRefreshing={isRefreshing} onRefresh={refresh} onMenu={onMenu}>
      {error && !data ? <Card><ErrorState message={error} onRetry={refresh} /></Card> : (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
            {[
              ["Bullish", metrics.bullish, <TrendingUp className="h-4 w-4" />],
              ["Bearish", metrics.bearish, <TrendingDown className="h-4 w-4" />],
              ["Neutral", metrics.neutral, <Minus className="h-4 w-4" />],
              ["Avg Confidence", confidence == null ? "N/A" : `${(confidence * 100).toFixed(1)}%`, <Brain className="h-4 w-4" />],
            ].map(([label, value, icon]) => (
              <Card key={String(label)}><CardBody><p className="flex items-center gap-2 text-xs text-muted">{icon}{label}</p><p className="tabular mt-2 text-2xl font-semibold">{value}</p></CardBody></Card>
            ))}
          </div>
          <div className="grid gap-4 lg:grid-cols-2">
            <Card><CardHeader title="Sentiment Distribution" subtitle="CryptoBERT" icon={<BarChart3 className="h-4 w-4" />} /><CardBody>{isLoading ? <Skeleton className="h-52" /> : <SentimentDonut metrics={metrics} />}</CardBody></Card>
            <Card><CardHeader title="Interpretation" subtitle="How the dashboard classifies posts" /><CardBody className="space-y-3 text-sm text-muted">
              <p><span className="font-medium text-bullish">Bullish</span> includes positive/bullish model labels.</p>
              <p><span className="font-medium text-bearish">Bearish</span> includes negative/bearish model labels.</p>
              <p><span className="font-medium text-foreground">Neutral</span> includes neutral or unrecognized labels.</p>
              <p className="text-xs">Posts analyzed: {metrics.total}</p>
            </CardBody></Card>
          </div>
        </div>
      )}
    </PageShell>
  )
}
