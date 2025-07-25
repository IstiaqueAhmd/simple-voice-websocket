from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class MongoDatabase:
    def __init__(self):
        self.client = None
        self.database = None
        self.conversations = None
        
    async def connect(self):
        try:
            # Get MongoDB connection string from environment
            mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
            db_name = os.getenv("MONGODB_DATABASE", "voice_assistant")
            
            self.client = AsyncIOMotorClient(mongo_uri)
            self.database = self.client[db_name]
            self.conversations = self.database.conversations
            
            # Test the connection
            await self.client.admin.command('ismaster')
            logger.info(f"Connected to MongoDB at {mongo_uri}")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def create_conversation(self, session_id: str) -> str:
        """Create a new conversation session"""
        conversation = {
            "session_id": session_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "messages": []
        }
        
        result = await self.conversations.insert_one(conversation)
        logger.info(f"Created new conversation with session_id: {session_id}")
        return str(result.inserted_id)
    
    async def add_message(self, session_id: str, user_message: str, ai_response: str, transcription: Optional[str] = None):
        """Add a message exchange to the conversation"""
        message_entry = {
            "timestamp": datetime.utcnow(),
            "user_message": user_message,
            "ai_response": ai_response,
            "transcription": transcription
        }
        
        await self.conversations.update_one(
            {"session_id": session_id},
            {
                "$push": {"messages": message_entry},
                "$set": {"updated_at": datetime.utcnow()}
            },
            upsert=True
        )
        
        logger.info(f"Added message to conversation {session_id}")
    
    async def get_conversation_history(self, session_id: str, limit: int = 10) -> List[Dict]:
        """Get recent conversation history for context"""
        conversation = await self.conversations.find_one(
            {"session_id": session_id},
            {"messages": {"$slice": -limit}}
        )
        
        if conversation and "messages" in conversation:
            return conversation["messages"]
        return []
    
    async def get_conversation_context(self, session_id: str, context_limit: int = 5) -> str:
        """Get formatted conversation context for AI"""
        messages = await self.get_conversation_history(session_id, context_limit)
        
        if not messages:
            return ""
        
        context = "Previous conversation:\n"
        for msg in messages:
            context += f"User: {msg['user_message']}\n"
            context += f"Assistant: {msg['ai_response']}\n"
        
        return context
    
    async def delete_conversation(self, session_id: str):
        """Delete a conversation"""
        result = await self.conversations.delete_one({"session_id": session_id})
        logger.info(f"Deleted conversation {session_id}")
        return result.deleted_count > 0

# Global database instance
db = MongoDatabase()
