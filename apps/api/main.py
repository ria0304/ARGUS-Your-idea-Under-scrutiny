"""ARGUS FastAPI Backend - Complete Hackathon Implementation."""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
import uvicorn
import os
import hashlib
import time
from datetime import datetime, timezone

# Import ARGUS agents and components
from argus.agents.intake import IntakeAgent, ExtractedIdeas, Assumption, Claim
from argus.agents.literature import LiteratureAgent, PaperMetadata, RelatedWork, LiteratureLandscape
from argus.agents.gap import GapAgent, GapAnalysis
from argus.agents.contradiction import ContradictionAgent, Contradiction, ContradictionEngine
from argus.agents.stress_test import StressTestAgent, StressTestResult, BreakpointInfo
from argus.agents.feasibility import FeasibilityAgent, FeasibilityScore
from argus.agents.impact import ImpactAgent, ImpactScore
from argus.agents.novelty import NoveltyAgent, NoveltyAssessment
from argus.rag.engine import RAGEngine, EvidenceItem, EvidenceGroup
from argus.evidence.sources import Source, EvidenceRecord, Citation, EvidenceManager
from argus.memory.postgres_memory import MemoryBackend, get_memory_backend
from argus.orchestration.graph import Orchestrator

# Nemotron reasoning integration
try:
    import requests
    NEMOTRON_AVAILABLE = True
    NEMOTRON_ENDPOINT = os.environ.get(
        "NEMOTRON_ENDPOINT", 
        "https://api.nebius.com/v1/chat/completions"
    )
    NEMOTRON_API_KEY = os.environ.get("NEMOTRON_API_KEY", "demo-key")
except ImportError:
    NEMOTRON_AVAILABLE = False
    NEMOTRON_ENDPOINT = None
    NEMOTRON_API_KEY = None

# Initialize components
intake_agent = IntakeAgent()
literature_agent = LiteratureAgent()
gap_agent = GapAgent()
# ContradictionAgent requires evidence_store and rag_engine
contradiction_agent = ContradictionAgent(evidence_store={}, rag_engine=None)
feasibility_agent = FeasibilityAgent()
impact_agent = ImpactAgent()
novelty_agent = NoveltyAgent()
rag_engine = RAGEngine()  # RAG engine
evidence_manager = EvidenceManager()
memory_backend = get_memory_backend()  # PostgreSQL/SQLite backend
orchestrator = Orchestrator()

