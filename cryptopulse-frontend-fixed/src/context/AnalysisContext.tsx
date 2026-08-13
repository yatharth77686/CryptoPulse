import { createContext, useContext, type ReactNode } from "react"
import { useAnalysis } from "@/hooks/useAnalysis"
import type { AnalyzedPost } from "@/types/api"

interface AnalysisContextValue {
  data: AnalyzedPost[] | null
  error: string | null
  isLoading: boolean
  isRefreshing: boolean
  lastUpdated: Date | null
  refresh: () => void
}

const AnalysisContext = createContext<AnalysisContextValue | null>(null)

export function AnalysisProvider({ children }: { children: ReactNode }) {
  const state = useAnalysis()
  return <AnalysisContext.Provider value={state}>{children}</AnalysisContext.Provider>
}

export function useAnalysisContext(): AnalysisContextValue {
  const ctx = useContext(AnalysisContext)
  if (!ctx) throw new Error("useAnalysisContext must be used within AnalysisProvider")
  return ctx
}
