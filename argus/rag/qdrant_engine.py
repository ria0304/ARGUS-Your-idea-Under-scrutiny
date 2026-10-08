"""RAG Engine with Qdrant Vector Store Integration."""

from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field
import numpy as np

from argus.rag.engine import EvidenceGroup, EvidenceItem

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import (
        VectorParams, PointStruct, Filter, FieldCondition, MatchValue,
        Distance
    )
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


# Module-level singleton for embedding model to avoid reloading
_embedding_model_cache = {}

def get_embedding_model(model_name: str = "all-MiniLM-L6-v2"):
    """Get or create embedding model singleton."""
    if model_name not in _embedding_model_cache:
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                _embedding_model_cache[model_name] = SentenceTransformer(model_name)
            except Exception as e:
                print(f"Failed to load {model_name}: {e}")
                if model_name != "all-MiniLM-L6-v2":
                    return get_embedding_model("all-MiniLM-L6-v2")
                _embedding_model_cache[model_name] = None
        else:
            _embedding_model_cache[model_name] = None
    return _embedding_model_cache[model_name]


class QdrantRAGEngine:
    """RAG engine using Qdrant vector database with BGE embeddings."""
    
    def __init__(
        self, 
        qdrant_url: str = "localhost:6333", 
        qdrant_api_key: Optional[str] = None,
        embedding_model: str = "all-MiniLM-L6-v2",
        collection_name: str = "argus_evidence"
    ):
        self.collection_name = collection_name
        self.embedding_model_name = embedding_model
        
        # Initialize Qdrant client
        if QDRANT_AVAILABLE:
            if qdrant_api_key:
                self.client = QdrantClient(
                    url=qdrant_url, 
                    api_key=qdrant_api_key
                )
            else:
                self.client = QdrantClient(url=qdrant_url, check_compatibility=False)
        else:
            self.client = None
        
        # Get embedding model from cache
        self.embedding_model = get_embedding_model(embedding_model)
        
        # Initialize collection if it doesn't exist
        self._init_collection()
    
    def _init_collection(self):
        """Initialize Qdrant collection if it doesn't exist."""
        if not self.client:
            return
        
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_model.get_sentence_embedding_dimension() 
                        if self.embedding_model else 768,
                        distance=Distance.COSINE
                    ),
                    on_disk_payload=True
                )
                print(f"Created Qdrant collection: {self.collection_name}")
        except Exception as e:
            print(f"Qdrant collection init: {e}")
    
    def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for a text string."""
        if self.embedding_model:
            embedding = self.embedding_model.encode(text)
            return embedding
        else:
            # Dummy embedding if no model
            return np.random.rand(768).astype(np.float32)
    
    def store_evidence(
        self, 
        evidence_items: List[Dict[str, Any]],
        source_ids: List[str] = None
    ) -> List[str]:
        """Store evidence items in Qdrant vector database."""
        if not self.client or not self.embedding_model:
            print("Qdrant or embedding model not available, skipping storage")
            return []
        
        point_ids = []
        vectors = []
        payloads = []
        
        for i, evidence in enumerate(evidence_items):
            # Generate embedding from content
            content = evidence.get("content", "")
            embedding = self.embed_text(content)
            
            # Build payload with metadata
            payload = {
                "source": evidence.get("source", ""),
                "title": evidence.get("title", ""),
                "claim": evidence.get("claim", ""),
                "support_type": evidence.get("support_type", "neutral"),
                "confidence": evidence.get("confidence", 0.5),
                "section": evidence.get("section", ""),
                "year": evidence.get("year"),
                "author": evidence.get("author"),
                "page": evidence.get("page"),
            }
            
            if source_ids and i < len(source_ids):
                payload["source_id"] = source_ids[i]
            
            vectors.append(embedding)
            payloads.append(payload)
        
        # Create points
        points = []
        for i, (vector, payload) in enumerate(zip(vectors, payloads)):
            point = PointStruct(
                id=i,
                vector=vector.tolist(),
                payload=payload
            )
            points.append(point)
            point_ids.append(point.id)
        
        # Upload to Qdrant
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            print(f"Stored {len(point_ids)} evidence items in Qdrant")
            return [str(pid) for pid in point_ids]
        except Exception as e:
            print(f"Qdrant upsert error: {e}")
            return []
    
    def search(
        self, 
        query: str, 
        top_k: int = 50,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for evidence similar to the query."""
        if not self.client or not self.embedding_model:
            return []
        
        # Embed the query
        query_embedding = self.embed_text(query).tolist()
        
        # Search Qdrant
        try:
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                query_filter=self._build_filter(filter_metadata) if filter_metadata else None
            )
            
            # Convert to result dicts
            results = []
            for result in search_result:
                results.append({
                    "id": result.id,
                    "score": result.score,
                    "payload": result.payload,
                    "content": payload_to_content(result.payload) if result.payload else ""
                })
            
            return results
        except Exception as e:
            print(f"Qdrant search error: {e}")
            return []
    
    def _build_filter(self, metadata: Dict[str, Any]) -> Any:
        """Build Qdrant filter from metadata dict."""
        if not metadata:
            return None
        
        conditions = []
        for key, value in metadata.items():
            if isinstance(value, str):
                conditions.append(
                    FieldCondition(key=key, match=MatchValue(value=value))
                )
        
        if conditions:
            return Filter(must=conditions)
        return None
    
    def retrieve_for_claim(self, claim: str, top_k: int = 30) -> EvidenceGroup:
        """Retrieve and group evidence for a specific claim."""
        # Search for evidence related to the claim
        results = self.search(query=claim, top_k=top_k)
        
        # Group by claim/support type
        group = EvidenceGroup(claim_id=claim)
        
        for result in results:
            payload = result.get("payload", {})
            content = result.get("content", "")
            
            # Determine support type from claim match or metadata
            support_type = payload.get("support_type", "neutral")
            if not support_type:
                # Simple heuristic: check if claim appears in content
                if claim.lower() in content.lower():
                    support_type = "supporting"
                else:
                    support_type = "neutral"
            
            evidence_item = EvidenceItem(
                id=str(payload.get("id", "")),
                source=payload.get("source", "unknown"),
                title=payload.get("title", ""),
                content=content,
                page=payload.get("page"),
                section=payload.get("section", ""),
                year=payload.get("year"),
                author=payload.get("author"),
                claim=claim,
                support_type=support_type,
                confidence=payload.get("confidence", 0.5)
            )
            
            if evidence_item.support_type == "supporting":
                group.supporting.append(evidence_item)
            elif evidence_item.support_type == "contradicting":
                group.contradicting.append(evidence_item)
            else:
                group.neutral.append(evidence_item)
        
        # Assess overall
        group.overall_assessment = self._assess_group(group)
        
        return group
    
    def _assess_group(self, group: EvidenceGroup) -> str:
        """Assess the overall evidence group."""
        supporting = len(group.supporting)
        contradicting = len(group.contradicting)
        neutral = len(group.neutral)
        
        total = supporting + contradicting + neutral
        if total == 0:
            return "unknown"
        
        ratio = (supporting - contradicting) / total if total > 0 else 0
        
        if ratio > 0.6:
            return "supports"
        elif ratio < -0.6:
            return "contradicts"
        else:
            return "mixed"
    
    def store_document(self, document_id: str, text: str, metadata: Dict[str, Any] = None):
        """Store a full document in Qdrant by chunking and embedding."""
        if not self.client or not self.embedding_model:
            return
        
        # Simple chunking - split by sentences or characters
        chunk_size = 512
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(text[start:end])
            start += chunk_size - 100  # 100 char overlap
        
        # Store each chunk as a point
        points = []
        for i, chunk in enumerate(chunks):
            embedding = self.embed_text(chunk)
            payload = {
                "document_id": document_id,
                "chunk_index": i,
                "chunk_text": chunk[:200] + "..." if len(chunk) > 200 else chunk,
                "metadata": metadata or {}
            }
            
            point = PointStruct(
                id=f"{document_id}_{i}",
                vector=embedding.tolist(),
                payload=payload
            )
            points.append(point)
        
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            print(f"Stored document {document_id} with {len(points)} chunks")
        except Exception as e:
            print(f"Qdrant document store error: {e}")


