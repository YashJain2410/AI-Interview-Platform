# test_audio_chain.py
import asyncio
import numpy as np
import soundfile as sf
import os

from backend.realtime.audio_stream.stt.whisper_stt import WhisperSTT

async def test_stt():
    """Test STT with known phrases"""
    
    stt = WhisperSTT()
    
    test_phrases = [
        "Hello, how are you today?",
        "My name is John Smith.",
        "I have five years of experience.",
        "Thank you for this opportunity."
    ]
    
    # Create test audio files
    for i, phrase in enumerate(test_phrases):
        # Generate synthetic speech or use pre-recorded
        print(f"\nTesting: '{phrase}'")
        
        # You can record yourself saying these phrases
        filename = f"test_{i}.wav"
        
        if os.path.exists(filename):
            result = await stt.transcribe(filename)
            print(f"Result: '{result}'")
            print(f"Match: {result.lower() == phrase.lower()}")

if __name__ == "__main__":
    asyncio.run(test_stt())