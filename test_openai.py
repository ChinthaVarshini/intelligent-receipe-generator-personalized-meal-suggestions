"""
Quick test to verify OpenAI API connection
"""
import sys
sys.path.append('backend/app')

from config import OPENAI_API_KEY
from openai import OpenAI

def test_openai_connection():
    """Test if OpenAI API key is working"""
    print("="*60)
    print("Testing OpenAI API Connection")
    print("="*60)
    
    if not OPENAI_API_KEY:
        print("❌ ERROR: OpenAI API key not found in .env file")
        print("Please add your OPENAI_API_KEY to the .env file")
        return False
    
    print(f"✓ OpenAI API key found: {OPENAI_API_KEY[:10]}...{OPENAI_API_KEY[-10:]}")
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Test with a simple request
        print("\nTesting API with a simple request...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'API connection successful' if you receive this."}
            ],
            max_tokens=20
        )
        
        result = response.choices[0].message.content
        print(f"\n✅ SUCCESS! OpenAI API Response: {result}")
        print("\n" + "="*60)
        print("OpenAI API is properly connected and working!")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to connect to OpenAI API")
        print(f"Error details: {str(e)}")
        print("\nPossible issues:")
        print("1. Invalid API key")
        print("2. Network connection issue")
        print("3. API key may have expired or been revoked")
        print("\nPlease check your API key at: https://platform.openai.com/api-keys")
        return False

if __name__ == "__main__":
    test_openai_connection()
