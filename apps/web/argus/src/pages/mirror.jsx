import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { InputField, btnPrimary, sectionHeader, sectionTitle } from "@/components/common/styles"

const MirrorPage = ({ navigate }) => {
  const [scenarios, setScenarios] = useState([])
  const [loading, setLoading] = useState(false)
  const navigateTo = useNavigate()
  
  const handleMirror = async () => {
    // In a full implementation, this would generate counterfactual scenarios
    // For the demo, we generate sample scenarios
    setLoading(true)
    
    const baseScenarios = [
      {
        name: "Best Case",
        type: "optimistic",
        assumption: "All assumptions hold true, optimal conditions",
        description: "Strong dataset quality, perfect hyperparameter tuning, ideal conditions",
        outcome: "Expected improvement: +10-12%",
        probability: "Low-Moderate"
      },
      {
        name: "Expected Case", 
        type: "realistic",
        assumption: "Normal conditions, moderate assumption validity",
        description: "Average dataset quality, reasonable hyperparameter tuning",
        outcome: "Expected improvement: +5-7%",
        probability: "High"
      },
      {
        name: "Failure Case",
        type: "pessimistic", 
        assumption: "Key assumptions fail, distribution shift",
        description: "Poor dataset quality, distribution shift, unexpected failure modes",
        outcome: "Expected: -1 to +2% or degradation",
        probability: "Moderate-Low"
      }
    ]
    
    setScenarios(baseScenarios)
    setLoading(false)
  }
  
  const handleNewInvestigation = () => {
    navigate("/investigate")
  }
  
  return (
    <div className="p-6">
      <sectionHeader>
        <sectionTitle>MIRROR</sectionTitle>
        <p className="text-[var(--muted)] mt-1">Counterfactual scenario analysis</p>
      </sectionHeader>
      
      <div className="mt-6 glass-panel p-6 rounded-lg">
        <button
          onClick={handleMirror}
          className="w-full btn-primary mb-6"
        >
          Generate Counterfactual Scenarios
        </button>
      </div>
      
      {scenarios.length > 0 && (
        <div className="mt-8">
          <sectionHeader>
            <sectionTitle>Counterfactual Scenarios</sectionTitle>
          </sectionHeader>
          
          {scenarios.map((scenario, idx) => (
            <div key={idx} className="p-4 rounded bg-[var(--card)] mb-4">
              <h3 className="font-medium text-[var(--accent)] mb-2">{scenario.name}</h3>
              <p className="text-sm text-[var(--muted)] mb-3">{scenario.description}</p>
              
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div>
                  <p className="text-[var(--muted)] text-xs">Type: {scenario.type}</p>
                  <p className="font-medium">{scenario.outcome}</p>
                </div>
                <div>
                  <p className="text-[var(--muted)] text-xs">Probability: {scenario.probability}</p>
                </div>
              </div>
            </div>
          ))}
          
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

export default MirrorPage