"""Novelty Agent - Compares proposed idea with existing work."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class NoveltyAssessment(BaseModel):
    """Novelty assessment result."""
    novelty_score: float = Field(
        description="Novelty score: 0-100, where 100 is completely novel",
        ge=0.0,
        le=100.0
    )
    overlap_percentage: float = Field(
        description="Percentage overlap with existing work: 0-100",
        ge=0.0,
        le=100.0
    )
    existing_papers_overlap: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Papers with their overlap percentages"
    )
    differentiators: List[str] = Field(
        default_factory=list,
        description="Identified differentiators"
    )
    novelty_risk: str = Field(
        description="Novelty risk level: 'high', 'moderate', 'low'"
    )
    assessment: str = Field(
        description="Detailed novelty assessment text"
    )


class NoveltyAgent:
    """Responsibilities: compare proposed idea with existing work, 
    detect overlap, identify differentiators, flag novelty risks."""
    
    def assess(self, 
                user_idea: str, 
                existing_work: List[Dict[str, Any]] = None) -> NoveltyAssessment:
        """Assess novelty of a user idea against existing work."""
        # If no existing work provided, use synthetic assessment
        if not existing_work:
            return self._synthetic_assessment(user_idea)
        
        idea_lower = user_idea.lower()
        
        # Extract topics/concepts from user idea
        user_topics = self._extract_topics(idea_lower)
        
        # Compare with each existing paper
        overlaps = []
        total_overlap = 0
        
        for work in existing_work:
            # Handle both dict and RelatedWork objects
            if hasattr(work, 'paper'):
                # RelatedWork object
                paper = work.paper
                paper_topics = paper.topics
                paper_title = paper.title
            else:
                # Dict
                paper_topics = work.get("topics", [])
                paper_title = work.get("title", "")
            
            # Calculate overlap based on topic intersection
            intersection = len(set(user_topics) & set(paper_topics))
            union = len(set(user_topics) | set(paper_topics))
            
            overlap = (intersection / union * 100) if union > 0 else 0
            total_overlap += overlap
            
            overlaps.append({
                "paper_title": paper_title,
                "overlap_percentage": round(overlap, 1),
                "paper_topics": paper_topics,
                "user_topics": user_topics
            })
        
        # Calculate average and best overlap
        avg_overlap = total_overlap / len(existing_work) if existing_work else 0
        best_overlap = max([o["overlap_percentage"] for o in overlaps]) if overlaps else 0
        
        # Novelty score: inverse of overlap (higher overlap = lower novelty)
        novelty_score = 100.0 - best_overlap  # Use best overlap as the main determinant
        novelty_score = max(0, min(100, novelty_score))  # Clamp to 0-100
        
        # Determine novelty risk
        if best_overlap >= 70:
            novelty_risk = "low"
        elif best_overlap >= 40:
            novelty_risk = "moderate"
        else:
            novelty_risk = "high"
        
        # Identify differentiators (topics in user idea not in existing work)
        differentiators = self._identify_differentiators(user_topics, overlaps)
        
        # Overall assessment text
        assessment = self._generate_assessment(
            novelty_score, best_overlap, novelty_risk, differentiators
        )
        
        return NoveltyAssessment(
            novelty_score=round(novelty_score, 1),
            overlap_percentage=round(best_overlap, 1),
            existing_papers_overlap=overlaps,
            differentiators=differentiators,
            novelty_risk=novelty_risk,
            assessment=assessment
        )
    
    def _synthetic_assessment(self, user_idea: str) -> NoveltyAssessment:
        """Generate a synthetic novelty assessment when no existing work is provided."""
        idea_lower = user_idea.lower()
        
        # Heuristic: check for novel combination keywords
        novel_keywords = ["novel", "first", "unique", "novelty", "novel combination",
                         "novel approach", "new paradigm", "innovative"]
        novel_count = sum(1 for kw in novel_keywords if kw in idea_lower)
        
        # Check for combining different modalities/domains
        combine_keywords = ["combine", "multimodal", "cross", "hybrid", "fusion"]
        combine_count = sum(1 for kw in combine_keywords if kw in idea_lower)
        
        # Base novelty
        base_novelty = min(novel_count * 15 + combine_count * 20, 90)
        if combine_count > 0:
            base_novelty = min(base_novelty + 10, 100)
        
        # Determine risk
        if base_novelty >= 70:
            novelty_risk = "high"
        elif base_novelty >= 40:
            novelty_risk = "moderate"
        else:
            novelty_risk = "low"
        
        # Differentiators
        differentiators = []
        if combine_count > 0:
            differentiators.append("Combines multiple approaches/methods")
        if novel_count > 0:
            differentiators.append("Addresses novel research question")
        
        if not differentiators:
            differentiators = ["Proposes a new research direction"]
        
        assessment = (
            f"The idea {'shows promise of novelty' if base_novelty > 50 else 'may have limited novelty'}. "
            f"Consider evaluating against existing work in the area."
        )
        
        return NoveltyAssessment(
            novelty_score=round(base_novelty, 1),
            overlap_percentage=round(100 - base_novelty, 1),
            existing_papers_overlap=[],
            differentiators=differentiators,
            novelty_risk=novelty_risk,
            assessment=assessment
        )
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract topic keywords from text."""
        # Focus on technical terms - use a curated list of AI/ML keywords
        # to avoid noise from generic words
        technical_terms = {
            "multimodal", "misinformation", "detection", "efficient", "model", "transformer",
            "clip", "cross-modal", "attention", "fusion", "alignment", "correlation",
            "distribution", "shift", "robustness", "generalization", "dataset", "benchmark",
            "fake", "news", "social", "media", "twitter", "facebook", "instagram",
            "classification", "accuracy", "f1", "precision", "recall", "auc",
            "distillation", "pruning", "quantization", "lora", "adapter", "compression",
            "continual", "learning", "streaming", "replay", "buffer", "domain", "adaptation",
            "modality", "dropout", "graceful", "degradation", "unimodal", "baseline",
            "cross-dataset", "cross-platform", "evaluation", "reproducibility"
        }
        
        stop_words = {"the", "a", "an", "and", "or", "but", "is", "are", "was", "were",
                     "been", "be", "being", "to", "of", "in", "for", "on", "with", "as",
                     "an", "this", "that", "these", "those", "my", "your", "our", "their"}
        
        words = [w.strip(".,!?;:").lower() for w in text.split()]
        topics = [w for w in words if w in technical_terms]
        
        # Add bigrams only for known compound terms
        compound_terms = {
            "cross_modal", "cross_dataset", "cross_platform", "fake_news",
            "modality_correlation", "distribution_shift", "modality_dropout",
            "knowledge_distillation", "gradient_descent", "attention_mechanism"
        }
        
        bigrams = []
        word_list = [w for w in words if w not in stop_words]
        for i in range(len(word_list) - 1):
            bigram = f"{word_list[i]}_{word_list[i+1]}"
            if bigram in compound_terms:
                bigrams.append(bigram)
        
        # Also check for hyphenated compounds
        for w in words:
            if "-" in w and w.replace("-", "_") in compound_terms:
                bigrams.append(w.replace("-", "_"))
        
        # Deduplicate and prioritize technical terms
        result = list(set(topics + bigrams))
        # Sort so technical terms come first
        result.sort(key=lambda x: 0 if x in technical_terms else 1)
        
        return result
    
    def _identify_differentiators(
        self, 
        user_topics: List[str], 
        existing_overlaps: List[Dict[str, Any]]
    ) -> List[str]:
        """Identify what differentiates the user idea from existing work."""
        differentiators = []
        
        # Find topics that are unique to the user idea
        all_existing_topics = set()
        for paper in existing_overlaps:
            all_existing_topics.update(paper.get("paper_topics", []))
        
        user_only = set(user_topics) - all_existing_topics
        
        # Filter out generic terms that aren't real differentiators
        generic_terms = {"model", "detection", "social", "media", "efficient", "multimodal", 
                        "system", "approach", "method", "framework", "algorithm", "network"}
        meaningful_unique = [t for t in user_only if t not in generic_terms]
        
        if meaningful_unique:
            for topic in meaningful_unique[:5]:
                differentiators.append(f"Unique focus: {topic}")
        
        # Check for novel combinations - more specific
        has_multimodal = "multimodal" in user_topics or any("multimodal" in t for t in user_topics)
        has_efficient = "efficient" in user_topics or "distillation" in str(user_topics).lower()
        has_cross_dataset = "cross_dataset" in user_topics or "cross-dataset" in str(user_topics).lower()
        has_robust = "robustness" in user_topics or "distribution_shift" in user_topics
        
        if has_multimodal and has_efficient:
            differentiators.append("Efficient multimodal architecture (cross-attention + LoRA adapters)")
        if has_multimodal and has_robust:
            differentiators.append("Robustness-focused multimodal training (modality dropout, domain adversarial)")
        if has_multimodal and has_cross_dataset:
            differentiators.append("Cross-dataset evaluation protocol for multimodal generalization")
        if has_efficient and has_cross_dataset:
            differentiators.append("Efficient model with cross-dataset robustness guarantees")
        
        # Original combination check as fallback
        combination_keywords = ["multimodal", "cross-domain", "hybrid", "fusion",
                              "combined", "integrated"]
        if any(ck in str(user_topics).lower() for ck in combination_keywords):
            if not any("combination" in d.lower() or "efficient" in d.lower() for d in differentiators):
                differentiators.append("Innovative combination of approaches")
        
        if not differentiators:
            differentiators = ["Unique perspective on the research problem"]
        
        return differentiators
    
    def _generate_assessment(
        self, 
        novelty_score: float, 
        best_overlap: float, 
        novelty_risk: str, 
        differentiators: List[str]
    ) -> str:
        """Generate the novelty assessment text."""
        risk_descriptions = {
            "high": "High novelty risk - significant overlap with existing work. "
                   "Strong differentiators needed.",
            "moderate": "Moderate novelty risk - some overlap detected. "
                       "Clear differentiators identified.",
            "low": "Low novelty risk - limited overlap with existing work. "
                  "Idea appears genuinely novel."
        }
        
        description = risk_descriptions.get(novelty_risk, "")
        
        diff_text = ""
        if differentiators:
            diff_text = f"Potential differentiators: {'. '.join(differentiators[:3])}. "
        
        return (
            f"Novelty Assessment:\n"
            f"  Novelty Score: {novelty_score}/100\n"
            f"  Best Overlap: {best_overlap}%\n"
            f"  Risk Level: {novelty_risk.upper()}\n"
            f"  {description}"
            f"{diff_text}"
            f"  Interpretation: {'The idea offers a genuinely new contribution.' 
            if novelty_score > 70 else 'The idea should be evaluated carefully for uniqueness.'}"
        )


# Example usage
if __name__ == "__main__":
    agent = NoveltyAgent()
    
    # Test with existing work
    existing = [
        {"title": "Text-only Misinformation Detection", "topics": ["text", "classification", "misinformation"]},
        {"title": "Image-only Misinformation Detection", "topics": ["image", "visual", "misinformation"]},
        {"title": "Large Multimodal Model", "topics": ["multimodal", "large-scale", "CLIP"]},
        {"title": "Efficient Misinformation Model", "topics": ["efficient", "lightweight", "misinformation"]},
    ]
    
    assessment = agent.assess(
        "Efficient multimodal model for misinformation detection + cross-dataset robustness",
        existing
    )
    print(f"Novelty Score: {assessment.novelty_score}")
    print(f"Best Overlap: {assessment.overlap_percentage}%")
    print(f"Risk: {assessment.novelty_risk}")
    print(f"Differentiators: {assessment.differentiators}")
    print(f"Assessment: {assessment.assessment}")