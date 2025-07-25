# Voice Assistant WebSocket Server with MongoDB Memory

A voice-enabled chat assistant that uses WebSockets for real-time communication and MongoDB for conversation memory. The application supports speech-to-text, AI responses, and text-to-speech functionality with persistent conversation history.

## Features

- 🎤 **Voice Input**: Speech-to-text using OpenAI Whisper
- 🤖 **AI Responses**: Contextual responses using OpenAI GPT-3.5
- 🔊 **Voice Output**: Text-to-speech using OpenAI TTS
- 💾 **Conversation Memory**: Persistent chat history with MongoDB
- 🔄 **Real-time Communication**: WebSocket-based for instant responses
- 📱 **Web Interface**: Simple web UI for voice interactions

## Prerequisites

- Python 3.8+
- MongoDB (local installation or MongoDB Atlas)
- OpenAI API key

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/simple-voice-websocket.git
   cd simple-voice-websocket
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` file and add your OpenAI API key and MongoDB connection string.

4. **Set up MongoDB**
   
   **Option A: Local MongoDB**
   - Install MongoDB locally
   - Start MongoDB service
   - Run the initialization script:
     ```bash
     mongosh voice_assistant init-mongo.js
     ```
   
   **Option B: MongoDB Atlas**
   - Create a MongoDB Atlas account
   - Create a cluster and database
   - Update the `MONGODB_URI` in your `.env` file

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `MONGODB_URI`: MongoDB connection string (default: `mongodb://localhost:27017`)
- `MONGODB_DATABASE`: Database name (default: `voice_assistant`)

### MongoDB Setup

The application automatically creates the necessary collections and indexes on startup. However, you can manually initialize the database using:

```bash
mongosh voice_assistant init-mongo.js
```

## Usage

1. **Start the server**
   ```bash
   python main.py
   ```

2. **Open your browser**
   Navigate to `http://localhost:8000`

3. **Start chatting**
   - Click the microphone button to start voice input
   - Speak your message
   - The AI will respond with both text and voice
   - All conversations are saved to MongoDB with session management

## API Endpoints

### WebSocket
- `GET /ws` - WebSocket endpoint for real-time voice chat

### REST API
- `GET /` - Web interface
- `GET /health` - Health check
- `GET /api/conversations/{session_id}` - Get conversation history
- `DELETE /api/conversations/{session_id}` - Delete conversation
- `POST /api/conversations` - Create new conversation session

### WebSocket Message Types

**Client to Server:**
```json
{
  "type": "audio_data",
  "audio": "base64_encoded_audio_data"
}
```

**Server to Client:**
```json
{
  "type": "ai_response",
  "transcription": "What you said",
  "message": "AI response text",
  "audio": "base64_encoded_response_audio",
  "session_id": "unique_session_id",
  "timestamp": 1234567890
}
```

## Database Schema

### Conversations Collection
```json
{
  "_id": "ObjectId",
  "session_id": "unique_session_identifier",
  "created_at": "ISODate",
  "updated_at": "ISODate",
  "messages": [
    {
      "timestamp": "ISODate",
      "user_message": "User's input text",
      "ai_response": "AI's response text",
      "transcription": "Transcribed audio (if voice input)"
    }
  ]
}
```

## Development

### Project Structure
```
simple-voice-websocket/
├── main.py              # FastAPI application with WebSocket endpoints
├── database.py          # MongoDB connection and operations
├── requirements.txt     # Python dependencies
├── init-mongo.js       # MongoDB initialization script
├── .env.example        # Environment variables template
└── static/             # Web interface files
    ├── index.html
    ├── script.js
    └── styles.css
```

### Running in Development Mode
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

## Troubleshooting

### Common Issues

1. **MongoDB Connection Error**
   - Ensure MongoDB is running
   - Check the `MONGODB_URI` in your `.env` file
   - Verify network connectivity for MongoDB Atlas

2. **OpenAI API Errors**
   - Verify your API key is correct
   - Check your OpenAI account credits
   - Ensure you have access to the required models (Whisper, GPT-3.5, TTS)

3. **Audio Issues**
   - Check browser permissions for microphone access
   - Ensure your browser supports WebRTC
   - Try using HTTPS for better audio support

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

