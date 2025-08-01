import sys
import os
from pathlib import Path
import uvicorn
from dotenv import load_dotenv

# Add the project root to Python path
project_root = Path(__file__).parent / "src"
sys.path.insert(0, str(project_root))

load_dotenv()

if __name__ == "__main__":
    # Verify environment variables
    if not os.getenv("OPENROUTER_API_KEY"):
        print("❌ OPENROUTER_API_KEY not found in environment variables")
        exit(1)
    
    print("🚀 Starting Course Generator Test API...")
    print("📝 API Documentation: http://localhost:8000/docs")
    print("🔗 Health Check: http://localhost:8000/health")
    
    uvicorn.run(
        "test_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
