import faiss
from sentence_transformers import SentenceTransformer
import os

def build_index():
    print("⏳ Loading Embedding Model...")
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    
    data_path = "./data/knowledge_base.txt"
    index_path = "./data/banking_faiss.index"

    if not os.path.exists(data_path):
        print("❌ Error: data/knowledge_base.txt not found!")
        return

    # Read Data
    with open(data_path, "r") as f:
        text = f.read()
    
    # Split into simple chunks
    chunks = [line.strip() for line in text.split('\n') if line.strip()]
    print(f"✅ Loaded {len(chunks)} policy documents.")

    # Create Vectors
    print("⏳ Creating Embeddings...")
    embeddings = embedder.encode(chunks)

    # Build FAISS Index
    d = embeddings.shape[1]
    index = faiss.IndexFlatL2(d)
    index.add(embeddings)

    # Save
    faiss.write_index(index, index_path)
    print(f"✅ Success! Index saved to {index_path}")

if __name__ == "__main__":
    build_index()