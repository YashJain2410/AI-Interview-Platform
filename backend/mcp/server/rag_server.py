from backend.mcp.server.base import MCPServer
from backend.ai.rag.retriever import RAGRetriever
from backend.ai.rag.context_builder import build_interview_context

class RAGContextServer(MCPServer):
    def __init__(self):
        self.resume_rag = RAGRetriever("resume")
        self.jd_rag = RAGRetriever("jd")

    async def get_context(self, answer: str | None = None, **kwargs) -> dict:

        if not answer:
            return {
                "rag_context": ""
            }

        resume_chunks = self.resume_rag.retrieve(answer)
        jd_chunks = self.jd_rag.retrieve(answer)

        return {
            "rag_context": build_interview_context(
                resume_chunks=resume_chunks,
                jd_chunks=jd_chunks,
                last_answer=answer
            )
        }