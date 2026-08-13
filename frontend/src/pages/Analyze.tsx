import { useState, type FormEvent } from "react"
import { Brain, Gauge, Send, Sparkles, Users } from "lucide-react"

import { PageShell } from "@/components/layout/PageShell"
import { Card, CardBody, CardHeader } from "@/components/common/Card"
import { ErrorState } from "@/components/common/States"
import {
  AssetTag,
  SentimentBadge,
  SignalTierBadge,
} from "@/components/common/Indicators"
import { ReactionDetail } from "@/components/market/ReactionCells"
import { api } from "@/services/api"
import type { AnalyzeResponse } from "@/types/api"


export function Analyze({ onMenu }: { onMenu: () => void }) {
  const [text, setText] = useState("")
  const [followers, setFollowers] = useState("10000")
  const [likes, setLikes] = useState("500")
  const [retweets, setRetweets] = useState("100")
  const [result, setResult] = useState<AnalyzeResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function submit(e: FormEvent) {
    e.preventDefault()

    if (!text.trim()) return

    setLoading(true)
    setError(null)

    try {
      const response = await api.analyze({
        text: text.trim(),
        followers: Number(followers) || 0,
        likes: Number(likes) || 0,
        retweets: Number(retweets) || 0,
        timestamp: new Date().toISOString(),
      })

      setResult(response)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Analysis failed"
      )
    } finally {
      setLoading(false)
    }
  }

  const primary = result?.assets?.primary
  const mentioned = result?.assets?.mentioned ?? []

  const reaction =
    primary &&
    result?.market_reaction &&
    !("status" in result.market_reaction)
      ? result.market_reaction[primary]
      : undefined

  const influence = result?.social_influence
  const signalStrength = result?.signal_strength


  return (
    <PageShell
      title="Analyze"
      subtitle="Run the CryptoPulse intelligence pipeline on text"
      onMenu={onMenu}
      lastUpdated={null}
    >
      <div className="grid gap-4 lg:grid-cols-2">

        {/* ================================================== */}
        {/* INPUT */}
        {/* ================================================== */}

        <Card>
          <CardHeader
            title="Manual Analysis"
            icon={<Sparkles className="h-4 w-4" />}
            subtitle="Uses the existing FastAPI /analyze endpoint"
          />

          <CardBody>
            <form onSubmit={submit} className="space-y-4">

              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Paste a crypto-related tweet or post..."
                className="min-h-40 w-full rounded-md border border-border bg-surface-2/40 p-3 text-sm outline-none focus:border-primary"
              />

              <div className="grid grid-cols-3 gap-2">

                <label className="space-y-1 text-xs text-muted">
                  <span>Followers</span>
                  <input
                    value={followers}
                    onChange={(e) => setFollowers(e.target.value)}
                    type="number"
                    min="0"
                    className="w-full rounded-md border border-border bg-surface-2/40 px-2 py-2 text-foreground outline-none focus:border-primary"
                  />
                </label>

                <label className="space-y-1 text-xs text-muted">
                  <span>Likes</span>
                  <input
                    value={likes}
                    onChange={(e) => setLikes(e.target.value)}
                    type="number"
                    min="0"
                    className="w-full rounded-md border border-border bg-surface-2/40 px-2 py-2 text-foreground outline-none focus:border-primary"
                  />
                </label>

                <label className="space-y-1 text-xs text-muted">
                  <span>Retweets</span>
                  <input
                    value={retweets}
                    onChange={(e) => setRetweets(e.target.value)}
                    type="number"
                    min="0"
                    className="w-full rounded-md border border-border bg-surface-2/40 px-2 py-2 text-foreground outline-none focus:border-primary"
                  />
                </label>

              </div>

              <button
                disabled={loading || !text.trim()}
                className="inline-flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground disabled:opacity-50"
              >
                <Send className="h-4 w-4" />

                {loading
                  ? "Analyzing..."
                  : "Analyze"}
              </button>

            </form>
          </CardBody>
        </Card>


        {/* ================================================== */}
        {/* RESULT */}
        {/* ================================================== */}

        <Card>

          <CardHeader
            title="Analysis Result"
            icon={<Brain className="h-4 w-4" />}
            subtitle="CryptoPulse intelligence report"
          />

          <CardBody>

            {error ? (

              <ErrorState message={error} />

            ) : !result ? (

              <div className="flex min-h-[300px] items-center justify-center text-center">
                <div>
                  <Brain className="mx-auto mb-3 h-8 w-8 text-muted" />

                  <p className="text-sm text-muted">
                    Submit text to generate an intelligence report.
                  </p>

                  <p className="mt-1 text-xs text-muted">
                    Crypto detection, sentiment, influence,
                    signal strength and market reaction will
                    appear here.
                  </p>
                </div>
              </div>

            ) : (

              <div className="space-y-4">

                {/* ========================================== */}
                {/* ASSET */}
                {/* ========================================== */}

                <section className="rounded-[var(--radius)] border border-border bg-surface-2/30 p-4">

                  <div className="flex items-start justify-between gap-3">

                    <div>
                      <p className="text-[10px] uppercase tracking-wider text-muted">
                        Primary Asset
                      </p>

                      <div className="mt-2 flex flex-wrap items-center gap-2">

                        {primary ? (
                          <AssetTag symbol={primary} />
                        ) : (
                          <span className="text-sm text-muted">
                            No asset detected
                          </span>
                        )}

                        {mentioned.map((asset) => (
                          <AssetTag
                            key={asset}
                            symbol={asset}
                            muted
                          />
                        ))}

                      </div>
                    </div>

                    {signalStrength != null && (
                      <SignalTierBadge
                        strength={signalStrength}
                      />
                    )}

                  </div>

                  <p className="mt-3 text-sm leading-relaxed text-foreground/90">
                    {text}
                  </p>

                </section>


                {/* ========================================== */}
                {/* SENTIMENT */}
                {/* ========================================== */}

                <section className="rounded-[var(--radius)] border border-border bg-surface-2/30 p-4">

                  <h4 className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted">
                    <Brain className="h-3.5 w-3.5 text-primary" />
                    Sentiment Models
                  </h4>

                  <div className="grid gap-3 sm:grid-cols-2">

                    <div className="rounded-md border border-border bg-surface px-3 py-3">

                      <p className="mb-2 text-[11px] text-muted">
                        CryptoBERT
                      </p>

                      <SentimentBadge
                        label={result.sentiment?.cryptobert?.label}
                        confidence={result.sentiment?.cryptobert?.confidence}
                      />

                    </div>

                    <div className="rounded-md border border-border bg-surface px-3 py-3">

                      <p className="mb-2 text-[11px] text-muted">
                        FinBERT
                      </p>

                      <SentimentBadge
                        label={result.sentiment?.finbert?.label}
                        confidence={result.sentiment?.finbert?.confidence}
                      />

                    </div>

                  </div>

                </section>


                {/* ========================================== */}
                {/* SIGNAL + INFLUENCE */}
                {/* ========================================== */}

                <div className="grid gap-4 sm:grid-cols-2">

                  {/* Signal */}

                  <section className="rounded-[var(--radius)] border border-border bg-surface-2/30 p-4">

                    <h4 className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted">
                      <Gauge className="h-3.5 w-3.5 text-primary" />
                      Signal Strength
                    </h4>

                    <div className="flex items-center gap-2">

                      <span className="tabular text-3xl font-semibold text-primary">
                        {signalStrength != null
                          ? signalStrength.toFixed(2)
                          : "N/A"}
                      </span>

                      {signalStrength != null && (
                        <SignalTierBadge
                          strength={signalStrength}
                        />
                      )}

                    </div>

                    <p className="mt-2 text-[11px] leading-relaxed text-muted">
                      Combined signal importance based on sentiment confidence and social influence.
                    </p>

                  </section>


                  {/* Influence */}

                  <section className="rounded-[var(--radius)] border border-border bg-surface-2/30 p-4">

                    <h4 className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted">
                      <Users className="h-3.5 w-3.5 text-primary" />
                      Social Influence
                    </h4>

                    <span className="tabular text-3xl font-semibold text-foreground">
                      {influence?.score != null
                        ? influence.score.toFixed(2)
                        : "N/A"}
                    </span>

                    <div className="mt-3 grid grid-cols-3 gap-2">

                      <div className="rounded border border-border bg-surface px-2 py-2">
                        <p className="text-[9px] uppercase text-muted">
                          Followers
                        </p>
                        <p className="mt-1 text-xs font-semibold">
                          {influence?.followers?.toLocaleString() ?? "0"}
                        </p>
                      </div>

                      <div className="rounded border border-border bg-surface px-2 py-2">
                        <p className="text-[9px] uppercase text-muted">
                          Likes
                        </p>
                        <p className="mt-1 text-xs font-semibold">
                          {influence?.likes?.toLocaleString() ?? "0"}
                        </p>
                      </div>

                      <div className="rounded border border-border bg-surface px-2 py-2">
                        <p className="text-[9px] uppercase text-muted">
                          Retweets
                        </p>
                        <p className="mt-1 text-xs font-semibold">
                          {influence?.retweets?.toLocaleString() ?? "0"}
                        </p>
                      </div>

                    </div>

                  </section>

                </div>


                {/* ========================================== */}
                {/* MARKET REACTION */}
                {/* ========================================== */}

                <section className="rounded-[var(--radius)] border border-border bg-surface-2/30 p-4">

                  <h4 className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted">
                    <Gauge className="h-3.5 w-3.5 text-primary" />

                    Market Reaction
                    {primary && (
                      <span className="text-primary">
                        — {primary}
                      </span>
                    )}

                  </h4>

                  {reaction ? (

                    <ReactionDetail
                      entry={reaction}
                    />

                  ) : (

                    <p className="text-xs text-muted">
                      {result.market_reaction &&
                      "status" in result.market_reaction &&
                      typeof result.market_reaction.message === "string"
                        ? result.market_reaction.message
                        : "Market reaction unavailable for this analysis."}
                    </p>

                  )}

                </section>

              </div>
            )}

          </CardBody>
        </Card>

      </div>
    </PageShell>
  )
}