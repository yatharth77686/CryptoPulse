import { api } from "@/services/api"
import { usePolling } from "@/hooks/usePolling"
import type { CryptoDetail, MarketResponse } from "@/types/api"

export function useMarketReaction(symbol: string | null) {
  return usePolling<MarketResponse>(() => api.getMarket(symbol as string), [symbol], {
    enabled: !!symbol,
  })
}

export function useCrypto(symbol: string | null) {
  return usePolling<CryptoDetail>(() => api.getCrypto(symbol as string), [symbol], {
    enabled: !!symbol,
  })
}
