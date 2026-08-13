// TypeScript interfaces mirroring the CryptoPulse FastAPI responses.

export interface SentimentModelResult {
  label: string
  confidence: number
}

export interface PostSentiment {
  cryptobert: SentimentModelResult
  finbert: SentimentModelResult
}

export interface AssetInfo {
  primary: string | null
  mentioned: string[]
}

export interface SocialInfluence {
  score: number
  followers: number
  likes: number
  retweets: number
}

export interface PriceReaction {
  price: number
  change_percent: number
}

export interface MarketReactionEntry {
  symbol: string
  post_timestamp: string
  base_price: number
  "5m"?: PriceReaction
  "15m"?: PriceReaction
  "1h"?: PriceReaction
}

export type MarketReactionMap = Record<string, MarketReactionEntry>

export interface AnalyzedPost {
  id: number
  tweet_id: string
  author: string
  text: string
  timestamp: string
  assets: AssetInfo
  sentiment: PostSentiment
  social_influence: SocialInfluence
  signal_strength: number
  market_reaction: MarketReactionMap
}

// GET /analysis
export interface AnalysisResponse {
  count: number
  results: AnalyzedPost[]
}

// GET /crypto/{symbol}
export interface CryptoDetail {
  symbol: string
  count: number
  results: AnalyzedPost[]
}

// GET /market/{symbol}
export interface MarketReactionRecord {
  post_id: string
  timestamp: string
  sentiment: PostSentiment
  reaction: MarketReactionEntry
}

export interface MarketEndpointResponse {
  symbol: string
  count: number
  reactions: MarketReactionRecord[]
}

export interface MarketUnavailable {
  status: "unavailable"
  message: string
}

export type MarketResponse = MarketEndpointResponse | MarketUnavailable

// GET /sentiment
export interface SentimentSummaryResponse {
  model: string
  summary: {
    bullish: number
    bearish: number
    neutral: number
  }
  total_posts: number
}

// POST /analyze
export interface AnalyzeRequest {
  text: string
  followers?: number
  likes?: number
  retweets?: number
  timestamp?: string
}

export interface AnalyzeResponse {
  assets?: AssetInfo
  sentiment?: PostSentiment
  social_influence?: SocialInfluence
  signal_strength?: number
  market_reaction?: MarketReactionMap | MarketUnavailable
  [key: string]: unknown
}

export type SentimentBucket = "bullish" | "bearish" | "neutral"
export type SignalTier = "very-strong" | "strong" | "moderate" | "weak"
export type TimeWindow = "5m" | "15m" | "1h"
