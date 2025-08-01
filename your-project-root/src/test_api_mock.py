from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import time
from pathlib import Path
import sys

# Add the src directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

app = FastAPI(title="YouTube Course Generator Mock API", version="1.0.0")

# Enable CORS for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TranscriptInput(BaseModel):
    content: str

class CourseResponse(BaseModel):
    success: bool
    course_data: dict = None
    error: str = None
    processing_stats: dict = None

def generate_mock_course(transcript_content: str) -> dict:
    """Generate a mock course structure for testing"""
    return {
        "courseInfo": {
            "title": "Sample Course Generated from Transcript",
            "description": "This is a sample course generated from the provided transcript content.",
            "totalLessons": 3,
            "estimatedDuration": "45 minutes",
            "difficulty": "Beginner"
        },
        "lessons": [
            {
                "id": "lesson-1",
                "title": "Introduction to the Topic",
                "content": f"Based on the transcript: {transcript_content[:200]}...",
                "duration": "15 minutes",
                "timestamp": "0:00",
                "quizzes": [
                    {
                        "question": "What is the main topic of this lesson?",
                        "options": [
                            "Advanced concepts",
                            "Basic introduction",
                            "Complex theories",
                            "None of the above"
                        ],
                        "correctAnswer": "Basic introduction",
                        "explanation": "This lesson covers the basic introduction to the topic."
                    }
                ]
            },
            {
                "id": "lesson-2",
                "title": "Core Concepts",
                "content": "This lesson covers the core concepts and fundamental principles discussed in the transcript.",
                "duration": "20 minutes",
                "timestamp": "15:00",
                "quizzes": [
                    {
                        "question": "Which of the following is a core concept?",
                        "options": [
                            "Advanced techniques",
                            "Basic principles",
                            "Complex algorithms",
                            "All of the above"
                        ],
                        "correctAnswer": "Basic principles",
                        "explanation": "Core concepts typically refer to basic principles."
                    }
                ]
            },
            {
                "id": "lesson-3",
                "title": "Practical Applications",
                "content": "This lesson focuses on practical applications and real-world examples from the transcript.",
                "duration": "10 minutes",
                "timestamp": "35:00",
                "quizzes": [
                    {
                        "question": "What is the focus of practical applications?",
                        "options": [
                            "Theoretical concepts",
                            "Real-world examples",
                            "Complex calculations",
                            "None of the above"
                        ],
                        "correctAnswer": "Real-world examples",
                        "explanation": "Practical applications focus on real-world examples."
                    }
                ]
            }
        ],
        "finalExam": [
            {
                "question": "What is the primary goal of this course?",
                "options": [
                    "To confuse students",
                    "To provide comprehensive learning",
                    "To make things complex",
                    "None of the above"
                ],
                "correctAnswer": "To provide comprehensive learning",
                "explanation": "The primary goal is to provide comprehensive learning."
            },
            {
                "question": "How many lessons are in this course?",
                "options": [
                    "1 lesson",
                    "2 lessons",
                    "3 lessons",
                    "4 lessons"
                ],
                "correctAnswer": "3 lessons",
                "explanation": "This course contains 3 lessons as specified in the course info."
            }
        ]
    }

@app.post("/generate-course", response_model=CourseResponse)
async def generate_course_from_transcript(transcript: TranscriptInput):
    """
    Mock endpoint: Generate sample course structure for testing
    """
    try:
        # Input validation
        if not transcript.content or len(transcript.content.strip()) < 10:
            raise HTTPException(status_code=400, detail="Transcript content too short")
        
        # Simulate processing time
        start_time = time.time()
        time.sleep(1)  # Simulate processing delay
        processing_time = time.time() - start_time
        
        # Generate mock course data
        course_data = generate_mock_course(transcript.content)
        
        # Processing statistics
        stats = {
            "processing_time_seconds": round(processing_time, 2),
            "input_tokens": len(transcript.content.split()),
            "output_size_kb": round(len(json.dumps(course_data)) / 1024, 2),
            "lessons_generated": len(course_data.get("lessons", [])),
            "total_quizzes": sum(len(lesson.get("quizzes", [])) for lesson in course_data.get("lessons", []))
        }
        
        return CourseResponse(
            success=True,
            course_data=course_data,
            processing_stats=stats
        )
    except Exception as e:
        return CourseResponse(
            success=False,
            error=str(e)
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Course Generator Mock API"}

@app.post("/test-deepseek")
async def test_deepseek_connection():
    """Mock test endpoint"""
    return {"success": True, "response": "Mock API - No real connection needed", "provider": "Mock"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Mock Course Generator API on http://localhost:8000")
    print("📝 This is a mock version for testing - no API key required")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)