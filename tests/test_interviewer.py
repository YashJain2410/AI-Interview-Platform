import asyncio
from backend.ai.interviewer import AIInterview

async def main():
    interviewer = AIInterview()

    print("\n---Initial Question---")
    q1 = await interviewer.ask_question(stage="technical")
    print(q1)

    print("\n---Follow-up---")
    q2, evaluation = await interviewer.ask_followup(
        answer="I have worked with Random Forest and Decision Trees.",
        stage="technical",
        previous_question=q1
    )
    print("AI: ", q2)
    print("Evaluation: ", evaluation)

asyncio.run(main())