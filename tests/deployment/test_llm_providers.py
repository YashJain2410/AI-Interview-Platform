"""Provider wire contracts and fail-closed routing; no external requests or credentials."""
import asyncio
import json
import os
import unittest
from unittest.mock import patch

import httpx
from fastapi.testclient import TestClient

from backend.ai.llm_router.settings import LLMConfigurationError, LLMSettings, PROVIDERS
from backend.ai.llm_router.service import LLMProviderError, LLMService
from backend.ai.llm_router.router import LLMRouter
from backend.api.interviews import Report
from backend.api.main import app
from backend.api import interviews
from backend.ai.llm_router.service import llm_service


REPORT = {
    'scores': dict.fromkeys(['technical_correctness', 'depth_of_understanding', 'communication', 'confidence'], 75),
    'summary': 'Useful practice.', 'strengths': ['Clear answer'], 'weaknesses': ['Needs depth'],
    'improvement_suggestions': ['Explain tradeoffs'],
}


def env_for(provider='google'):
    spec = PROVIDERS[provider]
    return {'LLM_PROVIDER': provider, 'LLM_MODEL': 'gemini-3.8-flash' if provider == 'google' else 'explicit-model:groq' if provider == 'huggingface' else 'explicit-model',
            spec.api_key_env: 'test-secret', 'OPENROUTER_PROVIDER': 'upstream',
            **({'LLM_BASE_URL': 'https://custom.example/v1'} if provider == 'openai_compatible' else {})}


def success(provider, text='Next question?'):
    if provider == 'google':
        return {'candidates': [{'finishReason': 'STOP', 'content': {'parts': [
            {'text': 'private reasoning', 'thought': True}, {'text': text}]}}]}
    if provider == 'openai':
        return {'status': 'completed', 'output': [{'type': 'message', 'content': [{'type': 'output_text', 'text': text}]}]}
    if provider == 'anthropic':
        return {'stop_reason': 'end_turn', 'content': [{'type': 'text', 'text': text}]}
    return {'choices': [{'finish_reason': 'stop', 'message': {'content': text}}]}


class SettingsTest(unittest.TestCase):
    def test_google_defaults_and_legacy_override(self):
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-secret'}, clear=True):
            settings = LLMSettings.from_env()
            self.assertEqual((settings.provider, settings.model), ('google', 'gemini-3.8-flash'))
            self.assertNotIn('test-secret', repr(settings))
            with patch.dict(os.environ, {'GEMINI_MODEL': 'gemini-exact'}):
                self.assertEqual(LLMSettings.from_env().model, 'gemini-exact')
                with patch.dict(os.environ, {'LLM_MODEL': 'generic-exact'}):
                    self.assertEqual(LLMSettings.from_env().model, 'generic-exact')

    def test_invalid_configuration_never_uses_other_credentials(self):
        cases = [
            {'LLM_PROVIDER': 'typo', 'GEMINI_API_KEY': 'present'},
            {'LLM_PROVIDER': 'openai', 'OPENAI_API_KEY': 'present'},
            {'LLM_PROVIDER': 'google', 'HF_API_TOKEN': 'present'},
            {**env_for(), 'LLM_TIMEOUT_SECONDS': 'nan'},
            {**env_for(), 'LLM_QUESTION_MAX_TOKENS': '0'},
            {**env_for(), 'LLM_BASE_URL': 'http://external.example/v1'},
            {**env_for(), 'LLM_BASE_URL': 'https://user:secret@example.com'},
            {**env_for(), 'LLM_BASE_URL': 'https://example.com:invalid'},
            {**env_for(), 'LLM_BASE_URL': 'https://[broken'},
            {**env_for(), 'GEMINI_THINKING_LEVEL': 'minimal'},
            {**env_for('openrouter'), 'OPENROUTER_PROVIDER': ''},
            {**env_for('openrouter'), 'LLM_MODEL': 'openrouter/auto'},
            {**env_for('openrouter'), 'LLM_MODEL': 'vendor/model:free'},
            {**env_for('huggingface'), 'LLM_MODEL': 'vendor/model'},
            {**env_for('huggingface'), 'LLM_MODEL': 'vendor/model:fastest'},
        ]
        for env in cases:
            with self.subTest(env=env), patch.dict(os.environ, env, clear=True):
                with self.assertRaises(LLMConfigurationError):
                    LLMSettings.from_env()

    def test_pooled_client_lifecycle(self):
        with TestClient(app):
            self.assertIsNotNone(llm_service.client)
            self.assertFalse(llm_service.client.is_closed)
            pooled = llm_service.client
        self.assertTrue(pooled.is_closed)
        self.assertIsNone(llm_service.client)

    def test_selected_provider_failure_reaches_websocket(self):
        interviews.starts.clear()
        async def fail(*args):
            raise LLMProviderError('google/gemini-3.8-flash: HTTP 429. No fallback was attempted.')
        with patch.object(llm_service, 'generate', fail), TestClient(app) as client:
            with client.websocket_connect('/ws/interview') as ws:
                ws.send_json({'candidate_name': 'Test'})
                self.assertEqual(ws.receive_json()['event'], 'session_started')
                error = ws.receive_json()
                self.assertEqual(error['event'], 'error')
                self.assertIn('google/gemini-3.8-flash', error['content'])
                self.assertIn('No fallback', error['content'])
        self.assertFalse(interviews.active_sessions)

    def test_health_uses_selected_provider(self):
        with patch.dict(os.environ, {'LLM_PROVIDER': 'openai', 'GEMINI_API_KEY': 'present'}, clear=True):
            result = TestClient(app).get('/health').json()
            self.assertFalse(result['ai_configured'])
            self.assertFalse(result['llm_fallback_enabled'])
        with patch.dict(os.environ, env_for(), clear=True):
            result = TestClient(app).get('/health').json()
            self.assertEqual(result['llm_model'], 'gemini-3.8-flash')
            self.assertTrue(result['ai_configured'])


