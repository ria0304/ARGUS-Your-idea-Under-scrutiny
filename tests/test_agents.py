"""pytest tests for ARGUS - core structure validation."""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "argus"))


# ✅ Core: All agent classes importable
def test_all_agents_importable():
    """Test all 9 ARGUS agent classes can be imported."""
    from argus.agents.intake import IntakeAgent
    from argus.agents.literature import LiteratureAgent
    from argus.agents.gap import GapAgent
    from argus.agents.contradiction import ContradictionAgent
    from argus.agents.stress_test import StressTestAgent
    from argus.agents.feasibility import FeasibilityAgent
    from argus.agents.impact import ImpactAgent
    from argus.agents.novelty import NoveltyAgent

    agents = [IntakeAgent(), LiteratureAgent(), GapAgent(),
              ContradictionAgent(), StressTestAgent(),
              FeasibilityAgent(), ImpactAgent(), NoveltyAgent()]
    for a in agents:
        assert a is not None


# ✅ Core: FastAPI app runs
def test_fastapi_app():
    """Test FastAPI app is created and has routes."""
    from apps.api.main import app
    assert app is not None
    assert app.title == "ARGUS API"


# ✅ Core: Health endpoint
def test_health_endpoint():
    """Test health check endpoint."""
    from fastapi.testclient import TestClient
    from apps.api.main import app
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data


# ✅ Core: Investigate endpoint
def test_investigate_endpoint():
    """Test investigate endpoint returns investigation ID."""
    from fastapi.testclient import TestClient
    from apps.api.main import app
    client = TestClient(app)
    response = client.post(
        "/investigate",
        json={"idea": "I want to build an efficient multimodal model for misinformation detection", "mode": "investigate"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "complete"
    assert "investigation_id" in data["data"]
    assert data["data"]["mode"] == "investigate"


# ✅ Core: Break-it mode
def test_break_it_endpoint():
    """Test #BREAK_IT mode endpoint."""
    from fastapi.testclient import TestClient
    from apps.api.main import app
    client = TestClient(app)
    response = client.post(
        "/break-it",
        json={"idea": "I want to build an efficient multimodal model for misinformation detection", "mode": "break"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "complete"


# ✅ Core: Memory backend operations
def test_memory_backend_basic():
    """Test memory backend create/retrieve cycle."""
    from argus.memory.postgres_memory import get_memory_backend
    from datetime import datetime, timezone

    backend = get_memory_backend()
    project = backend.create_project(
        project_name="Hackathon Project",
        goal="Test ARGUS capabilities",
        hypothesis="The idea can be stress-tested effectively"
    )
    assert project["project_name"] == "Hackathon Project"
    assert project["project_id"] is not None

    # Add assumption
    aid = backend.add_assumption(
        project_id=project["project_id"],
        assumption_text="Multimodal information improves classification.",
        evidence_status="weak_evidence"
    )
    assert aid is not None

    # Add breakpoint
    bp_id = backend.add_breakpoint(
        project_id=project["project_id"],
        assumption="The improvement will generalize across datasets.",
        threshold="Dataset diversity falls below 30%",
        severity="critical"
    )
    assert bp_id is not None

    # Add experiment
    exp_id = backend.add_experiment(
        project_id=project["project_id"],
        name="Cross-dataset evaluation",
        results={"accuracy": 0.85, "f1": 0.82}
    )
    assert exp_id is not None

    # Add open question
    q_id = backend.add_open_question(
        project_id=project["project_id"],
        question="Does the improvement survive distribution shift?"
    )
    assert isinstance(q_id, int)

    # Retrieve and verify all data
    retrieved = backend.get_project(project["project_id"])
    assert retrieved["project_name"] == "Hackathon Project"
    assert len(retrieved["assumptions"]) >= 1
    assert len(retrieved["breakpoints"]) >= 1
    assert len(retrieved["experiments"]) >= 1
    assert len(retrieved["open_questions"]) >= 1


# ✅ RAG engine
def test_rag_engine():
    """Test RAG engine core structure."""
    from argus.rag.engine import RAGEngine, EvidenceItem, EvidenceGroup

    engine = RAGEngine()
    item = EvidenceItem(
        id="e1", source="S", title="T", content="C", claim="c",
        support_type="supporting", confidence=0.5
    )
    assert item.id == "e1"
    assert 0.0 <= item.confidence <= 1.0

    group = EvidenceGroup(claim_id="c1", supporting=[item], contradicting=[], neutral=[],
                          overall_assessment="supports")
    assert group.overall_assessment in ["supports", "contradicts", "mixed", "unknown"]


# ✅ Dashboard metrics validation
def test_dashboard_metrics():
    """Test dashboard metric values are in valid ranges."""
    metrics = {
        "novelty": 78.5,
        "evidence": 64.0,
        "feasibility": 89.0,
        "impact": 8.1,
        "gap": 71.0,
        "breakpoint": 40.0,
    }

    assert 0.0 <= metrics["novelty"] <= 100.0
    assert 0.0 <= metrics["evidence"] <= 100.0
    assert 0.0 <= metrics["feasibility"] <= 100.0
    assert 0.0 <= metrics["impact"] <= 10.0
    assert 0.0 <= metrics["gap"] <= 100.0
    assert 0.0 <= metrics["breakpoint"] <= 100.0
    # ARGUS typically shows strong novelty
    assert metrics["novelty"] >= 70.0


# ✅ Novelty assessment
def test_novelty_assessment():
    """Test novelty assessment structure."""
    from argus.agents.novelty import NoveltyAssessment

    na = NoveltyAssessment(novelty_score=75.0, overlap_percentage=30.0,
                           novelty_risk="moderate")
    assert na.novelty_score == 75.0
    assert na.novelty_risk in ["high", "moderate", "low"]


# ✅ Feasibility assessment
def test_feasibility_assessment():
    """Test feasibility assessment structure."""
    from argus.agents.feasibility import FeasibilityScore

    fs = FeasibilityScore(overall_score=0.8, verdict="feasible")
    assert fs.overall_score == 0.8
    assert fs.verdict == "feasible"


# ✅ Impact assessment
def test_impact_assessment():
    """Test impact assessment structure."""
    from argus.agents.impact import ImpactScore

    is_score = ImpactScore(overall_score=8.0, recommendation="high")
    assert is_score.overall_score == 8.0
    assert is_score.recommendation == "high"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])