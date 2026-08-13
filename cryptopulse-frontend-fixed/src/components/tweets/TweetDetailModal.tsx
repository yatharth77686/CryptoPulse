import { useEffect } from "react"
import { Brain, Gauge, Heart, Repeat2, Users, X } from "lucide-react"
import { cn, formatCompact, formatDateTime, formatNumber } from "@/lib/utils"
import { AssetTag, SentimentBadge, SignalTierBadge } from "@/components/common/Indicators"
import { ReactionDetail } from "@/components/market/ReactionCells"
import type { AnalyzedPost } from "@/types/api"

function Section({ title, icon, children }: { title: string; icon: React.ReactNode; children: React.ReactNode }) {
  return (
    <section className="rounded-[var(--radius)] border border-border bg-surface-2/30 p-4">
      <h4 className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted">
        <span className="text-primary">{icon}</span>
        {title}
      </h4>
      {children}
    </section>
  )
}

function Stat({ label, value, className }: { label: string; value: string; className?: string }) {
  return (
    <div className="rounded-md border border-border bg-surface px-3 py-2">
      <p className="text-[10px] uppercase tracking-wider text-muted">{label}</p>
      <p className={cn("tabular mt-0.5 text-sm font-semibold text-foreground", className)}>{value}</p>
    </div>
  )
}

export function TweetDetailModal({ post, onClose }: { post: AnalyzedPost | null; onClose: () => void }) {
  useEffect(() => {
    if (!post) return
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose()
    document.addEventListener("keydown", onKey)
    document.body.style.overflow = "hidden"
    return () => {
      document.removeEventListener("keydown", onKey)
      document.body.style.overflow = ""
    }
  }, [post, onClose])

  if (!post) return null

  const primary = post.assets?.primary
  const mentioned = post.assets?.mentioned ?? []
  const reaction = primary ? post.market_reaction?.[primary] : undefined
  const influence = post.social_influence

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/70 p-4 backdrop-blur-sm sm:items-center"
      onClick={onClose}
    >
      <div
        className="relative w-full max-w-2xl animate-fade-in-up rounded-xl border border-border-strong bg-surface shadow-2xl"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-label="Tweet intelligence report"
      >
        {/* Header */}
        <div className="flex items-start justify-between gap-3 border-b border-border p-4">
          <div className="flex items-center gap-2">
            <span className="flex h-9 w-9 items-center justify-center rounded-md bg-primary/15 text-primary">
              <Brain className="h-5 w-5" />
            </span>
            <div>
              <p className="text-sm font-semibold text-foreground">Intelligence Report</p>
              <p className="text-[11px] tabular text-muted">Tweet #{post.tweet_id}</p>
            </div>
          </div>
          <button onClick={onClose} className="text-muted hover:text-foreground" aria-label="Close">
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="max-h-[75vh] space-y-4 overflow-y-auto scrollbar-thin p-4">
          {/* Tweet */}
          <section className="rounded-[var(--radius)] border border-border bg-surface-2/30 p-4">
            <div className="flex items-center justify-between gap-2">
              <p className="text-sm font-medium text-foreground">@{post.author ?? "unknown"}</p>
              <p className="text-[11px] tabular text-muted">{formatDateTime(post.timestamp)}</p>
            </div>
            <p className="mt-2 text-sm leading-relaxed text-foreground/90">{post.text}</p>
            <div className="mt-3 flex flex-wrap items-center gap-1.5">
              <span className="text-[10px] uppercase tracking-wider text-muted">Detected assets:</span>
              {primary ? <AssetTag symbol={primary} /> : <span className="text-xs text-muted">N/A</span>}
              {mentioned.map((m) => (
                <AssetTag key={m} symbol={m} muted />
              ))}
            </div>
          </section>

          <div className="grid gap-4 sm:grid-cols-2">
            {/* Sentiment */}
            <Section title="Sentiment Models" icon={<Brain className="h-3.5 w-3.5" />}>
              <div className="space-y-3">
                <div>
                  <p className="mb-1.5 text-[11px] text-muted">CryptoBERT</p>
                  <SentimentBadge
                    label={post.sentiment?.cryptobert?.label}
                    confidence={post.sentiment?.cryptobert?.confidence}
                  />
                </div>
                <div>
                  <p className="mb-1.5 text-[11px] text-muted">FinBERT</p>
                  <SentimentBadge
                    label={post.sentiment?.finbert?.label}
                    confidence={post.sentiment?.finbert?.confidence}
                  />
                </div>
              </div>
            </Section>

            {/* Signal */}
            <Section title="Signal Strength" icon={<Gauge className="h-3.5 w-3.5" />}>
              <div className="flex items-baseline gap-2">
                <span className="tabular text-3xl font-semibold text-primary">
                  {post.signal_strength != null ? post.signal_strength.toFixed(2) : "N/A"}
                </span>
                <SignalTierBadge strength={post.signal_strength} />
              </div>
              <p className="mt-2 text-[11px] leading-relaxed text-muted">
                Importance of this tweet as a crypto trading signal.
              </p>
            </Section>
          </div>

          {/* Social influence */}
          <Section title="Social Influence" icon={<Users className="h-3.5 w-3.5" />}>
            <div className="mb-3 flex items-baseline gap-2">
              <span className="tabular text-2xl font-semibold text-foreground">
                {influence?.score != null ? influence.score.toFixed(2) : "N/A"}
              </span>
              <span className="text-[11px] text-muted">influence score</span>
            </div>
            <div className="grid grid-cols-3 gap-2">
              <Stat label="Followers" value={formatNumber(influence?.followers)} />
              <Stat label="Likes" value={formatCompact(influence?.likes)} />
              <Stat label="Retweets" value={formatCompact(influence?.retweets)} />
            </div>
            <p className="mt-2 text-[11px] leading-relaxed text-muted">
              Influence of the account/tweet — distinct from signal strength.
            </p>
          </Section>

          {/* Market reaction */}
          <Section title={`Market Reaction${primary ? ` — ${primary}` : ""}`} icon={<Gauge className="h-3.5 w-3.5" />}>
            {primary && reaction ? (
              <ReactionDetail entry={reaction} />
            ) : (
              <p className="text-xs text-muted">Market reaction unavailable for this post.</p>
            )}
          </Section>
        </div>
      </div>
    </div>
  )
}
