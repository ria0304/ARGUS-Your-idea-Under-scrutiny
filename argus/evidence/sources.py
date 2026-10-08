"""Evidence Source Management - Handle document sources, citations, and provenance."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class Source(BaseModel):
    """A source of evidence - can be a paper, website, document, etc."""
    id: str = Field(description="Unique source identifier")
    title: str = Field(description="Source title")
    author: Optional[str] = Field(default=None, description="Author or organization")
    year: Optional[int] = Field(default=None, description="Publication year")
    url: Optional[str] = Field(default=None, description="URL if online")
    document_path: Optional[str] = Field(
        default=None, description="Local or stored path to document"
    )
    source_type: str = Field(
        description="Type: pdf, webpage, user_upload, tavily_search, etc.",
        default="unknown"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (pages, sections, etc.)"
    )


class EvidenceRecord(BaseModel):
    """A record of evidence retrieved and its properties."""
    id: str = Field(description="Unique evidence record identifier")
    source_id: str = Field(description="ID of the source this evidence came from")
    content: str = Field(description="The evidence passage text")
    claim: str = Field(description="Which claim this evidence supports/contradicts")
    support_type: str = Field(
        description="supporting, contradicting, or neutral",
        default="neutral"
    )
    relevance: float = Field(
        description="Relevance score: 0-1",
        ge=0.0,
        le=1.0
    )
    extraction_confidence: float = Field(
        description="How confident we are in the extraction: 0-1",
        ge=0.0,
        le=1.0
    )
    page: Optional[int] = Field(default=None, description="Page number in source")
    section: str = Field(default="", description="Section or subsection")


class Citation(BaseModel):
    """A citation pointing to evidence."""
    evidence_id: str = Field(description="ID of the evidence being cited")
    claim_id: str = Field(description="ID of the claim being supported")
    source_name: str = Field(description="Human-readable source name")
    passage: str = Field(description="The specific passage quoted")
    page: Optional[int] = Field(default=None, description="Page number")
    strength: float = Field(
        description="Citation strength: 0-1",
        ge=0.0,
        le=1.0
    )


class EvidenceManager:
    """Manage evidence sources, citations, and provenance tracking."""
    
    def __init__(self):
        self.sources: Dict[str, Source] = {}
        self.evidence: Dict[str, EvidenceRecord] = {}
    
    def add_source(self, source: Source) -> str:
        """Add a new evidence source."""
        self.sources[source.id] = source
        return source.id
    
    def add_evidence(self, evidence: EvidenceRecord) -> str:
        """Add a new evidence record."""
        self.evidence[evidence.id] = evidence
        return evidence.id
    
    def get_evidence_for_claim(self, claim_id: str) -> List[EvidenceRecord]:
        """Get all evidence records for a specific claim."""
        return [
            ev for ev in self.evidence.values()
            if ev.claim == claim_id
        ]
    
    def get_supporting_evidence(self, claim_id: str) -> List[EvidenceRecord]:
        """Get supporting evidence for a claim."""
        all_ev = self.get_evidence_for_claim(claim_id)
        return [ev for ev in all_ev if ev.support_type == "supporting"]
    
    def get_contradicting_evidence(self, claim_id: str) -> List[EvidenceRecord]:
        """Get contradicting evidence for a claim."""
        all_ev = self.get_evidence_for_claim(claim_id)
        return [ev for ev in all_ev if ev.support_type == "contradicting"]
    
    def generate_citations(self, claim_id: str) -> List[Citation]:
        """Generate citations for a claim's evidence."""
        evidence = self.get_evidence_for_claim(claim_id)
        citations = []
        
        for ev in evidence:
            source = self.sources.get(ev.source_id, Source(id="unknown"))
            citations.append(Citation(
                evidence_id=ev.id,
                claim_id=claim_id,
                source_name=source.title,
                passage=ev.content,
                page=ev.page,
                strength=ev.relevance * ev.extraction_confidence
            ))
        
        return citations