import { Gauge, Heart, Repeat2, Users } from "lucide-react"
import { formatCompact, timeAgo } from "@/lib/utils"
import { AssetTag, SentimentBadge, SignalTierBadge } from "@/components/common/Indicators"
import { ReactionRow } from "@/components/market/ReactionCells"
import type { AnalyzedPost } from "@/types/api"

export function TweetCard({
  post,
  onClick,
}: {
  post: AnalyzedPost
  onClick?: (post: AnalyzedPost) => void
}) {
  const primary = post.assets?.primary
  const mentioned = post.assets?.mentioned ?? []
  const reaction = primary ? post.market_reaction?.[primary] : undefined
  const influence = post.social_influence

  return (
    <article
      onClick={() => onClick?.(post)}
      className="group cursor-pointer rounded-[var(--radius)] border border-border bg-surface/80 p-4 transition-all hover:border-primary/40 hover:bg-surface"
    >
      <header className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2.5 min-w-0">
          <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-surface-2 text-xs font-semibold text-primary">
            {post.author?.slice(0, 2).toUpperCase() ?? "??"}
          </span>
          <div className="min-w-0">
            <p className="truncate text-sm font-medium text-foreground">@{post.author ?? "unknown"}</p>
            <p className="text-[11px] tabular text-muted">{timeAgo(post.timestamp)}</p>
          </div>
        </div>
        <div className="flex shrink-0 flex-wrap items-center justify-end gap-1">
          {primary ? <AssetTag symbol={primary} /> : <span className="text-[11px] text-muted">No asset</span>}
          {mentioned.slice(0, 2).map((m) => (
            <AssetTag key={m} symbol={m} muted />
          ))}
        </div>
      </header>

      <p className="mt-3 line-clamp-2 text-sm leading-relaxed text-foreground/90">{post.text}</p>

      <div className="mt-3 flex flex-wrap items-center gap-2">
        <SentimentBadge label={post.sentiment?.cryptobert?.label} confidence={post.sentiment?.cryptobert?.confidence} size="sm" />
        <span className="text-[10px] text-muted">CryptoBERT</span>
        <SentimentBadge label={post.sentiment?.finbert?.label} confidence={post.sentiment?.finbert?.confidence} size="sm" />
        <span className="text-[10px] text-muted">FinBERT</span>
      </div>

      <div className="mt-3 grid grid-cols-2 gap-2 border-t border-border pt-3">
        <div className="rounded border border-border bg-surface-2/40 px-2.5 py-1.5">
          <p className="flex items-center gap-1 text-[10px] uppercase tracking-wider text-muted">
            <Gauge className="h-3 w-3" /> Signal
          </p>
          <div className="mt-0.5 flex items-center justify-between">
            <span className="tabular text-sm font-semibold text-primary">
              {post.signal_strength != null ? post.signal_strength.toFixed(2) : "N/A"}
            </span>
            <SignalTierBadge strength={post.signal_strength} />
          </div>
        </div>
        <div className="rounded border border-border bg-surface-2/40 px-2.5 py-1.5">
          <p className="flex items-center gap-1 text-[10px] uppercase tracking-wider text-muted">
            <Users className="h-3 w-3" /> Influence
          </p>
          <div className="mt-0.5 flex items-center justify-between">
            <span className="tabular text-sm font-semibold text-foreground">
              {influence?.score != null ? influence.score.toFixed(2) : "N/A"}
            </span>
            <span className="flex items-center gap-2 text-[10px] tabular text-muted">
              <span className="flex items-center gap-0.5">
                <Users className="h-3 w-3" />
                {formatCompact(influence?.followers)}
              </span>
              <span className="flex items-center gap-0.5">
                <Heart className="h-3 w-3" />
                {formatCompact(influence?.likes)}
              </span>
              <span className="flex items-center gap-0.5">
                <Repeat2 className="h-3 w-3" />
                {formatCompact(influence?.retweets)}
              </span>
            </span>
          </div>
        </div>
      </div>

      {primary && (
        <div className="mt-2">
          <ReactionRow entry={reaction} />
        </div>
      )}
    </article>
  )
}
