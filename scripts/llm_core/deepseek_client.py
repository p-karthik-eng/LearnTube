import asyncio
import json
import os
from typing import Dict, List, Optional
import aiohttp
import time
import sys

class DeepSeekClient:
    def __init__(self, api_key: Optional[str] = None):
        # Use DeepSeek API key from environment
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.base_url = "https://api.deepseek.com/v1"  # DeepSeek API endpoint
        self.session = None
        
        if not self.api_key:
            raise ValueError("DeepSeek API key is required. Set DEEPSEEK_API_KEY environment variable")
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - cleanup session"""
        if self.session:
            await self.session.close()
    
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        max_tokens: int = 4000,
        temperature: float = 0.2,
        response_format: Optional[Dict] = None
    ) -> str:
        """
        Send chat completion request to DeepSeek API
        Enhanced with proper timeout handling and retry logic
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",  # DeepSeek model
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False  # Ensure non-streaming response
        }
        
        # Only add response_format if specifically requested
        if response_format:
            payload["response_format"] = response_format
        
        max_retries = 3
        base_delay = 2
        
        for attempt in range(max_retries):
            try:
                print(f" Attempt {attempt + 1}/{max_retries} - Sending request to DeepSeek...", file=sys.stderr)
                
                # Progressive timeout: start with 5 minutes, increase with retries
                timeout_seconds = 300 + (attempt * 120)  # 5min, 7min, 9min
                
                async with self.session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=timeout_seconds)
                ) as response:
                    
                    print(f" Response status: {response.status}", file=sys.stderr)
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Validate response structure
                        if "choices" not in data or not data["choices"]:
                            raise Exception("Invalid response structure from DeepSeek")
                        
                        content = data["choices"][0]["message"]["content"]
                        
                        if not content or content.strip() == "":
                            raise Exception("Empty response content from DeepSeek")
                        
                        print(f" Successfully received response ({len(content)} characters)", file=sys.stderr)
                        return content.strip()
                    
                    elif response.status == 429:  # Rate limit
                        error_text = await response.text()
                        print(f"Rate limit hit (429), retrying in {base_delay ** (attempt + 1)} seconds...", file=sys.stderr)
                        await asyncio.sleep(base_delay ** (attempt + 1))
                        continue
                    
                    elif response.status == 401:  # Unauthorized
                        error_text = await response.text()
                        raise Exception(f"Authentication failed: {error_text}", file=sys.stderr)
                    
                    elif response.status == 400:  # Bad request
                        error_text = await response.text()
                        raise Exception(f"Bad request: {error_text}", file=sys.stderr)
                    
                    else:
                        error_text = await response.text()
                        print(f" HTTP {response.status}: {error_text}", file=sys.stderr)
                        if attempt == max_retries - 1:
                            raise Exception(f"HTTP {response.status}: {error_text}", file=sys.stderr)
                        await asyncio.sleep(base_delay ** (attempt + 1))
                        continue
                        
            except asyncio.TimeoutError:
                print(f" Timeout on attempt {attempt + 1}/{max_retries}", file=sys.stderr)
                if attempt == max_retries - 1:
                    raise Exception("Request timed out after all retries", file=sys.stderr)
                await asyncio.sleep(base_delay ** (attempt + 1))
                continue
                
            except Exception as e:
                print(f" Error on attempt {attempt + 1}/{max_retries}: {str(e)}", file=sys.stderr)
                if attempt == max_retries - 1:
                    raise e
                await asyncio.sleep(base_delay ** (attempt + 1))
                continue
        
        raise Exception("All retry attempts failed")
    
    async def test_connection(self) -> Dict[str, str]:
        """
        Test the connection to DeepSeek API
        """
        try:
            response = await self.chat_completion(
                messages=[{"role": "user", "content": "Hello, this is a test message."}],
                max_tokens=10
            )
            return {
                "status": "success",
                "message": "DeepSeek API connection successful",
                "response": response
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"DeepSeek API connection failed: {str(e)}"
            }
    
    async def close_session(self):
        """Close the aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None 