import asyncio
from backend.ai.llm_router.huggingface_llm import HuggingFaceLLM

async def main():
    llm = HuggingFaceLLM()
    response = await llm.generate(
        "Ask a beginner level machine learning interview question"
    )
    print(response)

asyncio.run(main())