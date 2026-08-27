import re
import numpy as np
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class KnowledgeIndexer:
    """
    RAG Pipeline & Document Search Engine.
    Handles text cleaning, chunking, metadata attachment, TF-IDF vector indexing,
    and relevant evidence retrieval during section generation.
    """
    
    def __init__(self, chunk_size: int = 400, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.chunks: List[Dict[str, Any]] = []
        self.vectorizer = None
        self.tfidf_matrix = None

    def index_documents(self, documents: List[Dict[str, Any]]) -> int:
        self.chunks = []
        for doc in documents:
            filename = doc.get("filename", "Unknown")
            doc_type = doc.get("type", "Reference Paper")
            raw_text = doc.get("raw_text", "")
            
            # Clean and split into paragraphs/chunks
            cleaned_text = re.sub(r'\s+', ' ', raw_text)
            words = cleaned_text.split()
            
            for i in range(0, len(words), self.chunk_size - self.overlap):
                chunk_words = words[i:i + self.chunk_size]
                if len(chunk_words) < 20:
                    continue
                chunk_text = " ".join(chunk_words)
                self.chunks.append({
                    "chunk_id": len(self.chunks),
                    "filename": filename,
                    "doc_type": doc_type,
                    "text": chunk_text
                })
                
        if self.chunks:
            corpus = [c["text"] for c in self.chunks]
            self.vectorizer = TfidfVectorizer(stop_words='english')
            self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
            
        return len(self.chunks)

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if not self.chunks or self.vectorizer is None or self.tfidf_matrix is None:
            return []
            
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            if scores[idx] > 0.01:
                chunk = self.chunks[idx].copy()
                chunk["score"] = float(scores[idx])
                results.append(chunk)
        return results
