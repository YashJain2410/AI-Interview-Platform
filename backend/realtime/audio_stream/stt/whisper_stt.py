import whisper
import asyncio

class WhisperSTT:
    def __init__(self, model_name="base.en"):
        # Use English-specific model for better accuracy
        self.model = whisper.load_model(model_name)
    
    async def transcribe(self, wav_path: str) -> str:
        result = await asyncio.to_thread(
            self.model.transcribe,
            wav_path,
            fp16=False,
            language='en',
            temperature=0.0,
            best_of=5,
            beam_size=5,
            condition_on_previous_text=False,
            initial_prompt="You are in an interview. The user is speaking clearly."
        )
        return result.get("text", "").strip()
    

# import whisper
# import tempfile
# import asyncio
# import os
# import numpy as np
# import soundfile as sf

# class WhisperSTT:
#     def __init__(self, model_name="base", sample_rate = 16000):
#         self.model = whisper.load_model(model_name)
#         self.sample_rate = sample_rate

#     async def transcribe(self, audio_bytes: bytes) -> str:
#         """audio_bytes: raw PCM(int16, mono)"""

#         samples = np.frombuffer(audio_bytes, dtype=np.int16)
#         tmp_path = None

#         try:
#             with tempfile.NamedTemporaryFile(
#                 suffix=".wav",
#                 delete=False
#             ) as f:
#                 sf.write(
#                     f.name,
#                     samples,
#                     self.sample_rate,
#                     subtype="PCM_16"
#                 )
#                 tmp_path = f.name

#             result = await asyncio.to_thread(
#                 self.model.transcribe,
#                 tmp_path
#             )
#             return result.get("text", "")
        
#         finally:
#             if tmp_path and os.path.exists(tmp_path):
#                 os.remove(tmp_path)