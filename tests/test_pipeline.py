# test_pipeline.py
import asyncio
import numpy as np
import time

async def test_pipeline_basics():
    """Test basic pipeline functionality"""
    from backend.realtime.audio_stream.pipeline import AudioPipeline
    
    print("Testing AudioPipeline initialization...")
    pipeline = AudioPipeline()
    
    # Check attributes exist
    required_attrs = ['input_queue', 'output_queue', 'tts_buffer', 
                      'push_audio', 'pull_audio']
    
    for attr in required_attrs:
        if hasattr(pipeline, attr):
            print(f"✓ {attr} exists")
        else:
            print(f"✗ {attr} missing!")
    
    # Test push_audio
    print("\nTesting push_audio...")
    test_audio = np.zeros(960, dtype=np.int16).tobytes()  # 20ms of silence
    await pipeline.push_audio(test_audio)
    print("✓ push_audio successful")
    
    # Test pull_audio (should return None initially)
    print("\nTesting pull_audio...")
    audio = await pipeline.pull_audio()
    if audio is None:
        print("✓ pull_audio returns None (no TTS yet)")
    else:
        print(f"✓ pull_audio returned {len(audio)} samples")
    
    # Cleanup
    pipeline.stop()
    print("\nTest complete!")

if __name__ == "__main__":
    asyncio.run(test_pipeline_basics())