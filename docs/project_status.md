# Current capabilities

Source-reviewed on **October 6, 2026**. This describes the checked-in implementation, not a deployed service certification.

| Area | Present | Limit |
|---|---|---|
| Interface | Dashboard, setup, live room, reports, history, settings | Analytics and reports are fixed examples; settings/history are not backed by storage. |
| Text interview | Session start, first question, answer-based follow-ups | Needs providers and indexes; no automatic stage progression or final report. |
| Retrieval | Text chunking, embeddings, FAISS search | Local shared indexes; file picker does not upload documents. |
| Model routing | Concurrent Gemini/Hugging Face generation | Judge parsing defect; no validated timeout/retry policy. |
| Evaluation | Four-dimension rubric and JSON schema | Internal results only; score bounds and totals are not enforced. |
| Voice | Mic capture, SDP endpoint, speech components | Tuple passed to TTS; invalid audio timestamp; incomplete lifecycle cleanup. |
| Audio socket | Route exists | Calls a missing method; frontend does not use it. |
| Context providers | Rules, RAG, evaluation behind a Python host | No standard MCP protocol implementation. |
| Storage | In-memory session/evaluation objects | No account database, durable reports, or candidate isolation. |
| Delivery | Frontend build and Vercel rewrite config | Empty Compose and incomplete Python manifests; no CI or verified backend deployment. |

## Review boundaries

- Frontend build verifies TypeScript compilation and bundling; it does not prove browser behavior or interview completion.
- Most `tests/` files are manual provider/audio experiments, some with stale interfaces or local paths.
- No published benchmarks establish latency, accuracy, concurrent capacity, or score reliability.
- Authentication, quotas, data deletion, and operational monitoring are not implemented.

For a demo, label sample reports and fallback responses clearly. For public operation, use the [deployment gates](deployment.md#before-public-backend-access). These limits are part of the project’s documented scope.
