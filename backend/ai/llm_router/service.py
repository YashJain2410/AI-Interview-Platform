"""One selected model, one bounded request, no retries or fallback providers."""
import asyncio
import copy
import json
import logging
import time
from urllib.parse import quote

import httpx

from .base import LLMResponse
from .settings import LLMSettings, PROVIDERS

log = logging.getLogger(__name__)


class LLMProviderError(RuntimeError):
    """Safe to expose: excludes upstream bodies, prompts, URLs, and credentials."""


def strict_schema(schema: dict) -> dict:
    """Close objects for APIs requiring strict JSON Schema."""
    result = copy.deepcopy(schema)

    def visit(node):
        if isinstance(node, dict):
            if node.get('type') == 'object':
                node['additionalProperties'] = False
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for value in node:
                visit(value)
    visit(result)
    return result


class LLMService:
    def __init__(self, settings: LLMSettings | None = None, client: httpx.AsyncClient | None = None):
        self.settings = settings
        self.client = client

    async def generate(self, prompt: str, schema: dict | None = None) -> LLMResponse:
        settings = self.settings or LLMSettings.from_env()
        started = time.perf_counter()
        try:
            # A total deadline also bounds response bodies that arrive in small chunks.
            async with asyncio.timeout(settings.timeout):
                if self.client is None:
                    async with httpx.AsyncClient(follow_redirects=False) as client:
                        text = await self._request(client, settings, prompt, schema)
                else:
                    text = await self._request(self.client, settings, prompt, schema)
        except LLMProviderError:
            raise
        except (httpx.HTTPError, TimeoutError):
            raise LLMProviderError(
                f'{settings.provider}/{settings.model}: request timed out or could not connect. No fallback was attempted.'
            ) from None
        return LLMResponse(provider=settings.provider, model=settings.model, text=text,
                           latency=time.perf_counter() - started)

    async def _request(self, client, settings, prompt, schema):
        protocol = PROVIDERS[settings.provider].protocol
        tokens = settings.report_tokens if schema else settings.question_tokens
        headers = {'Authorization': f'Bearer {settings.api_key}'}
        if protocol == 'google':
            path = f'/models/{quote(settings.model, safe="")}:generateContent'
            headers = {'x-goog-api-key': settings.api_key}
            config = {'maxOutputTokens': tokens}
            if settings.model.startswith('gemini-3'):
                config['thinkingConfig'] = {
                    'thinkingLevel': settings.report_thinking_level if schema else settings.thinking_level,
                    'includeThoughts': False,
                }
            elif settings.model.startswith('gemini-2.5-flash'):
                config['thinkingConfig'] = {'thinkingBudget': 0}
            if schema:
                config.update(responseMimeType='application/json', responseJsonSchema=schema)
            body = {'contents': [{'role': 'user', 'parts': [{'text': prompt}]}], 'generationConfig': config}
        elif protocol == 'responses':
            path = '/responses'
            body = {'model': settings.model, 'input': prompt, 'max_output_tokens': tokens, 'store': False}
            if schema:
                body['text'] = {'format': {'type': 'json_schema', 'name': 'interview_report',
                                           'strict': True, 'schema': strict_schema(schema)}}
        elif protocol == 'anthropic':
            path = '/messages'
            headers = {'x-api-key': settings.api_key, 'anthropic-version': '2023-06-01'}
            body = {'model': settings.model, 'messages': [{'role': 'user', 'content': prompt}], 'max_tokens': tokens}
            if schema:
                # Claude's constrained schema excludes numeric limits; local Report validation enforces them.
                output_schema = strict_schema(schema)
                def remove_bounds(node):
                    if isinstance(node, dict):
                        for key in ('minimum', 'maximum'):
                            node.pop(key, None)
                        for value in node.values():
                            remove_bounds(value)
                    elif isinstance(node, list):
                        for value in node:
                            remove_bounds(value)
                remove_bounds(output_schema)
                body['output_config'] = {'format': {'type': 'json_schema', 'schema': output_schema}}
        else:
            path = '/chat/completions'
            if schema:
                prompt += '\nReturn only a JSON object matching this schema:\n' + json.dumps(schema)
            body = {'model': settings.model, 'messages': [{'role': 'user', 'content': prompt}], 'max_tokens': tokens}
            if schema:
                body['response_format'] = {'type': 'json_object'}
            if settings.provider == 'openrouter':
                body['provider'] = {'only': [settings.openrouter_provider], 'allow_fallbacks': False,
                                    'require_parameters': True}
        response = await client.post(settings.base_url + path, headers=headers, json=body,
                                     timeout=settings.timeout, follow_redirects=False)
        label = f'{settings.provider}/{settings.model}'
        if not response.is_success:
            # Never log an upstream body: it can echo private candidate data or credentials.
            log.warning('LLM request failed provider=%s model=%s status=%s',
                        settings.provider, settings.model, response.status_code)
            advice = {401: 'Check the selected provider API key.', 403: 'Check model access and permissions.',
                      404: 'Check the exact model ID and endpoint.', 429: 'Check provider quota or rate limits.'}
            raise LLMProviderError(f'{label}: HTTP {response.status_code}. '
                                   f'{advice.get(response.status_code, "Provider request failed.")} No fallback was attempted.')
        try:
            data = response.json()
            if protocol == 'google':
                candidate = data['candidates'][0]
                if candidate.get('finishReason') != 'STOP':
                    raise ValueError('incomplete or blocked')
                text = ''.join(p.get('text', '') for p in candidate['content']['parts'] if not p.get('thought'))
            elif protocol == 'responses':
                if data.get('status') != 'completed':
                    raise ValueError('incomplete')
                blocks = [part for item in data['output'] if item.get('type') == 'message'
                          for part in item.get('content', [])]
                if any(part.get('type') == 'refusal' for part in blocks):
                    raise ValueError('refusal')
                text = ''.join(part.get('text', '') for part in blocks if part.get('type') == 'output_text')
            elif protocol == 'anthropic':
                if data.get('stop_reason') != 'end_turn':
                    raise ValueError('incomplete or refused')
                text = ''.join(part.get('text', '') for part in data['content'] if part.get('type') == 'text')
            else:
                choice = data['choices'][0]
                if choice.get('finish_reason') != 'stop' or choice['message'].get('refusal'):
                    raise ValueError('incomplete or refused')
                text = choice['message']['content']
            if not isinstance(text, str) or not text.strip():
                raise ValueError('empty')
            if schema:
                parsed = json.loads(text)
                if not isinstance(parsed, dict):
                    raise ValueError('expected JSON object')
            return text.strip()
        except (ValueError, KeyError, IndexError, TypeError, AttributeError):
            raise LLMProviderError(f'{label}: empty, blocked, incomplete, or invalid response. No fallback was attempted.') from None


llm_service = LLMService()
