import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Test OpenAI connection
api_key = os.getenv("OPENAI_API_KEY")
print(f"API Key found: {'Yes' if api_key else 'No'}")
print(f"API Key length: {len(api_key) if api_key else 0}")
print(f"API Key starts with: {api_key[:10] if api_key else 'N/A'}...")

if api_key:
    try:
        client = OpenAI(api_key=api_key)
        print("OpenAI client created successfully")
        
        # Test with a simple request
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=10
        )
        print(f"Test response: {response.choices[0].message.content}")
        print("✅ OpenAI connection is working!")
        
    except Exception as e:
        print(f"❌ Error testing OpenAI: {e}")
else:
    print("❌ No API key found")
