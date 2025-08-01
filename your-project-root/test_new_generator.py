#!/usr/bin/env python3
"""
Simple test for the new course generator
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

async def test_new_generator():
    """Test the new course generator"""
    
    # Sample transcript content
    sample_transcript = """
    Welcome to this comprehensive Java programming tutorial. In this video, we'll cover inheritance in Java.
    Inheritance is a fundamental concept in object-oriented programming that allows classes to inherit attributes and methods from a parent class.
    
    Let's start with the basics. In Java, you use the 'extends' keyword to inherit from a superclass.
    For example, if you have a Dog class, you can create a Cat class that extends Dog.
    This means Cat will inherit all the properties and methods from Dog.
    
    Method overriding is another important concept. When a subclass provides a specific implementation for a method defined in the superclass, it's called method overriding.
    This allows you to customize behavior while maintaining the same interface.
    
    Constructors in inheritance are also crucial. When you create a subclass, you need to call the superclass constructor using the 'super' keyword.
    This ensures that the parent class is properly initialized before the child class.
    
    Static variables and methods belong to the class rather than instances.
    They can be accessed without creating an object of the class.
    This is useful for utility methods and shared data.
    
    Finally, let's talk about object comparison. You can override the 'equals' method to define how objects should be compared.
    You can also implement the 'Comparable' interface for custom comparison logic.
    """
    
    try:
        print("🧪 Testing new course generator...")
        
        # Initialize components
        processor = TranscriptProcessor()
        deepseek_client = DeepSeekClient(api_key=os.getenv("OPENROUTER_API_KEY"))
        course_generator = CourseGenerator(deepseek_client, processor)
        
        # Test the complete pipeline
        transcript_json = {"content": sample_transcript}
        course_data = await course_generator.generate_complete_course(transcript_json, "Java Programming Tutorial")
        
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
        with open('new_generated_course.json', 'w') as f:
            json.dump(course_data, f, indent=2)
        print("\n💾 Course saved to new_generated_course.json")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_new_generator()) 