def payload_to_content(payload: Dict[str, Any]) -> str:
    """Extract content from Qdrant payload."""
    # Try common fields
    for key in ["content", "chunk_text", "text", "passage"]:
        if key in payload:
            return str(payload[key])
    # Build from available fields
    parts = []
    for k in ["title", "section", "claim"]:
        if k in payload and payload[k]:
            parts.append(f"{k}: {payload[k]}")
    return " | ".join(parts) if parts else str(payload)


# Example usage
if __name__ == "__main__":
    engine = QdrantRAGEngine()
    
    # Store some evidence
    evidence = [
        {
            "source": "Paper A",
            "title": "Section 4",
            "content": "Multimodal models improve misinformation detection by 8.4%",
            "claim": "Multimodal improvement",
            "support_type": "supporting",
            "confidence": 0.85
        },
        {
            "source": "Paper B", 
            "title": "Section 5",
            "content": "Performance drops under distribution shift",
            "claim": "Distribution shift vulnerability",
            "support_type": "contradicting",
            "confidence": 0.72
        }
    ]
    
    engine.store_evidence(evidence)
    
    # Search for evidence
    results = engine.search("multimodal misinformation detection", top_k=5)
    print(f"Found {len(results)} results")
    
    # Retrieve for claim
    group = engine.retrieve_for_claim("Combining modalities improves detection")
    print(f"Evidence group: {group.overall_assessment}")
    print(f"Supporting: {len(group.supporting)}, Contradicting: {len(group.contradicting)}")