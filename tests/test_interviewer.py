import asyncio
from backend.ai.interviewer import AIInterview

async def main():
    interviewer = AIInterview()

    print("\n---Initial Question---")
    q1 = await interviewer.ask_question(stage="technical")
    print(q1)

    print("\n---Follow-up---")
    q2 = await interviewer.ask_followup(
        "I have worked with Random Forest and Decision Trees."
    )
    print(q2)

asyncio.run(main())