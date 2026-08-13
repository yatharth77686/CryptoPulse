import type {
  AnalysisResponse,
  AnalyzedPost,
  SentimentSummaryResponse,
  AnalyzeRequest,
  AnalyzeResponse,
  CryptoDetail,
  MarketResponse,
} from "@/types/api"

const BASE_URL = (import.meta.env.VITE_API_URL as string | undefined)?.replace(/\/$/, "") || "http://127.0.0.1:8000"

export class ApiError extends Error {
  status?: number
  constructor(message: string, status?: number) {
    super(message)
    this.name = "ApiError"
    this.status = status
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response
  try {
    res = await fetch(`${BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
      ...init,
    })
  } catch (err) {
    // Network / CORS / server down
    throw new ApiError(
      `Unable to reach the CryptoPulse API at ${BASE_URL}. Make sure the backend is running.`,
    )
  }

  if (!res.ok) {
    let detail = `Request failed (${res.status})`
    try {
      const body = await res.json()
      if (body?.detail) detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail)
    } catch {
      /* ignore parse errors */
    }
    throw new ApiError(detail, res.status)
  }

  return (await res.json()) as T
}

export const api = {
  baseUrl: BASE_URL,

  /** GET /analysis — all analyzed posts. */
  getAnalysis: async () => {
    const response = await request<AnalysisResponse>("/analysis")
    return response.results
  },

  /** GET /sentiment — aggregate sentiment (shape tolerant). */
  getSentiment: () => request<SentimentSummaryResponse>("/sentiment"),

  /** GET /crypto/{symbol} */
  getCrypto: (symbol: string) => request<CryptoDetail>(`/crypto/${encodeURIComponent(symbol.toUpperCase())}`),

  /** GET /market/{symbol} */
  getMarket: (symbol: string) => request<MarketResponse>(`/market/${encodeURIComponent(symbol.toUpperCase())}`),

  /** POST /analyze */
  analyze: (payload: AnalyzeRequest) =>
    request<AnalyzeResponse>("/analyze", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
}
