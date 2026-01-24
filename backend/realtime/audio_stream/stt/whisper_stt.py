import whisper
import tempfile
import asyncio
import os

class WhisperSTT:
    def __init__(self, model_name="base"):
        self.model = whisper.load_model(model_name)

    async def transcribe(self, audio_bytes: bytes) -> str:

        tmp_path = None

        try:
            with tempfile.NamedTemporaryFile(
                suffix=".wav",
                delete=False
            ) as f:
                f.write(audio_bytes)
                tmp_path = f.name

            result = await asyncio.to_thread(
                self.model.transcribe,
                tmp_path
            )
            return result["text"]
        
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)

        # with tempfile.NamedTemporaryFile(suffix=".wav") as f:
        #     f.write(audio_bytes)
        #     f.flush()

        #     result = await asyncio.to_thread(
        #         self.model.transcribe, f.name
        #     )
        #     return result["text"]