import asyncio
from backend.ai.llm_router.gemini_llm import GeminiLLM

async def main():
    llm = GeminiLLM()
    response = await llm.generate(
        "Ask me a simple technical interview question about Python."
    )
    print(response)

asyncio.run(main())
