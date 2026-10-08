#!/usr/bin/env python3
"""
Evidence Ingestion Script - Populates Qdrant with research papers for ARGUS.
Run this to seed the vector database with domain-relevant literature.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from argus.rag.qdrant_engine import QdrantRAGEngine


# Sample evidence corpus for multimodal misinformation detection
EVIDENCE_CORPUS = [
    {
        "source": "arXiv:2305.12345",
        "title": "CLIP-based Multimodal Misinformation Detection",
        "content": "We propose a CLIP-based multimodal framework for detecting misinformation in social media posts. Our model achieves 87.3% accuracy on the MM-COVID dataset, outperforming text-only baselines by 8.4%. The model leverages cross-modal attention to align visual and textual features.",
        "claim": "Multimodal fusion improves misinformation detection accuracy",
        "support_type": "supporting",
        "confidence": 0.85,
        "section": "Experiments",
        "year": 2023,
        "author": "Smith et al.",
        "topics": ["multimodal", "misinformation", "CLIP", "cross-modal attention"],
        "venue": "ICML 2023"
    },
    {
        "source": "arXiv:2308.06789",
        "title": "Efficient Transformers for Fake News Detection",
        "content": "We introduce a lightweight transformer architecture that reduces parameters by 68% while maintaining 92% of the performance of BERT-large on fake news detection. The model uses knowledge distillation and structured pruning.",
        "claim": "Efficient models can maintain accuracy on misinformation detection",
        "support_type": "supporting",
        "confidence": 0.78,
        "section": "Results",
        "year": 2024,
        "author": "Chen et al.",
        "topics": ["efficient", "transformer", "distillation", "fake-news"],
        "venue": "ACL 2024"
    },
    {
        "source": "arXiv:2304.01234",
        "title": "Cross-Modal Consistency Checking for Misinformation",
        "content": "We present a method that detects misinformation by checking consistency between image and text modalities. When modalities contradict, the system flags potential misinformation. Achieves 82% AUC on Twitter multimodal dataset.",
        "claim": "Cross-modal consistency is a reliable signal for misinformation",
        "support_type": "supporting",
        "confidence": 0.82,
        "section": "Methodology",
        "year": 2023,
        "author": "Lee et al.",
        "topics": ["cross-modal", "consistency", "misinformation", "Twitter"],
        "venue": "CVPR 2023"
    },
    {
        "source": "arXiv:2401.05678",
        "title": "Limitations of Multimodal Models under Distribution Shift",
        "content": "We evaluate multimodal misinformation models under domain shift (platform, topic, language). Performance drops 15-22% compared to 8-12% for unimodal text models. Multimodal models are MORE sensitive to distribution shift due to modality alignment assumptions.",
        "claim": "Multimodal models are more vulnerable to distribution shift",
        "support_type": "contradicting",
        "confidence": 0.88,
        "section": "Experiments",
        "year": 2024,
        "author": "Gupta et al.",
        "topics": ["distribution shift", "domain adaptation", "multimodal", "robustness"],
        "venue": "ICLR 2024"
    },
    {
        "source": "arXiv:2310.09876",
        "title": "When Does Multimodal Help? Modality Correlation Analysis",
        "content": "We systematically vary image-text correlation and measure multimodal model performance. Multimodal gains disappear when modality correlation drops below 0.3. Text-only models match or exceed multimodal performance when visual signals are noisy or irrelevant (e.g., stock photos, memes).",
        "claim": "Multimodal improvement depends critically on modality correlation",
        "support_type": "contradicting",
        "confidence": 0.91,
        "section": "Analysis",
        "year": 2023,
        "author": "Chen et al.",
        "topics": ["modality correlation", "multimodal", "ablation", "noisy images"],
        "venue": "NeurIPS 2023"
    },
    {
        "source": "arXiv:2403.01111",
        "title": "Distillation Degrades Out-of-Distribution Robustness",
        "content": "Knowledge distillation from large multimodal teachers to efficient students degrades OOD robustness by 12-18% on misinformation detection tasks. The student models learn spurious correlations that don't generalize. Robustness-aware distillation mitigates but doesn't eliminate this gap.",
        "claim": "Model compression via distillation harms OOD generalization",
        "support_type": "contradicting",
        "confidence": 0.85,
        "section": "Results",
        "year": 2024,
        "author": "Liu et al.",
        "topics": ["distillation", "OOD robustness", "compression", "misinformation"],
        "venue": "ICML 2024"
    },
    {
        "source": "arXiv:2309.04444",
        "title": "Cross-Platform Misinformation Detection Benchmark",
        "content": "We introduce XPlatform-Misinfo, a benchmark for cross-platform generalization. Models trained on Twitter data drop 18% accuracy on Facebook/Instagram data. Multimodal models show larger drops (22%) than text-only (14%) due to platform-specific visual styles.",
        "claim": "Cross-platform generalization is a major challenge for multimodal models",
        "support_type": "contradicting",
        "confidence": 0.83,
        "section": "Experiments",
        "year": 2023,
        "author": "Park et al.",
        "topics": ["cross-platform", "generalization", "benchmark", "domain shift"],
        "venue": "WWW 2023"
    },
    {
        "source": "arXiv:2402.02222",
        "title": "Efficient Multimodal Architectures: A Survey",
        "content": "Survey of efficient multimodal methods: late fusion, early fusion, cross-attention, and parameter-efficient adapters. Best trade-off: cross-attention with LoRA adapters (3x parameter reduction, <2% accuracy drop). Late fusion is most robust to modality dropout.",
        "claim": "Cross-attention with adapters offers best efficiency-accuracy tradeoff",
        "support_type": "supporting",
        "confidence": 0.75,
        "section": "Survey",
        "year": 2024,
        "author": "Kim et al.",
        "topics": ["efficient multimodal", "LoRA", "adapters", "cross-attention", "survey"],
        "venue": "arXiv 2024"
    },
    {
        "source": "arXiv:2311.03333",
        "title": "Measuring Modality Correlation in Multimodal Datasets",
        "content": "We propose metrics for quantifying image-text alignment in multimodal datasets. High correlation (>0.7) on curated datasets vs low correlation (0.15-0.25) on wild social media data. Most multimodal papers evaluate on high-correlation datasets, overestimating real-world gains.",
        "claim": "Real-world social media has low image-text correlation",
        "support_type": "contradicting",
        "confidence": 0.89,
        "section": "Analysis",
        "year": 2023,
        "author": "Rodriguez et al.",
        "topics": ["modality correlation", "dataset bias", "social media", "evaluation"],
        "venue": "EMNLP 2023"
    },
    {
        "source": "arXiv:2404.07777",
        "title": "Continual Learning for Evolving Misinformation",
        "content": "New misinformation types emerge weekly. We evaluate continual learning methods on streaming misinformation data. Experience replay with multimodal buffers maintains 85% accuracy on new types vs 62% for fine-tuning. Multimodal buffers are critical for preserving visual concepts.",
        "claim": "Continual learning with multimodal buffers handles emerging misinformation",
        "support_type": "supporting",
        "confidence": 0.77,
        "section": "Experiments",
        "year": 2024,
        "author": "Wang et al.",
        "topics": ["continual learning", "streaming", "misinformation", "replay buffer"],
        "venue": "ACL 2024"
    },
    {
        "source": "arXiv:2306.05555",
        "title": "Unimodal Baselines Are Stronger Than You Think",
        "content": "We re-evaluate 15 multimodal misinformation papers with strong unimodal baselines. In 9/15 cases, text-only BERT-large matches multimodal performance. Multimodal gains primarily come from: (1) OCR text in images, (2) dataset bias, (3) weak unimodal baselines.",
        "claim": "Many reported multimodal gains are artifacts of weak baselines",
        "support_type": "contradicting",
        "confidence": 0.92,
        "section": "Re-evaluation",
        "year": 2023,
        "author": "Thompson et al.",
        "topics": ["unimodal baselines", "reproducibility", "multimodal", "evaluation"],
        "venue": "ACL 2023"
    },
    {
        "source": "arXiv:2405.08888",
        "title": "Robust Multimodal Training with Modality Dropout",
        "content": "We propose modality dropout during training to improve robustness to missing or corrupted modalities. At test time, model gracefully degrades to unimodal performance. Improves worst-case accuracy by 14% under modality corruption with only 1% clean accuracy cost.",
        "claim": "Modality dropout training improves robustness to missing modalities",
        "support_type": "supporting",
        "confidence": 0.81,
        "section": "Method",
        "year": 2024,
        "author": "Zhang et al.",
        "topics": ["modality dropout", "robust training", "missing modality", "graceful degradation"],
        "venue": "ICLR 2024"
    }
]


def ingest_evidence():
    """Ingest evidence corpus into Qdrant."""
    print("Initializing Qdrant RAG Engine...")
    
    # Use environment variables or defaults
    qdrant_url = os.environ.get("QDRANT_URL", "http://localhost:6333")
    qdrant_api_key = os.environ.get("QDRANT_API_KEY")
    collection_name = os.environ.get("QDRANT_COLLECTION", "argus_evidence")
    
    # Use a model that works reliably
    embedding_model = "all-MiniLM-L6-v2"
    
    engine = QdrantRAGEngine(
        qdrant_url=qdrant_url,
        qdrant_api_key=qdrant_api_key,
        embedding_model=embedding_model,
        collection_name=collection_name
    )
    
    print(f"Storing {len(EVIDENCE_CORPUS)} evidence items...")
    ids = engine.store_evidence(EVIDENCE_CORPUS)
    
    if ids:
        print(f"✓ Successfully stored {len(ids)} evidence items in Qdrant")
    else:
        print("✗ Failed to store evidence (Qdrant may not be running)")
        print("  Start Qdrant with: docker run -p 6333:6333 qdrant/qdrant")
        return False
    
    # Verify by searching
    print("\nVerifying with test searches...")
    test_queries = [
        "multimodal misinformation detection",
        "modality correlation",
        "distribution shift multimodal",
        "efficient transformer fake news"
    ]
    
    for query in test_queries:
        results = engine.search(query, top_k=3)
        print(f"  '{query}': {len(results)} results")
        for r in results[:2]:
            print(f"    - {r['payload'].get('title', 'Unknown')[:60]} (score: {r['score']:.3f})")
    
    # Test claim retrieval
    print("\nTesting claim retrieval...")
    group = engine.retrieve_for_claim("Multimodal models improve misinformation detection")
    print(f"  Supporting: {len(group.supporting)}, Contradicting: {len(group.contradicting)}, Neutral: {len(group.neutral)}")
    print(f"  Overall assessment: {group.overall_assessment}")
    
    return True


if __name__ == "__main__":
    success = ingest_evidence()
    sys.exit(0 if success else 1)