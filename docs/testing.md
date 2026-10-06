# Validation

A successful build is useful evidence, but it does not establish that an interview works end to end.

## Available checks

| Check | Command or action | What it proves |
|---|---|---|
| Frontend build | `cd frontend/web && npm run build` | TypeScript compilation and production bundling |
| Built UI review | `npm run preview` in `frontend/web` | Manual inspection of the compiled interface |
| Backend health | `curl http://localhost:8000/health` | App startup and route response; not provider readiness |
| Text socket experiment | `python -m tests.test_ws_test` from root | Manual session/question/follow-up exchange if backend and providers work |

The text experiment can send provider requests and incur charges. It prints results; it does not assert correctness.

## Existing test directory

Most `tests/test_*.py` files are executable experiments with provider calls, model loads, files, or a running server. Some execute at import; some use stale APIs or absolute Windows paths. Empty placeholder test files have been removed. The remaining tests are not a deterministic regression suite.

Do not treat full pytest discovery as a reliable offline check. There is no CI workflow, coverage claim, deterministic regression suite, or load-test result.

## Manual acceptance review

1. Check desktop and mobile routes, keyboard focus, and direct route navigation.
2. Start a text session and confirm its UUID and first question; submit an answer and verify a follow-up.
3. Check provider failures and disconnects; distinguish fallback demo responses from backend results.
4. Inspect retrieved passages using synthetic documents; confirm no other candidate data enters prompts.
5. Verify voice capture, playback, and cleanup across networks only after known voice defects are fixed.
6. Treat reports/history as sample UI until real session results are generated and saved.

For any verification report, record the commit, environment, command, result, and limits. Publish performance claims only with measured results and a repeatable method.
