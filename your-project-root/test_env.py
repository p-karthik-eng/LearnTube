#!/usr/bin/env python3
"""
Test environment variables and API connection
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment():
    """Test if environment variables are set correctly"""
    print("🔍 Testing environment variables...")
    
    # Check OpenRouter API key
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    if openrouter_key:
        print(f"✅ OPENROUTER_API_KEY: {openrouter_key[:10]}...{openrouter_key[-4:]}")
    else:
        print("❌ OPENROUTER_API_KEY not found!")
        print("💡 Please create a .env file with:")
        print("   OPENROUTER_API_KEY=your_api_key_here")
        return False
    
    # Check if key looks valid
    if len(openrouter_key) < 20:
        print("⚠️  API key seems too short, might be invalid")
        return False
    
    print("✅ Environment variables look good!")
    return True

if __name__ == "__main__":
    test_environment() 