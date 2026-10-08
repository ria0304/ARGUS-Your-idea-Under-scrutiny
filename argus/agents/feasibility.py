"""Feasibility Agent - Checks practicality of implementing the idea."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class FeasibilityScore(BaseModel):
    """Feasibility assessment result."""
    overall_score: float = Field(
        description="Overall feasibility: 0-1, where 1 is most feasible",
        ge=0.0,
        le=1.0
    )
    dataset_availability: float = Field(
        description="Dataset availability score: 0-1",
        ge=0.0,
        le=1.0
    )
    compute_requirements: float = Field(
        description="Compute requirements feasibility: 0-1, where 1 is low compute",
        ge=0.0,
        le=1.0
    )
    implementation_complexity: float = Field(
        description="Implementation complexity: 0-1, where 1 is simple",
        ge=0.0,
        le=1.0
    )
    evaluation_difficulty: float = Field(
        description="Evaluation difficulty: 0-1, where 1 is easy to evaluate",
        ge=0.0,
        le=1.0
    )
    reproducibility: float = Field(
        description="Reproducibility score: 0-1",
        ge=0.0,
        le=1.0
    )
    deployment_feasibility: float = Field(
        description="Deployment feasibility: 0-1",
        ge=0.0,
        le=1.0
    )
    bottlenecks: List[str] = Field(
        default_factory=list,
        description="Identified bottleneck areas"
    )
    verdict: str = Field(
        description="Overall verdict: 'feasible', 'caution', 'challenging', 'very_difficult'"
    )


class FeasibilityAgent:
    """Responsibilities: check dataset availability, compute requirements, 
    implementation complexity, evaluation difficulty, reproducibility, deployment feasibility."""
    
    def assess(self, 
                idea: str, 
                assumptions: List[Dict[str, Any]] = None) -> FeasibilityScore:
        """Assess the feasibility of an idea."""
        # TODO: Implement comprehensive feasibility assessment
        # For now, use heuristics based on common research challenges
        
        # Analyze idea for keywords that suggest feasibility factors
        idea_lower = idea.lower()
        
        # Dataset availability heuristics
        dataset_keywords = ["dataset", "benchmark", "public", "dataset available"]
        compute_keywords = ["compute", "gpu", "resource", "training"]
        complexity_keywords = ["simple", "baseline", "efficient", "complex", "architecture"]
        
        dataset_score = self._calculate_keyword_score(idea_lower, dataset_keywords)
        compute_score = self._calculate_keyword_score(idea_lower, compute_keywords)
        complexity_score = self._calculate_keyword_score(idea_lower, complexity_keywords)
        
        # Invert complexity: more "simple" keywords = higher score
        complexity_final = 1.0 - complexity_score
        
        # Evaluation difficulty: depends on whether there are standard metrics
        eval_keywords = ["metric", "accuracy", "f1", "evaluation", "baseline"]
        eval_score = self._calculate_keyword_score(idea_lower, eval_keywords)
        
        # Reproducibility: open source, public code
        repo_keywords = ["open-source", "code", "reproducible", "github"]
        repo_score = self._calculate_keyword_score(idea_lower, repo_keywords)
        
        # Deployment: deployment, production, deployment-friendly
        deploy_keywords = ["deploy", "production", "lightweight", "mobile", "edge"]
        deploy_score = self._calculate_keyword_score(idea_lower, deploy_keywords)
        
        # Weighted overall score
        overall = (
            dataset_score * 0.25 +
            compute_score * 0.20 +
            complexity_final * 0.20 +
            (1.0 - eval_score) * 0.15 +  # Lower eval keywords = harder evaluation = lower score
            repo_score * 0.10 +
            deploy_score * 0.10
        )
        
        # Determine verdict
        if overall >= 0.7:
            verdict = "feasible"
        elif overall >= 0.4:
            verdict = "caution"
        elif overall >= 0.2:
            verdict = "challenging"
        else:
            verdict = "very_difficult"
        
        # Extract bottlenecks
        bottlenecks = []
        if dataset_score < 0.3:
            bottlenecks.append("Dataset availability")
        if compute_score < 0.3:
            bottlenecks.append("Compute requirements")
        if complexity_score < 0.3:
            bottlenecks.append("Implementation complexity")
        if eval_score < 0.3:
            bottlenecks.append("Evaluation difficulty")
        if repo_score < 0.3:
            bottlenecks.append("Reproducibility (lack of open code)")
        if deploy_score < 0.3:
            bottlenecks.append("Deployment feasibility")
        
        return FeasibilityScore(
            overall_score=round(overall, 3),
            dataset_availability=round(dataset_score, 3),
            compute_requirements=round(compute_score, 3),
            implementation_complexity=round(complexity_final, 3),
            evaluation_difficulty=round(1.0 - eval_score, 3),
            reproducibility=round(repo_score, 3),
            deployment_feasibility=round(deploy_score, 3),
            bottlenecks=bottlenecks,
            verdict=verdict
        )
    
    def _calculate_keyword_score(self, text: str, keywords: List[str]) -> float:
        """Calculate a score based on keyword presence in text."""
        if not keywords:
            return 0.0
        
        found = sum(1 for kw in keywords if kw in text)
        return min(found / len(keywords), 1.0) if keywords else 0.0