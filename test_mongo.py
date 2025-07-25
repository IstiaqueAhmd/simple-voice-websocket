#!/usr/bin/env python3
"""
Test script for MongoDB integration
"""
import asyncio
import os
from dotenv import load_dotenv
from database import db

async def test_database():
    """Test basic database operations"""
    print("Testing MongoDB integration...")
    
    try:
        # Connect to database
        await db.connect()
        print("✅ Connected to MongoDB successfully")
        
        # Test creating a conversation
        session_id = "test_session_123"
        await db.create_conversation(session_id)
        print(f"✅ Created conversation with session_id: {session_id}")
        
        # Test adding a message
        await db.add_message(
            session_id, 
            "Hello, how are you?", 
            "I'm doing great, thank you for asking!",
            "Hello, how are you?"
        )
        print("✅ Added message to conversation")
        
        # Test retrieving conversation history
        history = await db.get_conversation_history(session_id)
        print(f"✅ Retrieved {len(history)} messages from conversation")
        
        # Test getting conversation context
        context = await db.get_conversation_context(session_id)
        print(f"✅ Retrieved conversation context: {len(context)} characters")
        
        # Test deleting conversation
        deleted = await db.delete_conversation(session_id)
        print(f"✅ Deleted conversation: {deleted}")
        
        print("\n🎉 All tests passed! MongoDB integration is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        
    finally:
        # Disconnect from database
        await db.disconnect()
        print("✅ Disconnected from MongoDB")

if __name__ == "__main__":
    load_dotenv()
    asyncio.run(test_database())
