import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
import json
import argparse
import asyncio
import os
from llm_core.course_generator import CourseGenerator
from llm_core.deepseek_client import DeepSeekClient
from llm_core.transcript_processor import TranscriptProcessor

def main():
    parser = argparse.ArgumentParser(description="Generate structured learning content from a transcript and prompt.")
    parser.add_argument('--prompt', type=str, default=None, help='Custom prompt for the LLM (optional)')
    args = parser.parse_args()

    try:
        # Read transcript JSON from stdin
        transcript_json = json.load(sys.stdin)
    except Exception as e:
        print(json.dumps({"error": f"Failed to read transcript JSON from stdin: {str(e)}"}), file=sys.stderr)
        sys.exit(1)

    # Initialize services
    try:
        processor = TranscriptProcessor()
        client = DeepSeekClient()
        generator = CourseGenerator(client, processor)
    except Exception as e:
        print(json.dumps({"error": f"Initialization error: {str(e)}"}), file=sys.stderr)
        sys.exit(1)

    # Enhance transcript quality
    try:
        enhanced = processor.enhance_transcript_quality(transcript_json)
    except Exception as e:
        print(json.dumps({"error": f"Transcript enhancement error: {str(e)}"}), file=sys.stderr)
        sys.exit(1)

    # Run async course generation
    async def run_generation():
        try:
            result = await generator.generate_complete_course(enhanced)
            print(json.dumps(result, ensure_ascii=False))
        except Exception as e:
            print(json.dumps({"error": f"Course generation error: {str(e)}"}), file=sys.stderr)
            sys.exit(1)

    asyncio.run(run_generation())

if __name__ == '__main__':
    main() 