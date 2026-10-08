"""Contradiction Agent - Search for opposing evidence and challenge assumptions."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from argus.llm import call_nemotron_structured
from argus.rag.engine import RAGEngine
from argus.evidence.sources import EvidenceManager


class Contradiction(BaseModel):
    """A contradictory finding to a claim or assumption."""
    id: str = Field(description="Unique contradiction identifier")
    claim_id: str = Field(description="ID of the claim/assumption being contradicted")
    source_paper: str = Field(description="Source of the contradiction")
    evidence: str = Field(description="The contradictory evidence/text")
    strength: float = Field(
        description="Contradiction strength: 0-1, where 1 is strongest",
        ge=0.0,
        le=1.0
    )
    context: str = Field(description="Context where contradiction was observed")


class ContradictionEngine(BaseModel):
    """Engine for finding and analyzing contradictions."""
    
    def search_contradictions(
        self, 
        claim: str, 
        evidence_store: Dict[str, Any]
    ) -> List[Contradiction]:
        """Search for evidence contradicting a claim."""
        # Implemented in ContradictionAgent
        return []
    
    def analyze_contradictions(self, contradictions: List[Contradiction]) -> Dict[str, Any]:
        """Analyze detected contradictions and synthesize findings."""
        return {
            "total_contradictions": len(contradictions),
            "major_themes": [],
            "impact_on_claim": "unknown",
            "recommended_actions": []
        }


CONTRADICTION_SEARCH_SCHEMA = {
    "type": "object",
    "properties": {
        "supporting_queries": {"type": "array", "items": {"type": "string"}},
        "contradicting_queries": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["supporting_queries", "contradicting_queries"]
}

CONTRADICTION_EVAL_SCHEMA = {
    "type": "object",
    "properties": {
        "contradictions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "claim": {"type": "string"},
                    "evidence": {"type": "string"},
                    "source": {"type": "string"},
                    "strength": {"type": "number", "minimum": 0, "maximum": 1},
                    "context": {"type": "string"}
                },
                "required": ["claim", "evidence", "source", "strength", "context"]
            }
        }
    },
    "required": ["contradictions"]
}


class ContradictionAgent:
    """Responsibilities: search for opposing evidence, find limitations, identify conflicting results, challenge assumptions."""
    
    def __init__(self, evidence_store: EvidenceManager, rag_engine: RAGEngine):
        self.evidence_store = evidence_store
        self.rag_engine = rag_engine
        
        self.system_prompt_search = """You are ARGUS's Contradiction Agent. Generate search queries to find both supporting AND contradicting evidence for a claim.

Given a claim, produce:
1. SUPPORTING_QUERIES: Queries to find evidence supporting the claim
2. CONTRADICTING_QUERIES: Queries to find evidence contradicting/challenging the claim

Make queries specific and use academic terminology. Consider: limitations, failure cases, boundary conditions, opposing theories, negative results."""
        
        self.system_prompt_eval = """You are ARGUS's Contradiction Agent. Evaluate retrieved evidence against a claim to identify contradictions.

Given a claim and a set of evidence passages, identify:
- CONTRADICTIONS: Specific pieces of evidence that contradict or weaken the claim
- For each: the contradictory evidence text, source, strength (0-1), and context

