import dbConnect from '../../../lib/mongodb.js';
import AdminData from '../../../models/AdminData.js';
import { fetchTimedText } from '../../../utils/ytTimedText.js';
import { ProxyTranscriptFetcher } from '../../../utils/proxy-transcript.js';
import { validateGenerateBody, methodOnly } from '../../../utils/validation.js';
import { normaliseYouTubeUrl } from '../../../utils/youtube.js';

export async function POST(req) {
  let videoId, url, language;
  try {
    methodOnly('POST');
    const body = await req.json();
    ({ url, videoId, language } = validateGenerateBody(body));

    console.log(`🎯 Processing transcript request for: ${videoId}`);

    await dbConnect();
    const cached = await AdminData.findOne({ videoId, language });
    if (cached) {
      console.log(`✅ Cache hit for: ${videoId}`);
      return Response.json({ success: true, cached: true, data: cached });
    }

    console.log(`🔄 Cache miss, fetching transcript for: ${videoId}`);

    let transcript;
    let extractionMethod = 'direct';

    // Strategy 1: Direct YouTube API
    try {
      transcript = await fetchTimedText(videoId, language);
      extractionMethod = 'direct-api';
    } catch (directError) {
      console.log(`❌ Direct API failed: ${directError.message}`);
      
      // Strategy 2: Proxy-based fetch (for Indian IPs)
      try {
        console.log(`🌐 Attempting proxy-based extraction...`);
        const proxyFetcher = new ProxyTranscriptFetcher();
        transcript = await proxyFetcher.fetchWithProxy(videoId, language);
        extractionMethod = 'proxy-api';
      } catch (proxyError) {
        console.log(`❌ Proxy fetch failed: ${proxyError.message}`);
        
        // Strategy 3: Return detailed error for user
        throw new Error(`Transcript extraction failed: ${directError.message}. This video may not have accessible captions or may be region-restricted from India.`);
      }
    }

    if (!transcript || !transcript.cleanText || transcript.cleanText.length < 10) {
      throw new Error('Retrieved transcript is empty or too short');
    }

    console.log(`✅ Transcript extracted using ${extractionMethod}: ${transcript.cleanText.length} characters`);

    const record = await AdminData.create({
      videoId,
      language,
      url: normaliseYouTubeUrl(url),
      transcript,
      extractionMethod,
      fetchedAt: new Date()
    });

    return Response.json({ 
      success: true, 
      cached: false, 
      data: record,
      meta: {
        extractionMethod,
        transcriptLength: transcript.cleanText.length,
        processingTime: Date.now() - Date.now() // Placeholder
      }
    });

  } catch (err) {
    console.error(`❌ Error processing ${videoId}:`, err.message);
    // --- PYTHON FALLBACK ---
    try {
      console.log(`🐍 Attempting Python fallback for: ${videoId}`);
      const { spawn } = await import('child_process');
      const py = spawn('C:\\Users\\karth\\AppData\\Local\\Programs\\Python\\Python311\\python.exe', ['scripts/get_youtube_transcript.py', url]);
      let output = '';
      let error = '';
      for await (const data of py.stdout) {
        output += data.toString();
      }
      for await (const data of py.stderr) {
        error += data.toString();
      }
      const code = await new Promise((resolve) => py.on('close', resolve));
      if (code === 0 && output.trim().length > 0) {
        console.log(`🐍 Python output length: ${output.length} characters`);
        console.log(`🐍 Python output preview: ${output.substring(0, 200)}...`);
        
        // First, try to parse the entire output as JSON (in case it's pretty-printed)
        let parsed = null;
        try {
          parsed = JSON.parse(output.trim());
          console.log(`✅ Successfully parsed entire output as JSON`);
        } catch (e) {
          console.log(`⚠️ Failed to parse entire output, trying line-by-line...`);
          // If that fails, try line-by-line parsing
          const lines = output.split('\n');
          for (const line of lines) {
            try {
              parsed = JSON.parse(line);
              console.log(`✅ Successfully parsed line as JSON`);
              break; // Found valid JSON, stop searching
            } catch (e) {
              // Not JSON, continue to next line
            }
          }
        }
        
        if (parsed) {
          console.log(`✅ Python script returned data:`, { 
            hasError: !!parsed.error, 
            hasText: !!parsed.text, 
            source: parsed.source,
            textLength: parsed.text?.length || 0
          });
          
          // Check if it's an error response from Python
          if (parsed.error) {
            return Response.json({
              success: false,
              error: parsed.error,
              videoId,
              language,
              url
            }, { status: 500 });
          }
          
          // Convert Python output format to match expected Node.js format
          const transcriptData = {
            cleanText: parsed.text || '',
            source: parsed.source || 'python-fallback',
            language: parsed.language || language,
            isGenerated: parsed.is_generated || false,
            rawData: parsed.transcript || []
          };
          
          // Create a record similar to the successful case
          const record = {
            videoId,
            language,
            url: normaliseYouTubeUrl(url),
            transcript: transcriptData,
            extractionMethod: 'python-fallback',
            fetchedAt: new Date()
          };
          
          return Response.json({
            success: true,
            cached: false,
            data: record,
            meta: {
              extractionMethod: 'python-fallback',
              transcriptLength: transcriptData.cleanText.length,
              source: parsed.source
            }
          });
        } else {
          return Response.json({
            success: false,
            error: 'Failed to parse Python output as JSON',
            raw: output.substring(0, 500) + '...', // Truncate for readability
            videoId,
            language,
            url
          }, { status: 500 });
        }
      } else {
        throw new Error(error || 'Python transcript extraction failed');
      }
    } catch (pythonError) {
      // Final error response
      return Response.json({
        success: false,
        error: pythonError.message,
        videoId,
        suggestion: 'All transcript extraction methods failed. Try a different video.'
      }, { status: 500 });
    }
    // --- END PYTHON FALLBACK ---
  }
}

export async function GET() {
  return Response.json({ 
    error: 'Method not allowed. Use POST instead.',
    usage: {
      method: 'POST',
      body: { url: 'https://youtube.com/watch?v=VIDEO_ID', language: 'en' }
    }
  }, { status: 405 });
}
