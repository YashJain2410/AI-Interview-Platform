import tempfile
import edge_tts
import asyncio
import numpy as np
import soundfile as sf
import librosa
from pathlib import Path
import subprocess

class EdgeTTS:
    def __init__(self, voice: str | None = None):
        self.voice = voice or "en-US-GuyNeural"

    async def synthesize(self, text: str) -> np.ndarray:
        """
        Converts text to speech using Edge TTS.
        Returns 48kHz int16 mono PCM audio as numpy array.
        """
        
        communicate = edge_tts.Communicate(
            text=text,
            voice=self.voice
        )

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            mp3_path = Path(f.name)
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            wav_path = Path(f.name)

        try:
            # Save as MP3
            await communicate.save(mp3_path)
            
            # Convert MP3 to WAV using ffmpeg
            result = subprocess.run([
                'ffmpeg',
                '-i', str(mp3_path),
                '-ar', '48000',  # 48kHz
                '-ac', '1',      # Mono
                '-y',            # Overwrite
                str(wav_path)
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"[EdgeTTS] ffmpeg error: {result.stderr}")
                return np.array([], dtype=np.int16)
            
            # Read WAV file
            samples, sample_rate = sf.read(str(wav_path), dtype='float32')
            
            print(f"[EdgeTTS] Loaded: {sample_rate}Hz, {len(samples)} samples")
            
            # Should already be 48kHz from ffmpeg, but double-check
            if sample_rate != 48000:
                samples = librosa.resample(
                    samples,
                    orig_sr=sample_rate,
                    target_sr=48000
                )
                print(f"[EdgeTTS] Resampled to 48kHz")
            
            # Normalize
            max_val = np.max(np.abs(samples))
            if max_val > 0:
                samples = samples / max_val * 0.95
            
            # Convert to int16
            audio_int16 = (samples * 32767).astype(np.int16)
            
            duration = len(audio_int16) / 48000
            print(f"[EdgeTTS] Final: 48kHz, {len(audio_int16)} samples, {duration:.2f}s")
            
            return audio_int16
            
        finally:
            mp3_path.unlink(missing_ok=True)
            wav_path.unlink(missing_ok=True)