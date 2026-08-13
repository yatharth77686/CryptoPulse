import { NavLink } from "react-router-dom"
import {
  Activity,
  Compass,
  LayoutDashboard,
  LineChart,
  PieChart,
  Sparkles,
  X,
} from "lucide-react"
import { cn } from "@/lib/utils"

const NAV = [
  { to: "/", label: "Overview", icon: LayoutDashboard, end: true },
  { to: "/live", label: "Live Intelligence", icon: Activity },
  { to: "/explorer", label: "Crypto Explorer", icon: Compass },
  { to: "/market", label: "Market Reaction", icon: LineChart },
  { to: "/sentiment", label: "Sentiment", icon: PieChart },
  { to: "/analyze", label: "Analyze", icon: Sparkles },
]

export function Sidebar({ open, onClose }: { open: boolean; onClose: () => void }) {
  return (
    <>
      {/* Mobile overlay */}
      {open && (
        <div
          className="fixed inset-0 z-30 bg-black/60 backdrop-blur-sm lg:hidden"
          onClick={onClose}
          aria-hidden
        />
      )}

      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-40 flex w-60 flex-col border-r border-border bg-surface/95 backdrop-blur-md transition-transform duration-200 lg:static lg:translate-x-0",
          open ? "translate-x-0" : "-translate-x-full",
        )}
      >
        <div className="flex h-14 items-center justify-between gap-2 border-b border-border px-4">
          <div className="flex items-center gap-2.5">
            <span className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/15 text-primary">
              <Activity className="h-4.5 w-4.5" />
            </span>
            <div className="leading-tight">
              <p className="text-sm font-bold tracking-tight text-foreground">
                Crypto<span className="text-primary">Pulse</span>
              </p>
              <p className="text-[10px] uppercase tracking-widest text-muted">Intelligence</p>
            </div>
          </div>
          <button
            className="text-muted hover:text-foreground lg:hidden"
            onClick={onClose}
            aria-label="Close menu"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <nav className="flex-1 space-y-1 overflow-y-auto scrollbar-thin p-3">
          {NAV.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              onClick={onClose}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-primary/12 text-primary"
                    : "text-muted hover:bg-surface-2 hover:text-foreground",
                )
              }
            >
              {({ isActive }) => (
                <>
                  <Icon className={cn("h-4 w-4 shrink-0", isActive && "text-primary")} />
                  {label}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-border p-3">
          <p className="px-1 text-[10px] leading-relaxed text-muted">
            AI social-media intelligence. CryptoBERT + FinBERT + Binance reaction.
          </p>
        </div>
      </aside>
    </>
  )
}
