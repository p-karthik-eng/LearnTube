"""
Core modules for YouTube Course Generator
Contains transcript processing, DeepSeek client, and course generation logic
"""

from .transcript_processor import TranscriptProcessor
from .deepseek_client import DeepSeekClient
from .course_generator import CourseGenerator

__all__ = [
    "TranscriptProcessor",
    "DeepSeekClient", 
    "CourseGenerator"
]
