import type { ReactNode } from "react"
import { Header } from "@/components/layout/Header"

interface PageShellProps {
  title: string
  subtitle?: string
  lastUpdated: Date | null
  isRefreshing?: boolean
  onRefresh?: () => void
  onMenu: () => void
  live?: boolean
  children: ReactNode
}

export function PageShell({ children, ...header }: PageShellProps) {
  return (
    <>
      <Header {...header} />
      <main className="flex-1 overflow-y-auto scrollbar-thin p-4 sm:p-5 lg:p-6">
        <div className="mx-auto max-w-[1400px] animate-fade-in-up">{children}</div>
      </main>
    </>
  )
}
