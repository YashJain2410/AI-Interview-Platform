from pathlib import Path
from backend.ai.rag.ingest import RAGIngestor
from backend.ai.rag.retriever import RAGRetriever

ingestor = RAGIngestor()
ingestor.ingest_file(Path(r"C:\Users\HP\DATAA\YASH\Projects\Interview_Agent\data\resumes\resume.txt"), tag="resume")
ingestor.ingest_file(Path(r"C:\Users\HP\DATAA\YASH\Projects\Interview_Agent\data\job_descriptions\jd.txt"), tag="jd")

retriever = RAGRetriever(tag="resume")

query = "Has the candidate worked with RAG and FAISS?"
results = retriever.retrieve(query, k=3)

for r in results:
    print("-------------------")
    print(r)

retriever = RAGRetriever(tag="jd")

query = "What backend framework is required for this role ?"
results = retriever.retrieve(query)
print(results)