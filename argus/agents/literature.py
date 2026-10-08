"""Literature Agent - Find relevant literature and construct research landscape."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class PaperMetadata(BaseModel):
    """Metadata for a research paper."""
    title: str
    authors: List[str]
    year: int
    venue: str  # conference/journal
    abstract: str
    citations: int = 0
    topics: List[str] = Field(default_factory=list)


class RelatedWork(BaseModel):
    """Represents related work found by the literature agent."""
    paper: PaperMetadata
    relevance_score: float = 0.0  # 0-1, how relevant to the query
    relationship: str  # e.g., "baseline", "extension", "counterpoint", "parallel"


class LiteratureLandscape(BaseModel):
    """Complete research landscape constructed by the agent."""
    papers: List[PaperMetadata]
    related_work: List[RelatedWork]
    research_gaps: List[str]
    covered_topics: List[str]


class LiteratureAgent:
    """Responsibilities: find relevant literature, construct research landscape, identify related work, classify papers."""
    
    def search(self, query: str, top_k: int = 20) -> List[PaperMetadata]:
        """Search for papers matching the query."""
        # TODO: Implement search via Qdrant + Tavily + academic sources
        return []
    
    def build_landscape(self, query: str) -> LiteratureLandscape:
        """Build a complete research landscape around a query."""
        papers = self.search(query)
        # TODO: Classify papers, identify relationships, find gaps
        return LiteratureLandscape(
            papers=papers,
            related_work=[],
            research_gaps=[],
            covered_topics=[]
        )
    
    def classify_paper(self, paper: PaperMetadata, query_topics: List[str]) -> Dict[str, Any]:
        """Classify a paper's relationship to the research query."""
        # TODO: Implement classification
        return {"topics": [], "relationship": "unknown", "relevance": 0.0}