import { useMemo, useState } from "react"
import { SearchX } from "lucide-react"
import { PageShell } from "@/components/layout/PageShell"
import { Card } from "@/components/common/Card"
import { EmptyState, ErrorState, Skeleton } from "@/components/common/States"
import { FeedFilterBar } from "@/components/tweets/FeedFilters"
import { TweetCard } from "@/components/tweets/TweetCard"
import { TweetDetailModal } from "@/components/tweets/TweetDetailModal"
import { useAnalysisContext } from "@/context/AnalysisContext"
import { applyFilters, DEFAULT_FILTERS, extractSymbols, type FeedFilters } from "@/lib/filters"
import type { AnalyzedPost } from "@/types/api"

export function LiveIntelligence({ onMenu }: { onMenu: () => void }) {
  const { data, error, isLoading, isRefreshing, lastUpdated, refresh } = useAnalysisContext()
  const [filters, setFilters] = useState<FeedFilters>(DEFAULT_FILTERS)
  const [selected, setSelected] = useState<AnalyzedPost | null>(null)

  const symbols = useMemo(() => extractSymbols(data), [data])
  const filtered = useMemo(() => applyFilters(data, filters), [data, filters])

  return (
  <>
    <PageShell
      title="Live Intelligence"
      subtitle={`${filtered.length} of ${data?.length ?? 0} analyzed posts`}
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
          <FeedFilterBar
            filters={filters}
            symbols={symbols}
            onChange={setFilters}
          />

          {isLoading ? (
            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
              {Array.from({ length: 6 }).map((_, i) => (
                <Skeleton key={i} className="h-64" />
              ))}
            </div>
          ) : filtered.length === 0 ? (
            <Card>
              <EmptyState
                title="No posts match your filters"
                description="Try widening the time window or lowering the minimum signal strength."
                icon={<SearchX className="h-5 w-5" />}
              />
            </Card>
          ) : (
            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
              {filtered.map((post) => (
                <TweetCard
                  key={post.id}
                  post={post}
                  onClick={setSelected}
                />
              ))}
            </div>
          )}
        </div>
      )}
    </PageShell>

    {/* Keep modal outside the scrollable PageShell */}
    <TweetDetailModal
      post={selected}
      onClose={() => setSelected(null)}
    />
  </>
  )
}