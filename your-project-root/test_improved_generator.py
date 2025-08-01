#!/usr/bin/env python3
"""
Test script for the improved course generator with better content and quiz generation
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

async def test_improved_generator():
    """Test the improved course generator with better content"""
    
    # Sample transcript content for testing
    sample_transcript = """
    Welcome to this comprehensive Python programming tutorial. In this video, we'll cover object-oriented programming in Python.
    
    Object-oriented programming is a programming paradigm that uses objects to design applications and computer programs.
    In Python, everything is an object. When you create a variable, you're actually creating an instance of a class.
    
    Let's start with classes. A class is a blueprint for creating objects. It defines the attributes and methods that the objects will have.
    For example, if you want to create a Car class, you would define what properties a car has, like color, brand, and model.
    
    Methods are functions that belong to a class. They define the behavior of the objects. For instance, a Car class might have methods like start_engine(), stop_engine(), and drive().
    
    Inheritance is another important concept. It allows you to create a new class that inherits attributes and methods from an existing class.
    This promotes code reuse and establishes a relationship between classes. For example, you could create an ElectricCar class that inherits from the Car class.
    
    Polymorphism allows objects of different classes to be treated as objects of a common superclass. This means you can use the same method name for different classes.
    For example, both Car and ElectricCar might have a drive() method, but they implement it differently.
    
    Encapsulation is the bundling of data and methods that operate on that data within a single unit or object.
    It helps to hide the internal state of an object and only expose the necessary parts through a public interface.
    
    Let's look at a practical example. We'll create a simple class hierarchy for different types of vehicles.
    """
    
    try:
        print("🧪 Testing improved course generator...")
        
        # Initialize components
        processor = TranscriptProcessor()
        deepseek_client = DeepSeekClient(api_key=os.getenv("OPENROUTER_API_KEY"))
        course_generator = CourseGenerator(deepseek_client, processor)
        
        # Test the complete pipeline
        transcript_json = {"content": sample_transcript}
        course_data = await course_generator.generate_complete_course(transcript_json, "Python OOP Tutorial")
        
        print("✅ Course generation successful!")
        print(f"📚 Course Title: {course_data['courseInfo']['title']}")
        print(f"📖 Total Lessons: {course_data['courseInfo']['totalLessons']}")
        print(f"⏱️  Duration: {course_data['courseInfo']['duration']}")
        
        # Print lesson details with content analysis
        for lesson in course_data['lessons']:
            print(f"\n📝 Lesson {lesson['id']}: {lesson['title']}")
            print(f"   ⏰ Time: {lesson['videoMeta']['start']} - {lesson['videoMeta']['end']}")
            print(f"   📊 Sections: {len(lesson['content']['sections'])}")
            print(f"   ❓ Quizzes: {len(lesson['quizzes'])}")
            
            # Show content quality
            if lesson['content']['sections']:
                for section in lesson['content']['sections']:
                    print(f"   📋 Section: {section['title']} ({section['type']})")
                    print(f"   📝 Points: {len(section['points'])}")
                    for point in section['points']:
                        content_preview = point['content'][:100] + "..." if len(point['content']) > 100 else point['content']
                        print(f"      - {point['subtitle']}: {content_preview}")
            
            # Show quiz quality
            if lesson['quizzes']:
                for quiz in lesson['quizzes']:
                    print(f"   ❓ Quiz: {quiz['question'][:80]}...")
                    print(f"      Options: {len(quiz['options'])} realistic options")
                    print(f"      Answer: {quiz['answer']}")
                    print(f"      Explanation: {quiz['explanation'][:80]}...")
        
        # Save the generated course
        with open('improved_generated_course.json', 'w') as f:
            json.dump(course_data, f, indent=2)
        print("\n💾 Improved course saved to improved_generated_course.json")
        
        # Analyze content quality
        analyze_content_quality(course_data)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

def analyze_content_quality(course_data):
    """Analyze the quality of generated content"""
    print("\n🔍 Content Quality Analysis:")
    
    total_content_length = 0
    total_quiz_quality = 0
    lesson_count = len(course_data['lessons'])
    
    for lesson in course_data['lessons']:
        # Analyze content length
        content = lesson['content']
        intro_length = len(content['introduction'])
        conclusion_length = len(content['conclusion'])
        
        section_content = 0
        for section in content['sections']:
            for point in section['points']:
                section_content += len(point['content'])
        
        lesson_content = intro_length + conclusion_length + section_content
        total_content_length += lesson_content
        
        print(f"📝 Lesson '{lesson['title']}': {lesson_content} characters")
        
        # Analyze quiz quality
        quiz_quality = 0
        for quiz in lesson['quizzes']:
            # Check if options are realistic (not just "Option A, B, C, D")
            realistic_options = 0
            for option in quiz['options']:
                if not option.startswith('Option ') and len(option) > 5:
                    realistic_options += 1
            
            # Check if answer is meaningful
            answer_quality = len(quiz['answer']) > 10
            explanation_quality = len(quiz['explanation']) > 20
            
            quiz_quality += realistic_options + (2 if answer_quality else 0) + (2 if explanation_quality else 0)
        
        total_quiz_quality += quiz_quality
        print(f"   ❓ Quiz Quality Score: {quiz_quality}/12")
    
    avg_content_length = total_content_length / lesson_count if lesson_count > 0 else 0
    avg_quiz_quality = total_quiz_quality / lesson_count if lesson_count > 0 else 0
    
    print(f"\n📊 Summary:")
    print(f"   Average content length per lesson: {avg_content_length:.0f} characters")
    print(f"   Average quiz quality score: {avg_quiz_quality:.1f}/12")
    
    if avg_content_length > 500:
        print("   ✅ Content length is good")
    else:
        print("   ⚠️  Content length could be improved")
    
    if avg_quiz_quality > 8:
        print("   ✅ Quiz quality is excellent")
    elif avg_quiz_quality > 6:
        print("   ✅ Quiz quality is good")
    else:
        print("   ⚠️  Quiz quality needs improvement")

if __name__ == "__main__":
    asyncio.run(test_improved_generator()) 