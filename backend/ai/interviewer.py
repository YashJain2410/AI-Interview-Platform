from backend.ai.llm_router.router import LLMRouter
from backend.ai.prompts.loader import load_prompt
from backend.ai.llm_router.base import LLMResponse
from backend.ai.rag.retriever import RAGRetriever
from backend.ai.rag.context_builder import build_interview_context

class AIInterview:
    def __init__(self):
        self.llm_router = LLMRouter()
        self.resume_rag = RAGRetriever(tag="resume")
        self.jd_rag = RAGRetriever(tag="jd")

    async def ask_question(self, stage: str) -> str:
        """
        Initial interview question (stage-based, no candidate answer yet)
        """
        prompt = load_prompt("interviewer.txt").format(stage = stage, context = "No prior context available.")
        response: LLMResponse = await self.llm_router.generate(prompt)
        return response.text
    
    async def ask_followup(self, answer: str, stage: str = "technical") -> str:
        """
        Follow-up question using RAG (resume + Job description + last answer)
        """

        resume_chunks = self.resume_rag.retrieve(answer)
        jd_chunks = self.jd_rag.retrieve(answer)

        context = build_interview_context(
            resume_chunks = resume_chunks,
            jd_chunks=jd_chunks,
            last_answer=answer
        )

        prompt = load_prompt("interviewer.txt").format(
            stage = stage,
            context = context
        )

        response: LLMResponse = await self.llm_router.generate(prompt)
        return response.text