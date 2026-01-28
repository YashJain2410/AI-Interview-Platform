import asyncio
import numpy as np
import soundfile as sf
import tempfile
import os
import librosa
import time

from backend.realtime.audio_stream.stt.whisper_stt import WhisperSTT
from backend.realtime.audio_stream.tts.edge_tts import EdgeTTS
from backend.ai.interviewer import AIInterview


class AudioPipeline:
    def __init__(self):
        print("[AudioPipeline] Initializing...")
        
        # Initialize components
        self.stt = WhisperSTT()
        self.tts = EdgeTTS()
        self.ai = AIInterview()

        # Audio queues
        self.input_queue = asyncio.Queue()
        self.output_queue = asyncio.Queue()

        # Audio buffers
        self.tts_buffer = bytearray()  # Buffer for TTS output chunks
        self.speech_buffer = []  # Buffer for incoming speech chunks
        
        # Audio processing parameters
        self.chunk_size = 960  # 20ms at 48kHz (960 samples * 2 bytes)
        
        # Voice Activity Detection (VAD) parameters
        self.silence_chunks = 0
        self.speech_started = False
        self.SILENCE_THRESHOLD = 500  # Energy threshold for speech detection
        self.SILENCE_LIMIT = 25       # ~0.5 seconds of silence (25 × 20ms)
        self.MIN_SPEECH_DURATION = 1.0  # Minimum speech duration in seconds
        
        # Start worker task
        self.worker_task = asyncio.create_task(self._worker())
        print("[AudioPipeline] Initialized")

    async def push_audio(self, pcm: bytes):
        """Called continuously from IncomingAudioSink with audio chunks"""
        await self.input_queue.put(pcm)

    async def pull_audio(self):
        """Called from OutgoingAudioTrack to get TTS audio chunks"""
        try:
            # Check if we have buffered TTS audio
            if len(self.tts_buffer) >= self.chunk_size * 2:  # int16 = 2 bytes
                chunk = bytes(self.tts_buffer[:self.chunk_size * 2])
                del self.tts_buffer[:self.chunk_size * 2]
                return np.frombuffer(chunk, dtype=np.int16)
            
            # Try to get new TTS audio from output queue
            return await self.output_queue.get()
        except Exception as e:
            print(f"[AudioPipeline] Error in pull_audio: {e}")
            return None

    async def _worker(self):
        """Main processing loop - handles VAD, STT, AI, and TTS"""
        print("[AudioPipeline] Worker started")
        
        while True:
            try:
                # Get audio chunk from WebRTC
                pcm = await self.input_queue.get()
                
                # Add to speech buffer
                self.speech_buffer.append(pcm)
                
                # Process VAD
                await self._process_vad(pcm)
                
            except asyncio.CancelledError:
                print("[AudioPipeline] Worker cancelled")
                break
            except Exception as e:
                print(f"[AudioPipeline] Worker error: {e}")
                import traceback
                traceback.print_exc()

    async def _process_vad(self, pcm: bytes):
        """Process Voice Activity Detection"""
        # Convert to numpy for analysis
        samples = np.frombuffer(pcm, dtype=np.int16)
        energy = np.abs(samples).mean()
        
        if energy > self.SILENCE_THRESHOLD:
            # Speech detected
            if not self.speech_started:
                print(f"[AudioPipeline] Speech started (energy: {energy:.2f})")
                self.speech_started = True
            self.silence_chunks = 0
        else:
            # Silence detected
            if self.speech_started:
                self.silence_chunks += 1
                
                # Check if speech has ended
                if self.silence_chunks >= self.SILENCE_LIMIT:
                    print("[AudioPipeline] Speech ended - processing...")
                    await self._process_speech()
                    self.speech_buffer.clear()
                    self.speech_started = False
                    self.silence_chunks = 0

    async def _process_speech(self):
        """Process accumulated speech buffer"""
        if not self.speech_buffer:
            print("[AudioPipeline] No speech to process")
            return
        
        # Concatenate all speech chunks
        audio_bytes = b''.join(self.speech_buffer)
        
        # Check duration
        sample_count = len(audio_bytes) // 2  # 2 bytes per int16 sample
        duration = sample_count / 48000
        
        if duration < self.MIN_SPEECH_DURATION:
            print(f"[AudioPipeline] Speech too short ({duration:.2f}s), skipping")
            return
        
        print(f"[AudioPipeline] Processing speech: {duration:.2f}s, {sample_count} samples")
        
        try:
            # Step 1: Save raw audio for debugging
            raw_filename = f"debug_raw_{int(time.time())}.pcm"
            with open(raw_filename, "wb") as f:
                f.write(audio_bytes)
            print(f"[AudioPipeline] Saved raw audio: {raw_filename}")
            
            # Step 2: Convert to float32 and resample for Whisper
            samples = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
            
            # Resample from 48kHz to 16kHz for Whisper
            samples_16k = librosa.resample(
                samples,
                orig_sr=48000,
                target_sr=16000,
                res_type='kaiser_best'
            )
            
            # Normalize
            max_val = np.max(np.abs(samples_16k))
            if max_val > 0:
                samples_16k = samples_16k / max_val * 0.95
            
            # Step 3: Save processed audio for debugging
            processed_filename = f"debug_processed_{int(time.time())}.wav"
            sf.write(processed_filename, samples_16k, 16000, subtype='PCM_16')
            print(f"[AudioPipeline] Saved processed audio: {processed_filename}")
            
            # Step 4: Create temp file for Whisper
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                sf.write(f.name, samples_16k, 16000, subtype='PCM_16')
                tmp_path = f.name
            
            # Step 5: Transcribe with Whisper
            print("[AudioPipeline] Running STT...")
            text = await self.stt.transcribe(tmp_path)
            text = text.strip()
            print(f"[AudioPipeline] STT result: '{text}'")
            
            # Cleanup temp file
            os.remove(tmp_path)
            
            if not text or len(text) < 3:
                print("[AudioPipeline] Text too short or empty")
                return
            
            # Step 6: Get AI response
            print("[AudioPipeline] Getting AI response...")
            reply = await self.ai.ask_followup(text)
            print(f"[AudioPipeline] AI reply: '{reply}'")
            
            # Step 7: Generate TTS audio
            print("[AudioPipeline] Generating TTS...")
            tts_audio = await self.tts.synthesize(reply)
            
            # Convert to proper format if needed
            if isinstance(tts_audio, np.ndarray):
                if tts_audio.dtype == np.float32:
                    tts_audio = (tts_audio * 32767).astype(np.int16)
                tts_bytes = tts_audio.tobytes()
            elif isinstance(tts_audio, bytes):
                tts_bytes = tts_audio
            else:
                print(f"[AudioPipeline] Unexpected TTS audio type: {type(tts_audio)}")
                return
            
            # Step 8: Buffer TTS audio for streaming
            self.tts_buffer.extend(tts_bytes)
            tts_duration = len(tts_bytes) / (48000 * 2)  # 48kHz, 2 bytes per sample
            print(f"[AudioPipeline] Added {len(tts_bytes)} bytes ({tts_duration:.2f}s) to TTS buffer")
            
        except Exception as e:
            print(f"[AudioPipeline] Error processing speech: {e}")
            import traceback
            traceback.print_exc()

    def stop(self):
        """Cleanup resources"""
        if self.worker_task and not self.worker_task.done():
            self.worker_task.cancel()
        print("[AudioPipeline] Stopped")