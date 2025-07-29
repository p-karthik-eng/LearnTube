import { NextResponse } from 'next/server';
import { spawn } from 'child_process';

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
    const { url, prompt } = body;
    if (!url) {
      return NextResponse.json({ error: 'Missing YouTube URL' }, { status: 400 });
    }

    console.log(`🎯 Processing learning content generation for: ${url}`);

    // 1. Extract transcript using the existing Python script
    let transcriptResult;
    try {
      console.log(`📝 Extracting transcript...`);
      transcriptResult = await runPythonScript('scripts/get_youtube_transcript.py', [url]);
    } catch (err) {
      console.error(`❌ Transcript extraction failed: ${err.message}`);
      return NextResponse.json({ error: 'Transcript extraction failed', details: err.message }, { status: 500 });
    }

    if (!transcriptResult || !transcriptResult.text) {
      console.error(`❌ No transcript text found in result`);
      return NextResponse.json({ error: 'Transcript extraction returned no text', details: transcriptResult }, { status: 500 });
    }

    console.log(`✅ Transcript extracted successfully (${transcriptResult.text.length} characters)`);

    // Prepare transcript JSON for LLM script
    const transcriptJson = JSON.stringify({ content: transcriptResult.text });

    // 2. Generate learning content using the LLM Python entry script
    let llmResult;
    try {
      console.log(`🤖 Generating learning content...`);
      const llmArgs = prompt ? ['--prompt', prompt] : [];
      llmResult = await runPythonScript('scripts/generate_learning_content.py', llmArgs, transcriptJson);
    } catch (err) {
      console.error(`❌ Learning content generation failed: ${err.message}`);
      return NextResponse.json({ error: 'Learning content generation failed', details: err.message }, { status: 500 });
    }

    console.log(`✅ Learning content generated successfully`);

    // 3. Return the final JSON response
    return NextResponse.json({
      success: true,
      data: llmResult,
      meta: {
        transcriptSource: transcriptResult.source,
        transcriptLanguage: transcriptResult.language,
        isTranscriptGenerated: transcriptResult.is_generated,
        transcriptLength: transcriptResult.text.length,
        courseInfo: llmResult.courseInfo
      }
    });
  } catch (err) {
    console.error(`❌ Internal server error: ${err.message}`);
    return NextResponse.json({ error: 'Internal server error', details: err.message }, { status: 500 });
  }
}

export async function GET() {
  return NextResponse.json({ 
    error: 'Method not allowed. Use POST instead.',
    usage: {
      method: 'POST',
      body: { 
        url: 'https://youtube.com/watch?v=VIDEO_ID', 
        prompt: 'Optional custom prompt for course generation' 
      }
    }
  }, { status: 405 });
} 