"""Nemotron LLM client for ARGUS agents."""

import os
import json
import requests
from typing import Dict, Any, Optional, List
from pydantic import BaseModel


class NemotronConfig:
    """Configuration for Nemotron API."""
    ENDPOINT = os.environ.get(
        "NEMOTRON_ENDPOINT",
        "https://api.nebius.com/v1/chat/completions"
    )
    API_KEY = os.environ.get("NEMOTRON_API_KEY", "demo-key")
    MODEL = os.environ.get("NEMOTRON_MODEL", "nvidia/nemotron-3-ultra")
    TIMEOUT = 60


def call_nemotron(
    messages: List[Dict[str, str]],
    temperature: float = 0.3,
    max_tokens: int = 4096,
    response_format: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Call Nemotron API via Nebius.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        temperature: Sampling temperature (0.0-1.0)
        max_tokens: Maximum tokens in response
        response_format: Optional format specification (e.g., {"type": "json_object"})
    
    Returns:
        Parsed response dict with 'content' and metadata
    """
    if NemotronConfig.API_KEY == "demo-key":
        # Return mock response for demo mode
        return _mock_nemotron_response(messages)
    
    headers = {
        "Authorization": f"Bearer {NemotronConfig.API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": NemotronConfig.MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    
    if response_format:
        payload["response_format"] = response_format
    
    try:
        response = requests.post(
            NemotronConfig.ENDPOINT,
            headers=headers,
            json=payload,
            timeout=NemotronConfig.TIMEOUT
        )
        response.raise_for_status()
        data = response.json()
        
        return {
            "content": data["choices"][0]["message"]["content"],
            "usage": data.get("usage", {}),
            "model": data.get("model", NemotronConfig.MODEL)
        }
    except requests.RequestException as e:
        raise RuntimeError(f"Nemotron API call failed: {e}")
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"Unexpected Nemotron response format: {e}")


def call_nemotron_structured(
    messages: List[Dict[str, str]],
    schema: Dict[str, Any],
    temperature: float = 0.1,
    max_tokens: int = 4096
) -> Dict[str, Any]:
    """
    Call Nemotron with structured JSON output enforcement.
    
    Args:
        messages: List of message dicts
        schema: JSON schema for the expected output
        temperature: Sampling temperature
        max_tokens: Maximum tokens
    
    Returns:
        Parsed JSON object matching schema
    """
    # Add schema instruction to system message
    system_msg = messages[0] if messages and messages[0]["role"] == "system" else {"role": "system", "content": ""}
    system_msg["content"] += f"\n\nYou MUST output valid JSON matching this schema:\n{json.dumps(schema, indent=2)}"
    
    new_messages = [system_msg] + messages[1:] if messages else [system_msg]
    
    result = call_nemotron(
        new_messages,
        temperature=temperature,
        max_tokens=max_tokens,
        response_format={"type": "json_object"}
    )
    
    try:
        return json.loads(result["content"])
    except json.JSONDecodeError as e:
        # Try to extract JSON from response
        content = result["content"]
        start = content.find("{")
        end = content.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(content[start:end])
        raise RuntimeError(f"Failed to parse JSON from Nemotron: {e}")


def _mock_nemotron_response(messages: List[Dict[str, str]]) -> Dict[str, Any]:
    """Return mock response for demo mode without API key."""
    last_user_msg = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
    system_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
    
    # Check system prompt for agent identity first (more reliable)
    # Stress Test Agent - scenarios
    if "generate stress test" in last_user_msg.lower() or "stress test scenario" in last_user_msg.lower():
        return {
            "content": json.dumps({
                "scenarios": [
                    {"assumption": "Text and image modalities provide complementary signals for misinformation", "condition": "Low image-text correlation (stock photos, memes)", "expected_impact": "Multimodal gains disappear, text-only matches performance", "severity": 0.85},
                    {"assumption": "Training data covers diverse misinformation types and domains", "condition": "Emerging misinformation type not in training data", "expected_impact": "Model fails to detect novel misinformation patterns", "severity": 0.75},
                    {"assumption": "Model efficiency gains don't sacrifice detection accuracy", "condition": "Aggressive compression (distillation/pruning)", "expected_impact": "OOD robustness degrades 12-18% while in-domain accuracy maintained", "severity": 0.7}
                ]
            }),
            "usage": {"prompt_tokens": 140, "completion_tokens": 300, "total_tokens": 440},
            "model": "mock"
        }
    
    # Stress Test Agent - breakpoints
    if "stress" in last_user_msg.lower() or "breakpoint" in last_user_msg.lower() or ("assumption" in last_user_msg.lower() and "stress" in system_msg.lower()):
        return {
            "content": json.dumps({
                "breakpoints": [
                    {"assumption": "Text and image modalities provide complementary signals", "threshold": "Modality correlation < 0.3", "severity": "critical", "performance_at_breakpoint": 0.52, "recommended_action": "Measure modality correlation on target domain; add unimodal fallback"},
                    {"assumption": "Training data covers diverse misinformation types", "threshold": "New misinformation type > 30% of test set", "severity": "high", "performance_at_breakpoint": 0.58, "recommended_action": "Implement continual learning; monitor for distribution shift"},
                    {"assumption": "Efficiency gains don't sacrifice accuracy", "threshold": "Model size < 50M parameters", "severity": "moderate", "performance_at_breakpoint": 0.65, "recommended_action": "Run ablation on model size vs accuracy; find Pareto frontier"}
                ]
            }),
            "usage": {"prompt_tokens": 140, "completion_tokens": 300, "total_tokens": 440},
            "model": "mock"
        }

    # Literature Agent - Paper Classification
    if "classify" in last_user_msg.lower() or ("papers to classify" in last_user_msg.lower() and "literature" in system_msg.lower()):
        return {
            "content": json.dumps({
                "papers": [
                    {"title": "CLIP-based Multimodal Misinformation Detection", "authors": ["Smith et al."], "year": 2023, "venue": "ICML", "abstract": "CLIP-based multimodal model for misinformation detection...", "topics": ["multimodal", "misinformation", "CLIP"], "relevance": "baseline", "relevance_score": 0.85},
                    {"title": "Efficient Transformers for Fake News Detection", "authors": ["Chen et al."], "year": 2024, "venue": "ACL", "abstract": "Lightweight transformer architecture...", "topics": ["efficient", "transformer", "fake-news"], "relevance": "extension", "relevance_score": 0.78},
                    {"title": "Cross-Modal Consistency for Misinformation", "authors": ["Lee et al."], "year": 2023, "venue": "CVPR", "abstract": "Cross-modal consistency checking...", "topics": ["cross-modal", "consistency", "misinformation"], "relevance": "counterpoint", "relevance_score": 0.82},
                    {"title": "Limitations of Multimodal Models under Distribution Shift", "authors": ["Gupta et al."], "year": 2024, "venue": "ICLR", "abstract": "Multimodal models more vulnerable to distribution shift...", "topics": ["distribution shift", "domain adaptation", "multimodal"], "relevance": "counterpoint", "relevance_score": 0.88},
                    {"title": "Unimodal Baselines Are Stronger Than You Think", "authors": ["Thompson et al."], "year": 2023, "venue": "ACL", "abstract": "Text-only baselines match multimodal...", "topics": ["unimodal baselines", "reproducibility", "multimodal"], "relevance": "counterpoint", "relevance_score": 0.92}
                ]
            }),
            "usage": {"prompt_tokens": 150, "completion_tokens": 300, "total_tokens": 450},
            "model": "mock"
        }

    # Contradiction Agent - Search Queries
    if ("generate search queries" in last_user_msg.lower() or "search queries" in last_user_msg.lower()) and "contradiction" in system_msg.lower():
        return {
            "content": json.dumps({
                "supporting_queries": [
                    "evidence supporting multimodal misinformation detection accuracy",
                    "multimodal model accuracy misinformation detection",
                    "cross-modal consistency misinformation detection"
                ],
                "contradicting_queries": [
                    "limitations of multimodal misinformation detection accuracy",
                    "evidence against multimodal model accuracy",
                    "failure cases multimodal misinformation detection"
                ]
            }),
            "usage": {"prompt_tokens": 130, "completion_tokens": 280, "total_tokens": 410},
            "model": "mock"
        }

    # Contradiction Agent - Evaluation
    if ("evidence to evaluate" in last_user_msg.lower() or "evaluate evidence" in last_user_msg.lower()) and "contradiction" in system_msg.lower():
        return {
            "content": json.dumps({
                "contradictions": [
                    {"claim": "Multimodal always improves over unimodal", "evidence": "Study shows text-only matches multimodal when images are irrelevant", "source": "Chen et al. 2024", "strength": 0.75, "context": "Social media posts with stock photos"},
                    {"claim": "Efficient models maintain accuracy", "evidence": "Distillation often degrades performance on out-of-distribution data", "source": "Liu et al. 2023", "strength": 0.85, "context": "Domain shift evaluation on misinformation datasets"},
                    {"claim": "Cross-dataset generalization is achievable", "evidence": "Domain shift causes >15% accuracy drop in multimodal models", "source": "Gupta et al. 2024", "strength": 0.9, "context": "Cross-platform misinformation detection"}
                ]
            }),
            "usage": {"prompt_tokens": 130, "completion_tokens": 280, "total_tokens": 410},
            "model": "mock"
        }
    
    # Gap/Novelty Agent
    if "gap" in last_user_msg.lower() or "novelty" in last_user_msg.lower() or "classified" in last_user_msg.lower():
        return {
            "content": json.dumps({
                "gaps": [
                    "No work combines efficiency optimization with cross-dataset robustness for multimodal misinformation",
                    "Limited evaluation on low-resource languages and emerging misinformation types",
                    "Modality alignment assumptions rarely tested under distribution shift"
                ],
                "covered_topics": ["multimodal learning", "misinformation detection", "efficient transformers", "cross-modal alignment"],
                "gap_confidence": 0.75,
                "differentiators": [
                    "Joint efficiency + robustness objective",
                    "Explicit modality correlation analysis",
                    "Cross-dataset evaluation protocol"
                ]
            }),
            "usage": {"prompt_tokens": 120, "completion_tokens": 250, "total_tokens": 370},
            "model": "mock"
        }
    
    # Literature Agent - check system prompt for agent identity
    import re
    if "literature" in last_user_msg.lower() or (re.search(r'\bsearch\b', last_user_msg.lower()) and "literature" in system_msg.lower()):
        return {
            "content": json.dumps({
                "papers": [
                    {"title": "Multimodal Misinformation Detection with CLIP", "authors": ["Smith et al."], "year": 2023, "venue": "ICML", "abstract": "CLIP-based multimodal model for misinformation detection...", "topics": ["multimodal", "misinformation", "CLIP"], "relevance": "baseline", "relevance_score": 0.85},
                    {"title": "Efficient Transformers for Fake News Detection", "authors": ["Chen et al."], "year": 2024, "venue": "ACL", "abstract": "Lightweight transformer architecture...", "topics": ["efficient", "transformer", "fake-news"], "relevance": "extension", "relevance_score": 0.78},
                    {"title": "Cross-Modal Consistency for Misinformation", "authors": ["Lee et al."], "year": 2023, "venue": "CVPR", "abstract": "Cross-modal consistency checking...", "topics": ["cross-modal", "consistency", "misinformation"], "relevance": "counterpoint", "relevance_score": 0.82}
                ]
            }),
            "usage": {"prompt_tokens": 150, "completion_tokens": 300, "total_tokens": 450},
            "model": "mock"
        }
    
    # Intake Agent - only for explicit extraction requests
    if "extract" in last_user_msg.lower() and ("extract" in system_msg.lower() or "intake" in system_msg.lower()):
        return {
            "content": json.dumps({
                "goal": "Build an efficient multimodal model for misinformation detection",
                "domain": "AI/ML - Computer Vision & NLP",
                "inputs": "Text + image social media posts",
                "target": "Misinformation classification (true/false/misleading)",
                "hypothesis": "Multimodal fusion improves detection over unimodal baselines",
                "assumptions": [
                    {"id": "a1", "text": "Text and image modalities provide complementary signals for misinformation", "priority": 1},
                    {"id": "a2", "text": "Training data covers diverse misinformation types and domains", "priority": 2},
                    {"id": "a3", "text": "Model efficiency gains don't sacrifice detection accuracy", "priority": 3}
                ],
                "claims": [
                    {"id": "c1", "text": "Multimodal model achieves >85% accuracy on misinformation detection", "confidence": 0.7},
                    {"id": "c2", "text": "Model is 3x more efficient than comparable multimodal baselines", "confidence": 0.6}
                ],
                "constraints": "Limited compute budget, real-time inference requirement",
                "evaluation": "Accuracy, F1, latency, cross-dataset generalization"
            }),
            "usage": {"prompt_tokens": 100, "completion_tokens": 200, "total_tokens": 300},
            "model": "mock"
        }

    # Feasibility Agent
    if "assess feasibility" in last_user_msg.lower() and "feasibility" in system_msg.lower():
        return {
            "content": json.dumps({
                "overall_score": 68.0,
                "dataset_availability": 75.0,
                "compute_requirements": 60.0,
                "implementation_complexity": 55.0,
                "evaluation_difficulty": 70.0,
                "reproducibility": 50.0,
                "deployment_feasibility": 65.0,
                "bottlenecks": ["Dataset availability (paired data needed)", "Implementation complexity (multimodal fusion)", "Reproducibility (closed-source baselines)"],
                "verdict": "caution"
            }),
            "usage": {"prompt_tokens": 140, "completion_tokens": 300, "total_tokens": 440},
            "model": "mock"
        }

    # Impact Agent
    if "assess impact" in last_user_msg.lower() and "impact" in system_msg.lower():
        return {
            "content": json.dumps({
                "overall_score": 78.0,
                "significance": 85.0,
                "beneficiaries_score": 82.0,
                "domain_impact": 80.0,
                "external_impact": 75.0,
                "ethical_considerations": 65.0,
                "recommendation": "high",
                "key_beneficiaries": ["social media users", "platforms", "society", "researchers", "journalists", "fact-checkers"]
            }),
            "usage": {"prompt_tokens": 130, "completion_tokens": 280, "total_tokens": 410},
            "model": "mock"
        }
    
    # Generic fallback
    return {
        "content": json.dumps({"response": "Mock Nemotron response", "input": last_user_msg[:100]}),
        "usage": {"prompt_tokens": 50, "completion_tokens": 100, "total_tokens": 150},
        "model": "mock"
    }