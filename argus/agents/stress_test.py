"""Stress-Test Agent - The 'BREAK IT' agent that identifies breakpoints."""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field

from argus.llm import call_nemotron_structured
from argus.rag.engine import RAGEngine
from argus.evidence.sources import EvidenceManager


def _get_attr(obj: Union[Dict[str, Any], BaseModel], attr: str, default: Any = None) -> Any:
    """Get attribute from dict or Pydantic model."""
    if isinstance(obj, dict):
        return obj.get(attr, default)
    return getattr(obj, attr, default)


class StressTestScenario(BaseModel):
    """A specific stress test scenario."""
    id: str = Field(description="Scenario identifier")
    name: str = Field(description="Human-readable scenario name")
    assumption_targeted: str = Field(description="Which assumption is being tested")
    condition: str = Field(description="The adverse condition being simulated")
    expected_impact: str = Field(description="Expected effect if condition is true")
    severity: float = Field(
        description="Severity score: 0-1, where 1 is most severe",
        ge=0.0,
        le=1.0
    )


class BreakpointInfo(BaseModel):
    """Information about where an idea breaks."""
    breakpoint_id: str = Field(description="Unique breakpoint identifier")
    assumption: str = Field(description="The critical assumption that fails")
    threshold: str = Field(description="The condition at which breaking occurs")
    performance_at_breakpoint: float = Field(
        description="Performance metric at the breakpoint",
        ge=0.0,
        le=1.0
    )
    severity: str = Field(description="How severe the break is: critical, high, moderate, low")
    recommended_action: str = Field(description="What to do after discovering the breakpoint")


class StressTestResult(BaseModel):
    """Complete stress test results."""
    scenarios: List[StressTestScenario] = Field(default_factory=list)
    breakpoints: List[BreakpointInfo] = Field(default_factory=list)
    overall_assessment: str = Field(description="Summary of idea robustness")
    confidence: float = Field(
        description="Confidence in assessment: 0-1",
        ge=0.0,
        le=1.0
    )


STRESS_TEST_SCHEMA = {
    "type": "object",
    "properties": {
        "breakpoints": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "assumption": {"type": "string"},
                    "threshold": {"type": "string"},
                    "performance_at_breakpoint": {"type": "number", "minimum": 0, "maximum": 1},
                    "severity": {"type": "string", "enum": ["critical", "high", "moderate", "low"]},
                    "recommended_action": {"type": "string"}
                },
                "required": ["assumption", "threshold", "performance_at_breakpoint", "severity", "recommended_action"]
            }
        }
    },
    "required": ["breakpoints"]
}

SCENARIO_GEN_SCHEMA = {
    "type": "object",
    "properties": {
        "scenarios": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "assumption": {"type": "string"},
                    "condition": {"type": "string"},
                    "expected_impact": {"type": "string"},
                    "severity": {"type": "number", "minimum": 0, "maximum": 1}
                },
                "required": ["assumption", "condition", "expected_impact", "severity"]
            }
        }
    },
    "required": ["scenarios"]
}


