import { SlidersHorizontal } from "lucide-react"
import { Field, Select, TextInput, Toggle } from "@/components/common/Controls"
import { Card, CardBody } from "@/components/common/Card"
import type { FeedFilters } from "@/lib/filters"

export function FeedFilterBar({
  filters,
  symbols,
  onChange,
}: {
  filters: FeedFilters
  symbols: string[]
  onChange: (next: FeedFilters) => void
}) {
  const set = <K extends keyof FeedFilters>(key: K, value: FeedFilters[K]) =>
    onChange({ ...filters, [key]: value })

  return (
    <Card>
      <CardBody className="p-3">
        <div className="mb-3 flex items-center gap-2 text-xs font-medium uppercase tracking-wider text-muted">
          <SlidersHorizontal className="h-3.5 w-3.5 text-primary" />
          Filters
        </div>
        <div className="grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-6">
          <Field label="Crypto">
            <Select value={filters.crypto} onChange={(e) => set("crypto", e.target.value)}>
              <option value="">All assets</option>
              {symbols.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </Select>
          </Field>

          <Field label="Sentiment">
            <Select value={filters.sentiment} onChange={(e) => set("sentiment", e.target.value as FeedFilters["sentiment"])}>
              <option value="all">All</option>
              <option value="bullish">Bullish</option>
              <option value="bearish">Bearish</option>
              <option value="neutral">Neutral</option>
            </Select>
          </Field>

          <Field label="Min Signal">
            <TextInput
              type="number"
              min={0}
              step={1}
              value={filters.minSignal || ""}
              placeholder="0"
              onChange={(e) => set("minSignal", Number(e.target.value) || 0)}
            />
          </Field>

          <Field label="Time">
            <Select value={filters.timeWindow} onChange={(e) => set("timeWindow", e.target.value as FeedFilters["timeWindow"])}>
              <option value="all">All time</option>
              <option value="1h">Last 1h</option>
              <option value="6h">Last 6h</option>
              <option value="24h">Last 24h</option>
            </Select>
          </Field>

          <Field label="Sort by">
            <Select value={filters.sort} onChange={(e) => set("sort", e.target.value as FeedFilters["sort"])}>
              <option value="recent">Most recent</option>
              <option value="signal">Signal strength</option>
              <option value="influence">Social influence</option>
            </Select>
          </Field>

          <div className="flex items-end">
            <Toggle
              checked={filters.strongOnly}
              onChange={(v) => set("strongOnly", v)}
              label="Strong only"
            />
          </div>
        </div>
      </CardBody>
    </Card>
  )
}
