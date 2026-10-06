# Security and data handling

This is a development prototype. There is no designated security-supported release or public-service certification.

## Reporting a vulnerability

Use GitHub private vulnerability reporting if it is enabled on the repository. Otherwise request a private contact channel from the maintainer without posting exploit details, credentials, or candidate data. No monitored security email or response deadline is declared here.

Privately include the affected component/commit, reproduction steps, impact, and a suggested fix if available. Use synthetic examples.

## Current data boundaries

| Data | Current handling |
|---|---|
| Provider keys | Read from backend environment variables |
| Resume/job passages | Local text and pickle indexes; passages may be sent to LLM providers |
| Spoken answers | Local Whisper transcription; text enters follow-up prompts |
| AI replies | Sent to Edge TTS for speech generation |
| Audio and context | Debug files/prints can retain candidate content |
| Sessions/evaluations | Process memory; no durable account isolation or deletion API |

Authentication, authorization, quotas, origin checks for sockets, retention enforcement, and prompt-injection defenses are absent. HTTP CORS is currently permissive. Keep backend use restricted to development with synthetic data.

## Repository hygiene

- Keep backend credentials out of source control and all `VITE_*` values; browser variables are public.
- Load only trusted locally generated pickle indexes.
- `.gitignore` prevents new accidental additions; it does not remove tracked files or past commits.
- Review tracked files under `data/` before publication. Existing tracked resume/JD files remain tracked even with ignore rules.
- If a secret has been exposed, revoke/rotate it before addressing repository history.

See [deployment conditions](docs/deployment.md#before-public-backend-access) for operating requirements.
