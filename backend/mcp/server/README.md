# Context providers

| Module | Responsibility |
|---|---|
| `base.py` | Abstract `get_context(**kwargs)` interface |
| `interview_server.py` | Stage and interview rules |
| `rag_server.py` | Resume/job passages for the latest answer |
| `evaluation_server.py` | Optional question/answer evaluation |

These are local Python objects. See [context design](../../../docs/mcp_design.md) for merge behavior and protocol limitations.
