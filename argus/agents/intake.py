"""Intake Agent - Understand input and extract entities, claims, assumptions."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class Assumption(BaseModel):
    """A single assumption extracted from the user's input."""
    id: str = Field(description="Unique assumption identifier")
    text: str = Field(description="The assumption statement")
    status: str = Field(
        default="unknown",
        description="Evidence status: strongly_supported, moderately_supported, weak_evidence, unknown, contradictory"
    )
    priority: int = Field(
        default=3,
        description="Priority level: 1 (highest) to 5 (lowest)"
    )


class Claim(BaseModel):
    """A claim extracted from the user's input."""
    id: str = Field(description="Unique claim identifier")
    text: str = Field(description="The claim statement")
    confidence: float = Field(
        default=0.5,
        description="Initial confidence score 0-1"
    )


class IdeaInput(BaseModel):
    """Structured representation of user input."""
    raw_text: str
    goal: str
    domain: str
    inputs: str
    target: str
    hypothesis: str
    constraints: str = Field(default="")
    evaluation: str = Field(default="")


class ExtractedIdeas(BaseModel):
    """Complete extraction from user input."""
    goal: str
    domain: str
    inputs: str
    target: str
    hypothesis: str
    assumptions: List[Assumption] = Field(default_factory=list)
    claims: List[Claim] = Field(default_factory=list)
    constraints: str
    evaluation: str


class IntakeAgent:
    """Responsible for understanding input, identifying objective, extracting entities."""
    
    def extract(self, raw_input: str) -> ExtractedIdeas:
        """Extract structured information from raw user input."""
        # TODO: Implement NLP extraction or use LLM
        # For now, basic parsing
        return ExtractedIdeas(
            goal="",
            domain="",
            inputs="",
            target="",
            hypothesis="",
            assumptions=[],
            claims=[],
            constraints="",
            evaluation=""
        )
    
    def identify_assumptions(self, text: str) -> List[Assumption]:
        """Identify hidden assumptions in the proposal text."""
        # TODO: Implement assumption extraction
        return []
    
    def identify_claims(self, text: str) -> List[Claim]:
        """Identify explicit claims in the proposal text."""
        # TODO: Implement claim extraction
        return []