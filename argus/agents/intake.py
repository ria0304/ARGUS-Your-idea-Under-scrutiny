"""Intake Agent - Understand input and extract entities, claims, assumptions."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import json

from argus.llm import call_nemotron_structured


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


EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "goal": {"type": "string", "description": "The high-level objective or goal"},
        "domain": {"type": "string", "description": "Research/domain area"},
        "inputs": {"type": "string", "description": "Input data types and sources"},
        "target": {"type": "string", "description": "Target output or prediction"},
        "hypothesis": {"type": "string", "description": "Core hypothesis being proposed"},
        "assumptions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "text": {"type": "string"},
                    "priority": {"type": "integer", "minimum": 1, "maximum": 5}
                },
                "required": ["id", "text", "priority"]
            }
        },
        "claims": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "text": {"type": "string"},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1}
                },
                "required": ["id", "text", "confidence"]
            }
        },
        "constraints": {"type": "string"},
        "evaluation": {"type": "string"}
    },
    "required": ["goal", "domain", "inputs", "target", "hypothesis", "assumptions", "claims", "constraints", "evaluation"]
}


class IntakeAgent:
    """Responsible for understanding input, identifying objective, extracting entities."""
    
    def __init__(self):
        self.system_prompt = """You are ARGUS's Intake Agent. Your job is to analyze a research idea, proposal, or decision and extract structured information.

Extract the following from the user's input:
1. GOAL: The high-level objective
2. DOMAIN: The research/application domain
3. INPUTS: What data/types go into the system
4. TARGET: What the system outputs/predicts
5. HYPOTHESIS: The core claim being made
6. ASSUMPTIONS: Hidden premises the idea depends on (rank by priority 1=highest)
7. CLAIMS: Explicit measurable assertions (with confidence 0-1)
8. CONSTRAINTS: Limitations, requirements, boundaries
9. EVALUATION: How success would be measured

Be thorough but concise. Identify assumptions that are critical to the idea's success."""

    def extract(self, raw_input: str) -> ExtractedIdeas:
        """Extract structured information from raw user input using Nemotron."""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Analyze this research idea and extract structured information:\n\n{raw_input}"}
        ]
        
        try:
            result = call_nemotron_structured(messages, EXTRACTION_SCHEMA, temperature=0.1)
            
            # Convert to Pydantic models
            assumptions = [
                Assumption(
                    id=a.get("id", f"a{i}"),
                    text=a["text"],
                    status="unknown",
                    priority=a.get("priority", 3)
                )
                for i, a in enumerate(result.get("assumptions", []))
            ]
            
            claims = [
                Claim(
                    id=c.get("id", f"c{i}"),
                    text=c["text"],
                    confidence=c.get("confidence", 0.5)
                )
                for i, c in enumerate(result.get("claims", []))
            ]
            
            return ExtractedIdeas(
                goal=result.get("goal", ""),
                domain=result.get("domain", ""),
                inputs=result.get("inputs", ""),
                target=result.get("target", ""),
                hypothesis=result.get("hypothesis", ""),
                assumptions=assumptions,
                claims=claims,
                constraints=result.get("constraints", ""),
                evaluation=result.get("evaluation", "")
            )
        except Exception as e:
            # Fallback to basic extraction
            return self._fallback_extract(raw_input)
    
    def _fallback_extract(self, raw_input: str) -> ExtractedIdeas:
        """Fallback extraction when LLM is unavailable."""
        return ExtractedIdeas(
            goal="Investigate user idea",
            domain="Unknown",
            inputs="Not specified",
            target="Not specified",
            hypothesis="",
            assumptions=[],
            claims=[],
            constraints="",
            evaluation=""
        )
    
    def identify_assumptions(self, text: str) -> List[Assumption]:
        """Identify hidden assumptions in the proposal text."""
        extracted = self.extract(text)
        return extracted.assumptions
    
    def identify_claims(self, text: str) -> List[Claim]:
        """Identify explicit claims in the proposal text."""
        extracted = self.extract(text)
        return extracted.claims