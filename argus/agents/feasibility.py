"""Feasibility Agent - Checks practicality of implementing the idea."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from argus.llm import call_nemotron_structured


class FeasibilityScore(BaseModel):
    """Feasibility assessment result."""
    overall_score: float = Field(
        description="Overall feasibility: 0-100, where 100 is most feasible",
        ge=0.0,
        le=100.0
    )
    dataset_availability: float = Field(
        description="Dataset availability score: 0-100",
        ge=0.0,
        le=100.0
    )
    compute_requirements: float = Field(
        description="Compute requirements feasibility: 0-100, where 100 is low compute",
        ge=0.0,
        le=100.0
    )
    implementation_complexity: float = Field(
        description="Implementation complexity: 0-100, where 100 is simple",
        ge=0.0,
        le=100.0
    )
    evaluation_difficulty: float = Field(
        description="Evaluation difficulty: 0-100, where 100 is easy to evaluate",
        ge=0.0,
        le=100.0
    )
    reproducibility: float = Field(
        description="Reproducibility score: 0-100",
        ge=0.0,
        le=100.0
    )
    deployment_feasibility: float = Field(
        description="Deployment feasibility: 0-100",
        ge=0.0,
        le=100.0
    )
    bottlenecks: List[str] = Field(
        default_factory=list,
        description="Identified bottleneck areas"
    )
    verdict: str = Field(
        description="Overall verdict: 'feasible', 'caution', 'challenging', 'very_difficult'"
    )


FEASIBILITY_SCHEMA = {
    "type": "object",
    "properties": {
        "overall_score": {"type": "number", "minimum": 0, "maximum": 100},
        "dataset_availability": {"type": "number", "minimum": 0, "maximum": 100},
        "compute_requirements": {"type": "number", "minimum": 0, "maximum": 100},
        "implementation_complexity": {"type": "number", "minimum": 0, "maximum": 100},
        "evaluation_difficulty": {"type": "number", "minimum": 0, "maximum": 100},
        "reproducibility": {"type": "number", "minimum": 0, "maximum": 100},
        "deployment_feasibility": {"type": "number", "minimum": 0, "maximum": 100},
        "bottlenecks": {"type": "array", "items": {"type": "string"}},
        "verdict": {"type": "string", "enum": ["feasible", "caution", "challenging", "very_difficult"]}
    },
    "required": ["overall_score", "dataset_availability", "compute_requirements", "implementation_complexity", "evaluation_difficulty", "reproducibility", "deployment_feasibility", "bottlenecks", "verdict"]
}


class FeasibilityAgent:
    """Responsibilities: check dataset availability, compute requirements, 
    implementation complexity, evaluation difficulty, reproducibility, deployment feasibility."""
    
    def __init__(self):
        self.system_prompt = """You are ARGUS's Feasibility Agent. Assess the practical feasibility of implementing a research idea.

Score each dimension 0-100 (100 = most feasible):
1. DATASET_AVAILABILITY: Are suitable public datasets available? Benchmarks?
2. COMPUTE_REQUIREMENTS: Can this run on available hardware? (100 = runs on laptop, 0 = needs massive cluster)
3. IMPLEMENTATION_COMPLEXITY: How complex to implement? (100 = straightforward, 0 = novel architecture)
4. EVALUATION_DIFFICULTY: Are there standard metrics/baselines? (100 = easy to evaluate)
5. REPRODUCIBILITY: Is code likely to be open? Dependencies standard?
6. DEPLOYMENT_FEASIBILITY: Can the result be deployed? (100 = lightweight, edge-deployable)

Identify BOTTLENECKS and give VERDICT: feasible/caution/challenging/very_difficult.

Consider: multimodal models need paired data, efficient models need optimization expertise, misinformation has public datasets (MM-COVID, FakeNewsNet), standard metrics exist (accuracy, F1, AUC)."""

    def assess(self, 
                idea: str, 
                assumptions: List[Dict[str, Any]] = None) -> FeasibilityScore:
        """Assess the feasibility of an idea using Nemotron."""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Assess feasibility of this research idea:\n\n{idea}"}
        ]
        
        try:
            result = call_nemotron_structured(messages, FEASIBILITY_SCHEMA, temperature=0.2)
            
            return FeasibilityScore(
                overall_score=result.get("overall_score", 65.0),
                dataset_availability=result.get("dataset_availability", 70.0),
                compute_requirements=result.get("compute_requirements", 60.0),
                implementation_complexity=result.get("implementation_complexity", 55.0),
                evaluation_difficulty=result.get("evaluation_difficulty", 75.0),
                reproducibility=result.get("reproducibility", 50.0),
                deployment_feasibility=result.get("deployment_feasibility", 60.0),
                bottlenecks=result.get("bottlenecks", []),
                verdict=result.get("verdict", "caution")
            )
        except Exception as e:
            return self._fallback_assess(idea)
    
    def _fallback_assess(self, idea: str) -> FeasibilityScore:
        """Fallback heuristic assessment."""
        idea_lower = idea.lower()
        
        # Base scores for multimodal misinformation detection
        scores = {
            "dataset_availability": 75.0,  # MM-COVID, FakeNewsNet, etc.
            "compute_requirements": 55.0,  # Needs GPU but not massive
            "implementation_complexity": 50.0,  # Multimodal fusion is complex
            "evaluation_difficulty": 70.0,  # Standard metrics exist
            "reproducibility": 45.0,  # Often closed-source
            "deployment_feasibility": 60.0,  # Can be optimized
        }
        
        # Adjust for keywords
        if "efficient" in idea_lower:
            scores["compute_requirements"] += 10
            scores["deployment_feasibility"] += 10
        if "multimodal" in idea_lower:
            scores["implementation_complexity"] -= 10
            scores["dataset_availability"] -= 5  # Need paired data
        if "misinformation" in idea_lower:
            scores["dataset_availability"] += 10  # Public datasets exist
        
        # Clamp
        for k in scores:
            scores[k] = max(0, min(100, scores[k]))
        
        overall = (
            scores["dataset_availability"] * 0.25 +
            scores["compute_requirements"] * 0.20 +
            scores["implementation_complexity"] * 0.20 +
            scores["evaluation_difficulty"] * 0.15 +
            scores["reproducibility"] * 0.10 +
            scores["deployment_feasibility"] * 0.10
        )
        
        bottlenecks = []
        if scores["dataset_availability"] < 50: bottlenecks.append("Dataset availability")
        if scores["compute_requirements"] < 50: bottlenecks.append("Compute requirements")
        if scores["implementation_complexity"] < 50: bottlenecks.append("Implementation complexity")
        if scores["evaluation_difficulty"] < 50: bottlenecks.append("Evaluation difficulty")
        if scores["reproducibility"] < 50: bottlenecks.append("Reproducibility (lack of open code)")
        if scores["deployment_feasibility"] < 50: bottlenecks.append("Deployment feasibility")
        
        if overall >= 70: verdict = "feasible"
        elif overall >= 50: verdict = "caution"
        elif overall >= 30: verdict = "challenging"
        else: verdict = "very_difficult"
        
        return FeasibilityScore(
            overall_score=round(overall, 1),
            dataset_availability=scores["dataset_availability"],
            compute_requirements=scores["compute_requirements"],
            implementation_complexity=scores["implementation_complexity"],
            evaluation_difficulty=scores["evaluation_difficulty"],
            reproducibility=scores["reproducibility"],
            deployment_feasibility=scores["deployment_feasibility"],
            bottlenecks=bottlenecks,
            verdict=verdict
        )