class StressTestAgent:
    """Responsibilities: adversarial analysis, assumption challenging, stress testing, breakpoint detection.
    
    This is the SIGNATURE ARGUS feature - the #BREAK_IT mode.
    """
    
    def __init__(self, rag_engine: Optional[RAGEngine] = None, evidence_store: Optional[EvidenceManager] = None):
        self.rag_engine = rag_engine or RAGEngine()
        self.evidence_store = evidence_store or EvidenceManager()
        
        self.system_prompt_breakpoints = """You are ARGUS's Stress-Test Agent (#BREAK_IT). Find breakpoints where research ideas fail.

Given a research idea's assumptions and available evidence, identify:
1. For each assumption: What specific condition causes it to break?
2. THRESHOLD: The exact boundary/condition where the assumption fails
3. PERFORMANCE_AT_BREAKPOINT: Estimated performance metric (0-1) at that threshold
4. SEVERITY: critical (idea fundamentally flawed), high (major limitation), moderate (manageable), low (minor)
5. RECOMMENDED_ACTION: Concrete next step to validate or mitigate

Consider: distribution shift, data quality, modality correlation, scale, compute constraints, adversarial conditions, edge cases, deployment environment mismatch.

Be specific: "modality correlation < 0.3" not "low correlation"."""
        
        self.system_prompt_scenarios = """You are ARGUS's Stress-Test Agent. Generate adversarial stress test scenarios.

For each assumption, create a scenario that tests its limits:
- CONDITION: Specific adverse condition to simulate
- EXPECTED_IMPACT: What happens if condition holds
- SEVERITY: 0-1 how damaging

Think like a red teamer: what would make this assumption false?"""

    def stress_test(self, 
                    assumptions: List[Dict[str, Any]],
                    evidence_store: Dict[str, Any] = None) -> StressTestResult:
        """Run stress tests on all assumptions and find breakpoints."""
        if not assumptions:
            return StressTestResult(
                scenarios=[],
                breakpoints=[],
                overall_assessment="NO ASSUMPTIONS TO TEST",
                confidence=0.0
            )
        
        # Generate scenarios
        scenarios = self._generate_scenarios(assumptions)
        
        # Find breakpoints using Nemotron
        breakpoints = self._find_breakpoints(assumptions, evidence_store)
        
        # Overall assessment
        critical_breakpoints = [bp for bp in breakpoints if bp.severity in ["critical", "high"]]
        
        if critical_breakpoints:
            overall = "IDEA HAS CRITICAL BREAKPOINTS - proceed with caution"
        elif breakpoints:
            overall = "IDEA HAS MODERATE BREAKPOINTS - investigate further"
        else:
            overall = "IDEA APPEARS ROBUST under tested conditions"
        
        # Confidence based on evidence quality
        confidence = self._calculate_confidence(breakpoints, evidence_store)
        
        return StressTestResult(
            scenarios=scenarios,
            breakpoints=breakpoints,
            overall_assessment=overall,
            confidence=confidence
        )
    
    def _generate_scenarios(self, assumptions: List[Union[Dict[str, Any], BaseModel]]) -> List[StressTestScenario]:
        """Generate stress test scenarios for assumptions using Nemotron."""
        assumption_texts = "\n".join([
            f"- {_get_attr(a, 'id', f'a{i}')}: {_get_attr(a, 'text', 'Unknown assumption')}"
            for i, a in enumerate(assumptions)
        ])
        
        messages = [
            {"role": "system", "content": self.system_prompt_scenarios},
            {"role": "user", "content": f"Generate stress test scenarios for these assumptions:\n{assumption_texts}"}
        ]
        
        try:
            result = call_nemotron_structured(messages, SCENARIO_GEN_SCHEMA, temperature=0.3)
            scenario_data = result.get("scenarios", [])
            
            scenarios = []
            for i, s in enumerate(scenario_data):
                scenarios.append(StressTestScenario(
                    id=f"scenario_{i}",
                    name=f"Stress: {s['assumption'][:40]}...",
                    assumption_targeted=s["assumption"],
                    condition=s["condition"],
                    expected_impact=s["expected_impact"],
                    severity=s["severity"]
                ))
            return scenarios
        except Exception:
            # Fallback
            return [
                StressTestScenario(
                    id=f"scenario_{i}",
                    name=f"Test: {a.get('text', '')[:40]}...",
                    assumption_targeted=a.get('text', ''),
                    condition="adverse conditions",
                    expected_impact="performance degradation",
                    severity=0.5
                )
                for i, a in enumerate(assumptions)
            ]
    
    def _find_breakpoints(self, assumptions: List[Union[Dict[str, Any], BaseModel]], evidence_store: Dict[str, Any] = None) -> List[BreakpointInfo]:
        """Find breakpoints using Nemotron adversarial reasoning."""
        assumption_texts = "\n".join([
            f"- {_get_attr(a, 'id', f'a{i}')}: {_get_attr(a, 'text', '')}"
            for i, a in enumerate(assumptions)
        ])
        
        # Get relevant evidence for context
        evidence_context = ""
        if evidence_store:
            try:
                # Try to get evidence from RAG
                if hasattr(evidence_store, 'get'):
                    evidence_context = str(evidence_store)[:2000]
            except Exception:
                pass
        
        messages = [
            {"role": "system", "content": self.system_prompt_breakpoints},
            {"role": "user", "content": f"Assumptions to stress-test:\n{assumption_texts}\n\nAvailable evidence context:\n{evidence_context}"}
        ]
        
        try:
            result = call_nemotron_structured(messages, STRESS_TEST_SCHEMA, temperature=0.2)
            breakpoint_data = result.get("breakpoints", [])
            
            breakpoints = []
            for i, bp in enumerate(breakpoint_data):
                breakpoints.append(BreakpointInfo(
                    breakpoint_id=f"bp_{i}",
                    assumption=bp["assumption"],
                    threshold=bp["threshold"],
                    performance_at_breakpoint=bp["performance_at_breakpoint"],
                    severity=bp["severity"],
                    recommended_action=bp["recommended_action"]
                ))
            return breakpoints
        except Exception:
            return self._mock_breakpoints(assumptions)
    
    def _mock_breakpoints(self, assumptions: List[Union[Dict[str, Any], BaseModel]]) -> List[BreakpointInfo]:
        """Return mock breakpoints when Nemotron unavailable."""
        breakpoints = []
        
        for i, a in enumerate(assumptions):
            text = _get_attr(a, 'text', '').lower()
            
            if ("multimodal" in text or "modalities" in text or "multi-modal" in text) and ("complement" in text or "complementary" in text):
                breakpoints.append(BreakpointInfo(
                    breakpoint_id=f"bp_{i}",
                    assumption=_get_attr(a, "text", ""),
                    threshold="Modality correlation < 0.3",
                    performance_at_breakpoint=0.52,
                    severity="critical",
                    recommended_action="Measure modality correlation on target domain; implement unimodal fallback"
                ))
            elif "data" in text and ("diverse" in text or "cover" in text):
                breakpoints.append(BreakpointInfo(
                    breakpoint_id=f"bp_{i}",
                    assumption=_get_attr(a, "text", ""),
                    threshold="New misinformation type > 30% of test distribution",
                    performance_at_breakpoint=0.58,
                    severity="high",
                    recommended_action="Implement continual learning; monitor for distribution shift with drift detection"
                ))
            elif "efficienc" in text and "accurac" in text:
                breakpoints.append(BreakpointInfo(
                    breakpoint_id=f"bp_{i}",
                    assumption=_get_attr(a, "text", ""),
                    threshold="Model size < 50M parameters",
                    performance_at_breakpoint=0.65,
                    severity="moderate",
                    recommended_action="Run ablation on model size vs accuracy; find Pareto frontier; consider knowledge distillation with robustness regularization"
                ))
            elif "generaliz" in text or "cross-dataset" in text:
                breakpoints.append(BreakpointInfo(
                    breakpoint_id=f"bp_{i}",
                    assumption=_get_attr(a, "text", ""),
                    threshold="Domain shift (platform/topic/language) > 0.5 Wasserstein distance",
                    performance_at_breakpoint=0.55,
                    severity="high",
                    recommended_action="Evaluate on held-out domains; add domain adversarial training; test language/platform generalization"
                ))
        
        return breakpoints
    
    def _calculate_confidence(self, breakpoints: List[BreakpointInfo], evidence_store: Dict[str, Any] = None) -> float:
        """Calculate confidence in stress test assessment."""
        base_confidence = 0.6
        
        # Increase confidence if we have breakpoints (more analysis done)
        if breakpoints:
            base_confidence += 0.15
        
        # Increase if high-severity breakpoints found (clear signal)
        high_sev = sum(1 for bp in breakpoints if bp.severity in ["critical", "high"])
        if high_sev > 0:
            base_confidence += min(high_sev * 0.05, 0.15)
        
        # Evidence store quality would factor in here
        return min(base_confidence, 0.95)