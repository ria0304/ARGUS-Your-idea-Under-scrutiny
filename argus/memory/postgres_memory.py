"""Memory Agent - In-memory project storage (demo mode)."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import json
import hashlib


class MemoryBackend:
    """Backend for project memory storage.
    
    Uses in-memory storage for the hackathon demo.
    For production, deploy with PostgreSQL via NEBIUS_DB_URL env var.
    """
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or self._get_default_url()
        self._projects: Dict[str, dict] = {}
    
    def _get_default_url(self) -> str:
        """Get default database URL - checks env vars, falls back to demo mode."""
        pg_url = (
            __import__("os").environ.get("NEBIUS_DB_URL") or
            __import__("os").environ.get("POSTGRES_URL") or
            __import__("os").environ.get("DATABASE_URL")
        )
        if pg_url:
            # In production mode with PostgreSQL, would initialize DB connection
            return pg_url
        # Default to in-memory for demo
        return ""
    
    def _generate_project_id(self, project_name: str) -> str:
        """Generate a unique project ID."""
        return f"proj_{hash(project_name) % 100000:05d}"
    
    def create_project(self, project_name: str, goal: str, hypothesis: str) -> dict:
        """Create a new project in memory."""
        project_id = self._generate_project_id(project_name)
        
        # Ensure unique ID
        while project_id in self._projects:
            project_id = f"proj_{hash(project_id + str(datetime.now().timestamp())) % 100000:05d}"
        
        memory = {
            "project_id": project_id,
            "project_name": project_name,
            "goal": goal,
            "hypothesis": hypothesis,
            "assumptions": [],
            "claims": [],
            "related_work": [],
            "evidence_summary": {},
            "experiments": [],
            "decisions": [],
            "open_questions": [],
            "breakpoints": [],
            "scenarios": [],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
        self._projects[project_id] = memory
        return memory
    
    def get_project(self, project_id: str) -> Optional[dict]:
        """Retrieve a project's memory by ID."""
        return self._projects.get(project_id)
    
    def update_project(self, project_id: str, updates: dict) -> dict:
        """Update a project's memory."""
        if project_id not in self._projects:
            raise ValueError(f"Project {project_id} not found")
        
        project = self._projects[project_id]
        
        # Apply updates
        for key, value in updates.items():
            if key in project and value is not None:
                # Special handling for JSON-serializable fields
                if key in ["assumptions", "claims", "related_work", "experiments", 
                          "decisions", "open_questions", "breakpoints", "scenarios"]:
                    existing = project.get(key, [])
                    if isinstance(value, list):
                        existing.extend(value)
                        project[key] = existing
                    else:
                        project[key] = value
                else:
                    project[key] = value
        
        project["last_updated"] = datetime.now(timezone.utc).isoformat()
        return project
    
    def add_assumption(self, project_id: str, assumption_text: str, evidence_status: str = "unknown") -> str:
        """Add an assumption to a project's memory."""
        if project_id not in self._projects:
            raise ValueError(f"Project {project_id} not found")
        
        project = self._projects[project_id]
        assumptions = project.get("assumptions", [])
        assumption_entry = {
            "id": f"assump_{len(assumptions)}",
            "text": assumption_text,
            "evidence_status": evidence_status,
            "created": datetime.now(timezone.utc).isoformat()
        }
        assumptions.append(assumption_entry)
        project["assumptions"] = assumptions
        project["last_updated"] = datetime.now(timezone.utc).isoformat()
        
        return assumption_entry["id"]
    
    def add_breakpoint(self, project_id: str, assumption: str, threshold: str, severity: str) -> str:
        """Add a breakpoint to a project's memory."""
        if project_id not in self._projects:
            raise ValueError(f"Project {project_id} not found")
        
        project = self._projects[project_id]
        breakpoints = project.get("breakpoints", [])
        bp_entry = {
            "id": f"bp_{len(breakpoints)}",
            "assumption": assumption,
            "threshold": threshold,
            "severity": severity,
            "discovered": datetime.now(timezone.utc).isoformat()
        }
        breakpoints.append(bp_entry)
        project["breakpoints"] = breakpoints
        project["last_updated"] = datetime.now(timezone.utc).isoformat()
        
        return bp_entry["id"]
    
    def add_experiment(self, project_id: str, name: str, results: dict) -> str:
        """Add an experiment result to a project's memory."""
        if project_id not in self._projects:
            raise ValueError(f"Project {project_id} not found")
        
        project = self._projects[project_id]
        experiments = project.get("experiments", [])
        experiment_entry = {
            "id": f"exp_{len(experiments)}",
            "name": name,
            "results": results,
            "recorded": datetime.now(timezone.utc).isoformat()
        }
        experiments.append(experiment_entry)
        project["experiments"] = experiments
        project["last_updated"] = datetime.now(timezone.utc).isoformat()
        
        return experiment_entry["id"]
    
    def add_open_question(self, project_id: str, question: str) -> str:
        """Add an open question to a project's memory."""
        if project_id not in self._projects:
            raise ValueError(f"Project {project_id} not found")
        
        project = self._projects[project_id]
        questions = project.get("open_questions", [])
        questions.append(question)
        project["open_questions"] = questions
        project["last_updated"] = datetime.now(timezone.utc).isoformat()
        
        return str(len(questions) - 1)
    
    def get_all_projects(self) -> List[dict]:
        """Get all projects."""
        return list(self._projects.values())


