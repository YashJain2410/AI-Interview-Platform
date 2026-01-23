from pathlib import Path

PROMPT_DIR = Path(__file__).parent


def load_prompt(name: str) -> str:
    path = PROMPT_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Prompt not found: {name}")
    return path.read_text()
