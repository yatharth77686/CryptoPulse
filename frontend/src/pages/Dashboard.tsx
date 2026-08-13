import { useMemo, useState } from "react"
import { Link } from "react-router-dom"
import { ArrowRight, Gauge, PieChart, Radio, TrendingUp } from "lucide-react"
import { PageShell } from "@/components/layout/PageShell"
import { Card, CardBody, CardHeader } from "@/components/common/Card"
import { KpiCards } from "@/components/dashboard/KpiCards"
import { SentimentDonut } from "@/components/sentiment/SentimentDonut"
import { SignalDistributionBars, TopSignals } from "@/components/dashboard/TopSignals"
import { TweetCard } from "@/components/tweets/TweetCard"
import { TweetDetailModal } from "@/components/tweets/TweetDetailModal"
import { ErrorState, Skeleton } from "@/components/common/States"
import { useAnalysisContext } from "@/context/AnalysisContext"
import { useMetrics } from "@/hooks/useAnalysis"
import { signalDistribution } from "@/lib/signals"
import { parseTimestamp } from "@/lib/utils"
import type { AnalyzedPost } from "@/types/api"

export function Dashboard({ onMenu }: { onMenu: () => void }) {
  const { data, error, isLoading, isRefreshing, lastUpdated, refresh } = useAnalysisContext()
  const metrics = useMetrics(data)
  const [selected, setSelected] = useState<AnalyzedPost | null>(null)

  const distribution = useMemo(() => signalDistribution(data), [data])
  const recent = useMemo(
    () =>
      [...(data ?? [])]
        .sort((a, b) => (parseTimestamp(b.timestamp)?.getTime() ?? 0) - (parseTimestamp(a.timestamp)?.getTime() ?? 0))
        .slice(0, 4),
    [data],
  )

  return (
    <PageShell
      title="Overview"
      subtitle="AI social-media intelligence dashboard"
      lastUpdated={lastUpdated}
      isRefreshing={isRefreshing}
      onRefresh={refresh}
      onMenu={onMenu}
    >
      {error && !data ? (
        <Card>
          <ErrorState message={error} onRetry={refresh} />
        </Card>
      ) : (
        <div className="space-y-4">
          <KpiCards metrics={metrics} loading={isLoading} />

          <div className="grid gap-4 lg:grid-cols-3">
            <Card className="lg:col-span-1">
              <CardHeader title="Sentiment Overview" icon={<PieChart className="h-4 w-4" />} subtitle="CryptoBERT" />
              <CardBody>
                {isLoading ? <Skeleton className="h-44" /> : <SentimentDonut metrics={metrics} />}
              </CardBody>
            </Card>

            <Card className="lg:col-span-2">
              <CardHeader
                title="Top Crypto Signals"
                icon={<TrendingUp className="h-4 w-4" />}
                subtitle="Ranked by signal strength"
                action={
                  <Link to="/live" className="flex items-center gap-1 text-xs text-primary hover:brightness-110">
                    View all <ArrowRight className="h-3 w-3" />
                  </Link>
                }
              />
              <CardBody className="py-1">
                {isLoading ? (
                  <div className="space-y-2 py-2">
                    {Array.from({ length: 5 }).map((_, i) => (
                      <Skeleton key={i} className="h-10" />
                    ))}
                  </div>
                ) : (
                  <TopSignals posts={data} onSelect={setSelected} />
                )}
              </CardBody>
            </Card>
          </div>

          <div className="grid gap-4 lg:grid-cols-3">
            <Card className="lg:col-span-1">
              <CardHeader
                title="Signal Distribution"
                icon={<Gauge className="h-4 w-4" />}
                subtitle="By strength tier"
              />
              <CardBody>
                {isLoading ? <Skeleton className="h-40" /> : <SignalDistributionBars buckets={distribution} />}
              </CardBody>
            </Card>

            <Card className="lg:col-span-2">
              <CardHeader
                title="Live Intelligence Feed"
                icon={<Radio className="h-4 w-4" />}
                subtitle="Most recent analyzed posts"
                action={
                  <Link to="/live" className="flex items-center gap-1 text-xs text-primary hover:brightness-110">
                    Open feed <ArrowRight className="h-3 w-3" />
                  </Link>
                }
              />
              <CardBody>
                {isLoading ? (
                  <div className="grid gap-3 sm:grid-cols-2">
                    {Array.from({ length: 2 }).map((_, i) => (
                      <Skeleton key={i} className="h-56" />
                    ))}
                  </div>
                ) : (
                  <div className="grid gap-3 sm:grid-cols-2">
                    {recent.map((post) => (
                      <TweetCard key={post.id} post={post} onClick={setSelected} />
                    ))}
                  </div>
                )}
              </CardBody>
            </Card>
          </div>
        </div>
      )}

      <TweetDetailModal post={selected} onClose={() => setSelected(null)} />
    </PageShell>
  )
}