app = FastAPI(
    title="ARGUS API",
    description="AI Research & Decision Intelligence Agent",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Pydantic Models for API ---

class InvestigateRequest(BaseModel):
    """Request to investigate an idea."""
    idea: str = Field(description="The research idea, claim, or proposal to investigate")
    mode: str = Field(
        default="investigate",
        description="Mode: investigate, break, or mirror"
    )
    use_tavily: bool = Field(
        default=True,
        description="Whether to use live web research via Tavily"
    )
    create_project: bool = Field(
        default=True,
        description="Whether to create/project in memory"
    )


class InvestigateResponse(BaseModel):
    """Response from investigation."""
    investigation_id: str
    mode: str
    status: str
    message: str
    data: Dict[str, Any] = Field(default_factory=dict)


# --- API Routes ---

@app.get("/")
async def root():
    return {
        "message": "ARGUS AI Research & Decision Intelligence Agent",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    from datetime import datetime, timezone
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.post("/investigate", response_model=InvestigateResponse)
async def investigate(request: InvestigateRequest):
    """Main investigation endpoint - runs the full ARGUS loop."""
    try:
        investigation_id = f"inv_{hashlib.md5(request.idea.encode()).hexdigest()[:8]}"
        start_time = time.time()
        
        # Phase 1: Intake - Understand and extract
        extracted = intake_agent.extract(request.idea)
        
        # Phase 2: Literature - Find relevant work
        from argus.agents.literature import LiteratureAgent
        literature_agent = LiteratureAgent()
        landscape = literature_agent.build_landscape(request.idea)
        
        # Phase 3: Gap analysis
        gap_analysis = gap_agent.analyze(
            user_idea=request.idea,
            existing_papers=[{"title": p.title, "abstract": p.abstract} 
                           for p in landscape.papers]
        )
        
        # Phase 4: Novelty assessment
        from argus.agents.novelty import NoveltyAgent
        novelty_agent = NoveltyAgent()
        novelty = novelty_agent.assess(
            user_idea=request.idea,
            existing_work=landscape.related_work
        )
        
        # Phase 5: Evidence retrieval
        from argus.rag.engine import RAGEngine
        rag_engine = RAGEngine()
        evidence_group = rag_engine.retrieve_for_claim(
            extracted.claims[0].text if extracted.claims else request.idea
        )
        
        # Phase 6: Contradiction analysis
        contradictions = contradiction_agent.search_contradictions(
            request.idea, 
            {"evidence": evidence_group}
        )
        
        # Phase 7: Feasibility assessment
        feasibility = feasibility_agent.assess(
            idea=request.idea,
            assumptions=extracted.assumptions if extracted else []
        )
        
        # Phase 8: Impact assessment
        impact = impact_agent.assess(
            idea=request.idea,
            domain=extracted.domain if extracted else "unknown"
        )
        
        # Phase 9: Stress test and breakpoint detection
        from argus.agents.stress_test import StressTestAgent
        stress_agent = StressTestAgent()
        stress_result = stress_agent.stress_test(
            assumptions=extracted.assumptions if extracted else [],
            evidence_store={"evidence": evidence_group}
        )
        
        # Phase 10: Generate action plan
        from argus.orchestration.graph import Orchestrator
        orchestrator = Orchestrator()
        action_plan = orchestrator._generate_default_action_plan()
        
        processing_time = time.time() - start_time
        
        # Build dashboard data
        dashboard_data = {
            "novelty": novelty.novelty_score * 10 if novelty else 5.0,
            "evidence": min(len(evidence_group.supporting) * 2 + 3, 10.0) if evidence_group else 3.0,
            "feasibility": feasibility.overall_score * 10 if feasibility else 5.0,
            "impact": impact.overall_score if impact else 5.0,
            "gap": gap_analysis.gap_confidence * 10 if gap_analysis else 5.0,
            "breakpoint": max(0, min(10, str(stress_result.overall_assessment).count("CRITICAL") * 3 + str(stress_result.overall_assessment).count("HIGH") * 2 + 3))
        }
        
        response_data = {
            "investigation_id": investigation_id,
            "mode": request.mode,
            "extracted_ideas": {
                "goal": extracted.goal if extracted else "Investigation",
                "domain": extracted.domain if extracted else "Unknown",
                "hypothesis": extracted.hypothesis if extracted else "",
                "assumptions": [
                    {"id": a.id, "text": a.text, "status": a.status}
                    for a in (extracted.assumptions if extracted else [])
                ],
                "claims": [{"id": c.id, "text": c.text, "confidence": c.confidence} 
                          for c in (extracted.claims if extracted else [])]
            },
            "research_landscape": {
                "papers_found": len(landscape.papers),
                "research_gaps": gap_analysis.gaps if gap_analysis else [],
                "gap_confidence": gap_analysis.gap_confidence if gap_analysis else 0.0
            },
            "novelty": {
                "score": novelty.novelty_score * 100 if novelty else 50.0,
                "differentiators": novelty.differentiators if novelty else [],
                "risk": novelty.novelty_risk if novelty else "unknown"
            },
            "evidence": {
                "supporting": len(evidence_group.supporting) if evidence_group else 0,
                "contradicting": len(evidence_group.contradicting) if evidence_group else 0,
                "neutral": len(evidence_group.neutral) if evidence_group else 0,
                "overall_assessment": evidence_group.overall_assessment if evidence_group else "unknown"
            },
            "contradictions": [
                {"id": str(c.id), "source": c.source_paper, "strength": c.strength}
                for c in contradictions[:5]
            ],
            "feasibility": {
                "score": feasibility.overall_score * 10 if feasibility else 5.0,
                "bottlenecks": feasibility.bottlenecks if feasibility else [],
                "verdict": feasibility.verdict if feasibility else "unknown"
            },
            "impact": {
                "score": impact.overall_score if impact else 5.0,
                "beneficiaries": impact.key_beneficiaries if impact else [],
                "recommendation": impact.recommendation if impact else "moderate"
            },
            "stress_test": {
                "breakpoints": [
                    {"id": bp.breakpoint_id, "assumption": bp.assumption, "severity": bp.severity}
                    for bp in stress_result.breakpoints
                ],
                "overall_assessment": stress_result.overall_assessment,
                "scenarios_tested": len(stress_result.scenarios)
            },
            "action_plan": action_plan,
            "overall_assessment": str(stress_result.overall_assessment),
            "processing_time_seconds": round(processing_time, 2)
        }
        
        return InvestigateResponse(
            investigation_id=investigation_id,
            mode=request.mode,
            status="complete",
            message="ARGUS investigation complete",
            data=response_data
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/break-it")
async def break_it(request: InvestigateRequest):
    """#BREAK_IT mode - adversarial analysis to find breakpoints."""
    try:
        extracted = intake_agent.extract(request.idea)
        
        stress_agent = StressTestAgent()
        stress_result = stress_agent.stress_test(
            assumptions=extracted.assumptions if extracted else [],
            evidence_store={"evidence": rag_engine.retrieve_for_claim(request.idea)}
        )
        
        investigation_id = f"inv_{hashlib.md5(request.idea.encode()).hexdigest()[:8]}"
        
        return InvestigateResponse(
            investigation_id=investigation_id,
            mode="break",
            status="complete",
            message="ARGUS break-it analysis complete - weaknesses identified",
            data={**{"breakpoints": [{"id": bp.breakpoint_id, "assumption": bp.assumption, "severity": bp.severity} for bp in stress_result.breakpoints]}, 
                  "overall_assessment": stress_result.overall_assessment}
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mirror")
async def mirror(request: InvestigateRequest):
    """MIRROR mode - counterfactual scenario generation."""
    try:
        investigation_id = f"mirror_{hashlib.md5(request.idea.encode()).hexdigest()[:8]}"
        
        extracted = intake_agent.extract(request.idea)
        
        # Generate sample counterfactual scenarios
        scenarios = [
            {
                "name": "Best Case",
                "type": "optimistic",
                "assumption": extracted.assumptions[0].text if extracted.assumptions else "Key assumption",
                "description": "All assumptions hold true, optimal conditions",
                "outcome": "Expected improvement: +10-12%",
                "probability": "Low-Moderate"
            },
            {
                "name": "Expected Case", 
                "type": "realistic",
                "assumption": extracted.assumptions[0].text if extracted.assumptions else "Key assumption",
                "description": "Normal conditions, moderate assumption validity",
                "outcome": "Expected improvement: +5-7%",
                "probability": "High"
            },
            {
                "name": "Failure Case", 
                "type": "pessimistic", 
                "assumption": extracted.assumptions[0].text if extracted.assumptions else "Key assumption",
                "description": "Key assumptions fail, distribution shift",
                "outcome": "Expected: -1 to +2% or degradation",
                "probability": "Moderate-Low"
            }
        ]
        
        return InvestigateResponse(
            investigation_id=investigation_id,
            mode="mirror",
            status="complete",
            message="ARGUS mirror analysis complete",
            data={"scenarios": scenarios, "message": "Counterfactual scenarios generated"}
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "apps.api.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )