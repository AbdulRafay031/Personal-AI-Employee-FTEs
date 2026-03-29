"""
Test OpenRouter API Connection

Quick test to verify your API key is working correctly.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API configuration
api_key = os.getenv('OPENROUTER_API_KEY')
api_url = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
model = os.getenv('QWEN_MODEL', 'qwen/qwen-2.5-coder-32b-instruct')

print("=" * 60)
print("OpenRouter API Connection Test")
print("=" * 60)

# Check if API key exists
if not api_key:
    print("\n❌ ERROR: OPENROUTER_API_KEY not found in .env file")
    print("\nTo fix:")
    print("  1. Open .env file in a text editor")
    print("  2. Replace 'sk-or-v1-your-api-key-here' with your actual key")
    print("  3. Save and run this test again")
    exit(1)

print(f"\n✓ API Key found: {api_key[:10]}...{api_key[-4:]}")
print(f"✓ API URL: {api_url}")
print(f"✓ Model: {model}")

# Test the API
print("\n" + "=" * 60)
print("Testing API Connection...")
print("=" * 60)

try:
    from openai import OpenAI
    
    # Create client
    client = OpenAI(
        base_url=api_url,
        api_key=api_key,
        default_headers={
            "HTTP-Referer": "",
            "X-Title": "AI Employee FTE Test",
        }
    )
    
    # Send test message
    print("\nSending test request to Qwen...")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello! This is a test message. Please respond with 'API connection successful!' and tell me the current date."}
        ],
        temperature=0.7,
        max_tokens=100,
    )
    
    # Get response
    assistant_message = response.choices[0].message.content
    
    print("\n" + "=" * 60)
    print("✅ SUCCESS! API Connection Working!")
    print("=" * 60)
    print(f"\nQwen's Response:\n{assistant_message}")
    
    # Show usage info
    if hasattr(response, 'usage') and response.usage:
        print(f"\n📊 Usage:")
        print(f"   Prompt tokens: {response.usage.prompt_tokens}")
        print(f"   Completion tokens: {response.usage.completion_tokens}")
        print(f"   Total tokens: {response.usage.total_tokens}")
    
    print("\n" + "=" * 60)
    print("🎉 Your AI Employee is ready to use!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Drop a file into test_drop/ folder")
    print("  2. Start the orchestrator: python orchestrator.py AI_Employee_Vault")
    print("  3. Watch Qwen process your tasks automatically!")
    
except ImportError as e:
    print(f"\n❌ ERROR: Missing dependency")
    print(f"   {e}")
    print("\nTo fix:")
    print("  pip install openai python-dotenv")
    
except Exception as e:
    print(f"\n❌ ERROR: API request failed")
    print(f"   {type(e).__name__}: {e}")
    print("\nPossible causes:")
    print("  - Invalid API key (check your key in .env)")
    print("  - Insufficient credits (add credits at openrouter.ai/credits)")
    print("  - Network issue (check your internet connection)")
    print("  - Model not available (try a different model)")
