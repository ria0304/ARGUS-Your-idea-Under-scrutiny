import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { InputField, btnPrimary, btnSecondary, sectionHeader, sectionTitle } from "@/components/common/styles"
import DashboardSummary from "@/components/dashboard/DashboardSummary"

const BreakPage = ({ navigate, setMode, currentProject }) => {
  const [ideas, setIdeas] = useState("")
  const [breakResults, setBreakResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const navigateTo = useNavigate()
  
  const handleBreakIt = async () => {
    if (!ideas.trim()) return
    setLoading(true)
    try {
      const response = await fetch("/break-it", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ idea: ideas, mode: "break" }),
      })
      const data = await response.json()
      setBreakResults(data.data)
    } catch (error) {
      console.error("Break-it failed:", error)
    } finally {
      setLoading(false)
    }
  }
  
  const handleNewInvestigation = () => {
    navigateTo("/investigate")
  }
  
  return (
    <div className="p-6">
      <sectionHeader>
        <sectionTitle>#BREAK_IT</sectionTitle>
        <p className="text-[var(--muted)] mt-1">Try to break this idea before building it</p>
      </sectionHeader>
      
      <div className="mt-6 glass-panel p-6 rounded-lg">
        <textarea
          className="w-full input-field h-40 p-3 resize-y focus:outline-none focus:shadow-outline"
          placeholder="Paste your research idea, claim, or proposal to stress-test..."
          value={ideas}
          onChange={(e) => setIdeas(e.target.value)}
          disabled={loading}
        />
      </div>
      
      {loading && (
        <p className="mt-4 text-[var(--muted)]">ARGUS is breaking down your idea...</p>
      )}
      
      {breakResults && (
        <div className="mt-8 glass-panel p-6 rounded-lg">
          <sectionHeader>
            <sectionTitle>Breakdown Analysis</sectionTitle>
          </sectionHeader>
          
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <p className="text-sm text-[var(--muted)] mb-2">Overall Assessment</p>
              <p className={`font-medium ${breakResults.overall_assessment.includes("CRITICAL") ? "text-[var(--danger)]" : ""}`}>{breakResults.overall_assessment}</p>
            </div>
            
            <div>
              <p className="text-sm text-[var(--muted)] mb-2">Scenarios Tested</p>
              <p className="font-medium">{breakResults.scenarios_tested || 0}</p>
            </div>
          </div>
          
          {breakResults.breakpoints && breakResults.breakpoints.length > 0 && (
            <div className="mt-6">
              <p className="text-sm text-[var(--muted)] mb-2">Breakpoints Identified</p>
              <ul className="space-y-2 text-sm">
                {breakResults.breakpoints.map((bp, idx) => (
                  <li key={idx} className="p-3 rounded bg-[var(--card)]">
                    <p className="font-medium">{bp.assumption.substring(0, 60) + (bp.assumption.length > 60 ? "..." : "")}</p>
                    <p className="text-[var(--muted)] text-xs">Severity: {bp.severity}</p>
                    <p className="text-[var(--muted)] text-xs mt-1">Threshold: {bp.threshold}</p>
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          <div className="mt-6">
            <button
              onClick={handleNewInvestigation}
              className="w-full btn-secondary text-sm"
            >
              New Investigation
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default BreakPage