from backend.mcp.server.base import MCPServer

class InterviewContextServer(MCPServer):
    async def get_context(self, stage: str = "general", **kwargs) -> dict:
        """
        Interview rules + stage context
        """
        return {
            "interview_stage": stage,
            "rules": [
                "Ask one question at a time",
                "Do not give hints unless asked",
                "Adjust difficulty based on candidate response"
            ]
        }