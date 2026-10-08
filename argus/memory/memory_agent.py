"""Memory Agent - Persistent project memory and state tracking."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ProjectMemory(BaseModel):
    """Persistent memory for a project across sessions."""
    project_id: str = Field(description="Unique project identifier")
    project_name: str = Field(description="User-friendly project name")
    
    # Core project information
    goal: str = Field(description "The main goal or objective")
    hypothesis: str = Field(description "The main hypothesis being tested")
    
    # Extracted assumptions
    assumptions: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of extracted assumptions with evidence status"
    )
    
    # Claims extracted from the idea
    claims: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of extracted claims"
    )
    
    # Research landscape
    related_work: List[Dict[str, Any]] = Field(
        default_factory=list,
        description "Summary of related work found"
    )
    
    # Evidence tracked
    evidence_summary: Dict[str, Any] = Field(
        default_factory=dict,
        description "Summary of evidence found"
    )
    
    # Results from experiments/analyses
    experiments: List[Dict[str, Any]] = Field(
        default_factory=list,
        description "Record of experiments performed"
    )
    
    # Decisions made
    decisions: List[Dict[str, Any]] = Field(
        default_factory=list,
        description "Record of decisions made"
    )
    
    # Open questions
    open_questions: List[str] = Field(
        default_factory=list,
        description "Unresolved questions remaining"
    )
    
    # Breakpoints discovered
    breakpoints: List[Dict[str, Any]] = Field(
        default_factory=list,
        description "Breakpoints identified during stress testing"
    )
    
    # Counterfactual scenarios
    scenarios: List[Dict[str, Any]] = Field(
        default_factory=list,
        description "Counterfactual scenarios generated"
    )
    
    # Metadata
    created_at: str = Field(description="ISO timestamp of creation")
    last_updated: str = Field(description="ISO timestamp of last update")
    session_count: int = Field(
        default=0,
        description "Number of sessions this project has been accessed in"
    )


class MemoryAgent:
    """Responsibilities: store/retrieve project goals, hypotheses, assumptions, decisions, sources, experiments, results, failures, open questions, deadlines, previous analyses."""
    
    def __init__(self, storage_backend="postgresql"):
        self.storage = storage_backend
        self.projects: Dict[str, ProjectMemory] = {}
    
    def create_project(self, project_name: str, goal: str, hypothesis: str) -> ProjectMemory:
        """Create a new project with initial memory."""
        project_id = f"proj_{hash(project_name) % 10000:04d}"
        memory = ProjectMemory(
            project_id=project_id,
            project_name=project_name,
            goal=goal,
            hypothesis=hypothesis,
            created_at=self._now_iso(),
            last_updated=self._now_iso()
        )
        self.projects[project_id] = memory
        self._persist(memory)
        return memory
    
    def get_project(self, project_id: str) -> Optional[ProjectMemory]:
        """Retrieve a project's memory by ID."""
        return self.projects.get(project_id)
    
    def update_project(self, project_id: str, updates: Dict[str, Any]) -> ProjectMemory:
        """Update a project's memory with new information."""
        memory = self.get_project(project_id)
        if not memory:
            raise ValueError(f"Project {project_id} not found")
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(memory, key):
                setattr(memory, key, value)
        
        memory.last_updated = self._now_iso()
        memory.session_count += 1
        self._persist(memory)
        return memory
    
    def add_assumption(
        self, 
        project_id: str, 
        assumption_text: str, 
        evidence_status: str = "unknown"
    ) -> str:
        """Add an assumption to a project's memory."""
        memory = self.get_project(project_id)
        if not memory:
            raise ValueError(f"Project {project_id} not found")
        
        assumption = {
            "id": f"assump_{len(memory.assumptions)}",
            "text": assumption_text,
            "evidence_status": evidence_status,
            "created": self._now_iso()
        }
        memory.assumptions.append(assumption)
        memory.last_updated = self._now_iso()
        self._persist(memory)
        return assumption["id"]
    
    def add_breakpoint(
        self, 
        project_id: str, 
        assumption: str, 
        threshold: str, 
        severity: str
    ) -> str:
        """Add a breakpoint to a project's memory."""
        memory = self.get_project(project_id)
        if not memory:
            raise ValueError(f"Project {project_id} not found")
        
        breakpoint_entry = {
            "id": f"bp_{len(memory.breakpoints)}",
            "assumption": assumption,
            "threshold": threshold,
            "severity": severity,
            "discovered": self._now_iso()
        }
        memory.breakpoints.append(breakpoint_entry)
        memory.last_updated = self._now_iso()
        self._persist(memory)
        return breakpoint_entry["id"]
    
    def add_open_question(self, project_id: str, question: str) -> str:
        """Add an open question to a project's memory."""
        memory = self.get_project(project_id)
        if not memory:
            raise ValueError(f"Project {project_id} not found")
        
        memory.open_questions.append(question)
        memory.last_updated = self._now_iso()
        self._persist(memory)
        return question
    
    def add_experiment(
        self, 
        project_id: str, 
        name: str, 
        results: Dict[str, Any]
    ) -> str:
        """Add an experiment result to a project's memory."""
        memory = self.get_project(project_id)
        if not memory:
            raise ValueError(f"Project {project_id} not found")
        
        experiment = {
            "id": f"exp_{len(memory.experiments)}",
            "name": name,
            "results": results,
            "recorded": self._now_iso()
        }
        memory.experiments.append(experiment)
        memory.last_updated = self._now_iso()
        self._persist(memory)
        return experiment["id"]
    
    @staticmethod
    def _now_iso() -> str:
        """Get current time in ISO format."""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()


class PostgresMemoryBackend:
    """PostgreSQL-backed memory storage (for production)."""
    
    def __init__(self, connection_string: str):
        self.conn_string = connection_string
        # TODO: Implement actual PostgreSQL connection
        pass