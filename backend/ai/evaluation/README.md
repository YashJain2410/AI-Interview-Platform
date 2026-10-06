# Answer evaluation

`evaluator.py` sends a question/answer pair and the rubric to the model router. `schemas.py` parses JSON scores, strengths, weaknesses, and suggestions.

The rubric requests four scores out of five: technical correctness, understanding, communication, and confidence. Bounds and total consistency are not enforced by the schema. Results are internal to the text flow; there is no final report generator or validated hiring assessment.

See [API](../../../docs/api.md) and [current capabilities](../../../docs/project_status.md).
