# Provider and model configuration

The hosted API and legacy interview/evaluation pipelines share one HTTP model service.
Configure the root `.env` locally, or the backend service environment in production:

```dotenv
LLM_PROVIDER=google
LLM_MODEL=gemini-3.8-flash
GEMINI_API_KEY=<your-server-side-key>
```

Restart the backend after editing configuration. Process environment variables take precedence
over `.env`. Never place keys in frontend `VITE_*` variables. Selection is server-owned;
clients cannot override the provider, endpoint, or credentials through interview setup.

## Provider options

| `LLM_PROVIDER` | Credential | API |
|---|---|---|
| `google` (`gemini` alias) | `GEMINI_API_KEY` or `GOOGLE_API_KEY` | Gemini generateContent |
| `openai` | `OPENAI_API_KEY` | Responses, with storage disabled |
| `anthropic` | `ANTHROPIC_API_KEY` | Messages |
| `groq` | `GROQ_API_KEY` | Chat Completions |
| `mistral` | `MISTRAL_API_KEY` | Chat Completions |
| `deepseek` | `DEEPSEEK_API_KEY` | Chat Completions |
| `xai` | `XAI_API_KEY` | Chat Completions |
| `together` | `TOGETHER_API_KEY` | Chat Completions |
| `huggingface` (`hf` alias) | `HF_API_TOKEN` | Chat Completions; explicit `model:provider` required |
| `openrouter` | `OPENROUTER_API_KEY` | Chat Completions; one `OPENROUTER_PROVIDER` required |
| `openai_compatible` | `LLM_API_KEY` | Chat Completions at required `LLM_BASE_URL` |

To switch to OpenAI, set `LLM_PROVIDER=openai`, `LLM_MODEL=<exact-model-id>`, and
`OPENAI_API_KEY`. Anthropic uses `LLM_PROVIDER=anthropic`, an exact Claude model ID,
and `ANTHROPIC_API_KEY`. Other providers follow the same pattern. An API integration
does not guarantee that every model supports text chat or structured output. Select
a model that supports both; unsupported requests fail explicitly.

A nonempty `LLM_MODEL` takes precedence over the selected provider's model variable
(`GEMINI_MODEL`, `OPENAI_MODEL`, `ANTHROPIC_MODEL`, `GROQ_MODEL`, `MISTRAL_MODEL`,
`DEEPSEEK_MODEL`, `XAI_MODEL`, `TOGETHER_MODEL`, `HF_MODEL`, or `OPENROUTER_MODEL`).
Only Google has a default model (`gemini-3.8-flash`). All other providers require an
explicit model. Existing unrelated credentials never affect selection.

`LLM_BASE_URL` optionally overrides the selected adapter's API root, including its version
path, without a method suffix. It requires HTTPS, except for local HTTP endpoints.
Custom endpoints must implement the selected protocol. The application cannot control
routing performed inside a custom gateway or a provider-managed model alias; use fixed
model IDs and configure the gateway's routing policy when exact versions matter.

## Gemini 3.8 Flash tuning

Questions default to `GEMINI_THINKING_LEVEL=low` and `LLM_QUESTION_MAX_TOKENS=1024`.
Reports use `GEMINI_REPORT_THINKING_LEVEL=medium` and `LLM_REPORT_MAX_TOKENS=4096`.
These settings allocate more reasoning to feedback while keeping conversational turns
bounded. Both token limits include any provider-accounted reasoning tokens. Raise the
limits if the selected model returns incomplete output.

Gemini 3 models receive thinking-level controls without deprecated temperature/top-p/top-k
parameters. Gemini 2.5 Flash retains its zero-thinking-budget compatibility path. Other
Google model IDs receive no model-specific thinking override. These settings follow
[Google's Gemini 3.8 migration guidance](https://ai.google.dev/gemini-api/docs/generate-content/whats-new-gemini-3.8);
latency improvements have not been benchmarked in this project.

Reports use native JSON Schema for Google, [OpenAI](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses),
and [Anthropic](https://platform.claude.com/docs/en/build-with-claude/structured-outputs).
Other adapters request JSON-object mode and include the schema in the prompt. The hosted
API validates every completed report against its Pydantic schema, including score bounds.
Unsupported JSON modes fail without retrying a weaker request.

## Failure behavior

There is deliberately no fallback toggle: each operation makes one request to the selected
provider/model. Missing credentials, invalid configuration, authentication failures, quota
errors, unknown models, timeouts, redirects, refusals, truncation, and invalid output produce
an error. They never trigger a different model, provider, ranking judge, mock answer, or
unbounded retry. Errors identify the selected provider/model and HTTP status when available;
upstream response bodies and candidate prompts are excluded from application logs.

For [OpenRouter](https://openrouter.ai/docs/guides/routing/provider-selection), set one
`OPENROUTER_PROVIDER` slug. Requests use `only`, `allow_fallbacks=false`, and
`require_parameters=true`. Automatic model routing IDs and colon variants are rejected.
For [Hugging Face](https://huggingface.co/docs/inference-providers/index), use an exact
`LLM_MODEL=organization/model:provider` ID; automatic `fastest`, `cheapest`, `preferred`,
and `auto` routing is rejected.

`LLM_TIMEOUT_SECONDS` defaults to 60 (allowed: 1–300), bounding the entire outbound
request as well as network operations. Token limits allow 128–65536; a model may have a
lower limit and reject the request. FastAPI reuses one async HTTP connection pool and
closes it on shutdown. Legacy scripts create and close a client per call.

`GET /health` reports whether the selected configuration is valid, its provider/model
when valid, and `llm_fallback_enabled=false`. It does not make a billable request or verify
model availability, quota, or key validity. Provider failures are surfaced through the
existing WebSocket `error` event.

Run offline contracts with:

```bash
.venv/bin/python -m unittest discover -s tests/deployment -v
```

These tests use mocked HTTP transports. Live provider access and model quality require
separate verification with the selected account.
