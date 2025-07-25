// MongoDB initialization script for voice assistant
// Run this with: mongosh voice_assistant init-mongo.js

// Create the voice_assistant database
use('voice_assistant');

// Create conversations collection with indexes
db.createCollection('conversations');

// Create indexes for better performance
db.conversations.createIndex({ "session_id": 1 }, { unique: true });
db.conversations.createIndex({ "created_at": 1 });
db.conversations.createIndex({ "updated_at": 1 });

// Insert a sample conversation (optional)
db.conversations.insertOne({
  session_id: "sample_session",
  created_at: new Date(),
  updated_at: new Date(),
  messages: [
    {
      timestamp: new Date(),
      user_message: "Hello, how are you?",
      ai_response: "Hello! I'm doing well, thank you for asking. How can I help you today?",
      transcription: "Hello, how are you?"
    }
  ]
});

print("MongoDB initialization completed!");
print("Database: voice_assistant");
print("Collection: conversations");
print("Indexes created for session_id, created_at, and updated_at");