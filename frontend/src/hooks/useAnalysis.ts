import { useMemo } from "react"
import { api } from "@/services/api"
import { usePolling } from "@/hooks/usePolling"
import { safeAvg, toSentimentBucket } from "@/lib/utils"
import type { AnalyzedPost, SentimentBucket } from "@/types/api"

const POLL_INTERVAL = 30_000

/** Fetch all analyzed posts with 30s polling. */
export function useAnalysis(options?: { poll?: boolean }) {
  return usePolling<AnalyzedPost[]>(() => api.getAnalysis(), [], {
    intervalMs: options?.poll === false ? 0 : POLL_INTERVAL,
  })
}

export interface DashboardMetrics {
  total: number
  bullish: number
  bearish: number
  neutral: number
  avgSignal: number | null
  avgInfluence: number | null
  sentimentBreakdown: { bucket: SentimentBucket; count: number }[]
}

/** Derive all KPI/dashboard metrics purely from /analysis data (never invented). */
export function computeMetrics(posts: AnalyzedPost[] | null): DashboardMetrics {
  const list = posts ?? []
  let bullish = 0
  let bearish = 0
  let neutral = 0

  for (const p of list) {
    const bucket = toSentimentBucket(p.sentiment?.cryptobert?.label)
    if (bucket === "bullish") bullish++
    else if (bucket === "bearish") bearish++
    else neutral++
  }

  return {
    total: list.length,
    bullish,
    bearish,
    neutral,
    avgSignal: safeAvg(list.map((p) => p.signal_strength)),
    avgInfluence: safeAvg(list.map((p) => p.social_influence?.score)),
    sentimentBreakdown: [
      { bucket: "bullish", count: bullish },
      { bucket: "bearish", count: bearish },
      { bucket: "neutral", count: neutral },
    ],
  }
}

export function useMetrics(posts: AnalyzedPost[] | null): DashboardMetrics {
  return useMemo(() => computeMetrics(posts), [posts])
}
