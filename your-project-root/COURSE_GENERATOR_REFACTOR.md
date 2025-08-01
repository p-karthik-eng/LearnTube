# Course Generator Refactor: Analysis-to-Course Conversion

## Problem Statement

The original course generator was returning analysis data instead of the structured course format needed for the learning platform. The response contained static topics, concepts, and quiz questions but lacked the modular lesson structure with timestamps, sections, and proper quiz formatting.

## Solution: Two-Step Generation Process

### Step 1: Analysis Generation
The system now first generates analysis data from DeepSeek AI with this structure:

```json
{
  "analysis": {
    "main_topics": ["Topic 1", "Topic 2", "Topic 3"],
    "key_concepts": ["Concept 1", "Concept 2", "Concept 3"],
    "examples_demonstrations": ["Example 1", "Example 2", "Example 3"],
    "potential_quiz_questions": ["Question 1", "Question 2", "Question 3"],
    "learning_objectives": ["Objective 1", "Objective 2", "Objective 3"]
  }
}
```

### Step 2: Course Structure Conversion
The analysis data is then programmatically converted to the required course format:

```json
{
  "courseInfo": {
    "title": "Course Title",
    "subtitle": "Brief subtitle or tagline",
    "duration": "Total duration (e.g. '3h 12min')",
    "totalLessons": 5
  },
  "videoSource": {
    "url": "https://your-long-video-url.com"
  },
  "lessons": [
    {
      "id": 1,
      "title": "Lesson 1 Title",
      "subtitle": "Short description of this topic",
      "type": "video",
      "videoMeta": {
        "start": "00:00:00",
        "end": "00:10:30"
      },
      "completed": false,
      "current": false,
      "content": {
        "introduction": "Brief introduction to the lesson.",
        "sections": [
          {
            "title": "Section Title",
            "type": "concept | example | advanced",
            "points": [
              {
                "subtitle": "Sub Point Title",
                "content": "Explanation of this concept or subtopic."
              }
            ]
          }
        ],
        "conclusion": "What the learner should take away from this lesson."
      },
      "quizzes": [
        {
          "id": 1,
          "question": "Question text here",
          "type": "multiple_choice | text",
          "options": ["Option A", "Option B", "Option C", "Option D"],
          "correctAnswer": 0,
          "answer": "Correct answer text",
          "explanation": "Why this answer is correct"
        }
      ]
    }
  ]
}
```

## Key Features

### Dynamic Lesson Generation
- **Main Topics → Lessons**: Each main topic becomes a lesson with proper timestamps
- **Related Content Mapping**: Key concepts and examples are mapped to relevant lessons
- **Minimum Lesson Count**: Ensures at least 3 lessons are generated
- **Timestamp Calculation**: 15-minute intervals per lesson (00:00:00, 00:15:00, etc.)

### Content Organization
- **Concept Sections**: Key explanations and definitions
- **Example Sections**: Code demonstrations and real-world examples
- **Advanced Sections**: Edge cases and deeper understanding topics

### Quiz Generation
- **Topic-Based Questions**: Questions are matched to relevant lessons
- **Multiple Choice Format**: Standard 4-option format with explanations
- **Fallback Questions**: Generic questions when specific ones aren't available
- **2-3 Quizzes Per Lesson**: Balanced assessment coverage

### Smart Content Mapping
- **Keyword Matching**: Finds related concepts and examples for each topic
- **Content Limiting**: Prevents information overload (max 3 concepts, 2 examples per section)
- **Truncation Handling**: Long content is properly truncated with ellipsis

## Implementation Details

### Core Methods

1. **`_convert_analysis_to_course()`**: Main conversion logic
2. **`_create_lesson_from_topic()`**: Creates lessons from main topics
3. **`_create_lesson_from_concept()`**: Creates lessons from key concepts (fallback)
4. **`_generate_lesson_quizzes()`**: Generates quizzes for each lesson
5. **`_find_related_content()`**: Maps related content to lessons

### Error Handling
- **Fallback Course**: Basic structure when AI generation fails
- **Validation**: Ensures proper course structure before returning
- **Graceful Degradation**: Handles missing or incomplete analysis data

### Performance Optimizations
- **Token Counting**: Determines processing approach (direct vs chunked)
- **Content Deduplication**: Removes duplicate content while preserving order
- **Efficient Mapping**: Smart content matching reduces processing time

## Testing

### Test Scripts
1. **`test_course_generator.py`**: Tests the conversion logic with sample data
2. **`test_new_generator.py`**: End-to-end testing with real transcript
3. **Validation**: Ensures all required fields are present

### Validation Checks
- Required course fields (courseInfo, videoSource, lessons, finalExam)
- Lesson structure validation (id, title, videoMeta, content, quizzes)
- Content section validation (introduction, sections, conclusion)
- Quiz structure validation (question, options, correctAnswer, explanation)

## Usage

### Running the Tests
```bash
# Test the conversion logic
python test_course_generator.py

# Test end-to-end generation
python test_new_generator.py

# Start the FastAPI server
python run_test_server.py
```

### API Endpoint
```bash
POST http://localhost:8000/generate-course
Content-Type: application/json

{
  "content": "Your transcript content here..."
}
```

## Benefits

1. **Consistent Structure**: Always returns the expected course format
2. **Scalable**: Handles both short and long transcripts
3. **Maintainable**: Clear separation between analysis and conversion
4. **Reliable**: Fallback mechanisms ensure service availability
5. **Flexible**: Easy to modify content mapping and quiz generation logic

## Future Enhancements

1. **Better Quiz Generation**: Use AI to generate more specific quiz options and answers
2. **Advanced Content Mapping**: Use semantic similarity for better content matching
3. **Dynamic Timestamps**: Calculate timestamps based on actual content length
4. **Multi-language Support**: Extend to support multiple languages
5. **Content Enrichment**: Add additional metadata like difficulty levels and prerequisites 