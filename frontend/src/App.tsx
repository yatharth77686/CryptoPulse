import { useState } from "react"
import { Route, Routes } from "react-router-dom"
import { Sidebar } from "@/components/layout/Sidebar"
import { AnalysisProvider } from "@/context/AnalysisContext"
import { Dashboard } from "@/pages/Dashboard"
import { LiveIntelligence } from "@/pages/LiveIntelligence"
import { CryptoExplorer } from "@/pages/CryptoExplorer"
import { MarketReaction } from "@/pages/MarketReaction"
import { Sentiment } from "@/pages/Sentiment"
import { Analyze } from "@/pages/Analyze"

export default function App() {
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <AnalysisProvider>
      <div className="flex min-h-screen bg-background text-foreground">
        <Sidebar open={menuOpen} onClose={() => setMenuOpen(false)} />
        <div className="flex min-w-0 flex-1 flex-col">
          <Routes>
            <Route path="/" element={<Dashboard onMenu={() => setMenuOpen(true)} />} />
            <Route path="/live" element={<LiveIntelligence onMenu={() => setMenuOpen(true)} />} />
            <Route path="/explorer" element={<CryptoExplorer onMenu={() => setMenuOpen(true)} />} />
            <Route path="/market" element={<MarketReaction onMenu={() => setMenuOpen(true)} />} />
            <Route path="/sentiment" element={<Sentiment onMenu={() => setMenuOpen(true)} />} />
            <Route path="/analyze" element={<Analyze onMenu={() => setMenuOpen(true)} />} />
          </Routes>
        </div>
      </div>
    </AnalysisProvider>
  )
}
