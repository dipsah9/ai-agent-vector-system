import logging
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime, func, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pgvector.sqlalchemy import Vector
from datetime import datetime
import json

logger = logging.getLogger(__name__)
Base = declarative_base()

class DocumentEmbedding(Base):
    __tablename__ = 'document_embeddings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String(255), nullable=False, index=True)
    chunk_text = Column(Text, nullable=False)
    embedding = Column(Vector(768))
    meta_data = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

class VectorStore:
    def __init__(self, database_url: str):
        self.engine = create_engine(
            database_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600
        )
        self.Session = sessionmaker(bind=self.engine)
        self._create_tables()
        self._create_indexes()
    
    def _create_tables(self):
        Base.metadata.create_all(self.engine)
        logger.info("Vector database tables created")
    
    def _create_indexes(self):
        with self.engine.connect() as conn:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_embedding_hnsw 
                ON document_embeddings 
                USING hnsw (embedding vector_cosine_ops)
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_document_id 
                ON document_embeddings (document_id)
            """))
            conn.commit()
        logger.info("Vector database indexes created")
    
    def insert(self, document_id: str, chunks: List[str], 
               embeddings: List[List[float]], metadata: List[Dict[str, Any]] = None):
        if metadata is None:
            metadata = [{}] * len(chunks)
        
        session = self.Session()
        try:
            for chunk, embedding, meta in zip(chunks, embeddings, metadata):
                doc = DocumentEmbedding(
                    document_id=document_id,
                    chunk_text=chunk,
                    embedding=embedding,
                    meta_data=json.dumps(meta)
                )
                session.add(doc)
            
            session.commit()
            logger.info(f"Inserted {len(chunks)} embeddings for document {document_id}")
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to insert embeddings: {e}")
            raise
        finally:
            session.close()
    
    def search(self, query_embedding: List[float], 
               top_k: int = 5, 
               filter_metadata: Optional[Dict[str, Any]] = None,
               similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        
        # Build the query with named parameters
        sql = """
            SELECT 
                chunk_text,
                1 - (embedding <=> :emb) as similarity,
                meta_data
            FROM document_embeddings
        """
        
        # Parameters as a dictionary
        params = {'emb': query_embedding}
        
        if filter_metadata:
            sql += " WHERE meta_data::jsonb @> :filter"
            params['filter'] = json.dumps(filter_metadata)
        
        sql += f" ORDER BY embedding <=> :emb LIMIT {top_k}"
        
        session = self.Session()
        try:
            # Execute with dictionary parameters
            result = session.execute(text(sql), params)
            results = []
            for row in result:
                if row.similarity >= similarity_threshold:
                    results.append({
                        'text': row.chunk_text,
                        'similarity': float(row.similarity),
                        'metadata': json.loads(row.meta_data) if row.meta_data else {}
                    })
            
            logger.info(f"Found {len(results)} relevant chunks")
            return results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
        finally:
            session.close()
    
    def delete_document(self, document_id: str):
        session = self.Session()
        try:
            session.query(DocumentEmbedding).filter(
                DocumentEmbedding.document_id == document_id
            ).delete()
            session.commit()
            logger.info(f"Deleted embeddings for document {document_id}")
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to delete document: {e}")
            raise
        finally:
            session.close()
    
    def get_statistics(self) -> Dict[str, Any]:
        session = self.Session()
        try:
            total_docs = session.query(func.count(
                func.distinct(DocumentEmbedding.document_id)
            )).scalar()
            
            total_chunks = session.query(func.count(
                DocumentEmbedding.id
            )).scalar()
            
            return {
                'total_documents': total_docs or 0,
                'total_chunks': total_chunks or 0,
                'avg_chunks_per_document': round(total_chunks / total_docs, 2) if total_docs else 0
            }
        finally:
            session.close()