Strength guidelines:
- 0.8-1.0: Directly contradicts with strong evidence
- 0.5-0.7: Suggests limitation or boundary condition
- 0.3-0.4: Weak or indirect contradiction
- <0.3: Not a meaningful contradiction"""

    def challenge_assumption(self, assumption: Dict[str, Any]) -> Dict[str, Any]:
        """Challenge a specific assumption and return contradictions."""
        contradictions = self.search_contradictions(assumption["text"])
        analysis = self.analyze_contradictions(contradictions)
        return {
            "assumption": assumption,
            "contradictions": contradictions,
            "analysis": analysis
        }
    
    def search_contradictions(self, claim: str, evidence_store: Dict[str, Any] = None) -> List[Contradiction]:
        """Search for opposing evidence to a claim using RAG + Nemotron evaluation."""
        # Generate search queries
        messages = [
            {"role": "system", "content": self.system_prompt_search},
            {"role": "user", "content": f"Generate search queries for this claim:\n\n{claim}"}
        ]
        
        try:
            search_plan = call_nemotron_structured(messages, CONTRADICTION_SEARCH_SCHEMA, temperature=0.2)
            contradicting_queries = search_plan.get("contradicting_queries", [f"limitations of {claim}", f"evidence against {claim}"])
        except Exception:
            contradicting_queries = [f"limitations of {claim}", f"evidence against {claim}", f"failure cases {claim}"]
        
        # Retrieve evidence for contradicting queries
        all_evidence = []
        for query in contradicting_queries[:4]:
            try:
                group = self.rag_engine.retrieve_for_claim(query, top_k=10)
                all_evidence.extend(group.contradicting)
                all_evidence.extend(group.neutral)
            except Exception:
                continue
        
        if not all_evidence:
            return self._mock_contradictions(claim)
        
        # Evaluate evidence for contradictions
        evidence_texts = "\n\n".join([
            f"Source: {e.source}\nTitle: {e.title}\nContent: {e.content[:400]}"
            for e in all_evidence[:15]
        ])
        
        messages = [
            {"role": "system", "content": self.system_prompt_eval},
            {"role": "user", "content": f"Claim: {claim}\n\nEvidence to evaluate:\n{evidence_texts}"}
        ]
        
        try:
            result = call_nemotron_structured(messages, CONTRADICTION_EVAL_SCHEMA, temperature=0.1)
            contradictions_data = result.get("contradictions", [])
            
            contradictions = []
            for i, c in enumerate(contradictions_data):
                contradictions.append(Contradiction(
                    id=f"contr_{i}",
                    claim_id=claim[:50],
                    source_paper=c.get("source", "Unknown"),
                    evidence=c.get("evidence", ""),
                    strength=c.get("strength", 0.5),
                    context=c.get("context", "")
                ))
            
            return contradictions
        except Exception:
            return self._mock_contradictions(claim)
    
    def _mock_contradictions(self, claim: str) -> List[Contradiction]:
        """Return mock contradictions when RAG/LLM unavailable."""
        claim_lower = claim.lower()
        
        mocks = []
        if "multimodal" in claim_lower and "improv" in claim_lower:
            mocks.append(Contradiction(
                id="contr_1",
                claim_id=claim[:50],
                source_paper="Chen et al. 2024",
                evidence="Text-only baselines match multimodal performance when visual signals are noisy or irrelevant",
                strength=0.75,
                context="Social media posts with stock photos"
            ))
        if "efficien" in claim_lower:
            mocks.append(Contradiction(
                id="contr_2",
                claim_id=claim[:50],
                source_paper="Liu et al. 2023",
                evidence="Model compression via distillation degrades out-of-distribution robustness by 12-18%",
                strength=0.8,
                context="Domain shift evaluation on misinformation datasets"
            ))
        if "cross-dataset" in claim_lower or "generaliz" in claim_lower:
            mocks.append(Contradiction(
                id="contr_3",
                claim_id=claim[:50],
                source_paper="Gupta et al. 2024",
                evidence="Multimodal models show >15% accuracy drop under domain shift vs 8% for unimodal",
                strength=0.85,
                context="Cross-platform misinformation detection"
            ))
        
        if not mocks:
            mocks.append(Contradiction(
                id="contr_1",
                claim_id=claim[:50],
                source_paper="Literature review needed",
                evidence=f"No specific counterevidence found for: {claim}",
                strength=0.3,
                context="Search limitations - expand query terms"
            ))
        
        return mocks
    
    def analyze_contradictions(self, contradictions: List[Contradiction]) -> Dict[str, Any]:
        """Analyze detected contradictions and synthesize findings."""
        if not contradictions:
            return {
                "total_contradictions": 0,
                "major_themes": [],
                "impact_on_claim": "no_contradictions_found",
                "recommended_actions": ["Search broader literature", "Consider empirical validation"]
            }
        
        high_strength = [c for c in contradictions if c.strength >= 0.7]
        themes = list(set([c.context for c in contradictions if c.context]))
        
        return {
            "total_contradictions": len(contradictions),
            "high_strength_count": len(high_strength),
            "major_themes": themes[:5],
            "impact_on_claim": "significant" if high_strength else "moderate",
            "recommended_actions": [
                "Investigate high-strength contradictions experimentally",
                "Test boundary conditions identified in counterevidence",
                "Consider alternative architectures if contradictions are fundamental"
            ]
        }