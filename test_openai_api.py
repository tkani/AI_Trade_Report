#!/usr/bin/env python3
"""
Test OpenAI API Key for Hosted Environment
This script tests if the OpenAI API key is working correctly.
"""

import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_openai_api():
    """Test OpenAI API connection"""
    
    print("🔧 OPENAI API TEST")
    print("=" * 50)
    
    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ ERROR: OPENAI_API_KEY not found in environment variables")
        print("💡 Add OPENAI_API_KEY to your Render dashboard → Environment tab")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        # Set the API key
        openai.api_key = api_key
        
        # Test with a simple request
        print("🔧 Testing OpenAI API connection...")
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Hello, this is a test. Please respond with 'API test successful'."}
            ],
            max_tokens=50,
            temperature=0.1
        )
        
        print("✅ OpenAI API connection successful!")
        print(f"   Response: {response.choices[0].message.content}")
        return True
        
    except openai.error.AuthenticationError as e:
        print(f"❌ Authentication Error: {e}")
        print("💡 Check if your OpenAI API key is valid and active")
        return False
        
    except openai.error.RateLimitError as e:
        print(f"❌ Rate Limit Error: {e}")
        print("💡 You may have exceeded your OpenAI API usage limits")
        return False
        
    except openai.error.APIError as e:
        print(f"❌ API Error: {e}")
        print("💡 Check your OpenAI API key and account status")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        print("💡 Check your internet connection and API key")
        return False

def test_environment_variables():
    """Test if all required environment variables are set"""
    
    print("🔧 ENVIRONMENT VARIABLES TEST")
    print("=" * 50)
    
    required_vars = [
        "OPENAI_API_KEY",
        "DATABASE_URL"
    ]
    
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if "API_KEY" in var:
                masked_value = f"{value[:10]}...{value[-4:]}"
            else:
                masked_value = value
            print(f"   ✅ {var}: {masked_value}")
        else:
            print(f"   ❌ {var}: Not set")
            missing_vars.append(var)
    
    print()
    
    if missing_vars:
        print("❌ MISSING ENVIRONMENT VARIABLES:")
        for var in missing_vars:
            print(f"   - {var}")
        print()
        print("💡 Add these to your Render dashboard → Environment tab")
        return False
    else:
        print("✅ All required environment variables are set!")
        return True

if __name__ == "__main__":
    print("🧪 AI TRADE REPORT - OPENAI API TEST")
    print("=" * 60)
    print()
    
    # Test environment variables first
    env_ok = test_environment_variables()
    print()
    
    if env_ok:
        # Test OpenAI API
        api_ok = test_openai_api()
        print()
        
        if api_ok:
            print("🎉 ALL TESTS PASSED!")
            print("   Your OpenAI API should work for report generation.")
        else:
            print("❌ OPENAI API TEST FAILED!")
            print("   This is likely why report generation is failing.")
    else:
        print("❌ ENVIRONMENT VARIABLES MISSING!")
        print("   Set up environment variables in Render dashboard first.")
    
    print()
    print("=" * 60)
