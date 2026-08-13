import { useCallback, useEffect, useRef, useState } from "react"
import { ApiError } from "@/services/api"

interface PollingState<T> {
  data: T | null
  error: string | null
  isLoading: boolean
  isRefreshing: boolean
  lastUpdated: Date | null
  refresh: () => void
}

interface Options {
  /** Poll interval in ms. Pass 0 or undefined to disable auto-polling. */
  intervalMs?: number
  /** Whether the fetch should run at all. */
  enabled?: boolean
}

/**
 * Generic data hook with initial load, manual refresh, and optional polling.
 * Distinguishes the first load (isLoading) from background refreshes (isRefreshing)
 * so the UI never flashes skeletons on a poll tick.
 */
export function usePolling<T>(fetcher: () => Promise<T>, deps: unknown[], options: Options = {}): PollingState<T> {
  const { intervalMs = 0, enabled = true } = options
  const [data, setData] = useState<T | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  const fetcherRef = useRef(fetcher)
  fetcherRef.current = fetcher
  const hasLoaded = useRef(false)

  const load = useCallback(async (background: boolean) => {
    if (background) setIsRefreshing(true)
    else setIsLoading(true)
    try {
      const result = await fetcherRef.current()
      setData(result)
      setError(null)
      setLastUpdated(new Date())
      hasLoaded.current = true
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "Something went wrong while loading data."
      setError(message)
    } finally {
      setIsLoading(false)
      setIsRefreshing(false)
    }
  }, [])

  const refresh = useCallback(() => {
    load(hasLoaded.current)
  }, [load])

  useEffect(() => {
    if (!enabled) return
    load(false)
    if (!intervalMs) return
    const id = setInterval(() => load(true), intervalMs)
    return () => clearInterval(id)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [enabled, intervalMs, ...deps])

  return { data, error, isLoading, isRefreshing, lastUpdated, refresh }
}
