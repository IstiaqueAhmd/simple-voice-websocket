from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, Response
import json
import asyncio
from openai import OpenAI
import os
from dotenv import load_dotenv
from typing import Dict, List
import logging
import tempfile
import base64
import io

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Voice Assistant WebSocket Server")

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger.warning("OPENAI_API_KEY not found in environment variables. Please set it in your .env file.")
    client = None
else:
    try:
        client = OpenAI(api_key=api_key)
        logger.info("OpenAI client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {e}")
        client = None

# Store active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

def transcribe_audio(audio_data: bytes) -> str:
    """Transcribe audio using OpenAI Whisper"""
    if not client:
        logger.warning("OpenAI client not available - API key may be missing or invalid")
        return "I'm sorry, the speech recognition service is not available right now."
    
    try:
        # Create a temporary file with the audio data
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_file_path = temp_file.name
        
        logger.info("Transcribing audio with Whisper...")
        
        # Open the temporary file and send to Whisper
        with open(temp_file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        transcribed_text = transcript.text.strip()
        logger.info(f"Transcription result: {transcribed_text[:50]}...")
        return transcribed_text
        
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        # Clean up temporary file if it exists
        try:
            os.unlink(temp_file_path)
        except:
            pass
        return f"I'm sorry, I couldn't understand the audio: {str(e)}"

def get_ai_response(user_message: str) -> str:
    """Get response from OpenAI GPT model"""
    if not client:
        logger.warning("OpenAI client not available - API key may be missing or invalid")
        return "I'm sorry, the AI service is not available right now. Please check that your OpenAI API key is configured correctly."
    
    try:
        logger.info(f"Sending request to OpenAI for message: {user_message[:50]}...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a helpful voice assistant. Keep your responses concise and conversational, as they will be spoken aloud. Limit responses to 2-3 sentences maximum."
                },
                {"role": "user", "content": user_message}
            ],
            max_tokens=150,
            temperature=0.7
        )
        ai_message = response.choices[0].message.content.strip()
        logger.info(f"Received AI response: {ai_message[:50]}...")
        return ai_message
    except Exception as e:
        logger.error(f"Error getting AI response: {str(e)}")
        return f"I'm sorry, I encountered an error: {str(e)}"

def generate_speech(text: str) -> bytes:
    """Generate speech from text using OpenAI TTS"""
    if not client:
        logger.warning("OpenAI client not available - API key may be missing or invalid")
        return b""
    
    try:
        logger.info(f"Generating speech for text: {text[:50]}...")
        
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",  # Available voices: alloy, echo, fable, onyx, nova, shimmer
            input=text
        )
        
        logger.info("Speech generation completed")
        return response.content
        
    except Exception as e:
        logger.error(f"Error generating speech: {str(e)}")
        return b""

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            logger.info(f"Received message type: {data[:100]}...")
            
            try:
                message_data = json.loads(data)
                message_type = message_data.get("type")
                
                if message_type == "audio_data":
                    # Handle audio data for transcription
                    audio_base64 = message_data.get("audio", "")
                    if audio_base64:
                        try:
                            # Decode base64 audio data
                            audio_data = base64.b64decode(audio_base64)
                            
                            # Transcribe audio using Whisper
                            transcribed_text = transcribe_audio(audio_data)
                            
                            if transcribed_text and not transcribed_text.startswith("I'm sorry"):
                                # Get AI response
                                ai_response = get_ai_response(transcribed_text)
                                
                                # Generate speech for the response
                                speech_data = generate_speech(ai_response)
                                speech_base64 = base64.b64encode(speech_data).decode('utf-8') if speech_data else ""
                                
                                # Send response back to client
                                response = {
                                    "type": "ai_response",
                                    "transcription": transcribed_text,
                                    "message": ai_response,
                                    "audio": speech_base64,
                                    "timestamp": asyncio.get_event_loop().time()
                                }
                            else:
                                # Error in transcription
                                response = {
                                    "type": "error",
                                    "message": transcribed_text,
                                    "timestamp": asyncio.get_event_loop().time()
                                }
                                
                            await manager.send_personal_message(json.dumps(response), websocket)
                            
                        except Exception as e:
                            logger.error(f"Error processing audio: {str(e)}")
                            error_response = {
                                "type": "error",
                                "message": f"Error processing audio: {str(e)}"
                            }
                            await manager.send_personal_message(json.dumps(error_response), websocket)
                
                elif message_type == "voice_message":
                    # Handle text message (for backward compatibility)
                    user_message = message_data.get("message", "")
                    if user_message:
                        # Get AI response
                        ai_response = get_ai_response(user_message)
                        
                        # Generate speech for the response
                        speech_data = generate_speech(ai_response)
                        speech_base64 = base64.b64encode(speech_data).decode('utf-8') if speech_data else ""
                        
                        # Send response back to client
                        response = {
                            "type": "ai_response",
                            "message": ai_response,
                            "audio": speech_base64,
                            "timestamp": asyncio.get_event_loop().time()
                        }
                        await manager.send_personal_message(json.dumps(response), websocket)
                
                elif message_type == "ping":
                    # Respond to ping with pong
                    pong_response = {"type": "pong", "timestamp": asyncio.get_event_loop().time()}
                    await manager.send_personal_message(json.dumps(pong_response), websocket)
                    
            except json.JSONDecodeError:
                error_response = {
                    "type": "error",
                    "message": "Invalid JSON format"
                }
                await manager.send_personal_message(json.dumps(error_response), websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/")
async def get():
    return HTMLResponse(content=open("static/index.html").read(), media_type="text/html")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Voice assistant server is running"}

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
