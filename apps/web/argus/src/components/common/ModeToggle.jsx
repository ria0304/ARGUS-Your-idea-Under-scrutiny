import { cn } from "./utils"

const ModeToggle = ({ setMode, currentMode }) => {
  const modes = [
    { key: "investigate", label: "Investigate", color: "var(--accent)" },
    { key: "break", label: "Break It", color: "var(--danger)" },
    { key: "mirror", label: "Mirror", color: "#64b5f6" }
  ]
  
  return (
    <div className="flex gap-2">
      {modes.map(({ key, label, color }) => {
        const isActive = currentMode === key
        const baseClasses = "px-4 py-2 rounded text-sm font-medium transition-all"
        const activeClasses = `bg-${color} text-[var(--background)] shadow-[0_2px_8px_rgba(0,212,170,0.3)]`
        const inactiveClasses = "border border-[var(--border)] text-[var(--text_secondary)]"
        
        return (
          <button
            key={key}
            onClick={() => setMode(key)}
            className={`${baseClasses} ${isActive ? activeClasses : inactiveClasses}`}
          >
            {label}
          </button>
        )
      })}
    </div>
  )
}

export default ModeToggle