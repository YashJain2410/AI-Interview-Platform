from backend.realtime.audio_stream.stt.whisper_stt import WhisperSTT
from backend.realtime.audio_stream.tts.edge_tts import EdgeTTS
from backend.ai.interviewer import AIInterview

class AudioPipeline:
    """ 
    Handles:
    Audio input -> STT -> AI -> TTS -> Audio Output
    """

    def __init__(self):
        self.stt = WhisperSTT()
        self.tts = EdgeTTS()
        self.ai = AIInterview()

    async def process_audio_chunck(self, audio_bytes: bytes) -> bytes:
        text = await self.stt.transcribe(audio_bytes)
        ai_response = await self.ai.ask_followup(text)
        audio_out = await self.tts.synthesize(ai_response)

        return audio_out