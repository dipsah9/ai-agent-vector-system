-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create table for vector embeddings
CREATE TABLE IF NOT EXISTS document_embeddings (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR(255) NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding vector(768),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- HNSW index for fast similarity search
CREATE INDEX IF NOT EXISTS idx_embedding_hnsw 
ON document_embeddings 
USING hnsw (embedding vector_cosine_ops);

-- Index for document lookups
CREATE INDEX IF NOT EXISTS idx_document_id 
ON document_embeddings (document_id);

-- GIN index for filtering by metadata (e.g., by collection)
CREATE INDEX IF NOT EXISTS idx_document_embeddings_meta 
ON document_embeddings USING gin (metadata);

-- Auto-update trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Drop first so this is idempotent (safe to re-run)
DROP TRIGGER IF EXISTS update_document_embeddings_updated_at 
    ON document_embeddings;

CREATE TRIGGER update_document_embeddings_updated_at
    BEFORE UPDATE ON document_embeddings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();