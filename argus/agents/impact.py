"""Impact Agent - Evaluates the significance and reach of the idea."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ImpactScore(BaseModel):
    """Impact assessment result."""
    overall_score: float = Field(
        description="Overall impact: 0-10 scale",
        ge=0.0,
        le=10.0
    )
    significance: float = Field(
        description="Problem significance: 0-10",
        ge=0.0,
        le=10.0
    )
    beneficiaries: float = Field(
        description="Number/ proportion of beneficiaries: 0-10",
        ge=0.0,
        le=10.0
    )
    domain_impact: float = Field(
        description="Impact within the domain: 0-10",
        ge=0.0,
        le=10.0
    )
    external_impact: float = Field(
        description="Potential impact outside original domain: 0-10",
        ge=0.0,
        le=10.0
    )
    ethical_considerations: float = Field(
        description="Ethical impact score: 0-10 (higher = more ethical attention needed)",
        ge=0.0,
        le=10.0
    )
    recommendation: str = Field(
        description="Impact recommendation: 'high', 'moderate', 'low', 'controversial'"
    )
    key_beneficiaries: List[str] = Field(
        default_factory=list,
        description="Groups or entities that benefit"
    )


class ImpactAgent:
    """Responsibilities: check who benefits, what problem is solved, 
    significance outside experiment, broader impact."""
    
    def assess(self, 
                idea: str, 
                domain: str = "unknown") -> ImpactScore:
        """Assess the impact of an idea."""
        idea_lower = idea.lower()
        
        # Significance heuristics
        significant_keywords = ["critical", "major", "significant", "important", 
                               "problem", "challenge", "improve", " breakthrough"]
        significance_score = self._calculate_keyword_score(idea_lower, significant_keywords) * 8 + 3
        significance_score = min(significance_score, 10.0)
        
        # Beneficiary heuristics
        beneficiary_keywords = ["patients", "users", "society", "researchers", 
                               "industry", "healthcare", "education", "everyone"]
        beneficiary_count = sum(1 for kw in beneficiary_keywords if kw in idea_lower)
        beneficiaries_score = min(beneficiary_count * 2 + 3, 10.0)
        
        # Domain impact
        domain_score = 7.0  # Default moderate domain impact
        if domain and domain != "unknown":
            domain_score = 8.0
        
        # External impact (cross-domain)
        external_keywords = ["transfer", "generalize", "cross-domain", "applicable", 
                            "beyond", "other fields", "other domains"]
        external_score = self._calculate_keyword_score(idea_lower, external_keywords) * 6 + 2
        external_score = min(external_score, 10.0)
        
        # Ethical considerations
        ethical_keywords = ["ethical", "bias", "fairness", "privacy", "risk", 
                           "safety", "responsible"]
        ethical_score = self._calculate_keyword_score(idea_lower, ethical_keywords) * 5 + 2
        ethical_score = min(ethical_score, 10.0)
        
        # Determine recommendation
        if significance_score >= 8 or external_score >= 8:
            recommendation = "high"
        elif significance_score >= 6 or external_score >= 6:
            recommendation = "moderate"
        elif significance_score >= 4:
            recommendation = "low"
        else:
            recommendation = "controversial"
        
        # Identify key beneficiaries
        key_beneficiaries = []
        for kw in beneficiary_keywords:
            if kw in idea_lower:
                key_beneficiaries.append(kw)
        
        if not key_beneficiaries:
            key_beneficiaries = ["research community"]
        
        return ImpactScore(
            overall_score=round((significance_score + beneficiaries_score + external_score + domain_score) / 4, 1),
            significance=round(significance_score, 1),
            beneficiaries=round(beneficiaries_score, 1),
            domain_impact=round(domain_score, 1),
            external_impact=round(external_score, 1),
            ethical_considerations=round(ethical_score, 1),
            recommendation=recommendation,
            key_beneficiaries=key_beneficiaries
        )
    
    def _calculate_keyword_score(self, text: str, keywords: List[str]) -> float:
        """Calculate a normalized keyword score (0-1)."""
        if not keywords:
            return 0.0
        found = sum(1 for kw in keywords if kw in text)
        return min(found / len(keywords), 1.0)