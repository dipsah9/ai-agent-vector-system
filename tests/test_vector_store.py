import pytest
from src.core.vector_store import VectorStore

def test_insert_and_search():
    # Test the vector database
    store = VectorStore("postgresql://agent_user:agent_password@localhost:5432/agent_memory")
    
    # Insert test data
    test_embeddings = [
        [0.1, 0.2, 0.3, ...],  # Your test vectors
    ]
    
    store.insert(
        document_id="test_doc",
        chunks=["This is a test document"],
        embeddings=test_embeddings,
        metadata=[{"category": "test"}]
    )
    
    # Search
    results = store.search(
        query_embedding=[0.1, 0.2, 0.3, ...],
        top_k=1
    )
    
    assert len(results) > 0
    assert results[0]['similarity'] > 0.9