import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { InputField, btnPrimary, btnSecondary, sectionHeader, sectionTitle } from "@/components/common/styles"
import DashboardSummary from "@/components/dashboard/DashboardSummary"

const InvestigationPage = ({ navigate, setMode, currentProject }) => {
  const [idea, setIdea] = useState("")
  const [loading, setLoading] = useState(false)
  const navigateTo = useNavigate()
  
  const handleInvestigate = async () => {
    if (!idea.trim()) return
    setLoading(true)
    try {
      const response = await fetch("/investigate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ idea, mode }),
      })
      const data = await response.json()
      
      if (data.data && data.data.project_id) {
        // Store project in localStorage
        localStorage.setItem("argus_current_project", JSON.stringify({
          project_id: data.data.project_id,
          project_name: data.data.extracted_ideas?.goal || "ARGUS Investigation",
          goal: data.data.extracted_ideas?.goal || "Investigation",
          mode
        }))
        navigateTo("/dashboard")
      } else {
        // Show key results
        const novelty = data.data.novelty?.score || "N/A"
        const feasibility = data.data.feasibility?.score || "N/A"
        const impact = data.data.impact?.score || "N/A"
        const gap = data.data.gap || "N/A"
        
        alert(`ARGUS Investigation Results\n\n` +
          `Novelty: ${novity}%\n` +
          `Feasibility: ${feasibility}/10\n` +
          `Impact: ${impact}/10\n` +
          `Research Gap: ${gap}%\n\n` +
          `Click "Dashboard" to see full analysis.`)
      }
    } catch (error) {
      console.error("Investigation failed:", error)
      alert("ARGUS investigation failed. Please try again.")
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
        <sectionTitle>Investigate Idea</sectionTitle>
      </sectionHeader>
      
      <div className="mt-6 glass-panel p-6 rounded-lg">
        <textarea
          className="w-full input-field h-40 p-3 resize-y focus:outline-none focus:shadow-outline"
          placeholder="Paste your research idea, decision, claim, or proposal..."
          value={idea}
          onChange={(e) => setIdea(e.target.value)}
          disabled={loading}
        />
      </div>
      
      <div className="mt-6">
        <button
          onClick={handleInvestigate}
          className={btnPrimary} disabled={loading}
        >
          {loading ? "Investigating..." : "Run ARGUS Investigation"}
        </button>
        <button
          onClick={() => navigateTo("/dashboard")}
          className={btnSecondary}
        >
          View Dashboard
        </button>
      </div>
      
      {loading && (
        <p className="mt-4 text-[var(--muted)]">ARGUS is investigating your idea...</p>
      )}
    </div>
  )
}

export default InvestigationPage