class ProviderTest(unittest.IsolatedAsyncioTestCase):
    async def invoke(self, provider='google', payload=None, status=200, schema=None, env=None):
        requests = []
        def handle(request):
            requests.append(request)
            return httpx.Response(status, json=payload if payload is not None else success(provider))
        with patch.dict(os.environ, env or env_for(provider), clear=True):
            settings = LLMSettings.from_env()
        async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as client:
            service = LLMService(settings, client)
            result = await service.generate('Interview prompt', schema)
        return result, requests

    async def test_all_provider_protocols_and_model_selection(self):
        for provider, spec in PROVIDERS.items():
            with self.subTest(provider=provider):
                result, requests = await self.invoke(provider)
                self.assertEqual(len(requests), 1)
                self.assertEqual(result.provider, provider)
                self.assertEqual(result.text, 'Next question?')
                body = json.loads(requests[0].content)
                if provider == 'google':
                    self.assertIn('/gemini-3.8-flash:generateContent', requests[0].url.path)
                    self.assertEqual(requests[0].headers['x-goog-api-key'], 'test-secret')
                    self.assertNotIn('temperature', body['generationConfig'])
                    self.assertEqual(body['generationConfig']['thinkingConfig']['thinkingLevel'], 'low')
                else:
                    self.assertEqual(body['model'], 'explicit-model:groq' if provider == 'huggingface' else 'explicit-model')
                if provider == 'openrouter':
                    self.assertEqual(body['provider']['only'], ['upstream'])
                    self.assertFalse(body['provider']['allow_fallbacks'])

    async def test_structured_output_and_report_budget(self):
        for provider in PROVIDERS:
            with self.subTest(provider=provider):
                result, requests = await self.invoke(provider, success(provider, json.dumps(REPORT)),
                                                     schema=Report.model_json_schema())
                self.assertEqual(Report.model_validate_json(result.text).scores.communication, 75)
                body = json.loads(requests[0].content)
                if provider == 'google':
                    config = body['generationConfig']
                    self.assertEqual(config['maxOutputTokens'], 4096)
                    self.assertEqual(config['thinkingConfig']['thinkingLevel'], 'medium')
                    self.assertIn('responseJsonSchema', config)
                elif provider == 'openai':
                    self.assertFalse(body['store'])
                    self.assertEqual(body['text']['format']['schema']['additionalProperties'], False)
                    self.assertEqual(body['max_output_tokens'], 4096)
                elif provider == 'anthropic':
                    schema = body['output_config']['format']['schema']
                    self.assertNotIn('minimum', schema['$defs']['Scores']['properties']['communication'])
                else:
                    self.assertEqual(body['response_format'], {'type': 'json_object'})

    async def test_errors_never_retry_or_fallback_or_expose_secrets(self):
        for status in (302, 400, 401, 403, 404, 429, 500):
            requests = []
            def handle(request):
                requests.append(request)
                return httpx.Response(status, json={'error': 'test-secret candidate-private-data'},
                                      headers={'location': 'https://other-provider.example'})
            with self.subTest(status=status), patch.dict(os.environ, {**env_for(), 'HF_API_TOKEN': 'available'}, clear=True):
                async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as client:
                    with self.assertRaises(LLMProviderError) as error:
                        await LLMService(client=client).generate('private prompt')
                self.assertEqual(len(requests), 1)
                self.assertIn('No fallback', str(error.exception))
                self.assertNotIn('test-secret', str(error.exception))
                self.assertNotIn('candidate-private-data', str(error.exception))

    async def test_empty_blocked_truncated_and_malformed_responses_fail_closed(self):
        cases = [('google', {}), ('google', {'candidates': []}), ('google', success('google', '')),
                 ('google', {'candidates': [{'finishReason': 'MAX_TOKENS'}]}),
                 ('openai', {'status': 'incomplete', 'output': []}),
                 ('anthropic', {'stop_reason': 'max_tokens', 'content': []}),
                 ('groq', {'choices': [{'finish_reason': 'length', 'message': {'content': 'partial'}}]})]
        for provider, payload in cases:
            with self.subTest(provider=provider, payload=payload), self.assertRaises(LLMProviderError):
                await self.invoke(provider, payload)
        with self.assertRaises(LLMProviderError):
            await self.invoke(payload=success('google', 'not JSON'), schema=Report.model_json_schema())

    async def test_timeout_is_bounded_without_retry(self):
        requests = []
        async def handle(request):
            requests.append(request)
            await asyncio.sleep(2)
            return httpx.Response(200, json=success('google'))
        with patch.dict(os.environ, {**env_for(), 'LLM_TIMEOUT_SECONDS': '1'}, clear=True):
            async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as client:
                with self.assertRaises(LLMProviderError):
                    await LLMService(client=client).generate('prompt')
        self.assertEqual(len(requests), 1)

    async def test_legacy_router_uses_same_service(self):
        with patch('backend.ai.llm_router.router.llm_service.generate') as generate:
            generate.return_value = 'selected response'
            self.assertEqual(await LLMRouter().generate('prompt'), 'selected response')
            generate.assert_awaited_once_with('prompt')
