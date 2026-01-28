import pickle
from sentence_transformers import SentenceTransformer

class RAGRetriever:
    def __init__(self, tag: str):
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

        with open(f"data/embeddings/{tag}.pkl", "rb") as f:
            self.index, self.chunks = pickle.load(f)

    def retrieve(self, query: str, k: int = 3) -> list[str]:        # Number of relevant chunks to fetch
        q_emb = self.embedder.encode([query])
        _, indices = self.index.search(q_emb, k)

        return [self.chunks[i] for i in indices[0]]