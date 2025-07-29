# LLM Core Package
# Contains the core logic for course generation using DeepSeek API

from .course_generator import CourseGenerator
from .deepseek_client import DeepSeekClient
from .transcript_processor import TranscriptProcessor

__all__ = ['CourseGenerator', 'DeepSeekClient', 'TranscriptProcessor'] 