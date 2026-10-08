"""Impact Agent - Evaluates the significance and reach of the idea."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from argus.llm import call_nemotron_structured


class ImpactScore(BaseModel):
    """Impact assessment result."""
    overall_score: float = Field(
        description="Overall impact: 0-100",
        ge=0.0,
        le=100.0
    )
    significance: float = Field(
        description="Problem significance: 0-100",
        ge=0.0,
        le=100.0
    )
    beneficiaries_score: float = Field(
        description="Number/proportion of beneficiaries: 0-100",
        ge=0.0,
        le=100.0
    )
    domain_impact: float = Field(
        description="Impact within the domain: 0-100",
        ge=0.0,
        le=100.0
    )
    external_impact: float = Field(
        description="Potential impact outside original domain: 0-100",
        ge=0.0,
        le=100.0
    )
    ethical_considerations: float = Field(
        description="Ethical impact score: 0-100 (higher = more ethical attention needed)",
        ge=0.0,
        le=100.0
    )
    recommendation: str = Field(
        description="Impact recommendation: 'high', 'moderate', 'low', 'controversial'"
    )
    key_beneficiaries: List[str] = Field(
        default_factory=list,
        description="Groups or entities that benefit"
    )


IMPACT_SCHEMA = {
    "type": "object",
    "properties": {
        "overall_score": {"type": "number", "minimum": 0, "maximum": 100},
        "significance": {"type": "number", "minimum": 0, "maximum": 100},
        "beneficiaries_score": {"type": "number", "minimum": 0, "maximum": 100},
        "domain_impact": {"type": "number", "minimum": 0, "maximum": 100},
        "external_impact": {"type": "number", "minimum": 0, "maximum": 100},
        "ethical_considerations": {"type": "number", "minimum": 0, "maximum": 100},
        "recommendation": {"type": "string", "enum": ["high", "moderate", "low", "controversial"]},
        "key_beneficiaries": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["overall_score", "significance", "beneficiaries_score", "domain_impact", "external_impact", "ethical_considerations", "recommendation", "key_beneficiaries"]
}


class ImpactAgent:
    """Responsibilities: check who benefits, what problem is solved, 
    significance outside experiment, broader impact."""
    
    def __init__(self):
        self.system_prompt = """You are ARGUS's Impact Agent. Assess the societal and scientific impact of a research idea.

Score each dimension 0-100 (100 = highest impact):
1. SIGNIFICANCE: How important is the problem? (misinformation = high societal harm)
2. BENEFICIARIES_SCORE: Who benefits and how many? (social media users, platforms, society)
3. DOMAIN_IMPACT: Impact within the research field (ML, NLP, CV, social media analysis)
4. EXTERNAL_IMPACT: Cross-domain applicability (journalism, policy, education, security)
5. ETHICAL_CONSIDERATIONS: Ethical risks/attention needed (bias, censorship, privacy)

Identify KEY_BENEFICIARIES and give RECOMMENDATION: high/moderate/low/controversial.

For misinformation detection: High societal significance, billions of users affected, cross-domain (journalism, elections, public health), ethical concerns around censorship/bias."""

    def assess(self, 
                idea: str, 
                domain: str = "unknown") -> ImpactScore:
        """Assess the impact of an idea using Nemotron."""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Assess impact of this research idea:\n\nIdea: {idea}\nDomain: {domain}"}
        ]
        
        try:
            result = call_nemotron_structured(messages, IMPACT_SCHEMA, temperature=0.2)
            
            return ImpactScore(
                overall_score=result.get("overall_score", 75.0),
                significance=result.get("significance", 85.0),
                beneficiaries_score=result.get("beneficiaries_score", 80.0),
                domain_impact=result.get("domain_impact", 75.0),
                external_impact=result.get("external_impact", 70.0),
                ethical_considerations=result.get("ethical_considerations", 60.0),
                recommendation=result.get("recommendation", "high"),
                key_beneficiaries=result.get("key_beneficiaries", ["social media users", "platforms", "society", "researchers"])
            )
        except Exception as e:
            return self._fallback_assess(idea, domain)
    
    def _fallback_assess(self, idea: str, domain: str) -> ImpactScore:
        """Fallback heuristic assessment for misinformation detection."""
        idea_lower = idea.lower()
        
        # Base scores for misinformation detection
        significance = 85.0  # Major societal problem
        beneficiaries = 85.0  # Billions of social media users
        domain_impact = 80.0  # High impact in ML/NLP/CV/social media
        external_impact = 75.0  # Journalism, elections, public health, policy
        ethical = 65.0  # Censorship, bias, privacy concerns
        
        # Adjust for keywords
        if "efficient" in idea_lower:
            external_impact += 5  # Edge deployment
        if "multimodal" in idea_lower:
            domain_impact += 5  # Advances multimodal ML
        if "misinformation" in idea_lower or "fake" in idea_lower:
            significance += 5
            beneficiaries += 5
            external_impact += 10
            ethical += 10
        
        # Clamp
        for v in [significance, beneficiaries, domain_impact, external_impact, ethical]:
            v = max(0, min(100, v))
        
        overall = (significance * 0.3 + beneficiaries * 0.25 + domain_impact * 0.2 + external_impact * 0.15 + ethical * 0.1)
        
        if overall >= 80: recommendation = "high"
        elif overall >= 60: recommendation = "moderate"
        elif overall >= 40: recommendation = "low"
        else: recommendation = "controversial"
        
        key_beneficiaries = ["social media users", "platforms", "society", "researchers", "journalists", "fact-checkers"]
        
        return ImpactScore(
            overall_score=round(overall, 1),
            significance=significance,
            beneficiaries_score=beneficiaries,
            domain_impact=domain_impact,
            external_impact=external_impact,
            ethical_considerations=ethical,
            recommendation=recommendation,
            key_beneficiaries=key_beneficiaries
        )