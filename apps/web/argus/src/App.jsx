import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from "react-router-dom"
import { useState, useEffect } from "react"
import "./index.css"

// Import components
import DashboardPage from "./pages/dashboard.jsx"
import InvestigationPage from "./pages/investigation.jsx"
import BreakPage from "./pages/break.jsx"
import MirrorPage from "./pages/mirror.jsx"
import HomePage from "./pages/home.jsx"
import DashboardSummary from "./components/dashboard/DashboardSummary"
import ModeToggle from "./components/common/ModeToggle"

// Main ARGUS App Component
const App = () => {
  const navigate = useNavigate()
  const [mode, setMode] = useState("investigate") // investigate, break, mirror
  const [currentProject, setCurrentProject] = useState(null)

  // Check for project in localStorage
  useEffect(() => {
    const stored = localStorage.getItem("argus_current_project")
    if (stored) {
      setCurrentProject(JSON.parse(stored))
    }
  }, [])

  return (
    <Router>
      <div className="bg-patterned min-h-screen">
        {/* Header */}
        <header className="border-b var(--border) backdrop-bl-sm bg-opacity-50 sticky top-0 bg-[var(--background)] z-50">
          <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-accent flex items-center justify-center">
                <svg className="w-6 h-6 text-[var(--background)]" fill="none" stroke="currentColor">
                  <path d="M2 3a1 1 0 011-1h3.28a6.97 6.97 0 011.69 5.7 6.99 6.99 0 003.41 2.33 6.996 6.996 0 015.35 1.12 6.996 6.996 0 007.27-.35A8.967 8.967 0 0012.518 3 8.985 8.985 0 0011.233 1l.784-.777a2.1 2.1 0 01.397 1.06l1.179 5.165a2.1 2.1 0 001.626.605l1.179-5.165.396 2.038a2.1 2.1 0 01-.192.805l-1.18 5.165.396 2.038a2.1 2.1 0 01-.192.805l-1.18 5.165L23 7l-1.712-3.288a6.97 6.97 0 00-3.44-2.07 6.995 6.995 0 01-5.36-.95A6.993 6.993 0 005.377 7 2.99 2.99 0 012 5.25 1 1 0 012.18 2z"/>
                </svg>
              </div>
              <h1 className="text-xl font-bold tracking-tight">ARGUS</h1>
            </div>
            <nav>
              <div className="hidden sm:flex items-center gap-8">
                <Link to="/" className="text-[var(--text_secondary)] hover:text-[var(--accent)] transition-colors">
                  Investigate
                </Link>
                <Link to="/break" className="text-[var(--text_secondary)] hover:text-[var(--danger)] transition-colors">
                  Break It
                </Link>
                <Link to="/mirror" className="text-[var(--text_secondary)] hover:text-[#64b5f6] transition-colors">
                  Mirror
                </Link>
              </div>
              <button
                onClick={() => setMode("investigate")}
                className="hidden sm:inline-flex btn-secondary text-sm"
              >
                Investigate
              </button>
              <button
                onClick={() => setMode("break")}
                className="hidden sm:inline-flex btn-secondary text-sm"
              >
                Break It
              </button>
              <button
                onClick={() => setMode("mirror")}
                className="hidden sm:inline-flex btn-secondary text-sm"
              >
                Mirror
              </button>
            </nav>
          </div>
        </header>

        {/* Mode indicator */}
        <div className="py-2 px-6 bg-[var(--card)] text-sm text-[var(--text_secondary)]">
          Mode: <span className={`mode-badge mode-${mode}`}>{mode}</span>
        </div>

        {/* Main content */}
        <main className="max-w-7xl mx-auto p-6">
          <Routes>
            <Route
              path="/"
              element={
                <HomePage
                  navigate={navigate}
                  setMode={setMode}
                  currentProject={currentProject}
                />
              }
            />
            <Route
              path="/investigate"
              element={
                <InvestigationPage
                  navigate={navigate}
                  setMode={setMode}
                  currentProject={currentProject}
                />
              }
            />
            <Route
              path="/break"
              element={
                <BreakPage
                  navigate={navigate}
                  setMode={setMode}
                  currentProject={currentProject}
                />
              }
            />
            <Route
              path="/mirror"
              element={
                <MirrorPage
                  navigate={navigate}
                  setMode={setMode}
                  currentProject={currentProject}
                />
              }
            />
            <Route
              path="/dashboard"
              element={
                <DashboardPage
                  currentProject={currentProject}
                />
              }
            />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App