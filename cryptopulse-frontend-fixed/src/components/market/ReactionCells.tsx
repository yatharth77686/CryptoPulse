import { cn, formatPercent, formatPrice } from "@/lib/utils"
import type { MarketReactionEntry, PriceReaction, TimeWindow } from "@/types/api"

const WINDOWS: TimeWindow[] = ["5m", "15m", "1h"]

function changeColor(v: number | null | undefined) {
  if (v == null || Number.isNaN(v)) return "text-muted"
  if (v > 0) return "text-bullish"
  if (v < 0) return "text-bearish"
  return "text-neutral"
}

/** Compact 5m/15m/1h percentage row used in tweet cards. */
export function ReactionRow({ entry }: { entry: MarketReactionEntry | undefined }) {
  return (
    <div className="grid grid-cols-3 gap-1.5">
      {WINDOWS.map((w) => {
        const r = entry?.[w] as PriceReaction | undefined
        return (
          <div key={w} className="rounded border border-border bg-surface-2/50 px-2 py-1.5 text-center">
            <p className="text-[10px] uppercase tracking-wider text-muted">{w}</p>
            <p className={cn("tabular text-xs font-semibold", changeColor(r?.change_percent))}>
              {formatPercent(r?.change_percent)}
            </p>
          </div>
        )
      })}
    </div>
  )
}

/** Detailed reaction block with price + percent, used in modal & market page. */
export function ReactionDetail({ entry }: { entry: MarketReactionEntry | undefined }) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between rounded-md border border-border bg-surface-2/40 px-3 py-2">
        <span className="text-xs text-muted">Base price</span>
        <span className="tabular text-sm font-semibold text-foreground">{formatPrice(entry?.base_price)}</span>
      </div>
      <div className="grid grid-cols-3 gap-2">
        {WINDOWS.map((w) => {
          const r = entry?.[w] as PriceReaction | undefined
          return (
            <div key={w} className="rounded-md border border-border bg-surface-2/40 p-2.5 text-center">
              <p className="text-[10px] uppercase tracking-wider text-muted">{w} reaction</p>
              <p className={cn("tabular mt-1 text-sm font-semibold", changeColor(r?.change_percent))}>
                {formatPercent(r?.change_percent)}
              </p>
              <p className="tabular mt-0.5 text-[11px] text-muted">{formatPrice(r?.price)}</p>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export { changeColor, WINDOWS }
