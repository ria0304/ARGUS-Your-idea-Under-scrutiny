"""RAG Engine - Retrieve, rerank, and group evidence."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    """A single evidence item with provenance."""
    id: str = Field(description="Unique evidence identifier")
    source: str = Field(description="Source title/paper name")
    title: str = Field(description="Section or subsection title")
    content: str = Field(description="The evidence passage")
    page: Optional[int] = Field(default=None, description="Page number")
    section: str = Field(default="", description="Document section")
    year: Optional[int] = Field(default=None, description="Publication year")
    author: Optional[str] = Field(default=None, description="Author")
    claim: str = Field(description="The claim this evidence supports/contradicts")
    support_type: str = Field(
        description="supporting, contradicting, or neutral",
        default="neutral"
    )
    confidence: float = Field(
        description="Evidence confidence: 0-1",
        ge=0.0,
        le=1.0
    )


class EvidenceGroup(BaseModel):
    """A group of evidence items related to the same claim."""
    claim_id: str = Field(description="ID of the claim this group addresses")
    supporting: List[EvidenceItem] = Field(default_factory=list)
    contradicting: List[EvidenceItem] = Field(default_factory=list)
    neutral: List[EvidenceItem] = Field(default_factory=list)
    overall_assessment: str = Field(
        default="unknown",
        description="Net assessment: supports, contradicts, or mixed"
    )


class RAGEngine:
    """Core RAG pipeline for evidence retrieval and grouping."""
    
    def __init__(self, 
                 vector_db=None, 
                 reranker=None,
                 keyword_search=None):
        self.vector_db = vector_db
        self.reranker = reranker
        self.keyword_search = keyword_search
    
    def retrieve(self, query: str, top_k: int = 50) -> List[EvidenceItem]:
        """Retrieve evidence for a query using vector + keyword search + reranking."""
        # If no vector DB, return empty results
        if self.vector_db is None:
            return []
        
        # Step 1: Vector search
        vector_results = self.vector_db.search(query, top_k=top_k * 2)
        
        # Step 2: Keyword search (if available)
        keyword_results = []
        if self.keyword_search:
            keyword_results = self.keyword_search.search(query, top_k=top_k)
        
        # Step 3: Combine and deduplicate
        combined = self._deduplicate(vector_results, keyword_results)
        
        # Step 4: Rerank
        reranked = self.reranker.rerank(query, combined, top_k=top_k)
        
        # Step 5: Convert to EvidenceItem objects
        evidence_items = [self._to_evidence_item(r) for r in reranked]
        
        return evidence_items
    
    def _deduplicate(self, vector_results, keyword_results) -> List[Any]:
        """Remove duplicate results from vector and keyword searches."""
        # TODO: Implement deduplication
        return vector_results + keyword_results
    
    def _to_evidence_item(self, result: Any) -> EvidenceItem:
        """Convert a search result to an EvidenceItem."""
        # TODO: Implement proper conversion
        return EvidenceItem(
            id=result.get("id", ""),
            source=result.get("source", ""),
            title=result.get("title", ""),
            content=result.get("content", ""),
            page=result.get("page"),
            section=result.get("section", ""),
            year=result.get("year"),
            author=result.get("author"),
            claim=result.get("claim", ""),
            support_type=result.get("support_type", "neutral"),
            confidence=result.get("confidence", 0.5)
        )
    
    def group_by_claim(self, evidence_items: List[EvidenceItem]) -> Dict[str, EvidenceGroup]:
        """Group evidence items by the claim they address."""
        groups = {}
        for item in evidence_items:
            claim_id = item.claim
            if claim_id not in groups:
                groups[claim_id] = EvidenceGroup(claim_id=claim_id)
            
            if item.support_type == "supporting":
                groups[claim_id].supporting.append(item)
            elif item.support_type == "contradicting":
                groups[claim_id].contradicting.append(item)
            else:
                groups[claim_id].neutral.append(item)
        
        return groups
    
    def retrieve_for_claim(self, claim: str, top_k: int = 30) -> EvidenceGroup:
        """Retrieve and group evidence for a specific claim."""
        items = self.retrieve(claim, top_k=top_k)
        groups = self.group_by_claim(items)
        
        # Return the group for the main claim, or the most relevant one
        if claim in groups:
            return groups[claim]
        elif groups:
            # Return the first group found
            return list(groups.values())[0]
        else:
            return EvidenceGroup(claim_id="unknown", overall_assessment="unknown")