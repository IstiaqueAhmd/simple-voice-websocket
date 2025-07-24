#!/usr/bin/env python3
"""
Test script for OpenAI Whisper STT and TTS functionality
"""

import os
import tempfile
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_openai_connection():
    """Test OpenAI client initialization"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        return False
    
    try:
        client = OpenAI(api_key=api_key)
        print("✅ OpenAI client initialized successfully")
        return client
    except Exception as e:
        print(f"❌ Failed to initialize OpenAI client: {e}")
        return False

def test_tts(client, text="Hello, this is a test of OpenAI's text-to-speech functionality."):
    """Test OpenAI TTS functionality"""
    print(f"\n🔊 Testing TTS with text: '{text}'")
    
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=text
        )
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            temp_file.write(response.content)
            temp_file_path = temp_file.name
        
        print(f"✅ TTS successful! Audio saved to: {temp_file_path}")
        print(f"   Audio size: {len(response.content)} bytes")
        return temp_file_path
        
    except Exception as e:
        print(f"❌ TTS test failed: {e}")
        return None

def test_whisper_with_generated_audio(client, audio_file_path):
    """Test Whisper STT with the generated audio"""
    if not audio_file_path:
        print("❌ No audio file to test Whisper with")
        return False
    
    print(f"\n🎤 Testing Whisper STT with generated audio...")
    
    try:
        with open(audio_file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        
        print(f"✅ Whisper transcription successful!")
        print(f"   Transcribed text: '{transcript.text}'")
        
        # Clean up
        os.unlink(audio_file_path)
        print(f"   Cleaned up temporary file: {audio_file_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Whisper test failed: {e}")
        # Try to clean up anyway
        try:
            os.unlink(audio_file_path)
        except:
            pass
        return False

def main():
    """Run all tests"""
    print("🧪 Testing OpenAI Whisper STT and TTS Integration")
    print("=" * 50)
    
    # Test OpenAI connection
    client = test_openai_connection()
    if not client:
        return
    
    # Test TTS
    test_text = "Hello, this is a test of OpenAI's text-to-speech functionality."
    audio_file = test_tts(client, test_text)
    
    # Test Whisper STT with generated audio
    if audio_file:
        test_whisper_with_generated_audio(client, audio_file)
    
    print("\n" + "=" * 50)
    print("🎉 OpenAI integration test completed!")
    print("\nIf all tests passed, your voice assistant should work correctly.")
    print("Make sure to start the server with: python main.py")

if __name__ == "__main__":
    main()
