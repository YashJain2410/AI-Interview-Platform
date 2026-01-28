import asyncio
from backend.ai.evaluation.evaluator import InterviewEvaluator

async def main():
    evaluator = InterviewEvaluator()

    result = await evaluator.evaluate_answer(
        question="Explain how random forest works",
        answer="Random Forest is am ensemble of decision trees where..."
    )

    print(result)

asyncio.run(main())