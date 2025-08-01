import { NextResponse } from 'next/server';
import { spawn } from 'child_process';
import fetch from 'node-fetch';

// Helper to run a Python script and return its output as JSON
async function runPythonScript(scriptPath, args = [], input = null) {
  return new Promise((resolve, reject) => {
    const py = spawn('python', [scriptPath, ...args]);
    let output = '';
    let error = '';

    if (input) {
      py.stdin.write(input);
      py.stdin.end();
    }

    py.stdout.on('data', (data) => {
      output += data.toString();
    });
    py.stderr.on('data', (data) => {
      error += data.toString();
    });
    py.on('close', (code) => {
      if (code === 0 && output.trim().length > 0) {
        try {
          resolve(JSON.parse(output.trim()));
        } catch (e) {
          reject(new Error('Failed to parse Python output as JSON: ' + e.message));
        }
      } else {
        reject(new Error(error || 'Python script failed'));
      }
    });
  });
}

export async function POST(req) {
  try {
    const body = await req.json();
    const { url } = body;
    if (!url) {
      return NextResponse.json({ error: 'Missing YouTube URL' }, { status: 400 });
    }

    // Extract videoId from URL
    const videoId = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)/)?.[1];
    if (!videoId) {
      return NextResponse.json({ error: 'Invalid YouTube URL' }, { status: 400 });
    }

    // 1. Extract transcript using the existing Python script
    let transcriptResult;
    try {
      transcriptResult = await runPythonScript('scripts/get_youtube_transcript.py', [url]);
    } catch (err) {
      return NextResponse.json({ error: 'Transcript extraction failed', details: err.message }, { status: 500 });
    }

    if (!transcriptResult || !transcriptResult.text) {
      return NextResponse.json({ error: 'Transcript extraction returned no text', details: transcriptResult }, { status: 500 });
    }

    // 2. Send transcript to Python FastAPI server for course generation
    let pythonApiResponse;
    try {
      const response = await fetch('http://localhost:8000/generate-course', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: transcriptResult.text })
      });
      pythonApiResponse = await response.json();
    } catch (err) {
      return NextResponse.json({ error: 'Failed to contact Python FastAPI server', details: err.message }, { status: 500 });
    }

    // 3. Validate and return the Python server's response
    if (!pythonApiResponse.success) {
      return NextResponse.json({ 
        error: pythonApiResponse.error || 'Course generation failed' 
      }, { status: 500 });
    }

    // Return the successful response without database storage
    return NextResponse.json({
      success: true,
      course_data: pythonApiResponse.course_data,
      processing_stats: pythonApiResponse.processing_stats,
      video_id: videoId,
      transcript_length: transcriptResult.text.length
    });
  } catch (err) {
    return NextResponse.json({ error: 'Internal server error', details: err.message }, { status: 500 });
  }
}

export async function GET() {
  return NextResponse.json({ 
    error: 'Method not allowed. Use POST instead.',
    usage: {
      method: 'POST',
      body: { 
        url: 'https://youtube.com/watch?v=VIDEO_ID'
      }
    }
  }, { status: 405 });
} 