def build_interview_context(resume_chunks: list[str], jd_chunks: list[str], last_answer: str) -> str:
    context = f"""
Candidate Resume Highlights:
{chr(10).join(resume_chunks)}

Job Description Requirements:
{chr(10).join(jd_chunks)}

Candidate's Last Answer:
{last_answer}
"""
    return context.strip()