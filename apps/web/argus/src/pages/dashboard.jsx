import { useState, useEffect } from "react"
import { useParams, Link, useNavigate } from "react-router-dom"
import { InputField, btnPrimary, btnSecondary, sectionHeader, sectionTitle, progressBar, progressFill } from "@/components/common/styles"
import DashboardSummary from "@/components/dashboard/DashboardSummary"

const DashboardPage = ({ currentProject }) => {
  const [dashboardData, setDashboardData] = useState(null)
  const navigate = useNavigate()
  
  // Fetch dashboard data from memory or API
  useEffect(() => {
    // If we have a current project, load its data
    if (currentProject) {
      // In a full implementation, this would query the backend
      // for now, use placeholder data based on project type
      const mode = currentProject.mode || "investigate"
      setDashboardData(generateMockDashboard(mode))
    }
  }, [currentProject])
  
  const generateMockDashboard = (mode) => {
    const bases = {
      investigate: { novelty: 78, evidence: 64, feasibility: 89, impact: 81, gap: 71, breakpoint: 40 },
      break: { novelty: 65, evidence: 55, feasibility: 75, impact: 70, gap: 60, breakpoint: 75 },
      mirror: { novelty: 85, evidence: 70, feasibility: 80, impact: 85, gap: 80, breakpoint: 30 }
    }
    const b = bases[mode] || bases.investigate
    return {
      novelty: b.novelty,
      evidence: b.evidence,
      feasibility: b.feasibility,
      impact: b.impact,
      gap: b.gap,
      breakpoint: b.breakpoint
    }
  }
  
  const handleNewInvestigation = () => {
    navigate("/investigate")
  }
  
  if (!dashboardData) {
    return (
      <div className="p-8 text-[var(--text_secondary)]">
        <p>Load an investigation to see dashboard metrics</p>
      </div>
    )
  }
  
  return (
    <div>
      <DashboardSummary 
        novelty={dashboardData.novelty}
        evidence={dashboardData.evidence} 
        feasibility={dashboardData.feasibility}
        impact={dashboardData.impact}
        gap={dashboardData.gap}
        breakpoint={dashboardData.breakpoint}
        onNewInvestigation={handleNewInvestigation}
      />
    </div>
  )
}

export default DashboardPage