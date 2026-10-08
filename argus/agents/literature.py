"""Literature Agent - Find relevant literature and construct research landscape."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from argus.llm import call_nemotron_structured
from argus.rag.engine import RAGEngine


class PaperMetadata(BaseModel):
    """Metadata for a research paper."""
    title: str
    authors: List[str]
    year: int
    venue: str
    abstract: str
    citations: int = 0
    topics: List[str] = Field(default_factory=list)


class RelatedWork(BaseModel):
    """Represents related work found by the literature agent."""
    paper: PaperMetadata
    relevance_score: float = 0.0
    relationship: str


class LiteratureLandscape(BaseModel):
    """Complete research landscape constructed by the agent."""
    papers: List[PaperMetadata]
    related_work: List[RelatedWork]
    research_gaps: List[str]
    covered_topics: List[str]


SEARCH_QUERY_SCHEMA = {
    "type": "object",
    "properties": {
        "search_queries": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Optimized search queries for literature retrieval"
        },
        "key_concepts": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Key technical concepts to search for"
        }
    },
    "required": ["search_queries", "key_concepts"]
}

CLASSIFICATION_SCHEMA = {
    "type": "object",
    "properties": {
        "papers": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "authors": {"type": "array", "items": {"type": "string"}},
                    "year": {"type": "integer"},
                    "venue": {"type": "string"},
                    "abstract": {"type": "string"},
                    "topics": {"type": "array", "items": {"type": "string"}},
                    "relevance": {"type": "string", "enum": ["baseline", "extension", "counterpoint", "parallel", "unrelated"]},
                    "relevance_score": {"type": "number", "minimum": 0, "maximum": 1}
                },
                "required": ["title", "authors", "year", "venue", "abstract", "topics", "relevance", "relevance_score"]
            }
        }
    },
    "required": ["papers"]
}

GAP_SCHEMA = {
    "type": "object",
    "properties": {
        "gaps": {"type": "array", "items": {"type": "string"}},
        "covered_topics": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["gaps", "covered_topics"]
}


class LiteratureAgent:
    """Responsibilities: find relevant literature, construct research landscape, identify related work, classify papers."""
    
    def __init__(self, rag_engine: Optional[RAGEngine] = None):
        self.rag_engine = rag_engine or RAGEngine()
        
        self.system_prompt_search = """You are ARGUS's Literature Agent. Generate optimized search queries for academic literature retrieval.

Given a research idea, produce:
1. 5-8 specific search queries for academic databases (arXiv, Semantic Scholar, Google Scholar)
2. Key technical concepts that define the research space

Queries should be specific, use domain terminology, and cover different angles (methods, applications, datasets, theory)."""
        
        self.system_prompt_classify = """You are ARGUS's Literature Agent. Classify papers relative to a research query.

For each paper, determine:
- RELEVANCE: baseline (directly addresses problem), extension (builds on it), counterpoint (contradicts/challenges), parallel (related but different angle), unrelated
- RELEVANCE_SCORE: 0-1 confidence in classification
- TOPICS: Key technical topics from the paper"""

        self.system_prompt_gaps = """You are ARGUS's Literature Agent. Identify research gaps from a set of papers.

Given classified papers, identify:
1. GAPS: Specific unexplored areas, missing connections, unanswered questions
2. COVERED_TOPICS: Topics well-covered by existing work

Focus on actionable gaps - what specific research is missing?"""

    def search(self, query: str, top_k: int = 20) -> List[PaperMetadata]:
        """Search for papers matching the query using RAG engine."""
        # Use query directly for search (LLM-enhanced queries can be added later)
        queries = [query]
        
        # Retrieve from RAG for each query
        all_papers = []
        for q in queries:
            try:
                results = self.rag_engine.search(q, top_k=top_k)
                for r in results:
                    payload = r.get("payload", {})
                    paper = PaperMetadata(
                        title=payload.get("title", "Unknown"),
                        authors=payload.get("authors", ["Unknown"]),
                        year=payload.get("year", 2024),
                        venue=payload.get("venue", "Unknown"),
                        abstract=payload.get("abstract", payload.get("content", "")),
                        topics=payload.get("topics", [])
                    )
                    all_papers.append(paper)
            except Exception:
                continue
        
        # Deduplicate by title
        seen = set()
        unique_papers = []
        for p in all_papers:
            if p.title not in seen:
                seen.add(p.title)
                unique_papers.append(p)
        
        return unique_papers[:top_k]

    def build_landscape(self, query: str) -> LiteratureLandscape:
        """Build a complete research landscape around a query."""
        papers = self.search(query)
        
        if not papers:
            return self._mock_landscape(query)
        
        # Classify papers
        classified = self._classify_papers(papers, query)
        
        # Identify gaps
        gaps_result = self._identify_gaps(classified)
        
        related_work = [
            RelatedWork(
                paper=p,
                relevance_score=c["relevance_score"],
                relationship=c["relevance"]
            )
            for p, c in zip(papers, classified)
        ]
        
        return LiteratureLandscape(
            papers=papers,
            related_work=related_work,
            research_gaps=gaps_result["gaps"],
            covered_topics=gaps_result["covered_topics"]
        )
    
    def _classify_papers(self, papers: List[PaperMetadata], query: str) -> List[Dict[str, Any]]:
        """Classify papers using Nemotron."""
        paper_summaries = "\n\n".join([
            f"Title: {p.title}\nAuthors: {', '.join(p.authors)}\nYear: {p.year}\nVenue: {p.venue}\nAbstract: {p.abstract[:500]}"
            for p in papers
        ])
        
        messages = [
            {"role": "system", "content": self.system_prompt_classify},
            {"role": "user", "content": f"Research query: {query}\n\nPapers to classify:\n{paper_summaries}"}
        ]
        
        try:
            result = call_nemotron_structured(messages, CLASSIFICATION_SCHEMA, temperature=0.1)
            return result.get("papers", [])
        except Exception:
            # Fallback classification
            return [
                {"relevance": "baseline", "relevance_score": 0.5, "topics": p.topics}
                for p in papers
            ]
    
    def _identify_gaps(self, classified: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify research gaps from classified papers."""
        paper_summary = "\n".join([
            f"- {c.get('title', 'Unknown')}: {c.get('relevance', 'unknown')} (topics: {', '.join(c.get('topics', []))})"
            for c in classified
        ])
        
        messages = [
            {"role": "system", "content": self.system_prompt_gaps},
            {"role": "user", "content": f"Classified papers:\n{paper_summary}"}
        ]
        
        try:
            result = call_nemotron_structured(messages, GAP_SCHEMA, temperature=0.2)
            return result
        except Exception:
            return {"gaps": ["Insufficient literature to identify gaps"], "covered_topics": []}
    
    def _mock_landscape(self, query: str) -> LiteratureLandscape:
        """Return mock landscape when no papers found."""
        return LiteratureLandscape(
            papers=[],
            related_work=[],
            research_gaps=[
                "No existing literature found in knowledge base",
                "Consider expanding search to web sources (Tavily)"
            ],
            covered_topics=[]
        )
    
    def classify_paper(self, paper: PaperMetadata, query_topics: List[str]) -> Dict[str, Any]:
        """Classify a single paper's relationship to the research query."""
        # Delegate to batch classification
        classified = self._classify_papers([paper], " ".join(query_topics))
        return classified[0] if classified else {"topics": [], "relationship": "unknown", "relevance": 0.0}