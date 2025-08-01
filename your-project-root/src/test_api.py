from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# Add the src directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Now import your modules
from core.transcript_processor import TranscriptProcessor
from core.deepseek_client import DeepSeekClient
from core.course_generator import CourseGenerator

load_dotenv()

app = FastAPI(title="YouTube Course Generator Test API", version="1.0.0")

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

# Initialize components
processor = TranscriptProcessor()
deepseek_client = DeepSeekClient(api_key=os.getenv("OPENROUTER_API_KEY"))
course_generator = CourseGenerator(deepseek_client, processor)

@app.post("/generate-course", response_model=CourseResponse)
async def generate_course_from_transcript(transcript: TranscriptInput):
    """
    Test endpoint: Convert transcript JSON to complete course structure
    """
    try:
        # Input validation
        transcript_json = {"content": transcript.content}
        if not processor.validate_transcript(transcript_json):
            raise HTTPException(status_code=400, detail="Invalid transcript content")
        
        # Process through your complete pipeline
        start_time = time.time()
        course_data = await course_generator.generate_complete_course(transcript_json)
        processing_time = time.time() - start_time
        
        # Processing statistics
        stats = {
            "processing_time_seconds": round(processing_time, 2),
            "input_tokens": processor.count_tokens(transcript.content),
            "output_size_kb": round(len(json.dumps(course_data)) / 1024, 2),
            "lessons_generated": len(course_data.get("lessons", [])),
            "total_quizzes": sum(len(lesson.get("quizzes", [])) for lesson in course_data.get("lessons", []))
        }
        
        # Validate that we have actual course structure, not just analysis
        if "courseInfo" not in course_data or "lessons" not in course_data:
            return CourseResponse(
                success=False,
                error="Generated data is not in proper course format"
            )
        
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
    return {"status": "healthy", "service": "Course Generator API"}

@app.post("/test-deepseek")
async def test_deepseek_connection():
    """Test OpenRouter DeepSeek connection"""
    try:
        test_prompt = "Respond with just 'Connection successful' if you can read this."
        response = await deepseek_client.chat_completion(
            messages=[{"role": "user", "content": test_prompt}],
            max_tokens=50
        )
        return {"success": True, "response": response, "provider": "OpenRouter"}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
