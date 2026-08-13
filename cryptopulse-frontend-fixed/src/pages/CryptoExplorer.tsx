import { useMemo, useState } from "react"
import { Coins, Gauge, TrendingDown, TrendingUp, Users } from "lucide-react"
import { PageShell } from "@/components/layout/PageShell"
import { Card, CardBody, CardHeader } from "@/components/common/Card"
import { EmptyState, ErrorState, Skeleton } from "@/components/common/States"
import { SymbolSearch } from "@/components/crypto/SymbolSearch"
import { TweetCard } from "@/components/tweets/TweetCard"
import { TweetDetailModal } from "@/components/tweets/TweetDetailModal"
import { ReactionDetail } from "@/components/market/ReactionCells"
import { useAnalysisContext } from "@/context/AnalysisContext"
import { useMarketReaction } from "@/hooks/useMarketReaction"
import { extractSymbols } from "@/lib/filters"
import { computeSymbolStats } from "@/lib/symbolStats"
import { cn } from "@/lib/utils"
import type { AnalyzedPost, MarketReactionEntry } from "@/types/api"

function StatTile({ label, value, icon, accent }: { label: string; value: string; icon: React.ReactNode; accent?: string }) {
  return (
    <div className="rounded-md border border-border bg-surface-2/40 p-3">
      <p className="flex items-center gap-1.5 text-[10px] uppercase tracking-wider text-muted">
        <span className={accent}>{icon}</span>
        {label}
      </p>
      <p className={cn("tabular mt-1 text-lg font-semibold text-foreground", accent)}>{value}</p>
    </div>
  )
}

export function CryptoExplorer({ onMenu }: { onMenu: () => void }) {
  const { data, error, isLoading, isRefreshing, lastUpdated, refresh } = useAnalysisContext()
  const [symbol, setSymbol] = useState<string>("")
  const [selected, setSelected] = useState<AnalyzedPost | null>(null)

  const symbols = useMemo(() => extractSymbols(data), [data])
  const stats = useMemo(() => (symbol ? computeSymbolStats(data, symbol) : null), [data, symbol])
  const market = useMarketReaction(symbol || null)

  // Reshape market response into a reaction entry when available.
  const reactionEntry: MarketReactionEntry | undefined =
    market.data && !(("status" in market.data))
      ? market.data.reactions[0]?.reaction
      : undefined

  const marketUnavailable = market.data && "status" in market.data

  return (
    <PageShell
      title="Crypto Explorer"
      subtitle="Inspect intelligence for a single asset"
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
          <Card>
            <CardBody>
              <SymbolSearch value={symbol} suggestions={symbols} onSelect={setSymbol} />
            </CardBody>
          </Card>

          {!symbol ? (
            <Card>
              <EmptyState
                title="Select an asset to explore"
                description="Search a symbol or pick one of the suggestions above to see its posts, sentiment, and market reaction."
                icon={<Coins className="h-5 w-5" />}
              />
            </Card>
          ) : isLoading ? (
            <Skeleton className="h-40" />
          ) : stats && stats.count === 0 ? (
            <Card>
              <EmptyState
                title={`No analyzed posts for ${symbol}`}
                description="This asset has not appeared in any analyzed tweets yet."
                icon={<Coins className="h-5 w-5" />}
              />
            </Card>
          ) : (
            stats && (
              <>
                <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
                  <StatTile label="Posts" value={String(stats.count)} icon={<Coins className="h-3 w-3" />} accent="text-primary" />
                  <StatTile
                    label="Avg Signal"
                    value={stats.avgSignal != null ? stats.avgSignal.toFixed(2) : "N/A"}
                    icon={<Gauge className="h-3 w-3" />}
                    accent="text-primary"
                  />
                  <StatTile
                    label="Avg Influence"
                    value={stats.avgInfluence != null ? stats.avgInfluence.toFixed(2) : "N/A"}
                    icon={<Users className="h-3 w-3" />}
                  />
                  <StatTile
                    label="Bullish / Bearish"
                    value={`${stats.sentiment.bullish} / ${stats.sentiment.bearish}`}
                    icon={<TrendingUp className="h-3 w-3" />}
                    accent="text-bullish"
                  />
                </div>

                <div className="grid gap-4 lg:grid-cols-3">
                  <Card>
                    <CardHeader title="Sentiment Breakdown" subtitle="CryptoBERT" />
                    <CardBody className="space-y-2.5">
                      {(["bullish", "bearish", "neutral"] as const).map((k) => {
                        const count = stats.sentiment[k]
                        const pct = stats.count > 0 ? (count / stats.count) * 100 : 0
                        const color =
                          k === "bullish" ? "bg-bullish" : k === "bearish" ? "bg-bearish" : "bg-neutral"
                        const Icon = k === "bullish" ? TrendingUp : k === "bearish" ? TrendingDown : Gauge
                        return (
                          <div key={k}>
                            <div className="flex items-center justify-between text-xs capitalize">
                              <span className="flex items-center gap-1.5 text-muted">
                                <Icon className="h-3 w-3" /> {k}
                              </span>
                              <span className="tabular font-medium text-foreground">
                                {count} ({pct.toFixed(0)}%)
                              </span>
                            </div>
                            <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-surface-2">
                              <div className={cn("h-full rounded-full transition-all", color)} style={{ width: `${pct}%` }} />
                            </div>
                          </div>
                        )
                      })}
                    </CardBody>
                  </Card>

                  <Card className="lg:col-span-2">
                    <CardHeader title={`Market Reaction — ${symbol}`} subtitle="via /market endpoint" />
                    <CardBody>
                      {market.isLoading ? (
                        <Skeleton className="h-28" />
                      ) : market.error ? (
                        <ErrorState message={market.error} onRetry={market.refresh} compact />
                      ) : marketUnavailable ? (
                        <EmptyState
                          title="Market data unavailable"
                          description={(market.data as { message?: string })?.message ?? `No market data found for ${symbol}`}
                        />
                      ) : (
                        <ReactionDetail entry={reactionEntry} />
                      )}
                    </CardBody>
                  </Card>
                </div>

                <Card>
                  <CardHeader title="Recent Posts" subtitle={`${stats.count} total`} />
                  <CardBody>
                    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
                      {stats.posts.slice(0, 9).map((post) => (
                        <TweetCard key={post.id} post={post} onClick={setSelected} />
                      ))}
                    </div>
                  </CardBody>
                </Card>
              </>
            )
          )}
        </div>
      )}

      <TweetDetailModal post={selected} onClose={() => setSelected(null)} />
    </PageShell>
  )
}
