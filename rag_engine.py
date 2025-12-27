import faiss
from sentence_transformers import SentenceTransformer
import os

class BankingRAG:
    def __init__(self):
        print("⏳ Loading RAG System...")
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.index_path = "./data/banking_faiss.index"
        self.data_path = "./data/knowledge_base.txt"
        
        if not os.path.exists(self.index_path):
            raise FileNotFoundError("FAISS index not found. Run build_rag.py first.")
            
        self.index = faiss.read_index(self.index_path)
        
        # Load text chunks to map index -> text
        with open(self.data_path, "r") as f:
            self.chunks = [line.strip() for line in f.read().split('\n') if line.strip()]
            
    def search(self, query, top_k=1):
        query_vector = self.embedder.encode([query])
        distances, indices = self.index.search(query_vector, top_k)
        
        results = []
        for i in indices[0]:
            if i < len(self.chunks) and i >= 0:
                results.append(self.chunks[i])
        return results