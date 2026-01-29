from backend.ai.llm_router.router import LLMRouter
from backend.ai.prompts.loader import load_prompt
from backend.ai.llm_router.base import LLMResponse
from backend.ai.rag.retriever import RAGRetriever
from backend.ai.rag.context_builder import build_interview_context

from backend.mcp.host.host import MCPHost
from backend.mcp.server.interview_server import InterviewContextServer
from backend.mcp.server.rag_server import RAGContextServer

class AIInterview:
    def __init__(self):
        self.llm_router = LLMRouter()
        
        # MCP Host orchestrate all context providers
        self.mcp_host = MCPHost(
            servers=[
                InterviewContextServer(),
                RAGContextServer()
            ]
        )

    async def ask_question(self, stage: str) -> str:
        """
        Initial interview question (stage-based, no candidate answer yet)
        """

        context = await self.mcp_host.collect_context(stage = stage)

        prompt = load_prompt("interviewer.txt").format(
            stage = context["interview_stage"],
            context = "No prior context available."
        )

        response: LLMResponse = await self.llm_router.generate(prompt)
        return response.text
    
    async def ask_followup(self, answer: str, stage: str = "technical") -> str:
        """
        Follow-up question using RAG (resume + Job description + last answer)
        """

        context = await self.mcp_host.collect_context(
            stage = stage,
            answer = answer,
            question = None
        )

        prompt = load_prompt("followup.txt").format(
            stage = context["interview_stage"],
            context = context["rag_context"],
            answer = answer
        )

        response: LLMResponse = await self.llm_router.generate(prompt)
        return response.text