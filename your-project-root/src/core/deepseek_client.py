import asyncio
import json
import os
from typing import Dict, List, Optional
import aiohttp
import time

class DeepSeekClient:
    def __init__(self, api_key: Optional[str] = None):
        # Updated to use OpenRouter API key
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"  # OpenRouter endpoint
        self.session = None
        
        if not self.api_key:
            raise ValueError("OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable")
    
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
        Send chat completion request to DeepSeek via OpenRouter
        Enhanced with proper timeout handling and retry logic
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",  # Required by OpenRouter
            "X-Title": "YouTube Course Generator"      # Optional for rankings
        }
        
        payload = {
            "model": "deepseek/deepseek-r1:free",  # Free DeepSeek model
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
                print(f"🔄 Attempt {attempt + 1}/{max_retries} - Sending request to OpenRouter...")
                
                # Progressive timeout: start with 5 minutes, increase with retries
                timeout_seconds = 300 + (attempt * 120)  # 5min, 7min, 9min
                
                async with self.session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=timeout_seconds)
                ) as response:
                    
                    print(f"📡 Response status: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Validate response structure
                        if "choices" not in data or not data["choices"]:
                            raise Exception("Invalid response structure from OpenRouter")
                        
                        content = data["choices"][0]["message"]["content"]
                        
                        if not content or content.strip() == "":
                            raise Exception("Empty response content from OpenRouter")
                        
                        print(f"✅ Successfully received response ({len(content)} characters)")
                        return content.strip()
                    
                    elif response.status == 429:  # Rate limit
                        error_text = await response.text()
                        print(f"⚠️ Rate limit hit (429), retrying in {base_delay ** (attempt + 1)} seconds...")
                        await asyncio.sleep(base_delay ** (attempt + 1))
                        continue
                    
                    elif response.status == 401:  # Authentication error
                        error_text = await response.text()
                        raise Exception(f"Authentication failed. Check your OpenRouter API key: {error_text}")
                    
                    elif response.status == 400:  # Bad request
                        error_text = await response.text()
                        raise Exception(f"Bad request to OpenRouter API: {error_text}")
                    
                    else:
                        error_text = await response.text()
                        print(f"❌ OpenRouter API error {response.status}: {error_text}")
                        
                        if attempt < max_retries - 1:
                            await asyncio.sleep(base_delay ** (attempt + 1))
                            continue
                        else:
                            raise Exception(f"OpenRouter API error {response.status}: {error_text}")
                        
            except asyncio.TimeoutError:
                print(f"⏰ Request timed out on attempt {attempt + 1}")
                if attempt == max_retries - 1:
                    raise Exception(f"OpenRouter API timeout after {max_retries} attempts. DeepSeek-R1 may be taking longer than expected.")
                else:
                    print(f"🔄 Retrying in {base_delay ** (attempt + 1)} seconds...")
                    await asyncio.sleep(base_delay ** (attempt + 1))
            
            except aiohttp.ClientError as e:
                print(f"🔌 Connection error on attempt {attempt + 1}: {str(e)}")
                if attempt == max_retries - 1:
                    raise Exception(f"Connection failed after {max_retries} attempts: {str(e)}")
                else:
                    await asyncio.sleep(base_delay ** (attempt + 1))
            
            except json.JSONDecodeError as e:
                print(f"📄 JSON parsing error on attempt {attempt + 1}: {str(e)}")
                if attempt == max_retries - 1:
                    raise Exception(f"Invalid JSON response from OpenRouter: {str(e)}")
                else:
                    await asyncio.sleep(base_delay ** (attempt + 1))
                    
            except Exception as e:
                print(f"💥 Unexpected error on attempt {attempt + 1}: {str(e)}")
                if attempt == max_retries - 1:
                    raise e
                else:
                    await asyncio.sleep(base_delay ** (attempt + 1))
        
        raise Exception("Failed to get response from OpenRouter API after all retry attempts")
    
    async def test_connection(self) -> Dict[str, str]:
        """
        Test the connection to OpenRouter API
        """
        try:
            response = await self.chat_completion(
                messages=[{"role": "user", "content": "Respond with just 'Connection successful' if you can read this."}],
                max_tokens=50,
                temperature=0.1
            )
            return {
                "success": True,
                "response": response,
                "provider": "OpenRouter",
                "model": "deepseek/deepseek-r1:free"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider": "OpenRouter"
            }
    
    async def close_session(self):
        """
        Manually close the aiohttp session
        """
        if self.session and not self.session.closed:
            await self.session.close()
            print("🔌 OpenRouter session closed")
    
    def __del__(self):
        """
        Destructor to ensure session cleanup
        """
        if hasattr(self, 'session') and self.session and not self.session.closed:
            # Note: Can't await in __del__, but this helps in some cases
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.session.close())
            except:
                pass  # Ignore errors during cleanup
