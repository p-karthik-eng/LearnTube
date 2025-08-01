# Updates to Project Workflow and Codebase

## 1. Pipeline Integration
- Integrated a modular workflow where the Node.js backend extracts YouTube transcripts and sends them to a Python FastAPI backend for course generation.
- The Python backend processes the transcript, chunks it, and uses an LLM (DeepSeek via OpenRouter) to generate structured course content.

## 2. Prompt Engineering
- Designed world-class, explicit prompts for both chunk analysis and course synthesis, instructing the LLM to:
  - Structure content into major/minor timestamps
  - Generate dynamic quizzes (MCQ, fill-in-the-blanks, etc.)
  - Provide detailed, engaging, and accessible course content for any subject
- Prompts are now subject-agnostic and suitable for any educational video.

## 3. Chunking and Rate Limit Handling
- Increased chunk size to reduce the number of LLM requests per video.
- Switched from parallel to sequential chunk processing to avoid API rate limits.
- Added a long delay (up to 60 seconds) between each LLM request to further reduce rate limit errors.
- Provided guidance for further increasing delay or batching if needed.

## 4. Error Handling and Logging
- Improved logging for chunk content and prompt sent to the LLM.
- Added error handling for rate limits (429) and connection errors.
- Provided user guidance for handling OpenRouter rate limits and best practices for development/testing.

## 5. API and Output Improvements
- The FastAPI backend now accepts transcript content and returns a rich, structured JSON suitable for frontend consumption.
- The output JSON includes course info, lessons, timestamps, quizzes, and a final exam.

## 6. Revert and Flexibility
- Reverted the YouTube video title extraction feature; the backend now only uses transcript content for course generation.
- Maintained flexibility to switch between strict and generic prompt modes as needed.

---

**This updates.md summarizes all major changes and improvements made to the original folder and workflow.** 