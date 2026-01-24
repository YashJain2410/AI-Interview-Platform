import tempfile
import edge_tts
import asyncio
from pathlib import Path

class EdgeTTS:
    def __init__(self, voice: str | None = None):
        self.voice = voice or "en-US-GuyNeural"

    async def synthesize(self, text: str) -> bytes:
        """
        Converts text to speech using Edge TTS.
        Returns row audio bytes (mp3).
        """

        communicate = edge_tts.Communicate(
            text=text,
            voice=self.voice
        )

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            output_path = Path(f.name)

        await communicate.save(output_path)

        audio_bytes = output_path.read_bytes()
        output_path.unlink(missing_ok=True)

        return audio_bytes