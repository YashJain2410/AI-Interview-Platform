"""Server-owned model selection. Credentials never determine routing."""
import math
import os
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[3] / '.env')


class LLMConfigurationError(RuntimeError):
    """Invalid operator configuration; no provider request has been made."""


@dataclass(frozen=True)
class Provider:
    api_key_env: str
    model_env: str
    base_url: str
    protocol: str = 'chat'


PROVIDERS = {
    'google': Provider('GEMINI_API_KEY', 'GEMINI_MODEL', 'https://generativelanguage.googleapis.com/v1beta', 'google'),
    'openai': Provider('OPENAI_API_KEY', 'OPENAI_MODEL', 'https://api.openai.com/v1', 'responses'),
    'anthropic': Provider('ANTHROPIC_API_KEY', 'ANTHROPIC_MODEL', 'https://api.anthropic.com/v1', 'anthropic'),
    'groq': Provider('GROQ_API_KEY', 'GROQ_MODEL', 'https://api.groq.com/openai/v1'),
    'mistral': Provider('MISTRAL_API_KEY', 'MISTRAL_MODEL', 'https://api.mistral.ai/v1'),
    'deepseek': Provider('DEEPSEEK_API_KEY', 'DEEPSEEK_MODEL', 'https://api.deepseek.com/v1'),
    'xai': Provider('XAI_API_KEY', 'XAI_MODEL', 'https://api.x.ai/v1'),
    'together': Provider('TOGETHER_API_KEY', 'TOGETHER_MODEL', 'https://api.together.ai/v1'),
    'huggingface': Provider('HF_API_TOKEN', 'HF_MODEL', 'https://router.huggingface.co/v1'),
    'openrouter': Provider('OPENROUTER_API_KEY', 'OPENROUTER_MODEL', 'https://openrouter.ai/api/v1'),
    'openai_compatible': Provider('LLM_API_KEY', 'LLM_MODEL', ''),
}


def _number(name: str, default: str, lower: float, upper: float, cast=float):
    try:
        value = cast(os.getenv(name, default))
    except ValueError:
        raise LLMConfigurationError(f'{name} must be a number.') from None
    if not math.isfinite(value) or not lower <= value <= upper:
        raise LLMConfigurationError(f'{name} must be between {lower:g} and {upper:g}.')
    return value


@dataclass(frozen=True)
class LLMSettings:
    provider: str
    model: str
    api_key: str = field(repr=False)
    base_url: str
    timeout: float = 60
    question_tokens: int = 1024
    report_tokens: int = 4096
    thinking_level: str = 'low'
    report_thinking_level: str = 'medium'
    openrouter_provider: str = ''

    @classmethod
    def from_env(cls):
        provider = os.getenv('LLM_PROVIDER', 'google').strip().lower()
        provider = {'gemini': 'google', 'hf': 'huggingface'}.get(provider, provider)
        if provider not in PROVIDERS:
            raise LLMConfigurationError('Unsupported LLM_PROVIDER. Choose: ' + ', '.join(PROVIDERS))
        spec = PROVIDERS[provider]
        # A blank generic override permits the provider-specific model variable.
        model = os.getenv('LLM_MODEL', '').strip() or os.getenv(spec.model_env, '').strip()
        if not model and provider == 'google':
            model = 'gemini-3.8-flash'
        if not model or any(c.isspace() for c in model) or any(c in model for c in '?#'):
            raise LLMConfigurationError(f'Set LLM_MODEL or {spec.model_env} to an explicit model ID.')
        if provider == 'openrouter' and (model in {'openrouter/auto', 'openrouter/free'} or ':' in model):
            raise LLMConfigurationError('OpenRouter requires a fixed model ID without routing variants.')
        if provider == 'huggingface':
            # HF's bare IDs select an upstream automatically; require an explicit suffix.
            parts = model.rsplit(':', 1)
            if (len(parts) != 2 or not all(parts) or ':' in parts[0]
                    or parts[1] in {'auto', 'fastest', 'cheapest', 'preferred'}):
                raise LLMConfigurationError('Hugging Face requires an explicit model:provider ID to prevent automatic routing.')
        key = os.getenv(spec.api_key_env, '').strip()
        if provider == 'google':
            key = key or os.getenv('GOOGLE_API_KEY', '').strip()
        if not key or key in {'your_key_here', 'your_token_here'}:
            raise LLMConfigurationError(f'{provider}: set {spec.api_key_env} on the server.')
        base_url = os.getenv('LLM_BASE_URL', '').strip() or spec.base_url
        try:
            parsed = urlsplit(base_url)
            parsed.port  # Validate malformed/out-of-range ports before opening a connection.
        except ValueError:
            raise LLMConfigurationError('LLM_BASE_URL is not a valid API root URL.') from None
        if (parsed.scheme not in {'https', 'http'} or not parsed.hostname or parsed.username
                or parsed.password or parsed.query or parsed.fragment):
            raise LLMConfigurationError('LLM_BASE_URL must be an HTTP(S) API root without credentials, query, or fragment.')
        if parsed.scheme != 'https' and parsed.hostname not in {'localhost', '127.0.0.1', '::1'}:
            raise LLMConfigurationError('LLM_BASE_URL requires HTTPS except for localhost.')
        thinking = os.getenv('GEMINI_THINKING_LEVEL', 'low').strip().lower()
        report_thinking = os.getenv('GEMINI_REPORT_THINKING_LEVEL', 'medium').strip().lower()
        if provider == 'google' and any(x not in {'low', 'medium', 'high'} for x in (thinking, report_thinking)):
            raise LLMConfigurationError('Gemini thinking levels must be low, medium, or high.')
        upstream = os.getenv('OPENROUTER_PROVIDER', '').strip()
        if provider == 'openrouter' and not upstream:
            raise LLMConfigurationError('Set OPENROUTER_PROVIDER to one upstream provider slug to prevent fallback.')
        return cls(provider, model, key, base_url.rstrip('/'),
                   _number('LLM_TIMEOUT_SECONDS', '60', 1, 300),
                   _number('LLM_QUESTION_MAX_TOKENS', '1024', 128, 65536, int),
                   _number('LLM_REPORT_MAX_TOKENS', '4096', 128, 65536, int),
                   thinking, report_thinking, upstream)
