#!/usr/bin/env python3
"""
Test script for the new course generator that converts analysis to structured course format
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the src directory to Python path
project_root = Path(__file__).parent / "src"
sys.path.insert(0, str(project_root))

from core.transcript_processor import TranscriptProcessor
from core.deepseek_client import DeepSeekClient
from core.course_generator import CourseGenerator

load_dotenv()

async def test_course_generation():
    """Test the new course generation with analysis conversion"""
    
    # Sample analysis data (similar to what DeepSeek returns)
    sample_analysis = {
        "analysis": {
            "main_topics": [
                "Inheritance in Java",
                "Method overriding", 
                "Constructors in inheritance",
                "Class variables (static variables)",
                "Static methods"
            ],
            "key_concepts": [
                "Inheritance allows classes to inherit attributes and methods from a parent class (superclass).",
                "Method overriding enables subclasses to provide specific implementations for methods defined in the superclass.",
                "Using 'super' keyword to call the superclass constructor.",
                "Static variables and methods belong to the class rather than instances.",
                "Comparing objects using 'equals' method and implementing 'Comparable' for custom comparisons."
            ],
            "examples_demonstrations": [
                "Creating a Cat class that inherits from Dog and overrides the 'speak' method.",
                "Using 'super' in the Cat constructor to initialize inherited attributes.",
                "Adding a 'food' attribute to the Cat class as an example of extending a subclass.",
                "Demonstrating static variables with a 'count' in Dog class to track instances.",
                "Implementing 'equals' and 'compareTo' methods in a Student class for object comparison."
            ],
            "potential_quiz_questions": [
                "What keyword is used to inherit from a superclass in Java?",
                "How do you call a superclass constructor from a subclass?",
                "What is the difference between static and instance variables?",
                "Why would you override the 'equals' method in a class?",
                "What is the purpose of the 'toString' method?"
            ],
            "learning_objectives": [
                "Understand and apply inheritance to create subclasses.",
                "Override methods to provide subclass-specific implementations.",
                "Use 'super' to access superclass constructors and methods.",
                "Differentiate between static and instance members and their use cases.",
                "Implement object comparison using 'equals' and 'Comparable'."
            ]
        }
    }
    
    try:
        print("🧪 Testing course generation with analysis conversion...")
        
        # Initialize components
        processor = TranscriptProcessor()
        deepseek_client = DeepSeekClient(api_key=os.getenv("OPENROUTER_API_KEY"))
        course_generator = CourseGenerator(deepseek_client, processor)
        
        # Test the conversion method directly
        course_data = course_generator._convert_analysis_to_course(
            sample_analysis, 
            "Java Programming Tutorial", 
            "Sample transcript content"
        )
        
        print("✅ Course generation successful!")
        print(f"📚 Course Title: {course_data['courseInfo']['title']}")
        print(f"📖 Total Lessons: {course_data['courseInfo']['totalLessons']}")
        print(f"⏱️  Duration: {course_data['courseInfo']['duration']}")
        
        # Print lesson details
        for lesson in course_data['lessons']:
            print(f"\n📝 Lesson {lesson['id']}: {lesson['title']}")
            print(f"   ⏰ Time: {lesson['videoMeta']['start']} - {lesson['videoMeta']['end']}")
            print(f"   📊 Sections: {len(lesson['content']['sections'])}")
            print(f"   ❓ Quizzes: {len(lesson['quizzes'])}")
        
        # Save the generated course
        with open('test_generated_course.json', 'w') as f:
            json.dump(course_data, f, indent=2)
        print("\n💾 Test course saved to test_generated_course.json")
        
        # Validate the structure
        validate_course_structure(course_data)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

def validate_course_structure(course_data):
    """Validate that the course structure matches the expected format"""
    print("\n🔍 Validating course structure...")
    
    required_fields = ['courseInfo', 'videoSource', 'lessons', 'finalExam']
    for field in required_fields:
        if field not in course_data:
            print(f"❌ Missing required field: {field}")
            return False
    
    # Validate courseInfo
    course_info = course_data['courseInfo']
    required_course_fields = ['title', 'subtitle', 'duration', 'totalLessons']
    for field in required_course_fields:
        if field not in course_info:
            print(f"❌ Missing courseInfo field: {field}")
            return False
    
    # Validate lessons
    lessons = course_data['lessons']
    if not lessons:
        print("❌ No lessons generated")
        return False
    
    for i, lesson in enumerate(lessons):
        required_lesson_fields = ['id', 'title', 'subtitle', 'type', 'videoMeta', 'completed', 'current', 'content', 'quizzes']
        for field in required_lesson_fields:
            if field not in lesson:
                print(f"❌ Missing lesson field in lesson {i+1}: {field}")
                return False
        
        # Validate lesson content
        content = lesson['content']
        required_content_fields = ['introduction', 'sections', 'conclusion']
        for field in required_content_fields:
            if field not in content:
                print(f"❌ Missing content field in lesson {i+1}: {field}")
                return False
        
        # Validate sections
        sections = content['sections']
        if not sections:
            print(f"⚠️  No sections in lesson {i+1}")
        
        for section in sections:
            required_section_fields = ['title', 'type', 'points']
            for field in required_section_fields:
                if field not in section:
                    print(f"❌ Missing section field in lesson {i+1}: {field}")
                    return False
        
        # Validate quizzes
        quizzes = lesson['quizzes']
        if not quizzes:
            print(f"⚠️  No quizzes in lesson {i+1}")
        
        for quiz in quizzes:
            required_quiz_fields = ['id', 'question', 'type', 'options', 'correctAnswer', 'answer', 'explanation']
            for field in required_quiz_fields:
                if field not in quiz:
                    print(f"❌ Missing quiz field in lesson {i+1}: {field}")
                    return False
    
    print("✅ Course structure validation passed!")
    return True

if __name__ == "__main__":
    asyncio.run(test_course_generation()) 