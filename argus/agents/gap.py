"""Gap Agent - Identify research gaps and compare research areas."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from argus.llm import call_nemotron_structured


class GapAnalysis(BaseModel):
    """Analysis of research gaps identified by the agent."""
    gaps: List[str] = Field(description="List of identified research gaps")
    gap_confidence: float = Field(
        description="Confidence in gap existence: 0-1",
        ge=0.0,
        le=1.0
    )
    existing_coverage: Dict[str, float] = Field(
        description="How well each major topic is covered: topic->coverage(0-1)"
    )
    search_limitations: List[str] = Field(
        default_factory=list,
        description="Known limitations in search coverage"
    )


GAP_ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "gaps": {"type": "array", "items": {"type": "string"}},
        "gap_confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "existing_coverage": {"type": "object", "additionalProperties": {"type": "number", "minimum": 0, "maximum": 1}},
        "search_limitations": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["gaps", "gap_confidence", "existing_coverage", "search_limitations"]
}


class GapAgent:
    """Responsibilities: compare research areas, identify missing combinations, identify underexplored conditions, estimate gap confidence."""
    
    def __init__(self):
        self.system_prompt = """You are ARGUS's Gap Agent. Identify research gaps by comparing a user's idea with existing literature.

Given a user's research idea and a set of existing papers, identify:
1. SPECIFIC GAPS: What is missing from the literature that this idea addresses?
2. GAP_CONFIDENCE: How confident are you this is a genuine gap (0-1)?
3. EXISTING_COVERAGE: For each major topic in the idea, how well covered is it by existing work (0-1)?
4. SEARCH_LIMITATIONS: What might the literature search have missed?

Focus on actionable, specific gaps - not vague statements. Consider:
- Missing combinations of methods/domains
- Underexplored conditions or assumptions
- Missing evaluation protocols
- Unexplored theoretical connections"""

    def analyze(self, 
                user_idea: str, 
                existing_papers: List[Dict[str, Any]]) -> GapAnalysis:
        """Analyze research gaps given user idea and existing work."""
        # Summarize existing papers
        paper_summary = self._summarize_papers(existing_papers)
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"User idea (gap analysis):\n{user_idea}\n\nExisting papers:\n{paper_summary}"}
        ]
        
        try:
            result = call_nemotron_structured(messages, GAP_ANALYSIS_SCHEMA, temperature=0.2)
            
            return GapAnalysis(
                gaps=result.get("gaps", []),
                gap_confidence=result.get("gap_confidence", 0.5),
                existing_coverage=result.get("existing_coverage", {}),
                search_limitations=result.get("search_limitations", [])
            )
        except Exception as e:
            return self._fallback_analyze(user_idea, existing_papers)
    
    def _summarize_papers(self, papers: List[Dict[str, Any]]) -> str:
        """Create a concise summary of existing papers."""
        if not papers:
            return "No existing papers provided."
        
        summaries = []
        for p in papers[:15]:
            title = p.get("title", p.get("paper", {}).get("title", "Unknown"))
            abstract = p.get("abstract", p.get("paper", {}).get("abstract", ""))[:300]
            topics = p.get("topics", p.get("paper", {}).get("topics", []))
            relevance = p.get("relevance", p.get("relationship", "unknown"))
            
            summaries.append(f"- {title} [{relevance}]: {abstract}... (topics: {', '.join(topics)})")
        
        return "\n".join(summaries)
    
    def _fallback_analyze(self, user_idea: str, existing_papers: List[Dict[str, Any]]) -> GapAnalysis:
        """Fallback gap analysis using heuristics."""
        idea_lower = user_idea.lower()
        
        # Simple keyword-based gap detection
        gaps = []
        if "multimodal" in idea_lower and "efficienc" in idea_lower:
            gaps.append("Efficient multimodal architectures for this domain are underexplored")
        if "cross-dataset" in idea_lower or "robust" in idea_lower:
            gaps.append("Cross-dataset generalization evaluation is rarely systematic")
        if "misinformation" in idea_lower:
            gaps.append("Multimodal misinformation detection under distribution shift is limited")
        
        if not gaps:
            gaps = ["Specific gaps require literature analysis"]
        
        return GapAnalysis(
            gaps=gaps,
            gap_confidence=0.4,
            existing_coverage={},
            search_limitations=["Fallback heuristic used - LLM unavailable"]
        )
    
    def identify_underexplored_combinations(
        self, 
        user_topics: List[str], 
        existing_topics: List[List[str]]
    ) -> List[str]:
        """Find topic combinations that are missing from existing work."""
        if not existing_topics:
            return [f"All combinations involving {', '.join(user_topics)} are unexplored"]
        
        # Find user topics not well-covered
        all_existing = set()
        for topics in existing_topics:
            all_existing.update(topics)
        
        missing = set(user_topics) - all_existing
        combinations = []
        
        for t in missing:
            combinations.append(f"Novel topic: {t}")
        
        # Pairwise combinations with existing
        for t1 in user_topics:
            for t2 in list(all_existing)[:5]:
                if t1 != t2:
                    combinations.append(f"Combination: {t1} + {t2}")
        
        return combinations[:10]