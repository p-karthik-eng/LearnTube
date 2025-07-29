import json
import asyncio
from typing import Dict, List
from .transcript_processor import TranscriptProcessor
from .deepseek_client import DeepSeekClient
import sys

class CourseGenerator:
    def __init__(self, deepseek_client: DeepSeekClient, processor: TranscriptProcessor):
        self.client = deepseek_client
        self.processor = processor
    
    async def generate_complete_course(self, transcript_json: Dict) -> Dict:
        """
        Main method to generate complete course from transcript
        """
        content = transcript_json["content"]
        token_count = self.processor.count_tokens(content)
        
        if token_count <= 50000:  # Direct processing
            return await self._direct_course_generation(content)
        else:  # Micro-chunking approach
            return await self._chunked_course_generation(content)
    
    async def _direct_course_generation(self, content: str) -> Dict:
        """
        Generate course directly for shorter transcripts
        """
        prompt = f"""
        Transform this YouTube video transcript into a structured course format.
        
        Create a comprehensive course with:
        1. Course title and subtitle based on the content
        2. Multiple hierarchical lessons with realistic timestamps
        3. Detailed content sections per lesson
        4. Multiple assessment questions for each lesson
        5. Final exam structure
        
        Return valid JSON matching this exact structure:
        {{
          "courseInfo": {{
            "title": "Descriptive Course Title Based on Content",
            "subtitle": "Brief subtitle describing what students will learn",
            "duration": "Estimated total duration",
            "totalLessons": 3
          }},
          "videoSource": {{
            "url": "original_video_url"
          }},
          "lessons": [
            {{
              "id": 1,
              "title": "Lesson 1 Title Based on Content",
              "subtitle": "What this lesson covers",
              "type": "video",
              "videoMeta": {{
                "start": "00:00:00",
                "end": "00:25:00"
              }},
              "completed": False,
              "current": False,
              "content": {{
                "introduction": "Introduction to this lesson topic",
                "sections": [
                  {{
                    "title": "Section Title from Content",
                    "type": "concept",
                    "points": [
                      {{
                        "subtitle": "Key Point Title",
                        "content": "Detailed explanation of the concept"
                      }}
                    ]
                  }}
                ],
                "conclusion": "Key takeaways from this lesson"
              }},
              "quizzes": [
                {{
                  "id": 1,
                  "question": "Relevant question based on lesson content",
                  "type": "multiple_choice",
                  "options": ["Option A", "Option B", "Option C", "Option D"],
                  "correctAnswer": 0,
                  "answer": "Correct answer",
                  "explanation": "Why this answer is correct based on the lesson"
                }}
              ]
            }}
          ],
          "finalExam": {{
            "enabled": True,
            "prerequisiteCompletion": 100,
            "timeLimit": "2h 30min",
            "questionCount": 5,
            "passingScore": 70,
            "examType": "application_based"
          }}
        }}
        
        Transcript: {content}
        """
        
        try:
            print(f" DEBUG: Sending request to DeepSeek...", file=sys.stderr)
            response = await self.client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=8000,
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            print(f" DEBUG: DeepSeek response received", file=sys.stderr)
            course_data = json.loads(response)
            print(f" DEBUG: JSON parsing successful", file=sys.stderr)
            return course_data
            
        except Exception as e:
            print(f" DEBUG: Error in course generation: {str(e)}", file=sys.stderr)
            # Fallback simple course structure
            return self._create_fallback_course(content)
    
    async def _chunked_course_generation(self, content: str) -> Dict:
        """
        Generate course using micro-chunking for long transcripts
        """
        chunks = self.processor.create_semantic_micro_chunks(content)
        
        # Process chunks in parallel
        chunk_analyses = []
        batch_size = 5
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            batch_results = await asyncio.gather(*[
                self._analyze_chunk(chunk, i+j+1, len(chunks))
                for j, chunk in enumerate(batch)
            ])
            chunk_analyses.extend(batch_results)
            await asyncio.sleep(0.5)  # Rate limiting
        
        # Synthesize final course
        return await self._synthesize_course_from_chunks(chunk_analyses)
    
    async def _analyze_chunk(self, chunk: str, chunk_num: int, total_chunks: int) -> Dict:
        """
        Analyze individual chunk for content extraction
        """
        prompt = f"""
        Analyze this segment ({chunk_num}/{total_chunks}) of an educational video transcript.
        
        Extract and return JSON with:
        - Main topics covered
        - Key concepts explained
        - Examples or demonstrations
        - Potential quiz questions
        - Learning objectives
        
        Segment: {chunk}
        """
        
        try:
            response = await self.client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            return {
                "chunk_number": chunk_num,
                "analysis": json.loads(response),
                "original_text": chunk
            }
        except Exception:
            return {
                "chunk_number": chunk_num,
                "analysis": {"topics": ["Content analysis unavailable"]},
                "original_text": chunk
            }
    
    async def _synthesize_course_from_chunks(self, chunk_analyses: List[Dict]) -> Dict:
        """
        Combine chunk analyses into final course structure
        """
        combined_analysis = {
            "total_chunks": len(chunk_analyses),
            "analyses": [chunk["analysis"] for chunk in chunk_analyses]
        }
        
        prompt = f"""
        Create a comprehensive course structure from these analyzed transcript segments.
        
        Generate complete JSON course structure with multiple lessons, detailed content, and assessments.
        
        Analyzed segments: {json.dumps(combined_analysis, indent=2)}
        """
        
        try:
            response = await self.client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=8000,
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response)
        except Exception as e:
            print(f" DEBUG: Error in course synthesis: {str(e)}", file=sys.stderr)
            return self._create_fallback_course("Synthesized content")
    
    def _create_fallback_course(self, content: str) -> Dict:
        """
        Create a simple fallback course structure
        """
        return {
            "courseInfo": {
                "title": "Course from Video Content",
                "subtitle": "Learning material extracted from video",
                "duration": "Variable",
                "totalLessons": 1
            },
            "videoSource": {
                "url": "original_video_url"
            },
            "lessons": [
                {
                    "id": 1,
                    "title": "Main Content",
                    "subtitle": "Key concepts from the video",
                    "type": "video",
                    "videoMeta": {
                        "start": "00:00:00",
                        "end": "00:00:00"
                    },
                    "completed": False,
                    "current": False,
                    "content": {
                        "introduction": "Content from the video transcript",
                        "sections": [
                            {
                                "title": "Main Points",
                                "type": "concept",
                                "points": [
                                    {
                                        "subtitle": "Key Content",
                                        "content": content[:500] + "..." if len(content) > 500 else content
                                    }
                                ]
                            }
                        ],
                        "conclusion": "Summary of the video content"
                    },
                    "quizzes": [
                        {
                            "id": 1,
                            "question": "What did you learn from this video?",
                            "type": "text",
                            "options": [],
                            "correctAnswer": 0,
                            "answer": "Open-ended question",
                            "explanation": "Reflect on the key points from the video"
                        }
                    ]
                }
            ],
            "finalExam": {
                "enabled": False,
                "prerequisiteCompletion": 100,
                "timeLimit": "30min",
                "questionCount": 1,
                "passingScore": 70,
                "examType": "reflection"
            }
        } 