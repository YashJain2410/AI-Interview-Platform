from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import faiss
import pickle

class RAGIngestor:
    def __init__(self):
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size = 500,
            chunk_overlap = 100
        )

    def ingest_file(self, file_path: Path, tag: str):
        text = file_path.read_text()
        chunks = self.splitter.split_text(text)

        embeddings = self.embedder.encode(chunks)

        index = faiss.IndexFlatL2(len(embeddings[0]))
        index.add(embeddings)

        with open(f"data/embeddings/{tag}.pkl", "wb") as f:
            pickle.dump((index, chunks), f)