import re
import json
import tiktoken
from typing import Dict, List
import asyncio
import time

class TranscriptProcessor:
    def __init__(self, model_name="deepseek-chat", max_tokens=60000):
        self.encoding = tiktoken.get_encoding("cl100k_base")
        self.max_tokens = max_tokens
        self.chunk_size = 12000  # Increased chunk size to reduce number of requests
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.encoding.encode(text))
    
    def enhance_transcript_quality(self, transcript_json: Dict) -> Dict:
        """Enhance transcript quality before processing"""
        content = transcript_json["content"]
        
        # Remove common transcript artifacts
        content = re.sub(r'\b(um|uh|ah|like|you know)\b', '', content, flags=re.IGNORECASE)
        
        # Fix common transcription errors
        content = re.sub(r'\b(gonna)\b', 'going to', content, flags=re.IGNORECASE)
        content = re.sub(r'\b(wanna)\b', 'want to', content, flags=re.IGNORECASE)
        
        # Clean multiple spaces
        content = re.sub(r'\s+', ' ', content)
        content = content.strip()
        
        return {"content": content}
    
    def create_semantic_micro_chunks(self, transcript_text: str) -> List[str]:
        """Break transcript into semantic micro-chunks"""
        # Split by natural boundaries (sentences)
        sentences = re.split(r'[.!?]+', transcript_text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if not sentence.strip():
                continue
                
            temp_chunk = current_chunk + sentence.strip() + ". "
            
            if self.count_tokens(temp_chunk) < self.chunk_size:
                current_chunk = temp_chunk
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence.strip() + ". "
        
        # Add final chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def validate_transcript(self, transcript_json: Dict) -> bool:
        """Validate transcript JSON structure and content"""
        if not isinstance(transcript_json, dict):
            return False
        
        if "content" not in transcript_json:
            return False
        
        if not transcript_json["content"] or not transcript_json["content"].strip():
            return False
        
        # Check minimum content length
        if len(transcript_json["content"].strip()) < 100:
            return False
        
        return True
