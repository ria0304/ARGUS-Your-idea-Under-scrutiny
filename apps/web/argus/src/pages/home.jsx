import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { InputField, btnPrimary, sectionHeader, sectionTitle } from "@/components/common/styles"

const HomePage = ({ navigate }) => {
  const [idea, setIdea] = useState("")
  const [loading, setLoading] = useState(false)

  const handleInvestigate = async () => {
    if (!idea.trim()) return
    setLoading(true)
    try {
      const response = await fetch("/investigate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ idea, mode: "investigate" }),
      })
      const data = await response.json()
      
      if (data.data && data.data.project_id) {
        // Store project in localStorage
        localStorage.setItem("argus_current_project", JSON.stringify({
          project_id: data.data.project_id,
          project_name: data.data.extracted_ideas?.goal || "ARGUS Investigation",
          goal: data.data.extracted_ideas?.goal || "Investigation",
          mode: "investigate"
        }))
        navigate("/dashboard")
      } else {
        // Show investigation results inline or redirect
        alert("ARGUS Investigation Complete\n\n" + 
          `Novelty: ${data.data.novelty?.score || 'N/A'}%\n` +
          `Feasibility: ${data.data.feasibility?.score || 'N/A'}/10\n` +
          `Impact: ${data.data.impact?.score || 'N/A'}/10\n` +
          `Gap: ${data.data.gap || 'N/A'}`)
      }
    } catch (error) {
      console.error("Investigation failed:", error)
      alert("ARGUS investigation failed. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto p-6">
      <sectionHeader>
        <sectionTitle>Investigate an Idea</sectionTitle>
      </sectionHeader>
      
      <div className="mt-6 glass-panel p-6 rounded-lg">
        <textarea
          className="w-full input-field h-24 p-3 resize-none focus:outline-none focus:shadow-outline"
          placeholder="Paste your research idea, decision, claim, or proposal..."
          value={idea}
          onChange={(e) => setIdea(e.target.value)}
          disabled={loading}
        />
      </div>
      
      <div className="mt-8">
        <button
          onClick={handleInvestigate}
          className={btnPrimary} disabled={loading}
        >
          {loading ? "Investigating..." : "Investigate Idea"}
        </button>
      </div>
      
      {loading && (
        <p className="mt-4 text-[var(--muted)]">ARGUS is investigating your idea...</p>
      )}
    </div>
  )
}

export default HomePage