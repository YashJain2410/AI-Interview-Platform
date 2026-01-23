import asyncio
from typing import List
from .base import LLMResponse, BaseLLM
from .evaluator import LLMResponseEvaluator

class LLMAggregator:
    def __init__(self, llms: list[BaseLLM]):
        self.llms = llms
        self.evaluator = LLMResponseEvaluator()

    async def generate(self, prompt: str) -> LLMResponse:
        tasks = [llm.generate(prompt) for llm in self.llms]
        responses: List[LLMResponse] = await asyncio.gather(*tasks)

        # FOR TESTING ->
        # print("RAW RESPONSES:")
        # for r in responses:
        #     print(r)

        valid_responses: List[LLMResponse] = [r for r in responses if r.error is None and r.text]

        if not valid_responses:
            raise RuntimeError("All LLMs failed to generate a response")
        
        scored: List[tuple[LLMResponse, float]] = []
        for response in valid_responses:
            score = await self.evaluator.score(prompt, response.text)
            scored.append((response, score))
        
        best_response = max(
            scored,
            key=lambda x: (x[1], -x[0].latency)
        )[0]

        return best_response