# Singleton instance for the demo
_memory_backend = None

def get_memory_backend() -> MemoryBackend:
    """Get the singleton memory backend instance."""
    global _memory_backend
    if _memory_backend is None:
        _memory_backend = MemoryBackend()
    return _memory_backend


# For direct script usage
if __name__ == "__main__":
    # Demo: Create and use memory backend
    backend = get_memory_backend()
    
    # Create a project
    project = backend.create_project(
        project_name="Multimodal Misinformation Detection",
        goal="Build a lightweight multimodal model for detecting misinformation",
        hypothesis="Combining text and image modalities improves detection accuracy"
    )
    print(f"Created project: {project['project_id']}")
    print(f"Project name: {project['project_name']}")
    
    # Add assumptions
    asum1 = backend.add_assumption(
        project_id=project['project_id'],
        assumption_text="Multimodal information improves classification.",
        evidence_status="weak_evidence"
    )
    print(f"Added assumption: {asum1}")
    
    asum2 = backend.add_assumption(
        project_id=project['project_id'],
        assumption_text="Image and text signals are complementary.",
        evidence_status="moderately_supported"
    )
    print(f"Added assumption: {asum2}")
    
    # Add a breakpoint
    bp_id = backend.add_breakpoint(
        project_id=project['project_id'],
        assumption="The improvement will generalize across datasets.",
        threshold="Dataset diversity falls below 30%",
        severity="critical"
    )
    print(f"Added breakpoint: {bp_id}")
    
    # Add an experiment
    backend.add_experiment(
        project_id=project['project_id'],
        name="Cross-dataset evaluation",
        results={"accuracy": 0.85, "f1": 0.82, "dataset": "Dataset B"}
    )
    print("Added experiment")
    
    # Add an open question
    q_id = backend.add_open_question(
        project_id=project['project_id'],
        question="Does the improvement survive distribution shift?"
    )
    print(f"Added open question: {q_id}")
    
    # Retrieve the project
    retrieved = backend.get_project(project['project_id'])
    print(f"\nRetrieved project: {retrieved['project_name']}")
    print(f"Assumptions: {len(retrieved['assumptions'])}")
    print(f"Breakpoints: {len(retrieved['breakpoints'])}")
    print(f"Open questions: {len(retrieved['open_questions'])}")
    print(f"Experiments: {len(retrieved['experiments'])}")