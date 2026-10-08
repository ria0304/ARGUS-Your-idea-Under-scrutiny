import { cn } from "../utils"

// Dashboard Summary Component
const DashboardSummary = ({
  novelty,
  evidence,
  feasibility,
  impact,
  gap,
  breakpoint,
  onNewInvestigation
}) => {
  const noveltyColor = novelty > 70 ? "text-[var(--accent)]" : novelty > 40 ? "text-[#e6a817]" : "text-[var(--danger)]"
  const feasibilityColor = feasibility > 80 ? "text-[var(--accent)]" : feasibility > 50 ? "text-[#e6a817]" : "text-[var(--danger)]"
  const gapColor = gap > 70 ? "text-[var(--accent)]" : gap > 40 ? "text-[#e6a817]" : "text-[var(--danger)]"
  
  return (
    <div>
      <sectionHeader>
        <sectionTitle>Idea Health</sectionTitle>
      </sectionHeader>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        <div>
          <p className="text-xs text-[var(--muted)] uppercase tracking-wider">Novelty</p>
          <div className="h-4 bg-[var(--border)] rounded-full overflow-hidden">
            <div 
              className={`h-full progress-fill bg-[var(--accent)] transition-width ease-out ${novelty > 0 ? `width-${novelty}%` : ""} ${noveltyColor}`}
              style={{width: `${novelty}%`}}
            />
          </div>
          <p className="text-[var(--accent)] mt-1 font-medium">{novelty}%</p>
        </div>
        
        <div>
          <p className="text-xs text-[var(--muted)] uppercase tracking-wider">Evidence</p>
          <div className="h-4 bg-[var(--border)] rounded-full overflow-hidden">
            <div 
              className={`h-full progress-fill bg-[var(--accent)] transition-width ease-out ${evidence > 0 ? `width-${evidence}%` : ""}`}
              style={{width: `${evidence}%`}}
            />
          </div>
          <p className="text-[var(--accent)] mt-1 font-medium">{evidence}%</p>
        </div>
        
        <div>
          <p className="text-xs text-[var(--muted)] uppercase tracking-wider">Feasibility</p>
          <div className="h-4 bg-[var(--border)] rounded-full overflow-hidden">
            <div 
              className={`h-full progress-fill ${feasibilityColor} transition-width ease-out ${feasibility > 0 ? `width-${feasibility}%` : ""}`}
              style={{width: `${feasibility}%`}}
            />
          </div>
          <p className="text-[var(--accent)] mt-1 font-medium">{feasibility}%</p>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        <div>
          <p className="text-xs text-[var(--muted)] uppercase tracking-wider">Impact</p>
          <div className="h-4 bg-[var(--border)] rounded-full overflow-hidden">
            <div 
              className={`h-full progress-fill bg-[var(--accent)] transition-width ease-out ${impact > 0 ? `width-${impact}%` : ""}`}
              style={{width: `${impact}%`}}
            />
          </div>
          <p className="text-[var(--accent)] mt-1 font-medium">{impact}%</p>
        </div>
        
        <div>
          <p className="text-xs text-[var(--muted)] uppercase tracking-wider">Research Gap</p>
          <div className="h-4 bg-[var(--border)] rounded-full overflow-hidden">
            <div 
              className={`h-full progress-fill ${gapColor} transition-width ease-out ${gap > 0 ? `width-${gap}%` : ""}`}
              style={{width: `${gap}%`}}
            />
          </div>
          <p className="text-[var(--accent)] mt-1 font-medium">{gap}%</p>
        </div>
        
        <div>
          <p className="text-xs text-[var(--muted)] uppercase tracking-wider">Breakpoint</p>
          <div className="h-4 bg-[var(--border)] rounded-full overflow-hidden">
            <div 
              className={`h-full progress-fill ${breakpoint > 60 ? "text-[var(--danger)]" : "text-[var(--accent)]"} transition-width ease-out ${breakpoint > 0 ? `width-${breakpoint}%` : ""}`}
              style={{width: `${breakpoint}%`}}
            />
          </div>
          <p className={`mt-1 font-medium ${breakpoint > 60 ? "text-[var(--danger)]" : "text-[var(--accent)]"}`}>{breakpoint}%</p>
        </div>
      </div>
      
      <div>
        <button
          onClick={onNewInvestigation}
          className="w-full mt-4 px-6 py-2 btn-primary text-sm"
        >
          New Investigation
        </button>
      </div>
    </div>
  )
}

export default DashboardSummary