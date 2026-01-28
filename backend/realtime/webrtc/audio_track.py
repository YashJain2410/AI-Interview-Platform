from aiortc import MediaStreamTrack
from aiortc.mediastreams import MediaStreamError
import av
import asyncio
import numpy as np
import time

from backend.realtime.audio_stream.pipeline import AudioPipeline

class IncomingAudioSink:
    """
    Alternative implementation using av.AudioResampler
    to properly handle format conversion
    """
    def __init__(self, track, pipeline):
        self.track = track
        self.pipeline = pipeline
        self.running = True
        self.resampler = None
        self._task = asyncio.create_task(self._run())

    async def _run(self):
        print("[IncomingAudioSink] Started (Alternative Implementation)")
        frame_count = 0
        try:
            while self.running:
                try:
                    frame = await self.track.recv()
                    frame_count += 1
                    
                    # Log first frame
                    if frame_count == 1:
                        print(f"[IncomingAudioSink] First frame:")
                        print(f"  format: {frame.format.name}")
                        print(f"  layout: {frame.layout.name}")
                        print(f"  sample_rate: {frame.sample_rate}")
                        print(f"  samples: {frame.samples}")
                        print(f"  channels: {len(frame.layout.channels)}")
                    
                    # Create resampler on first frame
                    if self.resampler is None:
                        self.resampler = av.AudioResampler(
                            format='s16',
                            layout='mono',
                            rate=48000
                        )
                        print(f"[IncomingAudioSink] Created resampler: {frame.layout.name} -> mono")
                    
                    # Resample to mono
                    resampled_frames = self.resampler.resample(frame)
                    
                    for resampled_frame in resampled_frames:
                        # Convert to numpy array
                        pcm = resampled_frame.to_ndarray()
                        
                        if frame_count == 1:
                            print(f"[IncomingAudioSink] Resampled frame:")
                            print(f"  shape: {pcm.shape}")
                            print(f"  dtype: {pcm.dtype}")
                            print(f"  range: [{pcm.min()}, {pcm.max()}]")
                        
                        # Flatten if needed
                        if pcm.ndim > 1:
                            pcm = pcm.flatten()
                        
                        # Convert to bytes
                        pcm_bytes = pcm.tobytes()
                        
                        # Push to pipeline
                        await self.pipeline.push_audio(pcm_bytes)
                    
                    if frame_count == 100:
                        print(f"[IncomingAudioSink] Processed 100 frames")
                    
                except MediaStreamError:
                    print("[IncomingAudioSink] Track ended")
                    break
                except asyncio.CancelledError:
                    print("[IncomingAudioSink] Cancelled")
                    break
                except Exception as e:
                    print(f"[IncomingAudioSink] Error: {e}")
                    import traceback
                    traceback.print_exc()
                    break
        finally:
            self.running = False
            print("[IncomingAudioSink] Stopped")

    def stop(self):
        self.running = False
        if self._task and not self._task.done():
            self._task.cancel()


class OutgoingAudioTrack(MediaStreamTrack):
    kind = "audio"

    def __init__(self, pipeline, sample_rate=48000):
        super().__init__()
        self.pipeline = pipeline
        self.sample_rate = sample_rate
        self.timestamp = 0
        self.samples_per_frame = 960  # 20ms at 48kHz
        self._start_time = time.time()

    async def recv(self):
        # Calculate proper timing
        current_time = time.time()
        elapsed = current_time - self._start_time
        expected_frames = int(elapsed * self.sample_rate / self.samples_per_frame)
        
        # Catch up if we're behind
        if self.timestamp < expected_frames * self.samples_per_frame:
            self.timestamp = expected_frames * self.samples_per_frame
        
        pts = self.timestamp
        self.timestamp += self.samples_per_frame
        
        # Try to get audio from pipeline (non-blocking)
        response_audio = None
        try:
            response_audio = await asyncio.wait_for(
                self.pipeline.pull_audio(), 
                timeout=0.001
            )
        except asyncio.TimeoutError:
            pass
        except Exception as e:
            print(f"[OutgoingAudioTrack] Error getting audio: {e}")

        if response_audio is None:
            # Generate silence frame
            silence = np.zeros((self.samples_per_frame,), dtype=np.int16)
            frame = av.AudioFrame.from_ndarray(
                silence.reshape(1, -1),
                format="s16",
                layout="mono"
            )
        else:
            # Ensure correct shape and type
            if isinstance(response_audio, bytes):
                response_audio = np.frombuffer(response_audio, dtype=np.int16)
            
            if not isinstance(response_audio, np.ndarray):
                response_audio = np.array(response_audio, dtype=np.int16)
            
            # Ensure 1D array
            if response_audio.ndim > 1:
                response_audio = response_audio.flatten()
            
            # Pad or trim to exact frame size
            if len(response_audio) < self.samples_per_frame:
                response_audio = np.pad(
                    response_audio, 
                    (0, self.samples_per_frame - len(response_audio))
                )
            elif len(response_audio) > self.samples_per_frame:
                response_audio = response_audio[:self.samples_per_frame]
            
            frame = av.AudioFrame.from_ndarray(
                response_audio.reshape(1, -1),
                format="s16",
                layout="mono"
            )

        frame.sample_rate = self.sample_rate
        frame.pts = pts
        frame.time_base = "1/48000"
        
        # Precise timing control
        await asyncio.sleep(0.02)  # 20ms
        
        return frame