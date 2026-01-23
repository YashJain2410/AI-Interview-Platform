import os
from huggingface_hub import AsyncInferenceClient

class HuggingFaceLLM:
    def __init__(self):
            self.model_id = os.getenv("HF_MODEL", "meta-llama/Llama-3.1-8B-Instruct")
            self.client = AsyncInferenceClient(
            model=self.model_id,
            token=os.getenv("HF_API_TOKEN")
        )

    async def generate(self, prompt: str) -> str:
        response = await self.client.chat_completion(
            messages=[
                {"role": "system", "content": "You are a professional AI Interviewer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7
        )
        return response.choices[0].message.content